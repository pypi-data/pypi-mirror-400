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
              
    @staticmethod
    def copy_group(
        fname_cur,
        addr_cur,
        addr_new,
        fname_new=None,
        compression="default",
        conn_kwargs = {},
        **init_kwargs
        ):
        """Recursively copy group I guess"""
        # Create the new group
        if fname_new is None:
            fname_new = fname_cur
        # Open connection
        with CopyPair(fname_cur, fname_new, **conn_kwargs) as pair:
            # Identify current data
            if addr_cur not in pair.src.file:
                raise RuntimeError(f"No such dataset {addr_cor}")
            elif not isinstance(pair.src.file[addr_cur], h5py._hl.group.Group):
                raise TypeError(
                    f"Cannot use copy_group for {pair.src.file[addr_cur]}")
            ## Define maximum depth dset function ##
            def copy_dataset(cur, new):
                if compression == "default":
                    pair.src.file.copy(
                        pair.src.file[cur],
                        pair.out.file,
                        name=new,
                    )
                else:
                    # Create dataset
                    pair.out.file.create_dataset(
                        new,
                        pair.src.file[cur].shape,
                        dtype=dtype,
                        compression=compression,
                        **init_kwargs
                    )
                    # Copy values
                    pair.out.file[new][...] = pair.src.file[cur][...]

                # Copy attributes
                for key, value in pair.src.file[cur].attrs.items():
                    pair.out.file[new].attrs[key] = value

            ## Define recursive copy group function ##
            def copy_group(cur, new):
                # Create the group
                if new not in pair.out.file:
                    pair.out.file.create_group(new)
                # Copy the attributes
                for key, value in pair.src.file[cur].attrs.items():
                    pair.out.file[new].attrs[key] = value
                # Copy contents
                for item in pair.src.file[cur]:
                    # Get full path
                    cur_item = os.path.join(cur, item)
                    new_item = os.path.join(new, item)
                    if isinstance(pair.src.file[cur_item],h5py._hl.dataset.Dataset):
                        copy_dataset(cur_item, new_item)
                    elif isinstance(pair.src.file[cur_item],h5py._hl.group.Group):
                        copy_group(cur_item, new_item)
                    else:
                        raise TypeError(
                            f"Unknown type: {type(pair.src.file[cur_item])}"+\
                            f" for {pair.src.file[cur_item]}"
                        )
            ## Do the recursion ##
            copy_group(addr_cur, addr_new)

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

    def copy(
            self,
            other,
            compression="default",
            **init_kwargs
        ):
        """Instance method that calls DatasetHandle.copy_dataset"""
        if isinstance(other, str):
            fname_other = self.fname
            addr_other = other
            if self.readonly:
                raise ReadOnlyError
        elif isinstance(other, AddressHandle):
            if other.readonly: raise ReadOnlyError
            fname_other = other.fname
            addr_other = other.addr
        else:
            raise TypeError(f"Other has unknown type: {type(other)}")
        ## Do the recursion ##
        self.copy_group(
            self.fname,
            self.addr,
            addr_other,
            fname_new=fname_other,
            compression=compression,
            conn_kwargs = self.conn_kwargs,
            **init_kwargs
        )
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
