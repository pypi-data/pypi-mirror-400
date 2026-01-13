#!/usr/env/bin python3
"""Create and manage address handle for groups
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
from xdata.address import *
from xdata.attributes import *

######## Setup ########
__all__ = [
    "GroupHandle",
]

FNAME_TEST = "test_group.hdf5"

######## Objects ########
#### Group Handle ####
class GroupHandle(AddressHandle):
    """An object for groups in an hdf5 database"""
    def __init__(
            self, 
            fname, 
            addr, 
            **kwargs
        ):
        # Initialize address
        super().__init__(fname, addr, **kwargs)
        # Initialize attributes
        self.attrs = AttributesHandle(fname, addr, **kwargs)
        # Make sure this is a group
        if self.kind not in ["group", None]:
            raise ValueError(
                f"Address {addr} in {fname} is kind {self.kind} " + \
                f"(and is not Group)!"
            )

    #### Static methods ####
    ## Readonly methods ##
    @staticmethod
    def list_items(
            fname,
            addr,
            kind = None,
            **kwargs
        ):
        """List the items in a group"""
        with Connection(fname, 'r', **kwargs) as conn:
            # Initialize list
            items = []
            # Loop current group
            for item in conn.file[addr]:
                # Initialize append
                append = False

                # Keep track of what you want to append
                if kind is None:
                    append = True
                elif kind == "group":
                    if isinstance(conn.file[addr][item],h5py._hl.group.Group):
                        append = True
                elif kind == "dset":
                    if isinstance(conn.file[addr][item],h5py._hl.dataset.Dataset):
                        append = True
                else:
                    raise RuntimeError(f"kind is type {type(kind)}")
                
                if append:
                    items.append(item)
        return items

    ## Read / Write methods ##
    @staticmethod
    def create_group(fname, addr, force=False, **kwargs):
        """Create a group within an hdf5 database"""
        with Connection(fname, 'r+', **kwargs) as conn:
            if addr not in conn.file:
                conn.file.create_group(addr)
            elif force:
                pass
            else:
                raise RuntimeError(
                    f"Group {addr} already exists in {fname}!")
              
    #### Instance methods ####
    ## Readonly methods ##
    def list(
        self,
        kind=None,
        ):
        """List items in *this* group"""
        return self.list_items(
            self.fname,
            self.addr,
            kind=kind,
            **self.conn_kwargs
        )
        
    ## Read / Write methods ##
    def create_subgroup(self, key, force=False):
        if self.readonly:
            raise ReadOnlyError
        if self.kind != "group":
            raise WrongH5ItemKind(
                f"Cannot create group over {self.kind} " + \
                f"at {addr} in {fname}"
            )
        if key.startswith("/"):
            path = key
        else:
            path = os.path.join(self.addr, key)
        self.create_group(
            self.fname, 
            path,
            force=force, 
            **self.conn_kwargs
        )
    
    # Alias
    def create(self, *args, **kwargs):
        self.create_subgroup(*args, **kwargs)

######## Tests ########

def test_group():
    group1 = "apples"
    group2 = "oranges"
    group3 = "/"
    group4 = "five"
    with Connection(FNAME_TEST, 'w') as conn:
        conn.file.create_group(group1)
    slash = GroupHandle(FNAME_TEST, group3)
    assert group1 in slash.list()
    assert group2 not in slash.list()
    slash.create_subgroup(group2)
    assert group1 in slash.list()
    assert group2 in slash.list()
    oranges = GroupHandle(FNAME_TEST, group2)
    oranges.create_subgroup(group4)
    assert not group4 in slash.list()
    assert group4 in oranges.list()
    return

######## Execution ########
if __name__ == "__main__":
    test_group()
