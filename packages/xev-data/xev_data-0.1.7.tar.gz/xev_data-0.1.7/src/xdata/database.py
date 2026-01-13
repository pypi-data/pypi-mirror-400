#!/usr/bin/env python3
'''\
A layer of wrappers for an hdf5 database

database.py

Vera Del Favero

This database class will handle all access to the hdf5 databses
    we'll be using in this module
'''
######## Imports ########
#### Standard Library ####
import time
from pathlib import Path
import os
from os.path import join, isfile, isdir
#### Third Party ####
import numpy as np
import h5py
#### Local ####
from xdata.error import AddressNotFoundError
from xdata.error import AttributeNotFoundError
from xdata.error import WrongH5ItemKind
from xdata.error import ReadOnlyError
from xdata.error import address_not_found
from xdata.error import attribute_not_found
from xdata.connection import touch
from xdata.connection import Connection
from xdata.address import AddressHandle
from xdata.address import address_exists
from xdata.address import assert_address_exists
from xdata.attributes import AttributesHandle
from xdata.attributes import attribute_exists
from xdata.attributes import assert_attribute_exists
from xdata.dataset import DatasetHandle
from xdata.group import GroupHandle

######## Database Class ########

class Database(object):
    '''\
    This is a wrapper for hdf5 databases
        inteded to simplify calling and reduce clutter

    Inputs:
        fname (str): file name and location
        group (str): point to a particular group in the database

    Methods: 
        #### General ####

        change_group: change the group the object points to
        visit: visit each item in the databse
        merge: merge a similar database into this one
        shard: create a new databse with some data from the current database
        list_items: list databases and groups in a particular group within
            the hdf5 database
        scan: scan a particular group in the database and print it
            without changing the group we point to
        kind: determine if a particular item is a database or a group
        exists: determine if a particular item exists

        #### dset methods Methods ####

        dset_init: initialize new dataset in the hdf5 database
        dset_size: return the size of the dataset
        dset_compression: return the compression of the dataset
        dset_shape: return the shape of the dataset
        dset_dtype: return the dtype of the dataset
        dset_fields: return the fields for a dataset stored with fields
        dset_value: return the value of a dataset, 
            for a given field and set of indicies
        dset_sum: return the sum of a given dataset for some field 
            on some indicies
        dset_min: return the mix of a given dataset for some field 
            on some indicies
        dset_max: return the max of a given dataset for some field 
            on some indicies
        dset_set: set the values of a dataset, with some intelligence
        dset_rm: remove a given dataset (this does not free the disk space)
        dset_copy: copy a given dataset
        dset_recompress: copy a dataset to a temporary location and
            copy it back, changing the compression.
            WARNING: This is extraordinarily inneficient, and should only
            be used for testing

        #### attr methods ####

        attr_exists: check if attribute exists
        attr_value: return attribute value
        attr_set: set a given attribute
        attr_list: list attributes for a given dataset or group
        attr_dict: return the dictionary of attributes for a given dataset
            or group
        attr_set_dict: set each attribute from a given dictionary

    '''

    def __init__(
                 self, 
                 fname,
                 group = '/',
                 readonly = False,
                 **conn_kwargs
                ):
        '''\
        Point to and ensure the existence of the database
    
        Parameters
        ----------
        fname : str
            File location
        group : str
            Path to location in database we would like to explore
        readonly : bool
            Open in readonly mode?
        conn_kwars : dict
            h5py.File keyword arguments
        '''
        self.readonly = readonly
        self._conn_kwargs = conn_kwargs
        self.fname = fname
        # Set addr last; order matters
        self.group = group

        # Check if group exists
        if not GroupHandle.check_exists(self.fname, self.group):
            GroupHandle.create_group(self.fname, self.group)

    # Handle readonly
    @property
    def readonly(self):
        return self._readonly
    @readonly.setter
    def readonly(self, value):
        self._readonly = bool(value)

    # Handle fname property
    @property
    def fname(self):
        return self._fname
    @fname.setter
    def fname(self, value):
        if not os.path.isfile(value):
            if self.readonly:
                raise FileNotFoundError(f"No such file {value}")
            else:
                with Connection(value,'w-',**self.conn_kwargs) as conn:
                    pass
        self._fname = value

    # Handle address
    @property
    def group(self):
        return self._group
    @group.setter
    def group(self, value):
        if self.readonly:
            assert_address_exists(self.fname, value, **self.conn_kwargs)
        self._group = value

    # Handle other inputs
    @property
    def conn_kwargs(self):
        return self._conn_kwargs

    def handle(self, item=None, kind=None):
        # Identify the path
        if item is None:
            path = self.group
        elif item.startswith("/"):
            path = item
        else:
            path = join(self.group, item)
        # general address handle might be useful
        if item is None:
            kind = 'group'
        elif kind is None:
            if AddressHandle.check_exists(self.fname, path):
                kind = AddressHandle.check_kind(self.fname, path)
            else:
                kind = "addr"
        # construct handle
        if kind == "addr":
            return AddressHandle(self.fname, path, **self.conn_kwargs)
        elif kind == "dset":
            return DatasetHandle(self.fname, path, **self.conn_kwargs)
        elif kind == "group":
            return GroupHandle(self.fname, path, **self.conn_kwargs)
        else:
            raise ValueError(f"Unknown kind: {kind}; not in (dset, group)")

    def size_on_disk(
                     self,
                     group="/",
                    ):
        '''
        Return the size on disk of the database
        '''
        return Path(self.fname).stat().st_size
                        
    def path(self, item):
        if item.startswith("/"):
            return item
        else:
            return join(self.group, item)

    def change_group(
                     self,
                     group = '/',
                    ):
        '''\
        Recreate the database with new group

        Inputs:
            group: New group
        '''
        # Create a new database object and assign it to this group
        self.group = self.path(group)

    def visit(self, fn = print):
        '''\
        Visit the database
        
        Inputs:
            fn: function to visit every item in database with
        '''
        with Connection(self.fname,'r',**self.conn_kwargs) as conn:
            group_obj = conn.file[self.group]
            group_obj.visit(fn)

    def legacy_merge(self, fname_head):
        """Merge another database (head) into this one (origin)"""
        # Instantiate connections
        with Connection(self.fname, 'r+', **self.conn_kwargs) as Origin:
            with Connection(fname_head,'r',**self.conn_kwargs)as Head:
                # Define visit function
                def visit_function(parcel):
                    obj = Head.file[parcel]
                    if obj.name not in Origin.file:
                        Head.file.copy(obj.name, Origin.file[obj.parent.name])
                # Visit head
                Head.file.visit(visit_function)
                # Copy top level attributes
                for key, value in Head.file.attrs.items():
                    Origin.file.attrs[key] = value

    def merge(self, fname_head, compression="default"):
        '''\
        Merge another similar database (the head) into this one (the origin)

            Inputs:
                fname_head: the file name and location for the head node
        '''
        if compression == "default":
            self.legacy_merge(fname_head)
        else:
            slash = self.handle('/',kind='group')
            head = GroupHandle(fname_head,'/')
            head.copy(slash, compression=compression)

    def rebase(self, fname_alias, compression="default"):
        '''\
        Rebase the database to fee disk space
        '''
        # Check that there's not the alias file already
        with Connection(fname_alias, 'w-', **self.conn_kwargs) as conn:
            pass

        # Create alias database
        db_alias = Database(fname_alias)
        # use merge to do the dirty work
        if compression == "default":
            db_alias.legacy_merge(self.fname)
        else:
            slash = self.handle('/',kind='group')
            head = GroupHandle(fname_head,'/')
            slash.copy(head, compression=compression)
            
        # overwrite file
        os.remove(self.fname)
        os.rename(fname_alias, self.fname)

    def shard(
            self, 
            fname_head, 
            names = None,
            compression = "default",
            **init_kwargs
        ):
        '''\
        Create a smaller database with less data

        option to compress data differently
        
        Inputs:
            fname_head: file name and location for desired shard database
            names: list of items for copying
            compression: file compression option for database
        '''
        # Make sure we don't delete everything
        if self.fname == fname_head:
            raise Exception("shard name cannot be origin name")
        # Make sure the shard exists
        with Connection(fname_head,'a',**self.conn_kwargs) as conn:
            if self.group not in conn.file:
                conn.file.create_group(self.group)
        # Initialize group handles
        handle = self.handle(kind='group')
        shard = GroupHandle(fname_head,self.group)
        # Get names
        if names is None:
            names = handle.list(kind="dset")
        # Set attrs
        shard.attrs.set_dict(handle.attrs.dict())
        # Loop items in names
        for item in names:
            item_handle = self.handle(item)
            other_handle = self.handle(item)
            other_handle.fname = fname_head
            item_handle.copy(other_handle, compression=compression)

    def list_items(self, path="./", kind = None):
        '''\
        Return list of groups in current group
        
        Inputs:
            path: Path to group inside database.
                can be relative or absolute
            kind: list only datasets or only groups
        '''
        return self.handle(path,kind='group').list(kind=kind)

    def scan(self, path="./", kind=None):
        '''\
        Return basic information about the objects in the current group

        This is really useful when exploring an unknown database
        Inputs:
            path: Path to group inside database.
                can be relative or absolute
            kind: list only datasets or only groups
        '''
        # Create temporary database object pointing at path
        handle = self.handle(path)
        if handle.kind is None:
            print(f"No such path {handle.addr}")
        elif handle.kind == "group":
            items = handle.list(kind=kind)
            # Check each item
            for item in items:
                # Item information
                item_dict = {}
                # Name each item
                item_dict["name"] = item
                # Figure out if it is a dset or group
                item_dict["kind"] = AddressHandle.check_kind(
                    self.fname,
                    join(handle.addr, item),
                    **self.conn_kwargs
                )
                # Get a handle for this item
                item_handle = self.handle(join(handle.addr,item))
                # List attributes
                item_dict["attrs"] = item_handle.attrs.dict()
                # Dset only things
                if item_dict["kind"] == "dset":
                    # Return the shape of the dset
                    item_dict["shape"] = item_handle.shape
                    # Return the dtype of the dset
                    item_dict["dtype"] = item_handle.dtype
                    # Return the compression of the dset
                    item_dict["compression"] = item_handle.compression
                    # Return the fields of the dset
                    item_dict["fields"] = item_handle.fields
                # Print item_dict
                print(item_dict)
        elif handle.kind == "dset":
            item_dict = {}
            item_dict["name"] = path
            item_dict["kind"] = "dset"
            # Return the shape of the dset
            item_dict["shape"] = handle.shape
            # Return the dtype of the dset
            item_dict["dtype"] = handle.dtype
            # Return the compression of the dset
            item_dict["compression"] = handle.compression
            # Return the fields of the dset
            item_dict["fields"] = handle.fields
            item_dict["attrs"] = handle.attrs.dict()
        else:
            raise RuntimeError(f"Strange handle")

    def create_group(self, item, clean = True):
        '''\
        Create a new group
        '''
        return self.handle().create(item)

    def kind(self, item):
        '''\
        Return the kind of item, be it a group or dset
        '''
        return self.handle(item,kind='addr').kind

    def exists(self, item, kind=None):
        '''\
        Check if item exists
        '''
        return self.handle(item,kind='addr').exists()

    def dset_init(
            self,
            item,
            shape,
            dtype,
            compression=None,
            **init_kwargs
        ):
        '''\
        Initialize a new dataset

        Inputs:
            item: name of dataset
            shape: shape of dataset
            dtype: dtype of dataset
            compression: desired compression of data
        '''
        handle = self.handle(item, kind='dset')
        handle.initialize(
            shape,
            dtype,
            compression=compression,
            **init_kwargs
        )

    def dset_size(self, item):
        '''\
        Return the size of a dataset

        Inputs:
            item: the dataset we would like to know the size of
        '''
        return self.handle(item, kind='dset').size

    def dset_compression(self, item):
        '''\
        Return the compression of a dataset

        Inputs:
            item: the dataset we would like to know the size of
        '''
        return self.handle(item, kind='dset').compression

    def dset_shape(self, item):
        '''\
        Return the sum of a dataset

        Inputs:
            item: the dataset we would like to know the size of
        '''
        return self.handle(item, kind='dset').shape

    def dset_dtype(self, item):
        '''\
        Return the dtype of a dataset

        Inputs:
            item: the dataset we would like to know the size of
        '''
        return self.handle(item, kind='dset').dtype

    def dset_fields(self, item):
        '''\
        Return the fields of a dataset with an informative dtype

        Inputs:
            item: the dataset we would like to know the size of
        '''
        return self.handle(item, kind='dset').fields

    def dset_value(
            self, 
            item, 
            samples = None, 
            **kwargs
        ):
        '''\
        Return the values of a dataset

        Inputs:
            item: the dataset we would like to know the size of
            field: the field of interest for a complex data type
            samples: an array of indexes pointing to which part of the set
                we would like to analyze

        '''
        if samples is not None:
            kwargs["indices"] = samples
        return self.handle(item, kind='dset').value(**kwargs)

    def dset_sum(
            self, 
            item, 
            samples = None,
            **kwargs
        ):
        '''\
        Return the sum of a dataset

        Inputs:
            item: the dataset we would like to know the size of
            field: the field of interest for a complex data type
            samples: an array of indexes pointing to which part of the set
                we would like to analyze
        '''
        if samples is not None:
            kwargs["indices"] = samples
        return self.handle(item, kind='dset').sum(**kwargs)
        
    def dset_min(
            self, 
            item, 
            samples = None,
            **kwargs
        ):
        '''\
        Return the minimum value of a dataset

        Inputs:
            item: the dataset we would like to know the size of
            field: the field of interest for a complex data type
            samples: an array of indexes pointing to which part of the set
                we would like to analyze
        '''
        if samples is not None:
            kwargs["indices"] = samples
        return self.handle(item, kind='dset').min(**kwargs)

    def dset_max(
            self, 
            item, 
            samples = None,
            **kwargs
        ):
        '''\
        Return the maximum value of a dataset
        '''
        if samples is not None:
            kwargs["indices"] = samples
        return self.handle(item, kind='dset').max(**kwargs)

    def dset_set(
            self, 
            item, 
            value, 
            samples=None, 
            **kwargs
        ):
        '''\
        Create a new dataset or update the existing one

        Inputs:
            item: the dataset we would like to know the size of
            data: the data belonging to the dataset

            samples: an array of indexes pointing to which part of the set
                we would like to analyze
            fields: fields for complex datatype
            compression: Desired data compression
        '''
        handle = self.handle(item, kind='dset')
        if samples is not None:
            kwargs["indices"] = samples
        handle.set(value,**kwargs)

    def remove(self, item):
        self.handle(item).remove()
    # alias
    def dset_rm(self, item):
        self.remove(item)

    def dset_copy(
            self, 
            addr_cur,
            addr_new,
            **kwargs
        ):
        '''\
        Copy a dataset

        Inputs:
            item: the name of the item we would like to copy
            copy: the destination of the copy
            compression: the desired compression level of the copy
            dtype: the desired datatype for the new data
        '''
        handle = self.handle(addr_cur, kind='dset')
        handle.copy(addr_new, **kwargs)
    
    def dset_recompress(
            self, 
            item,
            **kwargs
        ):
        '''\
        Compress and copy data, and recopy it back to the same name

        This is actually much less useful than it sounds,
            and should only be used for testing
        '''
        handle = self.handle(item, kind='dset')
        handle.recompress(**kwargs)

    def attr_exists(self, item, attr):
        '''\
        Check if given attribute exists

        Inputs:
            item: the dataset or group the attribute would belong to
            attr: the name of the attribute
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.exists(attr)

    def attr_value(self, item, attr):
        '''\
        Get the value of an attribute

        Inputs:
            item: the dataset or group the attribute would belong to
            attr: the name of the attribute
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.value(attr)

    def attr_set(self, item, attr, value):
        '''\
        Set a value for an attribute

        Inputs:
            item: the dataset or group the attribute would belong to
            attr: the name of the attribute
            value: the value of the attribute
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.set(attr, value)

    def attr_list(self, item):
        '''\
        List the attributes of a given item

        Inputs:
            item: the dataset or group the attribute would belong to
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.list()

    def attr_dict(self, item):
        '''\
        return a dictionary with all of the attributes for a given item

        Inputs:
            item: the dataset or group the attribute would belong to
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.dict()

    def attr_set_dict(self, item, attrs):
        '''\
        set each attribute from the dictionary

        Inputs:
            item: the dataset or group the attribute would belong to
            attrs: the dictionary of attributes
        '''
        handle = self.handle(item)
        if handle.kind is None:
            raise AddressNotFoundError(
                f"No such object {item} in {self.fname} from {self.group}")
        return handle.attrs.set_dict(attrs)
