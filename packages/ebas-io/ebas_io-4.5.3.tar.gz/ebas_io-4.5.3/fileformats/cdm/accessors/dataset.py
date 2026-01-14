"""
EBAS Dataset Accessor for xarray Datasets
"""
from __future__ import annotations
import logging
import datetime
import numpy as np
import xarray as xr
from typing import Any
from collections.abc import (
    Iterable,
    Mapping)
from ebas.domain.basic_domain_logic.dataset_types import is_auxiliary
from nilutility.datetime_helper import DatetimeInterval, DatetimeIntervalSet


SOURCE_NETCDF = 1
SOURCE_OPENDAP = 2
OPENDAP_BACKEND_NETCDF = 1
OPENDAP_BACKEND_PYDAP = 2

@xr.register_dataset_accessor("ebas")
class EbasDatasetAccessor:
    """
    Ebas dataset accessor adds methods to xarray Dataset for EBAS CDM datasets.
    """

    def __init__(self, ds_obj):
        self.source_type = None
        self.backend_type = None
        self.resource = None
        self.logger = logging.getLogger('ebascdm')
        self._obj = ds_obj
        if '__ebas_internal_source_type' in self._obj.attrs:
            self.source_type = self._obj.attrs['__ebas_internal_source_type']
        else:
            self.source_type = None
        if '__ebas_internal_backend_type' in self._obj.attrs:
            self.backend_type = self._obj.attrs['__ebas_internal_backend_type']
        else:
            self.backend_type = None
        if '__ebas_internal_resource' in self._obj.attrs:
            self.resource = self._obj.attrs['__ebas_internal_resource']
        else:
            self.resource = None
        for _, var in self._obj.coords.items():
            var.ebas.setup(self)
        for _, var in self._obj.data_vars.items():
            var.ebas.setup(self)

    def setup(self, resource, source_type, backend_type=None):
        """
        Setup accessor.
        Parameters:
            resource: file path or OPeNDAP url
        """
        if source_type not in (SOURCE_NETCDF, SOURCE_OPENDAP):
            raise ValueError(f'Invalid source_type: {source_type}')
        if source_type == SOURCE_OPENDAP:
            if backend_type not in (OPENDAP_BACKEND_NETCDF,
                                    OPENDAP_BACKEND_PYDAP):
                raise ValueError(f'Invalid backend_type: {backend_type}')
        if source_type == SOURCE_NETCDF and backend_type is not None:
            raise ValueError('backend_type must be None for SOURCE_NETCDF')
        self.resource = resource
        self._obj.attrs['__ebas_internal_resource'] = resource
        self.source_type = source_type
        self._obj.attrs['__ebas_internal_source_type'] = source_type
        self.backend_type = backend_type
        self._obj.attrs['__ebas_internal_backend_type'] = backend_type
        if source_type == SOURCE_OPENDAP:
            # fix coordinate dtypes for OPeNDAP byte strings:
            # All should be converted to str (is byes in OPeNDAP)
            for dim in self._obj.dims:
                for dim in self._obj.coords:
                    if self._obj.coords[dim].dtype.kind == 'S':
                        self._obj.coords[dim] = self._obj.coords[dim].astype(
                            str)


    def data_vars(self, statistics=None, auxiliary=True, nonauxiliary=True):
        """
        Get ebas data variables
        Parameters:
            statistics: list of statistics to filter, or None for all
            auxiliary: if True, include auxiliary variables
            nonauxiliary: if True, include non-auxiliary variables
        Yields:
            xarray DataArray objects
        """
        for var in self.data_varnames(
                statistics=statistics,
                auxiliary=auxiliary,
                nonauxiliary=nonauxiliary):
            yield self._obj[var]

    def data_varnames(self, statistics=None, auxiliary=True, nonauxiliary=True):
        """
        Get ebas data variable names
        Parameters:
            statistics: list of statistics to filter, or None for all
            auxiliary: if True, include auxiliary variables
            nonauxiliary: if True, include non-auxiliary variables
        Yields:
            variable names
        """
        if isinstance(statistics, str):
            statistics = [statistics]
        for var in self._obj.data_vars:
            if 'ebas_component' not in self._obj[var].attrs:
                continue
            if ('ebas_statistics' not in self._obj[var].attrs or
                (statistics is not None and
                 self._obj[var].attrs['ebas_statistics'] not in statistics)):
                continue
            if  not auxiliary and is_auxiliary(
                self._obj[var].attrs['ebas_matrix'],
                self._obj[var].attrs['ebas_component']):
                continue
            if not nonauxiliary and not is_auxiliary(
                self._obj[var].attrs['ebas_matrix'],
                self._obj[var].attrs['ebas_component']):
                continue
            yield var

    def acdd_metadata(self):
        """
        Get ebas metadata from variable attributes.
        Parameters:
            None
        Returns:
            dict with metadata
        """
        ret = {}
        for key, val in self._obj.attrs.items():
            if not key.startswith('ebas_') and (
                self.source_type != SOURCE_OPENDAP or key != 'comment'):
                # ebas_metadata is an old concept from EBAS netCDF V1 files
                # which are now deprecated.
                # For some reason, ebas_metadata show up as comment attribute
                # when accessing through OPeNDAP
                ret[key] = val
        return ret

    def metadata(self):
        """
        Get ebas metadata from global attributes.
        Parameters:
            None
        Returns:
            dict with metadata
        """
        # global attributes
        ret = {}
        for key, val in self._obj.attrs.items():
            if key.startswith('ebas_') and key != 'ebas_metadata':
                # ebas_metadata is an old concept from EBAS netCDF V1 files
                # which are now deprecated
                ret[key] = val
        return ret

    def dim_values(self, dimname):
        """
        Get a list of values for a dimension
        """
        if dimname not in self._obj.dims:
            raise ValueError(f'{dimname} is not a dimension')
        return self._obj[dimname].values.tolist()
    
    def sel(
        self,
        indexers: Mapping[Any, Any] | None = None,
        method: str | None = None,
        tolerance: int | float | Iterable[int | float] | None = None,
        drop: bool = False,
        **indexers_kwargs: Any,
    ) -> xr.Dataset:
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
                if option in (1, 2):
                    bnds = self._obj['time_bnds']
                else:
                    bnds = self._obj['metadata_time_bnds']

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


    def find_variables(self, criteria):
        """
        Find variables matching criteria.
        Parameters:
            criteria: dict with attribute names and values to match
                    If value is False in criteria, then the dimension may not
                    exist.
                    If value is True in criteria, then the dimension must exist.
                    Else, the dimension value must be equal the set value
                    None is not allowed.
            
                    special key 'dims' may be used to match dimensions,
                    (i.e. characteristics in ebas):
                    E.g. 'dims': {'Wavelength': True},
                         'dims': {'D': 10.0, 'SS': True}
                         
                    Accordingly the different cases apply also for dimension
                    values:                    
                     - value is False in criteria: the dimension may not exist
                     - value is True in criteria: the dimension must exist
                     - value is a slice object: dimensions are slices
                     - value is a list: list of wanted dimension values
                     - else: dimension value must be equal the set value
                    None is not allowed.
        Yields:
            data arrays matching criteria, may be sliced if criteria matches
                time dependent metadata of a variable.
        """
        
        def _recurse_time_dependent_metadata(var, criteria):
            """
            Recurse time dependent metadata to find matches
            """
            if 'time' not in var.dims:
                # not an ebas variable with time dependent metadata
                return
            if var.dims != ('time', ):
                # need to go deeper into extra dimensions in order to get
                # time dependent metadata
                res = []
                allwidth = True
                # all subdimensions matched criteria at least for some time
                alldepth = True
                # the subdimensions that matched, matched with all time
                # intervals
                allintervals = None
                # time intervals, if all subdimensions matched with same
                # intervals. None on start, [] if different intervals
                for idx in range(var.sizes[var.dims[0]]):
                    res.append([])
                    for v, width, depth, intervals in _recurse_time_dependent_metadata(
                            var.isel({var.dims[0]: idx}), criteria):
                        if not width:
                            allwidth = False
                        if not depth:
                            alldepth = False
                            if allintervals and intervals != allintervals:
                                allintervals = []
                            if allintervals is None:
                                allintervals = intervals
                        res[-1].append((v, intervals))
                    if not res[-1]:
                        del res[-1]
                        allwidth = False
                if not res:
                    return
                if allwidth and alldepth:
                    # all subdimensions matched at all time intervals
                    yield var, True, True, allintervals
                elif allwidth and allintervals:
                    # all subdimensions matched, but not all time intervals,
                    # but with same time intervals
                    for intv in allintervals:
                        yield var.ebas.sel(time=slice(intv[0], intv[1])), \
                            True, False, allintervals
                elif allintervals:
                    # not all subdimensions matched, but the ones that matched
                    # matched with all time intervals
                    yield var.ebas.sel({
                        'time': allintervals,
                        var.dims[0]:
                             [x[0][0].coords[var.dims[0]].values.tolist()
                              for x in res]
                        }), False, True, allintervals
                else:
                    # not all subdimensions matched, and not at the same time
                    # intervals: yield matched slices separately
                    for dimidx in range(len(res)):
                        for v, intervals in res[dimidx]:
                            yield v, False, False, intervals
                # end of subdimension handling
            else:
                # base case: variable with only time dimension
                all_depth = True
                intervals = DatetimeIntervalSet()
                for meta in var.ebas.metadata_timedependent():
                    skip = False
                    for key, val in criteria.items():
                        if val is True:
                            if key not in meta:
                                # this criteria failed for this timerange
                                skip = True
                                break
                            else:
                                # this criteria is met for this timerange
                                intervals.add(meta['time_range'])
                                continue
                        if val is False:
                            if key in meta:
                                # this criteria failed for this timerange
                                skip = True
                                break
                            else:
                                # this criteria is met for this timerange
                                intervals.add(meta['time_range'])
                                continue
                        # value match
                        if key not in meta:
                            # this criteria failed for this timerange
                            skip = True
                            break
                        if isinstance(val, slice):
                            # slice match, we assume a scalar attribute value
                            if [meta[key]][val]:
                                # the slicing deliver=d a non-empty list, thus
                                # match
                                intervals.add(meta['time_range'])
                                continue
                            else:
                                # no match
                                skip = True
                                break
                        elif isinstance(val, list):
                            # list match, we assume a scalar attribute value
                            if meta[key] in val:
                                # attribute value is in the list, thus match
                                intervals.add(meta['time_range'])
                                continue
                            else:
                                # no match
                                skip = True
                                break
                        else:
                            # exact value match
                            if meta[key] == val:
                                # exact match
                                intervals.add(meta['time_range'])
                                continue
                            else:
                                # no match
                                skip = True
                                break
                    if skip:
                        all_depth = False
                        continue
                if all_depth:
                    # all time dependent metadata matched the criteria
                    yield var, True, True, intervals
                else:
                    # yield slices for matched time ranges
                    for intv in intervals:
                        yield var.ebas.sel(time=slice(intv[0], intv[1])), \
                            True, False, intervals
        # end of _recurse_time_dependent_metadata


        for var in self.data_vars():
            wrk_crit = criteria.copy()
            if 'dims' in wrk_crit:
                # check dimensions first
                skip = False
                select = {}
                mdims = {x.rstrip('x'): x for x in var.dims}
                # Modified dimension names without 'x' suffix
                # x is used when two dimensions have the same characteristics
                # type. E.g. temperature has characteristic 'Location' with
                # 'inlet' and 'instrument internal' while 'pressure' has
                # characteristic 'Location' with 'inlet' only.
                # Thus temperature dimensions are 'Location' and pressure
                # dimension is 'Locationx'.
                # We compare the base charateristic names without 'x' suffix.
                # but when selecting, we must use the full dimension name,
                # which we store as dict value.
                for dim in wrk_crit['dims']:
                    mdim = dim.rstrip('x')
                    if wrk_crit['dims'][dim] is None:
                        raise ValueError(
                            'None is not allowed as dimension value')
                    if wrk_crit['dims'][dim] is True:
                        if mdim not in mdims:
                            skip = True
                            break
                    elif wrk_crit['dims'][dim] is False:
                        if mdim in mdims:
                            skip = True
                            break
                    else:
                        # value check (slice, list or exact value)
                        if mdim not in mdims:
                            skip = True
                            break
                        if isinstance(wrk_crit['dims'][dim], slice):
                            # slice selection, just add to sleect
                            select[mdims[mdim]] = wrk_crit['dims'][dim]
                            continue
                        elif isinstance(wrk_crit['dims'][dim], list):
                            # list of values, avoid KeyError if one wrong is in
                            # list.
                            lst = list(set(wrk_crit['dims'][dim]).intersection(
                                var.coords[mdims[mdim]].values.tolist()))
                            if not lst:
                                skip = True
                                break
                            select[mdims[mdim]] = lst
                        else:
                            # exact value, avoin KeyError
                            if wrk_crit['dims'][dim] not in \
                                    var.coords[mdims[mdim]].values:
                                skip = True
                                break
                            select[mdims[mdim]] = wrk_crit['dims'][dim]
                if skip:
                    continue
                if select:
                    var = var.ebas.sel(**select)
                del wrk_crit['dims']

            skip = False
            for key, val in list(wrk_crit.items()):
                if key is None:
                    raise ValueError('None is not allowed as attribute key')
                if (val is True and key in var.attrs and
                        var.attrs[key] is not None):
                    # this criteria is met for the whole variable
                    del wrk_crit[key]
                    continue
                if (val is False and key in var.attrs and \
                        var.attrs[key] is not None):
                    # the whole variable has the attribute, thus no match
                    skip = True
                    break
                if val is not True and val is not False and \
                        key in var.attrs and var.attrs[key] is not None:
                    # value match
                    if isinstance(val, slice):
                        # slice match, we assume a scalar attribute value
                        if [var.attrs[key]][val]:
                            # the slicing deliver=d a non-empty list, thus match
                            del wrk_crit[key]
                            continue
                    elif isinstance(val, list):
                        # list match, we assume a scalar attribute value
                        if var.attrs[key] in val:
                            # attribute value is in the list, thus match
                            del wrk_crit[key]
                            continue
                    else:
                        # exact value match
                        if var.attrs[key] == val:
                            # exact match
                            del wrk_crit[key]
                            continue
            if skip:
                # variable did not match criteria
                continue
            if not wrk_crit:
                # all criteria matched
                yield var
            else:
                # else some criteria did not match (yet), need to look into time
                # dependent metadata
                for v, _, _, _ in _recurse_time_dependent_metadata(var, wrk_crit):
                    yield v
            