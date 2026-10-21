from dotenv import load_dotenv

load_dotenv()  # before anything reads the environment; real values live in .env (gitignored)

from libraries.libraries import *

from views.login.views import login_main
from views.setup.views import setup_main
from views.admin.views import admin_main
from views.dashboard.views import dashboard_main
from views.companies.views import companies_main
from views.settings.views import settings_main
from views.users.views import users_main
from controllers.head.controllers import head_main
from controllers.feedback.controllers import feedback_main
from controllers.preloginnavbar.controllers import preloginnavbar_main
from controllers.postloginnavbar.controllers import postloginnavbar_main

app = Flask(__name__)
app.debug = False  # IMPORTANT: Keep False in production!

app.secret_key = os.getenv("FLASK_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError(
        "FLASK_SECRET_KEY is not set. Generate one with:\n"
        '  python -c "import secrets; print(secrets.token_hex(32))"\n'
        "then put it in .env."
    )

if os.getenv("TRUST_PROXY") == "1":
    # Behind the HTTPS proxy: take client IP and scheme from its X-Forwarded-* headers (one hop).
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

DEMO = os.getenv("IPAY_DEMO") == "1"

app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = os.getenv("SESSION_COOKIE_SECURE", "0") == "1"

# ---------------------------------------------------------------------------
# Access map: endpoint -> {method: what it needs}. Checked on every request.
#   None        signed in (and enabled)
#   "platform"  platform admin only
#   "<code>"    a permission from modules/platform/access.py
# An endpoint or method missing from this map is refused: new routes must be declared.
# ---------------------------------------------------------------------------
PUBLIC = {"static", "index", "login_main.login", "setup_main.setup"}
ACCESS = {
    "login_main.logout": {"POST": None},
    "dashboard_main.dashboard": {"GET": None},
    "companies_main.companies": {"GET": None, "POST": "companies.manage"},
    "companies_main.switch": {"POST": None},
    "settings_main.settings": {"GET": "settings.manage", "POST": "settings.manage"},
    "users_main.users": {"GET": "users.manage", "POST": "users.manage"},
    "users_main.update": {"POST": "users.manage"},
    "users_main.roles": {"POST": "users.manage"},
    "admin_main.admin": {"GET": "platform", "POST": "platform"},
    "admin_main.customer": {"POST": "platform"},
}


def _asset_version():
    """Newest mtime across CSS/JS, as a cache-busting stamp."""
    newest = 0
    for sub in ("css", "javascript"):
        for dirpath, _dirs, files in os.walk(os.path.join(app.static_folder, sub)):
            for name in files:
                try:
                    newest = max(newest, os.stat(os.path.join(dirpath, name)).st_mtime)
                except OSError:
                    pass
    return str(int(newest))


@app.context_processor
def inject_globals():
    if app.debug or not hasattr(app, "_asset_v"):
        app._asset_v = _asset_version()
    user = g.get("user")
    return {"v": app._asset_v, "csrf_token": lambda: csrf_token(session), "demo": DEMO,
            "user": user, "company": g.get("company"), "customer": g.get("customer"),
            "can": lambda permission: can(user, permission), "is_platform_admin": is_platform_admin(user)}


def deny(title="Not allowed", message="Your role does not allow this. Ask your administrator.", status=403):
    if request.headers.get("HX-Request"):
        return jsonify(problem(title, message)), status
    return render_template("error.html", code=status, title=title, message=message), status


def _customer_of(user, company):
    """The customer in context: the user's own, or (for a platform admin) the open company's."""
    if user and not user["is_platform_admin"]:
        return {"id": user["customer_id"], "name": user["customer_name"],
                "sg_payroll": user["customer_sg"], "my_payroll": user["customer_my"]}
    if company:
        return {"id": company["customer_id"], "name": company["customer_name"],
                "sg_payroll": company["customer_sg"], "my_payroll": company["customer_my"]}
    return None


@app.before_request
def guard():
    """Sign-in, CSRF and access rights for every request, so no view can forget them."""
    if request.endpoint == "static":
        return None
    if request.method in ("POST", "PUT", "PATCH", "DELETE"):
        sent = request.headers.get("X-CSRF-Token") or request.form.get("csrf")
        if not csrf_valid(session, sent):
            return jsonify(problem("Page expired", "Reload the page and try again.")), 403

    user = get_user(session["user_id"]) if session.get("user_id") else None
    if user and not is_enabled(user):
        user = None
    g.user = user
    g.company = company_for(user, session.get("company_id")) if user else None
    g.customer = _customer_of(user, g.company)

    if request.endpoint in PUBLIC:
        return None
    if request.endpoint is None:
        return None  # unknown URL: let the 404 handler answer
    if not user:
        # Drop only the sign-in keys: clearing the whole session would also drop the CSRF token.
        session.pop("user_id", None)
        session.pop("company_id", None)
        if request.headers.get("HX-Request"):
            return jsonify(problem("Signed out", "Your session has ended. Sign in again.")), 401
        return redirect(url_for("login_main.login"))

    rule = ACCESS.get(request.endpoint, {})
    if request.method not in rule:
        return deny()
    need = rule[request.method]
    if need == "platform" and not is_platform_admin(user):
        return deny()
    if need not in (None, "platform") and not can(user, need):
        return deny()
    return None


@app.route("/")
def index():
    if user_count() == 0:
        return redirect(url_for("setup_main.setup"))
    if not g.user:
        return redirect(url_for("login_main.login"))
    if is_platform_admin(g.user) and not g.company:
        return redirect(url_for("admin_main.admin"))
    return redirect(url_for("dashboard_main.dashboard"))


@app.after_request
def no_store(response):
    # Payroll data: nothing but static assets may be kept by a browser or a cache.
    if not request.path.startswith("/static/"):
        response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.errorhandler(404)
def not_found(_e):
    if request.headers.get("HX-Request"):
        return jsonify(problem("Not found", "That page or record does not exist.")), 404
    return render_template("error.html", code=404, title="Page not found",
                           message="The page you asked for does not exist."), 404


@app.errorhandler(500)
def server_error(_e):
    if request.headers.get("HX-Request"):
        return jsonify(problem("Something went wrong", "The server hit an error. Nothing was saved.")), 500
    return render_template("error.html", code=500, title="Something went wrong",
                           message="The server hit an error. Nothing was saved."), 500

# ---------------------------------------------------------------------------
# Blueprint registrations
# ---------------------------------------------------------------------------

app.register_blueprint(login_main, url_prefix="/")
app.register_blueprint(setup_main, url_prefix="/")
app.register_blueprint(admin_main, url_prefix="/")
app.register_blueprint(dashboard_main, url_prefix="/")
app.register_blueprint(companies_main, url_prefix="/")
app.register_blueprint(settings_main, url_prefix="/")
app.register_blueprint(users_main, url_prefix="/")
app.register_blueprint(head_main, url_prefix="/")
app.register_blueprint(feedback_main, url_prefix="/")
app.register_blueprint(preloginnavbar_main, url_prefix="/")
app.register_blueprint(postloginnavbar_main, url_prefix="/")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=4000, debug=True)
