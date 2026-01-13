#!/usr/env/bin python3
"""Create and manage address handle for datasets
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
    "DatasetHandle",
]
FNAME_TEST = "test_dataset.hdf5"

######## Objects ########
#### Dataset Handle ####
class DatasetHandle(AddressHandle):
    """An object for datasets in an hdf5 database"""
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
        # Make sure this is a dataset
        if self.kind not in ["dset", None]:
            raise ValueError(
                f"Address {addr} in {fname} is kind {self.kind} " + \
                f"(and is not Dataset)!"
            )

    #### Static methods ####
    ## Readonly methods ##
    @staticmethod
    def dataset_size(
            fname,
            addr,
            **conn_kwargs
        ):
        """Open the file in readonly and check the size
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            value = conn.file[addr].size
        return value
    
    @staticmethod
    def dataset_compression(
            fname,
            addr,
            **conn_kwargs
        ):
        """Open the file in readonly and check the compression
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            value = conn.file[addr].compression
        return value
    
    @staticmethod
    def dataset_shape(
            fname,
            addr,
            **conn_kwargs
        ):
        """Open the file in readonly and check the shape
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            value = conn.file[addr].shape
        return value
    
    @staticmethod
    def dataset_dtype(
            fname,
            addr,
            **conn_kwargs
        ):
        """Open the file in readonly and check the dtype
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            value = conn.file[addr].dtype
        return value
    
    @staticmethod
    def dataset_fields(
            fname,
            addr,
            **conn_kwargs
        ):
        """Open the file in readonly and check the fields
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            value = conn.file[addr].dtype.fields
        return value
    
    @staticmethod
    def dataset_value(
            fname,
            addr,
            field = None,
            indices = None,
            **conn_kwargs
        ):
        """Open the file in readonly and read the dataset
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            # Check indices
            if indices is None:
                # We have to use a slice, otherwise the data will
                # disappear when the connection is closed
                value = conn.file[addr][...]
            else:
                value = conn.file[addr][indices]

        # Check field argument
        if field is not None:
            value = value[field]

        return value

    @staticmethod
    def dataset_sum(
            fname,
            addr,
            field = None,
            indices = None,
            **conn_kwargs
        ):
        """Return the sum of a dataset
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            # Check usage 
            if (field is None) and (conn.file[addr].dtype.fields is not None):
                raise ValueError(f"Cannot compute the sum of a compound dtype")
            # Get data
            if indices is None:
                data = conn.file[addr][...]
            else:
                data = conn.file[addr][indices]
            # Compute sum
            value = np.sum(data)
        return value
    
    @staticmethod
    def dataset_min(
            fname,
            addr,
            field = None,
            indices = None,
            **conn_kwargs
        ):
        """Return the min of a dataset
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            # Check usage 
            if (field is None) and (conn.file[addr].dtype.fields is not None):
                raise ValueError(f"Cannot compute the min of a compound dtype")
            # Get data
            if indices is None:
                data = conn.file[addr][...]
            else:
                data = conn.file[addr][indices]
            # Compute min
            value = np.min(data)
        return value
    
    @staticmethod
    def dataset_max(
            fname,
            addr,
            field = None,
            indices = None,
            **conn_kwargs
        ):
        """Return the max of a dataset
        """
        with Connection(fname, 'r', **conn_kwargs) as conn:
            # Check usage 
            if (field is None) and (conn.file[addr].dtype.fields is not None):
                raise ValueError(f"Cannot compute the max of a compound dtype")
            # Get data
            if indices is None:
                data = conn.file[addr][...]
            else:
                data = conn.file[addr][indices]
            # Compute max
            value = np.max(data)
        return value
    

    ## Read / Write methods ##
    @staticmethod
    def initialize_dataset(
            fname,
            addr,
            shape,
            dtype,
            conn_kwargs = {},
            **init_kwargs
        ):
        """Initialize a new dataset

        Parameters
        ----------
        fname : str
            file location of database
        addr : str
            location of dataset within database
        shape : tuple
            shape of dataset
        dtype : dtype
            dtype of dataset
        conn_kwargs : dict
            Connection keyword arguments
        """
        # Make the syntax more forgiving than h5py.File
        if type(shape) is not tuple:
            shape = tuple([shape])
        with Connection(fname, 'r+', **conn_kwargs) as conn:
            conn.file.create_dataset(
                addr,
                shape,
                dtype=dtype,
                **init_kwargs
            )

    @staticmethod
    def set_dataset_value(
        fname,
        addr,
        value,
        indices=None,
        field=None,
        conn_kwargs = {},
        **init_kwargs
        ):
        """Set the value of a dataset
        
        Parameters
        ----------
        fname : str
            file location of database
        addr : str
            location of dataset within database
        value : np.ndarray
            Numpy array with values to be stored in the database
        indices : np.ndarray
            Indices associated with each value
        conn_kwargs : dict
            Connection keyword arguments
        """
        # Check compound datasets
        if field is not None:
            raise NotImplementedError(
                "Reading from fields is supported, but not writing them!"
            )

        # Open connection
        with Connection(fname, 'r+', **conn_kwargs) as conn:
            # Guarantee existence
            if addr not in conn.file:
                if indices is None:
                    conn.file.create_dataset(
                        addr,
                        value.shape,
                        dtype=value.dtype,
                        **init_kwargs
                    )
                else:
                    raise RuntimeError(
                        f"Cannot initialize dataset for incomplete data!"
                    )
            # Provide values
            if indices is None:
                conn.file[addr][...] = value
            else:
                conn.file[addr][indices] = value
       
    @staticmethod
    def copy_dataset(
        fname,
        addr_cur,
        addr_new,
        compression="default",
        dtype="default",
        field=None,
        indices=None,
        conn_kwargs = {},
        **init_kwargs
        ):
        """Set the value of a dataset
        
        Parameters
        ----------
        fname : str
            file location of database
        addr_cur : str
            location of dataset within database
        addr_new : str
            copy location of dataset within database
        compression : str
            compression method of dataset
        dtype : dtype
            dtype of dataset
        indices : np.ndarray
            Indices associated with each value
        conn_kwargs : dict
            Connection keyword arguments
        """
        # Check compound datasets
        if field is not None:
            raise NotImplementedError(
                "Copying fields is not yet supported!")
        if indices is not None:
            raise NotImplementedError(
                "Copying subsets of datasets is not yet supported!")

        # Open connection
        with Connection(fname, 'r+', **conn_kwargs) as conn:
            # Identify current data
            if addr_cur not in conn.file:
                raise RuntimeError(f"No such dataset {addr_cor}")
            elif not isinstance(conn.file[addr_cur], h5py._hl.dataset.Dataset):
                raise TypeError(
                    f"Cannot use copy_dataset for {conn.file[addr_cur]}")
            # Check new address
            if addr_new in conn.file:
                raise ValueError(
                    f"Cannot create dataset {addr_new}; already exists!")
            ## Cases ##
            # Never do this because it links, rather than copying data
            if (compression == "default") and (dtype == "default"):
                conn.file.copy(
                    conn.file[addr_cur],
                    conn.file, # TODO test this
                    name=addr_new,
                )
            else:
                # Check dtype
                if dtype == "default":
                    dtype = conn.file[addr_cur].dtype
                # Check compression
                if compression == "default":
                    compression = conn.file[addr_cur].compression
                # Create dataset
                conn.file.create_dataset(
                    addr_new,
                    conn.file[addr_cur].shape,
                    dtype=dtype,
                    compression=compression,
                    **init_kwargs
                )
                # Copy values
                conn.file[addr_new][...] = conn.file[addr_cur][...]

            # Copy attributes
            for key, value in conn.file[addr_cur].attrs.items():
                conn.file[addr_new].attrs[key] = value

    @staticmethod
    def recompress_dataset(
        fname,
        addr,
        compression="gzip",
        dtype="default",
        alias="TEMP",
        conn_kwargs = {},
        **init_kwargs
        ):
        """
        Parameters
        ----------
        fname : str
            file location of database
        addr : str
            location of dataset within database
        dtype : dtype
            dtype of dataset
        compression : str
            compression method of dataset
        alias : str
            Temporary copy location of dataset within database
        conn_kwargs : dict
            Connection keyword arguments
        """
        DatasetHandle.copy_dataset(
            fname,
            addr,
            alias,
            compression="default",
            dtype="default",
            conn_kwargs=conn_kwargs,
            **init_kwargs
        )
        DatasetHandle.remove_item(
            fname,
            addr,
            **conn_kwargs
        )
        DatasetHandle.copy_dataset(
            fname,
            alias,
            addr,
            compression=compression,
            dtype=dtype,
            conn_kwargs=conn_kwargs,
            **init_kwargs
        )
        DatasetHandle.remove_item(
            fname,
            alias,
            **conn_kwargs
        )
        
    #### Instance methods ####
    ## Readonly methods ##
    @property
    def size(self):
        """Instance method that calls DatasetHandle.dataset_size"""
        return self.dataset_size(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    @property
    def compression(self):
        """Instance method that calls DatasetHandle.dataset_compression"""
        return self.dataset_compression(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    @property
    def shape(self):
        """Instance method that calls DatasetHandle.dataset_shape"""
        return self.dataset_shape(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    @property
    def dtype(self):
        """Instance method that calls DatasetHandle.dataset_dtype"""
        return self.dataset_dtype(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    @property
    def fields(self):
        """Instance method that calls DatasetHandle.dataset_fields"""
        return self.dataset_fields(
            self.fname,
            self.addr,
            **self.conn_kwargs
        )

    def value(self,field=None,indices=None):
        """Instance method that calls DatasetHandle.dataset_value"""
        return self.dataset_value(
            self.fname,
            self.addr,
            field = field,
            indices = indices,
            **self.conn_kwargs
        )

    def sum(self,field=None,indices=None):
        """Instance method that calls DatasetHandle.dataset_sum"""
        if (field is None) and (indices is None) and \
                self.attrs.exists("sum"):
            return self.attrs.value("sum")
        else:
            value = self.dataset_sum(
                self.fname,
                self.addr,
                field = field,
                indices = indices,
                **self.conn_kwargs
            )
            if not self.readonly:
                self.attrs.set("sum", value)
            return value

    def min(self,field=None,indices=None):
        """Instance method that calls DatasetHandle.dataset_min"""
        if (field is None) and (indices is None) and \
                self.attrs.exists("min"):
            return self.attrs.value("min")
        else:
            value = self.dataset_min(
                self.fname,
                self.addr,
                field = field,
                indices = indices,
                **self.conn_kwargs
            )
            if not self.readonly:
                self.attrs.set("min", value)
            return value

    def max(self,field=None,indices=None):
        """Instance method that calls DatasetHandle.dataset_max"""
        if (field is None) and (indices is None) and \
                self.attrs.exists("max"):
            return self.attrs.value("max")
        else:
            value = self.dataset_max(
                self.fname,
                self.addr,
                field = field,
                indices = indices,
                **self.conn_kwargs
            )
            if not self.readonly:
                self.attrs.set("max", value)
            return value

    ## Read / Write methods ##
    def initialize(
            self,
            shape,
            dtype,
            **init_kwargs
        ):
        """Instance method that calls DatasetHandle.initialize_dataset"""
        if self.readonly:
            raise ReadOnlyError
        self.initialize_dataset(
            self.fname,
            self.addr,
            shape,
            dtype,
            conn_kwargs = self.conn_kwargs,
            **init_kwargs
        )
    def set(
            self,
            value,
            indices=None,
            field=None,
            **init_kwargs
        ):
        """Instance method that calls DatasetHandle.set_dataset_value"""
        if self.readonly:
            raise ReadOnlyError
        self.set_dataset_value(
            self.fname,
            self.addr,
            value,
            indices=indices,
            field=field,
            conn_kwargs=self.conn_kwargs,
            **init_kwargs
        )
    def copy(
            self,
            addr_new,
            compression="default",
            dtype="default",
            field=None,
            indices=None,
            **init_kwargs
        ):
        """Instance method that calls DatasetHandle.copy_dataset"""
        if self.readonly:
            raise ReadOnlyError
        self.copy_dataset(
            self.fname,
            self.addr,
            addr_new,
            compression=compression,
            dtype=dtype,
            field=field,
            indices=indices,
            conn_kwargs = self.conn_kwargs,
            **init_kwargs
        )
    def recompress(
            self,
            compression="gzip",
            dtype="default",
            alias="TEMP",
            **init_kwargs
        ):
        """Instance method that calls DatasetHandle.recompress_dataset"""
        if self.readonly:
            raise ReadOnlyError
        self.recompress_dataset(
            self.fname,
            self.addr,
            compression=compression,
            dtype=dtype,
            alias=alias,
            conn_kwargs = self.conn_kwargs,
            **init_kwargs
        )

######## Tests ########
def test_dataset():
    dset1_tag = "apples"
    dset2_tag = "oranges"
    dset1_value = np.arange(50)
    # Ensure fresh hdf5 file
    with Connection(FNAME_TEST, 'w') as conn:
        pass
    # Initialize read/write dataset handle
    dset1 = DatasetHandle(FNAME_TEST, dset1_tag)
    # Assert it doesn't already exist
    assert not dset1.exists()
    # Set it 
    dset1.set(dset1_value)
    assert dset1.exists()
    assert dset1.size == dset1_value.size
    assert dset1.shape == dset1_value.shape
    assert dset1.compression is None
    assert dset1.dtype == dset1_value.dtype
    assert dset1.fields is None
    assert np.all(dset1.value() == dset1_value)
    # read/write calls
    dset1.copy(dset2_tag)
    # Create readonly reference
    dset2 = DatasetHandle(FNAME_TEST, dset2_tag, readonly=True)
    assert dset2.exists()
    assert np.all(dset1.value() == dset2.value())
    assert dset1.dtype == dset2.dtype
    # Try and fail to remove
    failed_successfully = False
    try:
        dset2.remove()
    except ReadOnlyError as exc:
        failed_successfully = True
    assert failed_successfully
    # Try and fail to set
    failed_successfully = False
    try:
        dset2.set(dset1_value)
    except ReadOnlyError as exc:
        failed_successfully = True
    assert failed_successfully
    # Try and fail to copy
    failed_successfully = False
    try:
        dset2.copy(dset1_tag)
    except ReadOnlyError as exc:
        failed_successfully = True
    assert failed_successfully
    # Try and fail to recompress
    failed_successfully = False
    try:
        dset2.recompress(dset1_tag)
    except ReadOnlyError as exc:
        failed_successfully = True
    assert failed_successfully
    # Get the sum
    assert not dset1.attrs.exists('sum')
    assert not dset2.attrs.exists('sum')
    dset_sum = dset2.sum()
    assert not dset2.attrs.exists('sum')
    assert dset_sum == dset1.sum()
    assert dset1.attrs.exists('sum')
    assert not dset2.attrs.exists('sum')

    # Get the min
    assert not dset1.attrs.exists('min')
    assert not dset2.attrs.exists('min')
    dset_min = dset2.min()
    assert not dset2.attrs.exists('min')
    assert dset_min == dset1.min()
    assert dset1.attrs.exists('min')
    assert not dset2.attrs.exists('min')

    # Get the max
    assert not dset1.attrs.exists('max')
    assert not dset2.attrs.exists('max')
    dset_max = dset2.max()
    assert dset_max == dset1.max()
    assert not dset2.attrs.exists('max')
    assert dset1.attrs.exists('max')
    assert not dset2.attrs.exists('max')

    dset1.recompress(compression="gzip")
    assert dset1.compression != dset2.compression

    
    return

######## Execution ########
if __name__ == "__main__":
    test_dataset()
