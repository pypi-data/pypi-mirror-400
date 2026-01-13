import odoo.release


def _auto_load_cron_patch(environ) -> bool:
    return odoo.release.serie >= "15.0"
