"""webdav_tck: WebDAV server protocol compliance test suite."""

from __future__ import annotations

try:
    from webdav_tck._version import (  # ty: ignore[unresolved-import]
        version as __version__,
    )
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
