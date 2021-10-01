from .base import _base_potc_cli
from .export import _export_cli
from .trans import _trans_cli
from .utils import _cli_builder

potc_cli = _cli_builder(
    _base_potc_cli,
    _trans_cli,
    _export_cli,
)
