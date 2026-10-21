import sys
sys.path.append("../../")
from libraries.libraries import *

# Include-only controller: registered so its templates/ is on the search path.
preloginnavbar_main = Blueprint("preloginnavbar_main", __name__, static_folder="static", template_folder="templates")
