"""
This lib is used to sign a request using aws signature version 4. You
need to provide a python dict which represent your request(it typically
contains `verb`, `uri`, `args`, `headers`, `body`), and your access key
and your secret key. This lib will add signature to the request.
"""

from importlib.metadata import version

from .awssign import (
    Signer,
)

__version__ = version("k3awssign")
__name__ = "k3awssign"

__all__ = [
    "Signer",
]
