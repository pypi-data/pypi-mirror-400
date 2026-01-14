from __future__ import annotations

from environ_odoo_config.config_section.api import OdooConfigGroup, SimpleKey
from minio import Minio


class FilestoreS3EnvConfig(OdooConfigGroup):
    _ini_section = "odoo_s3_filestore"

    access_key: str = SimpleKey("S3_FILESTORE_ACCESS_KEY", ini_dest="s3_access_key")
    secret: str = SimpleKey("S3_FILESTORE_SECRET_KEY", ini_dest="s3_secret")
    region: str = SimpleKey("S3_FILESTORE_REGION", ini_dest="s3_region", py_default="us-east-1")
    host: str = SimpleKey("S3_FILESTORE_HOST", ini_dest="s3_host")
    bucket_name: str = SimpleKey("S3_FILESTORE_BUCKET", ini_dest="s3_bucket_name")
    secure: bool = SimpleKey("S3_FILESTORE_SECURE", py_default=True, ini_dest="s3_secure")
    sub_dir: bool = SimpleKey("S3_FILESTORE_SUB_DIR", ini_dest="sub_dir_by_dbname")

    @property
    def enable(self) -> bool:
        return bool(self.host and self.secret and self.access_key)

    @property
    def s3_session(self) -> Minio:
        return Minio(
            endpoint=self.host,
            access_key=self.access_key,
            secret_key=self.secret,
            region=self.region,
            secure=self.secure,
        )
