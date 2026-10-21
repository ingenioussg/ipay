import sys
sys.path.append("../../")
from libraries.libraries import *

dashboard_main = Blueprint('dashboard_main', __name__, static_folder="static", template_folder="templates")


@dashboard_main.route("/dashboard", methods=["GET"])
def dashboard():
    if not g.company:
        return redirect(url_for("companies_main.companies"))
    c = g.company
    profile = registry.read(c["schema_name"])
    ids_done = (not c["sg_payroll"] or bool(profile.get("sg.uen"))) and (not c["my_payroll"] or bool(profile.get("my.epf_employer_no")))
    steps = [
        ("Create the company", True),
        ("Add statutory identifiers", ids_done),
        ("Add employees", False),
        ("Set up pay items", False),
        ("Run the first payroll", False),
    ]
    done = sum(1 for _s, ok in steps if ok)
    return render_template("dashboard.html", crumb="Overview", steps=steps,
                           progress=round(100 * done / len(steps)))
