from __future__ import annotations

import functools
import logging
import os
from typing import TYPE_CHECKING, BinaryIO, Callable, Sequence

import wrapt

from .s3_api.adapter import IrAttachementAdapter

if TYPE_CHECKING:
    import odoo.model.ir_attachment

try:
    from odoo import api, release

    _odoo_version = release.version_info[0]
except ImportError:
    _odoo_version = float(os.getenv("ODOO_VERSION", "0"))

    class _Api:
        def model(self, f):
            return f

        def mutli(self, f):
            return f

        def autovacuum(self, f):
            return f

    api = _Api()

_BASE_MODULE = "odoo.addons.base"
_IR_ATTACHEMENT_CLASS = "models.ir_attachment.IrAttachment"
base64_value = _odoo_version <= 14
_logger = logging.getLogger(__name__)


def _no_call_adapter(instance: "odoo.model.ir_attachment" | None):
    if instance is None:
        return True
    return instance.env.context.get("_no_s3_wrap") or instance.env.context.get("force_attachment_storage", "s3") != "s3"


def _extract_value(args: Sequence, kwargs: dict, *, key: str, idx: int, default=None):
    _default = default
    if len(args) >= idx + 1:
        _default = args[idx]
    return kwargs.get(key, _default)


def dummy_read() -> bytes:
    return b""


def patch_function(module: str, name: str, enabled: bool = True):
    _logger.info("Activate monkey patch on %s#%s -> %s", module, name, enabled)
    if not enabled:

        def pass_wrapper(wrapper):
            return wrapper

        return pass_wrapper
    return wrapt.patch_function_wrapper(module, name)


@patch_function(_BASE_MODULE, f"{_IR_ATTACHEMENT_CLASS}._file_read")
@api.model
def _s3_file_read_wrapper(wrapped, instance: "odoo.model.ir_attachment", args, kwargs) -> BinaryIO | str | int:
    patched_func = functools.partial(wrapped, *args, **kwargs)
    if _no_call_adapter(instance):
        return patched_func()

    fname = _extract_value(args, kwargs, key="fname", idx=0)
    bin_size = _extract_value(args, kwargs, key="bin_size", idx=1, default=False)
    if bin_size:
        if not IrAttachementAdapter.exist_in_cache(instance, fname):
            IrAttachementAdapter(_odoo_version).file_read(instance, fname, _origin=dummy_read)
        return patched_func()
    return IrAttachementAdapter(_odoo_version).file_read(instance, fname, _origin=patched_func)


@patch_function(_BASE_MODULE, f"{_IR_ATTACHEMENT_CLASS}._file_write")
@api.model
def _s3_file_write_wrapper(
    wrapped,
    instance: "odoo.model.ir_attachment",
    args: Sequence[str | BinaryIO],
    kwargs: dict[str, str | BinaryIO],
) -> str:
    patched_func = functools.partial(wrapped, *args, **kwargs)
    if _no_call_adapter(instance):
        return patched_func()

    if _odoo_version < 14:
        content = _extract_value(args, kwargs, key="value", idx=0)
    else:
        content = _extract_value(args, kwargs, key="bin_value", idx=0)
    checksum = _extract_value(args, kwargs, key="checksum", idx=1)
    return IrAttachementAdapter(_odoo_version).file_write(instance, content, checksum, _origin=patched_func)


@patch_function(_BASE_MODULE, f"{_IR_ATTACHEMENT_CLASS}._storage")
@api.model
def _storage(wrapped: Callable[[], str], instance, args, kwargs) -> str:
    patched_func = functools.partial(wrapped, *args, **kwargs)
    if _no_call_adapter(instance):
        return patched_func()
    return "s3"


@patch_function(_BASE_MODULE, f"{_IR_ATTACHEMENT_CLASS}._mark_for_gc")
def _mark_for_gc(wrapped: Callable[[str], None], instance, args, kwargs):
    patched_func = functools.partial(wrapped, *args, **kwargs)
    if _no_call_adapter(instance):
        return patched_func()
    fname = _extract_value(args, kwargs, key="fname", idx=0)
    return IrAttachementAdapter(_odoo_version).mark_for_gc(instance, fname, _origin=patched_func)


@patch_function("odoo", "http.Stream.from_attachment", enabled=16 <= _odoo_version <= 17)
def _patch_from_attachment(wrapped, instance, args, kwargs):
    attachment = _extract_value(args, kwargs, key="attachment", idx=0)
    IrAttachementAdapter(_odoo_version).file_read(attachment, attachment.store_fname, _origin=dummy_read)
    return wrapped(*args, **kwargs)


@patch_function(_BASE_MODULE, f"{_IR_ATTACHEMENT_CLASS}._to_http_stream", enabled=_odoo_version >= 18)
def _patch_to_http_stream(wrapped, instance, args, kwargs):
    if instance and instance.store_fname:
        IrAttachementAdapter(_odoo_version).file_read(instance, instance.store_fname, _origin=dummy_read)
    return wrapped(*args, **kwargs)
