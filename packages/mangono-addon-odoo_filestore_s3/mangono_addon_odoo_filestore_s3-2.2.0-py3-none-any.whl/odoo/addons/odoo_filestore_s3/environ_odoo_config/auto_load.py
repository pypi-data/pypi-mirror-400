from environ_odoo_config.environ import Environ

from odoo.addons.odoo_filestore_s3.env_config import FilestoreS3EnvConfig


def auto_load_s3_filestore(environ: Environ) -> bool:
    s3_config = FilestoreS3EnvConfig(environ)
    return bool(s3_config.host and s3_config.secret and s3_config.access_key)
