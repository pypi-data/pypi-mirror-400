#!/usr/env/bin python3
"""Attribute methods for hdf5 handles"""
######## Imports ########
#### Standard Library ####
import os
import time
#### Third Party ####
import numpy as np
#### Local ####
from xdata.error import *
from xdata.connection import *
from xdata.address import *

######## Define all ########
__all__ = [
    "AttributesHandle",
    "attribute_exists",
    "assert_attribute_exists",
]

FNAME_TEST = "test_attributes.hdf5"

######## Functions ########
def attribute_exists(fname, addr, key, **kwargs):
    """Check if an attribute exists
    """
    # Open connection
    with Connection(fname, 'r', **kwargs) as conn:
        if addr in conn.file:
            found_addr = True
            if key in conn.file[addr].attrs:
                found_key = True
            else:
                found_key = False
        else:
            found_addr = False
            found_key = False
    # If not found_addr, die
    if not found_addr:
        address_not_found(fname, addr)
    return found_key

def assert_attribute_exists(fname, addr, key, **kwargs):
    if not attribute_exists(fname, addr, key, **kwargs):
        attribute_not_found(fname, addr, key)

######## Object ########
class AttributesHandle(AddressHandle):
    """Handle for all attributes at a particular handle"""
    #### Static methods ####
    ## Readonly methods ##
    @staticmethod
    def check_exists(fname, addr, key, **kwargs):
        """Check to see if an attribute exists"""
        return attribute_exists(fname, addr, key, **kwargs)

    @staticmethod
    def read_value(fname, addr, key, **kwargs):
        """Read the value of an attribute

        Error checking doesn't go here. The h5py.File object
            will take care of it.
        """
        # Open connection
        with Connection(fname, 'r', **kwargs) as conn:
            value = conn.file[addr].attrs[key]
        return value

    @staticmethod
    def read_list(fname, addr, **kwargs):
        """Read the list of attributes at an address"""
        with Connection(fname, 'r', **kwargs) as conn:
            attrs = list(conn.file[addr].attrs)
        return attrs

    @staticmethod
    def read_dict(fname, addr, **kwargs):
        """Instantiate and return a dictionary of attributes"""
        attrs = {}
        with Connection(fname, 'r', **kwargs) as conn:
            for key in conn.file[addr].attrs:
                attrs[key] = conn.file[addr].attrs[key]
        return attrs

    ## Read/Write methods ##
    @staticmethod
    def write_attr(fname, addr, key, value, **kwargs):
        """Set a particular attribute

        Note: This is a read/write method
        """
        with Connection(fname, 'r+', **kwargs) as conn:
            conn.file[addr].attrs[key] = value

    @staticmethod
    def write_attr_dict(fname, addr, attrs, **kwargs):
        """Set a particular attribute

        Note: This is a read/write method
        """
        with Connection(fname, 'r+', **kwargs) as conn:
            for key in attrs:
                conn.file[addr].attrs[key] = attrs[key]

    #### Instance methods ####
    ## Readonly methods ##
    def exists(self, key):
        return self.check_exists(
            self.fname, 
            self.addr, 
            key, 
            **self.conn_kwargs
        )
    
    def value(self, key):
        return self.read_value(
            self.fname,
            self.addr,
            key,
            **self.conn_kwargs
        )

    def list(self):
        return self.read_list(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    def dict(self):
        return self.read_dict(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )
    ## Read/Write methods ##
    def set(self, key, value):
        if self.readonly:
            raise ReadOnlyError(
                f"{self.fname} was opened by {self.__class__} as readonly; "+\
                f"{self.__class__}.set is incompatible with readonly!"
            )
        self.write_attr(
            self.fname,
            self.addr,
            key,
            value,
            **self.conn_kwargs
        )

    def set_dict(self, attrs):
        if self.readonly:
            raise ReadOnlyError(
                f"{self.fname} was opened by {self.__class__} as readonly; "+\
                f"{self.__class__}.set_dict is incompatible with readonly!"
            )
        self.write_attr_dict(
            self.fname,
            self.addr,
            attrs,
            **self.conn_kwargs
        )

######## Testing ########
def test_attributes():
    group1 = "apples"
    attr_label = "skeletons"
    attr_value = 8.
    with Connection(FNAME_TEST, 'w') as conn:
        conn.file.create_group(group1)
    attrs1 = AttributesHandle(FNAME_TEST, group1)
    assert not attribute_exists(FNAME_TEST, group1, attr_label)
    assert not attrs1.exists(attr_label)
    assert len(attrs1.list()) == 0
    assert len(list(attrs1.dict().keys())) == 0
    attrs1.set(attr_label, attr_value)
    assert attribute_exists(FNAME_TEST, group1, attr_label)
    assert attrs1.exists(attr_label)
    assert attrs1.value(attr_label) == attr_value
    assert len(attrs1.list()) == 1
    assert len(list(attrs1.dict().keys())) == 1
    assert attrs1.dict()[attr_label] == attr_value
    attrs1.set_dict(attrs1.dict())
    assert attribute_exists(FNAME_TEST, group1, attr_label)
    assert attrs1.exists(attr_label)
    assert attrs1.value(attr_label) == attr_value
    assert len(attrs1.list()) == 1
    assert len(list(attrs1.dict().keys())) == 1
    assert attrs1.dict()[attr_label] == attr_value
    return


######## Execution ########
if __name__ == "__main__":
    test_attributes()
