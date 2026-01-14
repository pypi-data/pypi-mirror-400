import os

def get_wit_path() -> str:
    """Returns the absolute path to vtx.wit included in the package."""
    return os.path.join(os.path.dirname(__file__), "wit", "vtx.wit")

__all__ = [
    "get_wit_path",
]