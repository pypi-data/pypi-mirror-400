from __future__ import annotations

import base64
import logging
import os
from typing import TYPE_CHECKING, BinaryIO, Callable

try:
    from odoo.exceptions import UserError
except ImportError:

    class UserError(Exception): ...


if TYPE_CHECKING:
    import odoo.model.ir_attachment

from .odoo_s3_fs import S3Odoo

_logger = logging.getLogger(__name__)


class OdooS3Error(UserError):
    """S3 error class to filter them from UserError when catching them
    Not just S3Error because Minio already has an error class named like this"""


class IrAttachementAdapter:
    def __init__(self, odoo_version: float | int):
        self.use_b64 = odoo_version < 14

    @staticmethod
    def remove_from_cache(attachement: "odoo.model.ir_attachment", store_fname: str = None) -> str | None:
        if full_path := IrAttachementAdapter.exist_in_cache(attachement, store_fname):
            _logger.debug("Removing %s", full_path)
            os.remove(full_path)
        return full_path

    @staticmethod
    def exist_in_cache(attachement: "odoo.model.ir_attachment", store_fname: str = None) -> str | None:
        full_path = attachement._full_path(store_fname or attachement.store_fname)
        return full_path if os.path.exists(full_path) else None

    def file_read(
        self, odoo_inst: "odoo.model.ir_attachment", fname: str, *, _origin: Callable[[], bytes | str | int]
    ) -> BinaryIO | str | int:
        s3 = S3Odoo.from_env(odoo_inst.env.cr.dbname)
        if not s3.conn.enable:
            return _origin()
        if IrAttachementAdapter.exist_in_cache(odoo_inst, fname):
            return _origin()
        res = s3.file_read(fname)
        if not res:
            return _origin()
        try:
            checksum = odoo_inst._compute_checksum(res)
            odoo_inst.with_context(_no_s3_wrap=True)._file_write(self.encode_content(res), checksum)
        except Exception:
            _logger.debug("Failed to write in cache")
        return _origin()

    def decode_content(self, content: str | bytes) -> bytes:
        if not self.use_b64:
            return content
        return base64.b64decode(content)

    def encode_content(self, content: str | bytes) -> str | bytes:
        if not self.use_b64:
            return content
        return base64.b64encode(content)

    def file_write(
        self, odoo_inst: "odoo.model.ir_attachment", content: [bytes, str], checksum: str, *, _origin: Callable[[], str]
    ) -> str:
        # content is passed as `value` in V11, V12, V13 and as `bin_value` in V14, V15
        s3 = S3Odoo.from_env(odoo_inst.env.cr.dbname)
        fname = _origin()
        if not s3.conn.enable:
            return fname
        try:
            bin_content = self.decode_content(content)
            s3.file_write(fname, bin_content)
        except Exception as e:
            raise OdooS3Error(f"_file_write was not able to write ({fname})") from e
        return fname

    def mark_for_gc(self, odoo_inst: "odoo.model.ir_attachment", fname, *, _origin: Callable[[], None]):
        _origin()
        if odoo_inst.env.context.get("s3_no_gc"):
            return
        s3 = S3Odoo.from_env(odoo_inst.env.cr.dbname)
        if not s3.conn.enable:
            _logger.debug("S3: _file_delete bypass to filesystem storage")
        try:
            s3.mark_for_gc(fname)
        except Exception as err:
            raise OdooS3Error(f"Can't mark for Gc the file: {fname}") from err
