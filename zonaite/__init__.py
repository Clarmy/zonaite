"""Zonaite - 气象数据处理工具包"""

from zonaite.version import __version__

from .forecast import download_gfs_data  # noqa
from .obser import DecodedSynopCollector, get_decoded_synop_data  # noqa

__all__ = ["__version__"]
