from __future__ import annotations

from typing import Any

from environ_odoo_config.environ import Environ


def s3_mapper(curr_env: Environ | dict[str, Any]) -> Environ:
    return _s3filestore_compat(_s3_minio(_s3_clevercloud_cellar(Environ(curr_env))))


def _s3_clevercloud_cellar(curr_env: Environ) -> Environ:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "CELLAR_ADDON_HOST"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "CELLAR_ADDON_KEY_SECRET"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEY", "CELLAR_ADDON_KEY_ID"),
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "CELLAR_ADDON_REGION"),
    }


def _s3_minio(curr_env: Environ) -> Environ:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "MINIO_DOMAIN", "MINIO_HOST"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "MINIO_SECRET_KEY"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEY", "MINIO_ACCESS_KEY"),
        "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "MINIO_BUCKET"),
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "MINIO_REGION"),
        "S3_FILESTORE_SECURE": curr_env.gets("S3_FILESTORE_SECURE", "MINIO_SECURE"),
    }


def _s3filestore_compat(curr_env: Environ) -> Environ:
    """ """
    return curr_env + {
        "S3_FILESTORE_HOST": curr_env.gets("S3_FILESTORE_HOST", "ODOO_S3_HOST"),
        "S3_FILESTORE_SECRET_KEY": curr_env.gets("S3_FILESTORE_SECRET_KEY", "ODOO_S3_SECRET_KEY"),
        "S3_FILESTORE_ACCESS_KEY": curr_env.gets("S3_FILESTORE_ACCESS_KEY", "ODOO_S3_ACCESS_KEY"),
        "S3_FILESTORE_BUCKET": curr_env.gets("S3_FILESTORE_BUCKET", "ODOO_S3_BUCKET"),
        # Pas de region fournit par S3 CleverCloud
        "S3_FILESTORE_REGION": curr_env.gets("S3_FILESTORE_REGION", "ODOO_S3_REGION"),
        "S3_FILESTORE_SECURE": curr_env.gets("S3_FILESTORE_SECURE", "ODOO_S3_SECURE", "S3_SECURE"),
    }
