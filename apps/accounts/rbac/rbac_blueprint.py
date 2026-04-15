# apps/accounts/services/rbac_blueprint.py

RBAC_BLUEPRINT = {

    "system": [
        "system.view",
        "system.manage",
    ],

    "user": [
        "user.view",
        "user.create",
        "user.update",
        "user.delete",
    ],

    "role": [
        "role.view",
        "role.create",
        "role.update",
        "role.delete",
    ],

    "company": [
        "company.view",
        "company.create",
        "company.update",
        "company.delete",
    ],

    "branch": [
        "branch.view",
        "branch.create",
        "branch.update",
        "branch.delete",
    ],
    
    "finance": [
    "close_period",
    "close_year",
]

}