"""
CDM reader
"""

import logging
import os
import xarray as xr
from xarray import backends
from requests.exceptions import HTTPError
from pydap.client import open_url
import fileformats.cdm.accessors.dataarray  # register dataarray accessor
import fileformats.cdm.accessors.dataset  # register dataset accessor
from .accessors.dataset import SOURCE_NETCDF, SOURCE_OPENDAP, \
    OPENDAP_BACKEND_NETCDF, OPENDAP_BACKEND_PYDAP


def open_dataset(resource, opendap_backend=None):
    """
    Open dataset using xarray and register the ebas accessors.
    Parameters:
        resource: file path or OPeNDAP url
        opendap_backend: backend to use for OPeNDAP (OPENDAP_BACKEND_NETCDF,
                            OPENDAP_BACKEND_PYDAP or None for auto selection)
    Returns:
        xarray Dataset
    """
    logger = logging.getLogger('ebascdm')
    if os.path.isfile(resource):
        logger.debug("Open local NetCDF file: %s", resource)
        try:
            dataset = xr.open_dataset(resource)
        except ValueError as excpt:
            # NetCDF for localfiles raises a ValueError on file not found
            raise FileNotFoundError from excpt
        dataset.ebas.setup(
            resource=resource,
            source_type=SOURCE_NETCDF)
        return dataset
    if resource.startswith('http'):
        return _open_opendap(resource, backend=opendap_backend)
    logger.error("Resource %s is not valid. ", resource)
    raise FileNotFoundError("Resource %s is not valid. ", resource)

def _open_opendap(url, backend=None):
    """
    Open the OPeNDAP url.

    There is a problem opening an OPeNDAP url with xarray using the
    NetCDF backend for some files/variables (many variables).

    An alternative is to use the pydap backend via xarray, but this is
    slower than the NetCDF backend.

    Caller can either choose a specific backend or use auto selection:
    In this case NetCDF is tried first, then pydap.
    The caller may use EbasCDMReader.backend_type to check which backend was
    used (e.g. for implementing some learning).

    Parameters:
        url: OPeNDAP url
        backend: backend to use (OPENDAP_BACKEND_NETCDF,
                 OPENDAP_BACKEND_PYDAP or None for auto selection)
        Returns:
            None
    """

    def _open_pydap(url):
        # Normaly, one could use xr.backends.PydapDataStore directly with url
        # but this gives warnings about the dap2 protocol.
        # We open a pydap dataset before (we can specify the dap2 protocol
        # version explicitly and get not warnings), and then pass this to
        # PydapDataStore instead of only the url. Additionally it needs to be
        # wrapped in a fake object with a 'ds' attribute.
        # The original code (giving warnings) was:
        # store = backends.PydapDataStore.open(
        #     url, user_charset='UTF-8')
        # return xr.open_dataset(store)
        try:
            pydp = open_url(url, protocol='dap2', user_charset='UTF-8')
        except HTTPError as excpt:
            # pydap raises HTTPError of file not found
            # unfortunately, no status code can be checked as bot request ands
            # response attributes are None. We do a glumsy string match...
            if ' 404 ' in str(excpt):
                raise FileNotFoundError(url) from excpt
            # else raise the exception as is
            raise excpt
        fakeobj = type('Wrapper', (object,), {'ds':pydp})
        store = backends.PydapDataStore.open(fakeobj)
        dataset =  xr.open_dataset(store)
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_PYDAP)
        return dataset

    def _open_netcdf(url):
        try:
            dataset = xr.open_dataset(url)
        except OSError as excpt:
            # NetCDF raises OSError -90 on file not found
            # OSError: [Errno -90] NetCDF: file not found: 'https://...'
            if excpt.errno == -90:
                raise FileNotFoundError(url) from excpt
            # else raise the exception as is
            raise excpt
        dataset.ebas.setup(
            resource=url,
            source_type=SOURCE_OPENDAP,
            backend_type=OPENDAP_BACKEND_NETCDF)
        return dataset

    logger = logging.getLogger('ebascdm')
    logger.debug("Open OPeNDAP url: %s", url)
    if backend == OPENDAP_BACKEND_PYDAP:
        # force pydap backend
        dataset =_open_pydap(url)
        return dataset
    if backend == OPENDAP_BACKEND_NETCDF:
        # force NetCDF backend
        return _open_netcdf(url)
    # auto select backend, try NetCDF first
    try:
        return _open_netcdf(url)
    except RuntimeError:
        # use pydap fallback
        return _open_pydap(url)
