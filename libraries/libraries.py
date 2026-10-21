import os
import sys
import json
import hmac
from functools import wraps
from flask import Flask, render_template, url_for, Blueprint, redirect, request, session, jsonify, make_response, abort, flash, g

# Business logic lives in modules/. Views reach it through here, like everything else.
from modules.security.csrf import csrf_token, csrf_valid
from modules.web.feedback import problem, toast_header
from modules.settings.validation import (
    clean, company_name_errors, country_errors, identifier_errors, account_errors, SG_FIELDS, MY_FIELDS,
)
from modules.settings import registry
from modules.platform.users import (
    user_count, create_user, authenticate, get_user, too_many_failures, record_failure, clear_failures,
)
from modules.platform.companies import companies_for, company_for, create_company, update_company
