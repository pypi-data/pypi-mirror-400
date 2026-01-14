{
    "name": "Redis Session Store",
    "version": "2.1.2",
    "depends": ["base"],
    "author": "mangono",
    "website": "http://mangono.fr/",
    "license": "AGPL-3",
    "description": """Use Redis Session instead of File system to store sessions""",
    "summary": "",
    "category": "Tools",
    "auto_install": False,
    "installable": False,
    "application": False,
    "post_load": "_post_load_module",
    "external_dependencies": {
        "python": ["redis"],
    },
}
