"""Errors for xdata module"""
######## All ########
__all__ = [
    "AddressNotFoundError",
    "AttributeNotFoundError",
    "WrongH5ItemKind",
    "ReadOnlyError",
    "address_not_found",
    "attribute_not_found",
]
######## Errors ########
class AddressNotFoundError(ValueError):
    """A ValueError for a missing attribute"""
    pass

class AttributeNotFoundError(ValueError):
    """A ValueError for a missing attribute"""
    pass

class WrongH5ItemKind(ValueError):
    """An error for trying to access dataset attributes of groups, etc..."""

class ReadOnlyError(RuntimeError):
    """An error for trying to write to a readonly file"""

def address_not_found(fname, addr):
    raise AddressNotFoundError(f"Cannot find address: {addr} in {fname}")

def attribute_not_found(fname, addr, key):
    raise AttributeNotFoundError(
        f"Cannot find attribute {key} at address {addr} in {fname}")
