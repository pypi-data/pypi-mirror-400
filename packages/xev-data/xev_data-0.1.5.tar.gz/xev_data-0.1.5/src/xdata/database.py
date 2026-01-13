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
        with Connection(self.fname, 'r',**self.conn_kwargs) as conn:
            if (not (group is '/')) and (not (group in conn.file)):
                group_exists = False
            else:
                group_exists = True

        # Create group
        if not group_exists:
            with Connection(self.fname, 'r+',**self.conn_kwargs) as conn:
                conn.file.create_group(group)

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

        # Check if group startswith /
        if group.startswith("/"):
            # group is to be interpreted global
            pass
        else:
            # Group is to be interpreted local
            group = join(self.group, group)

        # Create a new database object and assign it to this group
        Database(self.fname, group)
        self.group = group

    def visit(self, fn = print):
        '''\
        Visit the database
        
        Inputs:
            fn: function to visit every item in database with
        '''
        with Connection(self.fname,'r',**self.conn_kwargs) as conn:
            group_obj = conn.file[self.group]
            # TODO Bug?
            conn.file.visit(fn)

    def merge(self, fname_head):
        '''\
        Merge another similar database (the head) into this one (the origin)

            Inputs:
                fname_head: the file name and location for the head node
        '''

        # Initialize two database objects
        Origin = h5py.File(self.fname, 'r+')
        Head = h5py.File(fname_head, 'r')

        # Make use of visit functionality to recursively copy database
        def visit_function(parcel):
            item = Head[parcel]
            # If the group or dataset is not in origin, copy it
            if not (item.name in Origin):
                Head.copy(item.name, Origin[item.parent.name])
                # If the group or dataset has attributes, copy them
                attrs = dict(item.attrs)
                # For each attr in the dict
                for key in list(attrs.keys()):
                    # Copy it
                    Origin[item.name].attrs[key] = attrs[key]
        try:
            Head.visit(visit_function)

        finally:
            Origin.close()
            Head.close()
        # Open head database
        db_head = Database(fname_head)
        # Copy top level attributes
        top_attrs = db_head.attr_dict('/')
        # Store attributes
        self.attr_set_dict('/', top_attrs)
        # Scan everything


    def rebase(self, fname_alias, compression="gzip"):
        '''\
        Rebase the database to fee disk space
        '''
        import sys
        import os
        from os.path import isfile
        # Check that there's not the alias file already
        assert not isfile(fname_alias)

        # Create alias database
        db_alias = Database(fname_alias)
        # use merge to do the dirty work
        db_alias.merge(self.fname)

        # overwrite file
        cmd = "mv %s %s"%(fname_alias, self.fname)
        print(cmd,file=sys.stderr)
        os.system(cmd)

    def shard(self, fname_head, names = None, compression = "default"):
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

        # Create objects for current database (origin)
        with Connection(self.fname, 'r', **self.conn_kwargs) as Origin:
            with Connection(fname_head, 'a', **self.conn_kwargs) as Head:
                # If names is not given, assume all data is to be copied
                if names is None:
                    names = self.list_items(kind = "dset")
                #print("creating shard at %s with members: "%(self.group), names)


                # Make sure the group exists in the new dataset
                if not self.group == "/":
                    Head.file.create_group(self.group)

                # Copy group attributes
                group_attrs = self.attr_list('.')
                for item in group_attrs:
                    Head.file[self.group].attrs[item] = \
                        Origin.file[self.group].attrs[item]

                # Loop through each dataset
                for item in names:
                    # Find the data
                    dset = Origin.file[self.group][item]
                    # Check compression
                    if compression =="default" or dset.size <= 1:
                        # Default copy behavior includes attrs
                        Origin.file.copy(dset.name, Head.file[self.group])
                    else:
                        # Copy data
                        Head.file[self.group].create_dataset(
                            item,
                            data=dset[...],
                            dtype=dset.dtype,
                            compression=compression,
                        )
                        # copy attrs
                        for jtem in dset.attrs:
                            Head.file[self.group][item].attrs[jtem] = \
                                dset.attrs[jtem]

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
        db_scan = Database(self.fname, self.group)
        db_scan.change_group(path)
        # Read items in scanned pointer database
        items = db_scan.list_items(kind=kind)
        # Check each item
        for item in items:
            # Item information
            item_dict = {}
            # Name each item
            item_dict["name"] = item
            # Figure out if it is a dset or grou
            item_dict["kind"] = db_scan.kind(item)
            # List attributes
            item_dict["attrs"] = db_scan.attr_list(item)
            # Dset only things
            if item_dict["kind"] == "dset":
                # Return the shape of the dset
                item_dict["shape"] = db_scan.dset_shape(item)
                # Return the dtype of the dset
                item_dict["dtype"] = db_scan.dset_dtype(item)
                # Return the compression of the dset
                item_dict["compression"] = db_scan.dset_compression(item)
                # Return the fields of the dset
                item_dict["fields"] = db_scan.dset_fields(item)

            # Print item_dict
            print(item_dict)


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
