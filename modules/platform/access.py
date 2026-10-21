"""Access rights: the permission catalogue, the roles every new customer starts with,
and the checks. Pure functions over user dicts: no Flask, no SQL.
"""

from __future__ import annotations

# code -> (area, what it allows). Areas group the checkboxes in the role editor.
PERMISSIONS = {
    "employees.view": ("Employees", "View employees"),
    "employees.edit": ("Employees", "Add and edit employees"),
    "salary.view": ("Employees", "See salaries and pay amounts"),
    "payroll.view": ("Payroll", "View pay runs and payslips"),
    "payroll.run": ("Payroll", "Prepare and calculate pay runs"),
    "payroll.approve": ("Payroll", "Approve and lock pay runs"),
    "leave.view": ("Leave", "View leave"),
    "leave.edit": ("Leave", "Record and approve leave"),
    "statutory.submit": ("Statutory", "Create CPF, IRAS, EPF, SOCSO and LHDN files"),
    "reports.view": ("Reports", "View and export reports"),
    "settings.manage": ("Company", "Change company settings"),
    "companies.manage": ("Company", "Add companies"),
    "users.manage": ("Company", "Manage users and roles"),
}
ALL = frozenset(PERMISSIONS)

# (name, permissions, is_admin). The admin role always means every permission.
DEFAULT_ROLES = [
    ("Customer admin", sorted(ALL), True),
    ("Payroll manager", ["employees.view", "employees.edit", "salary.view", "payroll.view", "payroll.run",
                         "payroll.approve", "leave.view", "leave.edit", "statutory.submit", "reports.view"], False),
    ("Payroll officer", ["employees.view", "salary.view", "payroll.view", "payroll.run", "leave.view",
                         "leave.edit", "reports.view"], False),
    ("HR officer", ["employees.view", "employees.edit", "leave.view", "leave.edit"], False),
    ("Viewer", ["employees.view", "payroll.view", "leave.view", "reports.view"], False),
]


def areas() -> dict:
    """Permissions grouped by area, in catalogue order, for the role editor."""
    grouped: dict = {}
    for code, (area, label) in PERMISSIONS.items():
        grouped.setdefault(area, []).append((code, label))
    return grouped


def permissions_of(user: dict | None) -> frozenset:
    if not user or not user.get("is_active", True):
        return frozenset()
    if user.get("is_platform_admin") or user.get("role_is_admin"):
        return ALL
    return frozenset(user.get("permissions") or ()) & ALL


def can(user: dict | None, permission: str) -> bool:
    return permission in permissions_of(user)


def is_platform_admin(user: dict | None) -> bool:
    return bool(user and user.get("is_platform_admin"))
