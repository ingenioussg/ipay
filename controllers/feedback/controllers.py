import sys
sys.path.append("../../")
from libraries.libraries import *

# Include-only controller: registered so its templates/ is on the search path.
feedback_main = Blueprint("feedback_main", __name__, static_folder="static", template_folder="templates")
