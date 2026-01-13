#!/usr/env/bin python3
"""Create and manage base address handle class
"""
######## Imports ########
#### Standard Library ####
import os
import time
#### Third Party ####
import numpy as np
import h5py
#### Local ####
from xdata.error import *
from xdata.connection import *

######## Setup ########
__all__ = [
    "AddressHandle",
    "address_exists",
    "assert_address_exists",
]

FNAME_TEST = "test_address.hdf5"

######## Utilities ########
def address_exists(fname, addr, **kwargs):
    """Check if an address exists
    This one would otherwise be in the AddressHandle file,
        but is here instead to preserve dependency graph
    """
    # Check that file exists
    if not os.path.isfile(fname):   
        raise FileNotFoundError(f"No such file: {fname}")
    # Open connection
    with Connection(fname, 'r', **kwargs) as conn:
        if addr in conn.file:
            found = True
        else:
            found = False
    return found

def assert_address_exists(fname, addr, **kwargs):
    if not address_exists(fname, addr, **kwargs):
        address_not_found(fname, addr)

######## Objects ########
#### Generic Address Handle ####
class AddressHandle(object):
    """An object for groups and datasets in an hdf5 database"""
    def __init__(
            self, 
            fname, 
            addr, 
            readonly=False,
            **conn_kwargs
        ):
        self.fname = fname
        self.readonly = readonly
        self._conn_kwargs = conn_kwargs
        # Set addr last; order matters
        self.addr = addr

    # Handle fname property
    @property
    def fname(self):
        return self._fname
    @fname.setter
    def fname(self, value):
        if not os.path.isfile(value):
            raise FileNotFoundError(f"No such file {value}")
        self._fname = value

    # Handle readonly
    @property
    def readonly(self):
        return self._readonly
    @readonly.setter
    def readonly(self, value):
        self._readonly = bool(value)

    # Handle address
    @property
    def addr(self):
        return self._addr
    @addr.setter
    def addr(self, value):
        if self.readonly:
            assert_address_exists(self.fname, value, **self.conn_kwargs)
        self._addr = value

    # Handle other inputs
    @property
    def conn_kwargs(self):
        return self._conn_kwargs

    #### Static methods ####
    ## Readonly methods ##
    @staticmethod
    def check_exists(fname, addr, **kwargs):
        """Check if address exists"""
        return address_exists(fname, addr, **kwargs)
    @staticmethod
    def check_kind(fname, addr, **kwargs):
        """Check if address holds dset or group"""
        with Connection(fname, 'r', **kwargs) as conn:
            if addr == "/":
                return "group"
            elif addr not in conn.file:
                return None
            elif isinstance(conn.file[addr], h5py._hl.group.Group):
                return "group"
            elif isinstance(conn.file[addr], h5py._hl.dataset.Dataset):
                return "dset"
            else:
                raise TypeError(f"Unknown type: {type(conn.file[addr])}")

    ## Read / Write methods ##
    @staticmethod
    def remove_item(fname, addr, **kwargs):
        """Remove an item from the database"""
        with Connection(fname, 'r+', **kwargs) as conn:
            del conn.file[addr]

    #### Instance methods ####
    ## Readonly methods ##
    def exists(self):
        return self.check_exists(
            self.fname, 
            self.addr, 
            **self.conn_kwargs
        )
    @property
    def kind(self):
        return self.check_kind(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )
    ## Read / Write methods ##
    def remove(self):
        if self.readonly:
            raise ReadOnlyError(f"Cannot remove data in readonly mode!")
        self.remove_item(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

######## Tests ########
def test_address():
    with Connection(FNAME_TEST, 'w') as conn:
        pass
    if not os.path.isfile(FNAME_TEST):
        raise RuntimeError(f"touch command failed!")
    group1 = "apples"
    if address_exists(FNAME_TEST, group1):
        raise RuntimeError(f"Group {group1} should not exist in {FNAME_TEST}")
    addr1 = AddressHandle(FNAME_TEST,group1)
    assert os.path.isfile(addr1.fname)
    assert isinstance(addr1.readonly, bool)
    assert isinstance(addr1.addr, str)
    assert not addr1.exists()
    with Connection(FNAME_TEST, 'a') as conn:
        conn.file.create_group(group1)
    assert_address_exists(FNAME_TEST, group1)
    assert addr1.exists()
    addr1.remove()
    assert not addr1.exists()
    return

######## Execution ########
if __name__ == "__main__":
    test_address()
