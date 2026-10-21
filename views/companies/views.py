import sys
sys.path.append("../../")
from libraries.libraries import *

companies_main = Blueprint('companies_main', __name__, static_folder="static", template_folder="templates")


def go(path):
    resp = make_response("", 200)
    resp.headers["HX-Location"] = path
    return resp


@companies_main.route("/companies", methods=["GET", "POST"])
def companies():
    admin = is_platform_admin(g.user)
    if request.method == "GET":
        return render_template("companies.html", crumb="Companies", companies=companies_for(g.user),
                               customer_list=customers() if admin else [])

    f = request.form
    owner = get_customer(f.get("customer_id") if admin else g.user["customer_id"])
    if not owner:
        return jsonify(problem("Choose a customer", "Pick the customer this company belongs to.",
                               {"customer_id": "Choose a customer."})), 422
    name = clean(f.get("name"))
    sg, my = f.get("sg_payroll") == "on", f.get("my_payroll") == "on"
    errors = {**company_name_errors(name), **country_errors(sg, my),
              **entitlement_errors(owner["sg_payroll"], owner["my_payroll"], sg, my)}
    if errors:
        return jsonify(problem("Company not created", "Fix the highlighted fields.", errors)), 422
    created = create_company(owner["id"], name, sg, my)
    session["company_id"] = created["id"]
    flash(f"{name} created. Add its statutory identifiers next.")
    return go("/settings")


@companies_main.route("/companies/switch", methods=["POST"])
def switch():
    company = company_for(g.user, request.form.get("company_id"))
    if not company:
        return jsonify(problem("Company not found", "You do not have access to that company.")), 404
    session["company_id"] = company["id"]
    flash(f"Switched to {company['name']}.")
    return go("/dashboard")
