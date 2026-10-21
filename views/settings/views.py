import sys
sys.path.append("../../")
from libraries.libraries import *

settings_main = Blueprint('settings_main', __name__, static_folder="static", template_folder="templates")


@settings_main.route("/settings", methods=["GET", "POST"])
def settings():
    if not g.company:
        return redirect(url_for("companies_main.companies"))
    schema = g.company["schema_name"]
    if request.method == "GET":
        return render_template("settings.html", crumb="Settings", profile=registry.read(schema),
                               sg_fields=SG_FIELDS, my_fields=MY_FIELDS)

    f = request.form
    name = clean(f.get("name"))
    sg, my = f.get("sg_payroll") == "on", f.get("my_payroll") == "on"
    values = {k: clean(f.get(k)).upper() for k in (*SG_FIELDS, *MY_FIELDS)}
    # Only the countries turned on are checked; a hidden section's values are kept as they are.
    checked = {k: v for k, v in values.items() if (sg and k in SG_FIELDS) or (my and k in MY_FIELDS)}
    errors = {**company_name_errors(name), **country_errors(sg, my), **identifier_errors(checked),
              **entitlement_errors(g.customer["sg_payroll"], g.customer["my_payroll"], sg, my)}
    if errors:
        return jsonify(problem("Settings not saved", "Fix the highlighted fields. Nothing was changed.", errors)), 422
    update_company(g.company["id"], name, sg, my)
    registry.write(schema, values)
    flash("Settings saved.")
    resp = make_response("", 200)
    resp.headers["HX-Location"] = "/settings"
    return resp
