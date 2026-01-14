"""
EBAS CDM xarray DataArray accessor.
"""

from __future__ import annotations
import functools
import json
import re
import datetime
import logging
from typing import Any
from collections.abc import (
    Iterable,
    Mapping)
import requests
import xarray as xr
import numpy as np
from nilutility.datetime_helper import DatetimeInterval, DatetimeIntervalSet
from .dataset import SOURCE_NETCDF

functools.lru_cache(maxsize=100)
def lrucache_ebas_metadata_timedependent(self):
    """
    LRU chache for EbasCDMReader.get_time_dependent_metadata().
    """
    return EbasDataArrayAccessor._get_ebas_metadata_timedependent(self)


@xr.register_dataarray_accessor("ebas")
class EbasDataArrayAccessor:
    """
    Ebas data array accessor adds methods to xarray DataArray for EBAS CDM
    datasets.
    """

    def __init__(self, da_obj):
        self.logger = logging.getLogger('ebascdm')
        self._obj = da_obj
        if '__ebas_internal_parent_dataset' in self._obj.attrs:
            self._parent = self._obj.attrs['__ebas_internal_parent_dataset']
        else:
            self._parent = None

    def setup(self, parent):
        """
        Setup accessor.
        Parameters:
            parent: parent EbasDatasetAccessor
        """
        self._parent = parent
        self._obj.attrs['__ebas_internal_parent_dataset'] = parent

    def dim_values(self, dimname):
        """
        Get a list of values for a dimension
        """
        if dimname not in self._obj.dims:
            raise ValueError(f'{dimname} is not a dimension')
        # for some reason, OPeNDAP does not decode byte strings to utf-8 for
        # dimension values.
        # Local netCDF files are decoded correctly by xarray
        return [x.decode('utf-8') if isinstance(x, bytes) else x
                for x in self._obj.coords[dimname].values.tolist()]

    def metadata(self):
        """
        Get ebas metadata from variable attributes.
        Parameters:
            None
        Returns:
            dict with metadata
        """
        ret = {}
        for key, val in self._obj.attrs.items():
            if key.startswith('ebas_'):
                ret[key] = val
        return ret

    def metadata_timedependent(self):
        """
        Get time dependent metadata.
        Parameters:
            None
        Returns:
            list of dicts with metadata entries (each entry corresponds to a
            time interval, with added 'time_range' key)
        """
        return lrucache_ebas_metadata_timedependent(self)

    def time_bnds(self):
        """
        Get time bounds for the variable's time coordinate.
        Returns:
            DataArray with time bounds (list of DatetimeInterval)
        """
        if 'time' in self._obj.dims:
            time = self._parent._obj['time']
            bnds = self._parent._obj['time_bnds'].where(
                time == self._obj.coords['time'])
            return [DatetimeInterval(*x)
                    for x in bnds.values.astype( 'datetime64[us]' ).tolist()]
        elif 'metadata_time' in self._obj.dims:
            time = self._parent._obj['metadata_time']
            bnds = self._parent._obj['metadata_time_bnds'].where(
                time == self._obj.coords['metadata_time'])
            return [DatetimeInterval(*x)
                    for x in bnds.values.astype( 'datetime64[us]' ).tolist()]
        else:
            raise ValueError(
                'Variable has no time or metadata_time dimension')

    def sel(
        self,
        indexers: Mapping[Any, Any] | None = None,
        method: str | None = None,
        tolerance: int | float | Iterable[int | float] | None = None,
        drop: bool = False,
        **indexers_kwargs: Any,
    ) -> xr.DataArray:
        """
        Instead of base object's sel:
        Selection of time dimension is based on time_bnds, not time values.
        All samples that overlap with the selected time range are included.
        Time slicing supports also DatetimeInterval and DatetimeIntervalSet.
        Parameters:
            indexers: mapping of dimension names to indexers
            method: selection method
            tolerance: selection tolerance
            drop: whether to drop missing values
            **indexers_kwargs: indexers as keyword arguments
        Returns:
            selected/sliced DataArray
        """
        # change for both kwargs['time'] and indexers['time']...
        # and cases for metadata_time
        for option in range(4):
            # Option 1: time in indexers_kwargs
            # Option 2: time in indexers
            # Option 3: metadata_time in kwargs
            # Option 4: metadata_time in indexers
            if ((option == 1 and 'time' in indexers_kwargs) or
                (option == 2 and indexers and 'time' in indexers) or
                (option == 3 and 'metadata_time' in indexers_kwargs) or
                (option == 4 and indexers and 'metadata_time' in indexers)):
                time_sel = (indexers_kwargs['time'] if option == 1
                            else indexers['time'] if option == 2
                            else indexers_kwargs['metadata_time'] if option == 3
                            else indexers['metadata_time'])
                # We want to have bnds in the same size as our variable's
                # time
                if option in (1, 2):
                    time = self._parent._obj['time']
                    bnds = self._parent._obj['time_bnds'].where(
                        time == self._obj.coords['time'])
                else:
                    time = self._parent._obj['metadata_time']
                    bnds = self._parent._obj['metadata_time_bnds'].where(
                        time == self._obj.coords['metadata_time'])

                if isinstance(time_sel, slice) and time_sel.step is None:
                    # same as DatetimeInterval
                    new_sel = [time_sel.start, time_sel.stop]
                    for i in range(2):                       
                        if isinstance(new_sel[i], str):
                            # convert to np.datetime64 first for xarray
                            # compatible parsing
                            try:
                                new_sel[i] = np.datetime64(new_sel[i])
                            except ValueError:
                                continue
                        if isinstance(new_sel[i], np.datetime64):
                            # convert to datetime.datetime for DatetimeInterval
                            # datetime64[us] forces full precision, even if
                            # input has 'D' precision, which would generate a
                            # datetime.date
                            new_sel[i] = new_sel[i].astype(
                                'datetime64[us]').astype(datetime.datetime)
                    if ((new_sel[0] is not None and
                         not isinstance(new_sel[0], datetime.datetime) or
                        (new_sel[1] is not None and
                         not isinstance(new_sel[1], datetime.datetime)))):
                        # unknown type, let xarray handle it
                        continue
                    time_sel = DatetimeInterval(
                        new_sel[0], new_sel[1])
                    # no elif, we continue to process as DatetimeInterval
                if isinstance(time_sel, DatetimeInterval):
                    # Overlap selection based on time_bnds
                    # time_bnds values are always intervals with bounds '[)'
                    # i.e. including start, excluding end
                    # time_sel bounds can be '[)' (default), '[]', '(]' or '()'
                    # Overlap criteria for [a, b) and [c, d) or (c, d):
                    #     a < d and b > c
                    # Overlap criteria for [a, b) and [c, d] or (c, d]:
                    #     a <= d and b > c
                    # Only in the case where a and d are included we need to
                    # add equality in the comparison.
                    if time_sel.is_empty():
                        # empty interval, no matches, delete selection
                        if option == 1:
                            del indexers_kwargs['time']
                        elif option == 2:
                            del indexers['time']
                        elif option == 3:
                            del indexers_kwargs['metadata_time']
                        else:
                            # option == 4
                            del indexers['metadata_time']
                        continue
                    if time_sel.bounds in ('[)', '()'):
                        mask = xr.where(
                            (bnds[:,0] < np.datetime64(time_sel[1])) &
                            (bnds[:,1] > np.datetime64(time_sel[0])),
                            1, 0)
                    else:
                        # '[]' or '(]':
                        mask = xr.where(
                            (bnds[:,0] <= np.datetime64(time_sel[1])) &
                            (bnds[:,1] > np.datetime64(time_sel[0])),
                            1, 0)
                    if option == 1:
                        indexers_kwargs['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 2:
                        indexers['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 3:
                        indexers_kwargs['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                    else:
                        # option == 4
                        indexers['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                elif isinstance(time_sel, DatetimeIntervalSet):
                    if not time_sel:
                        # empty set, no matches, delete selection
                        if option == 1:
                            del indexers_kwargs['time']
                        elif option == 2:
                            del indexers['time']
                        elif option == 3:
                            del indexers_kwargs['metadata_time']
                        else:
                            del indexers['metadata_time']
                        continue
                    mask = None
                    # build combined mask for all intervals
                    for interval in time_sel:
                        if interval.is_empty():
                            # empty interval, no matches, ignore
                            continue
                        if interval.bounds in ('[)', '()'):
                            curmask = xr.where(
                                (bnds[:,0] < np.datetime64(interval[1])) &
                                (bnds[:,1] > np.datetime64(interval[0])),
                                1, 0)
                        else:
                            # '[]' or '(]':
                            curmask = xr.where(
                                (bnds[:,0] <= np.datetime64(interval[1])) &
                                (bnds[:,1] > np.datetime64(interval[0])),
                                1, 0)
                        if mask is None:
                            mask = curmask
                        else:
                            mask |= curmask
                    if option == 1:
                        indexers_kwargs['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 2:
                        indexers['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 3:
                        indexers_kwargs['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                    else:
                        # option == 4
                        indexers['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                elif isinstance(time_sel, (np.datetime64, datetime.datetime,
                                           str)):
                    # single time point
                    if isinstance(time_sel, str):
                        try:
                            np.datetime64(time_sel)
                        except ValueError:
                            continue  # let xarray handle invalid time string
                    mask = xr.where(
                        (bnds[:,0] <= np.datetime64(time_sel)) &
                        (bnds[:,1] > np.datetime64(time_sel)),
                        1, 0)
                    if not mask.any():
                        # no matches for this time, ignore selection
                        # We pass the original time selection and let xarray.sel
                        # handle the error.
                        continue
                    if option == 1:
                        indexers_kwargs['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 2:
                        indexers['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 3:
                        indexers_kwargs['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                    else:
                        # option == 4
                        indexers['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                elif isinstance(time_sel, Iterable):
                    # list of times
                    # !!! Needs to be in an elif after str, DatetimeInterval and
                    # DatetimeIntervalSet checks, as they are also Iterable!!!
                    if not time_sel:
                        # We only care about non empty selections, the rest will
                        # be handled by xarray
                        continue
                    mask = None
                    for tim in time_sel:
                        curmask = xr.where(
                            (bnds[:,0] <= np.datetime64(tim)) &
                            (bnds[:,1] > np.datetime64(tim)),
                            1, 0)
                        if not curmask.any():
                            # no matches for this time, for now we ignore it.
                            # Maybe raise an error? Or let xarray handle it?
                            # xarray's native sel raises an error if one
                            # of the selected times in a list has no match.
                            continue
                        if mask is None:
                            mask = curmask
                        else:
                            mask |= curmask
                    if option == 1:
                        indexers_kwargs['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 2:
                        indexers['time'] = \
                            self._obj.coords['time'].where(mask == 1, drop=True)
                    elif option == 3:
                        indexers_kwargs['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)
                    else:
                        # option == 4
                        indexers['metadata_time'] = \
                            self._obj.coords['metadata_time'].where(
                                mask == 1, drop=True)

        return self._obj.sel(
            indexers=indexers,
            method=method,
            tolerance=tolerance,
            drop=drop,
            **indexers_kwargs)

    def _get_ebas_metadata_timedependent(self):
        """
        Internal method to get time dependent metadata.
        Parameters:
            varname: variable name
            extra_dims: dict of extra dimension values
        Returns:
            list of dicts with metadata entries (each entry corresponds to a
            time interval, with added 'time_range' key)
        """
        varname = self._obj.name + '_ebasmetadata'
        dims = self._obj.dims
        if not dims:
            raise ValueError(
                f'Variable {self._obj.name} has no dimensions, '
                'no time dependent metadata available')
        if dims[-1] != 'time':
            raise ValueError(
                f'Variable {self._obj.name} does not have '
                'time as the last dimension, '
                'no time dependent metadata available')
        if len(dims) > 1:
            raise ValueError(
                f'Variable {varname} needs extra '
                f'dimension{"s" if len(dims) > 2 else ""} '
                f'{", ".join(dims[:-1])}')
        # get original variable's dims
        orig_dims =self._parent._obj[varname].dims
        if self._parent.source_type == SOURCE_NETCDF:
            # First prepare the section for extra dimensions
            # which are needed in the metadata variable to give it the same
            # shape. This might actually vary (given selection on data variable
            # can be done before by sel() on the whole dataset, or by sel() or
            # slice on the data array only).
            # Whatever the case, we will end up here with a metadata variable
            # devoid of any extra dimensions (only metadate_time left).
            selection = {}
            metadims = self._parent._obj[varname].dims
            for dim in orig_dims[:-1]:
                if dim in metadims:
                    dimval = self._obj.coords[dim].item()
                    selection[dim] = dimval
            # now prepare the slice for metadata_time dimension
            tbnds = self._parent._obj.time_bnds.sel(
                time=self._obj.coords['time'])
            selection['metadata_time'] = []
            for i, mtim in enumerate(self._parent._obj.metadata_time_bnds):
                if xr.where((tbnds[:,0] < mtim[1]) & (tbnds[:,1] > mtim[0]),
                            True, False).any():
                    selection['metadata_time'].append(
                        self._parent._obj.metadata_time[i].values)
            ret = [json.loads(txt)
                   for txt in self._parent._obj[varname].sel(
                       **selection).values]
            metatimebnds = self._parent._obj['metadata_time_bnds'].sel(
                metadata_time=selection['metadata_time'])
            for i in range(len(ret)):
                ret[i]['time_range'] = DatetimeInterval(
                    metatimebnds[i][0].values.astype(
                        'datetime64[us]').astype(datetime.datetime).replace(
                            tzinfo=datetime.timezone.utc),
                    metatimebnds[i][1].values.astype(
                        'datetime64[us]').astype(datetime.datetime).replace(
                            tzinfo=datetime.timezone.utc))
            return ret
        else:  # OPeNDAP:
            # There is a problem with reading the string arrays via xarray and
            # OPeNDAP (independent of the backend used). Only the first 64
            # characters are returned. This makes the json invalid.
            # As a workaround, the metadata variables are read via an OPenDAP
            # get ascii request manually, then converted to a clean json string
            # and parsed.
            # A note on the dods request: This had anoter issue with charset
            # encoding:
            #   The test only includes on NRT dataset, so the test case can not
            #   be referenced by DOI currently, here's a long description:
            #   The test case included PS 17642
            #     (address is "Chemin de l’Aeorologie"
            #   including \xe2\x80\x99 (unicode U+2019
            #     RIGHT SINGLE QUOTATION MARK)
            #   (this character has no iso-1 representation).
            #   The test case also included organisation CH08L (address
            #   "Chemin de l'Aérologie" with a normal ascii single quotation
            #   mark (0x27), and additionally an é character
            #   (\xc3\xa9, unicode U+00E9) LATIN SMALL LETTER E WITH ACUTE.
            #   This character is representable in iso-1 (E9).
            # The DODS, e.g
            #    https://thredds.nilu.no/thredds/dodsC/auto-pollen_nrt/CH0001G.20240701100000.20251020235427.pollen_monitor..aerosol.68w.1h.CH08L_JUPITER_CH0001G_1_NRT.FI01L_FMI_Poleno.lev1.5.nc.dods?pollen_alnus_amean_ebasmetadata)
            # The response conent contains:
            #   for the institute b"Chemin de l\'A\xe9rologie" -- the é is
            #   iso-1 encoded
            #   for the originator b"Chemin de l?Aeorologie" -- the U+2019 is
            #   replaced by ?
            # Conclusion: the DODS request returns iso-1 encoded content,
            # unicode characters not representable in iso-1 are lost (replaced
            # by ?).
            # --> DODS is not usable for metadata.
            #
            # Last resort: the ascii request is used, which returns utf-8
            # content.

            # First prepare the section for extra dimensions
            # For OPeNDAP, we always need to read from the full dataset,
            # so we need to reproduce ALL slices for extra dimensions which
            # have been applied to the data variable.
            slices = []
            for dim in orig_dims[:-1]:
                dimval = self._obj.coords[dim].item()
                dimind = self._parent._obj[dim].values.tolist().index(dimval)
                slices.append(dimind)
            # last dimension is metadata_time. Slice it according to time slices
            # in self._obj
            timeslices = []
            tbnds = self._parent._obj.time_bnds.sel(
                time=self._obj.coords['time'])
            for i, mtim in enumerate(self._parent._obj.metadata_time_bnds):
                if xr.where((tbnds[:,0] < mtim[1]) & (tbnds[:,1] > mtim[0]),
                            True, False).any():
                    timeslices.append(i)
            url = self._parent.resource + '.ascii?' + varname + \
                ''.join(['['+str(x)+']' for x in slices])
            res = requests.get(url, timeout=30)
            if res.status_code != 200:
                self.logger.error(
                    "Failed to fetch metadata via OPeNDAP ascii request: %s",
                    url)
                raise FileNotFoundError(
                    "Failed to fetch metadata via OPeNDAP ascii request")
            # OPeNDAP ascii request is UTF-8
            txt = res.content.decode('utf8')
            txt = re.sub(
                r'^Dataset.*---------------------------------------------\n'
                r'[^\n]*\n[\[\]\d, ]*"', '[',
                txt, flags=re.DOTALL)
            txt = re.sub(
                r'"\n}", "{\n', '"\n},\n{\n', txt, count=0,
                flags=re.DOTALL+re.MULTILINE)
            txt = re.sub(r'"\n*$', '\n]', txt)
            ret = [x for i, x in enumerate(json.loads(txt)) if i in timeslices]
            # add metadata time range to the metadata entries
            for i, times in enumerate(
                    self._parent._obj['metadata_time_bnds'][timeslices]):
                ret[i]['time_range'] = DatetimeInterval(
                    times[0].values.astype('datetime64[us]').astype(
                        datetime.datetime).replace(
                            tzinfo=datetime.timezone.utc),
                    times[1].values.astype('datetime64[us]').astype(
                        datetime.datetime).replace(
                            tzinfo=datetime.timezone.utc))
            return ret
