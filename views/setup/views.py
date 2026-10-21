import sys
sys.path.append("../../")
from libraries.libraries import *

setup_main = Blueprint('setup_main', __name__, static_folder="static", template_folder="templates")


def token_ok():
    """On a server, setup needs SETUP_TOKEN (from .env) so a stranger cannot claim the workspace first."""
    expected = os.getenv("SETUP_TOKEN", "")
    if not expected:
        return True  # local development
    sent = request.args.get("token") or request.form.get("token") or ""
    return hmac.compare_digest(expected.encode(), sent.encode())


@setup_main.route("/setup", methods=["GET", "POST"])
def setup():
    """First run only: create the owner account. Closed once any user exists."""
    if not token_ok():
        if request.method == "POST":
            return jsonify(problem("Setup is locked", "Open the setup link that includes the setup token.")), 403
        return render_template("error.html", code=403, title="Setup is locked",
                               message="Open the setup link that includes the setup token."), 403
    if user_count() > 0:
        if request.method == "POST":
            return jsonify(problem("Already set up", "An owner account exists. Sign in instead.")), 409
        return redirect(url_for("login_main.login"))
    if request.method == "GET":
        return render_template("setup.html")

    f = request.form
    errors = account_errors(f.get("display_name"), f.get("email"), f.get("password"), f.get("confirm"))
    if errors:
        return jsonify(problem("Check the highlighted fields", "Your account was not created.", errors)), 422
    user = create_user(f["display_name"], f["email"], f["password"], is_owner=True)
    session.clear()
    session["user_id"] = user["id"]
    flash("Owner account created. Now add your first company.")
    resp = make_response("", 200)
    resp.headers["HX-Location"] = "/companies"
    return resp
