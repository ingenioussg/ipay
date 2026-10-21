import sys
sys.path.append("../../")
from libraries.libraries import *

admin_main = Blueprint('admin_main', __name__, static_folder="static", template_folder="templates")


def go(path):
    resp = make_response("", 200)
    resp.headers["HX-Location"] = path
    return resp


@admin_main.route("/admin", methods=["GET", "POST"])
def admin():
    """Platform admin: customers, which payroll countries each may use, and their first admin."""
    if request.method == "GET":
        return render_template("admin.html", crumb="Customers", customer_list=customers())

    f = request.form
    name = clean(f.get("name"))
    sg, my = f.get("sg_payroll") == "on", f.get("my_payroll") == "on"
    errors = {**text_errors(name, "name", "Customer name"), **country_errors(sg, my),
              **new_user_errors(f.get("admin_display_name"), f.get("admin_email"), f.get("admin_password"), prefix="admin_")}
    if "admin_email" not in errors and email_taken(f.get("admin_email")):
        errors["admin_email"] = "A user with this email already exists."
    if errors:
        return jsonify(problem("Customer not created", "Fix the highlighted fields.", errors)), 422
    create_customer(name, sg, my, clean(f.get("admin_display_name")), clean(f.get("admin_email")), f.get("admin_password"))
    flash(f"{name} created. Its admin can sign in now.")
    return go("/admin")


@admin_main.route("/admin/customer", methods=["POST"])
def customer():
    f = request.form
    current = get_customer(f.get("customer_id"))
    if not current:
        return jsonify(problem("Customer not found", "That customer does not exist.")), 404
    name = clean(f.get("name"))
    sg, my = f.get("sg_payroll") == "on", f.get("my_payroll") == "on"
    errors = {**text_errors(name, "name", "Customer name"), **country_errors(sg, my)}
    used = countries_in_use(current["id"])
    blocked = [f"{label} payroll is used by {', '.join(names)}" for on, names, label in
               ((sg, used["sg"], "Singapore"), (my, used["my"], "Malaysian")) if not on and names]
    if blocked:
        errors["countries"] = "; ".join(blocked) + ". Turn it off in those companies first."
    if errors:
        return jsonify(problem("Customer not saved", "Fix the highlighted fields. Nothing was changed.", errors)), 422
    update_customer(current["id"], name, sg, my, f.get("is_active") == "on")
    flash(f"{name} saved.")
    return go("/admin")
