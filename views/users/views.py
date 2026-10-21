import sys
sys.path.append("../../")
from libraries.libraries import *

users_main = Blueprint('users_main', __name__, static_folder="static", template_folder="templates")


def go(path):
    resp = make_response("", 200)
    resp.headers["HX-Location"] = path
    return resp


def _company_access(customer_id, f):
    """All companies, or a chosen subset of this customer's companies."""
    all_companies = f.get("all_companies") == "on"
    allowed = {c["id"] for c in companies_of(customer_id)}
    picks = [int(x) for x in f.getlist("company_ids") if x.isdigit() and int(x) in allowed]
    if not all_companies and not picks:
        return all_companies, picks, {"company_ids": "Choose at least one company, or allow all companies."}
    return all_companies, picks, {}


@users_main.route("/users", methods=["GET", "POST"])
def users():
    """A customer's users and roles. Platform admins work on the customer of the open company."""
    if not g.customer:
        return redirect(url_for("companies_main.companies"))
    cid = g.customer["id"]
    if request.method == "GET":
        return render_template("users.html", crumb="Users and roles", people=users_of(cid), roles=roles_of(cid),
                               company_list=companies_of(cid), areas=areas(),
                               labels={code: label for code, (_area, label) in PERMISSIONS.items()})

    f = request.form
    errors = new_user_errors(f.get("display_name"), f.get("email"), f.get("password"))
    if "email" not in errors and email_taken(f.get("email")):
        errors["email"] = "A user with this email already exists."
    role = role_of(cid, f.get("role_id"))
    if not role:
        errors["role_id"] = "Choose a role."
    all_companies, picks, more = _company_access(cid, f)
    errors.update(more)
    if errors:
        return jsonify(problem("User not added", "Fix the highlighted fields.", errors)), 422
    create_user(clean(f.get("display_name")), clean(f.get("email")), f.get("password"), customer_id=cid,
                role_id=role["id"], all_companies=all_companies, company_ids=picks)
    flash(f"{clean(f.get('display_name'))} added. Share the temporary password with them directly.")
    return go("/users")


@users_main.route("/users/update", methods=["POST"])
def update():
    if not g.customer:
        return jsonify(problem("No customer", "Open a company first.")), 409
    cid, f = g.customer["id"], request.form
    try:
        user_id = int(f.get("user_id", ""))
    except ValueError:
        return jsonify(problem("User not found", "That user does not exist.")), 404
    name = clean(f.get("display_name"))
    active = f.get("is_active") == "on"
    role = role_of(cid, f.get("role_id"))
    errors = {}
    if not 1 <= len(name) <= 80:
        errors["display_name"] = "Enter the person's name (up to 80 characters)."
    if not role:
        errors["role_id"] = "Choose a role."
    elif user_id == g.user["id"] and (not active or role["id"] != g.user["role_id"]):
        errors["role_id"] = "You cannot change your own role or disable yourself."
    all_companies, picks, more = _company_access(cid, f)
    errors.update(more)
    if errors:
        return jsonify(problem("User not saved", "Fix the highlighted fields. Nothing was changed.", errors)), 422
    if not update_user(cid, user_id, name, role["id"], active, all_companies, picks):
        return jsonify(problem("User not found", "That user is not part of this customer.")), 404
    flash(f"{name} saved.")
    return go("/users")


@users_main.route("/users/roles", methods=["POST"])
def roles():
    if not g.customer:
        return jsonify(problem("No customer", "Open a company first.")), 409
    cid, f = g.customer["id"], request.form
    existing = role_of(cid, f.get("role_id")) if f.get("role_id") else None
    if f.get("role_id") and (not existing or existing["is_admin"]):
        return jsonify(problem("Role cannot be changed", "The customer admin role always has every permission.")), 422
    name = clean(f.get("name"))
    errors = text_errors(name, "name", "Role name", 2, 60)
    if not errors and role_name_taken(cid, name, existing["id"] if existing else None):
        errors["name"] = "Another role already has this name."
    perms = [p for p in f.getlist("permissions") if p in PERMISSIONS]
    if not perms:
        errors["permissions"] = "Tick at least one permission."
    if errors:
        return jsonify(problem("Role not saved", "Fix the highlighted fields.", errors)), 422
    save_role(cid, name, perms, existing["id"] if existing else None)
    flash(f"Role {name} saved.")
    return go("/users")
