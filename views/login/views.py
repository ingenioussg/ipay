import sys
sys.path.append("../../")
from libraries.libraries import *

login_main = Blueprint('login_main', __name__, static_folder="static", template_folder="templates")


def go(path):
    """Reply that makes htmx navigate (smoothly, without a full reload) to path."""
    resp = make_response("", 200)
    resp.headers["HX-Location"] = path
    return resp


@login_main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if user_count() == 0:
            return redirect(url_for("setup_main.setup"))
        if g.user:
            return redirect(url_for("dashboard_main.dashboard"))
        return render_template("login.html")

    email = request.form.get("email")
    if too_many_failures(email):
        return jsonify(problem("Too many attempts", "Sign-in for this account is paused. Try again in 15 minutes.")), 429
    user = authenticate(email, request.form.get("password"))
    if not user:
        record_failure(email, request.remote_addr)
        return jsonify(problem("Sign-in failed", "The email or password is incorrect.",
                               {"password": "Check your email and password, then try again."})), 422
    if not is_enabled(user):
        return jsonify(problem("Account disabled", "This account or its customer is disabled. Contact your administrator.")), 403
    clear_failures(email)
    session.clear()  # a fresh session on sign-in: no fixation
    session["user_id"] = user["id"]
    mine = companies_for(user)
    if len(mine) == 1:
        session["company_id"] = mine[0]["id"]
    flash(f"Welcome back, {user['display_name']}.")
    if session.get("company_id"):
        return go("/dashboard")
    return go("/admin" if user["is_platform_admin"] else "/companies")


@login_main.route("/login/logout", methods=["POST"])
def logout():
    session.clear()
    resp = make_response("", 200)
    resp.headers["HX-Redirect"] = "/login"
    return resp
