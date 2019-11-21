# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, unicode_literals

import datetime as dt
from io import StringIO
import logging
import numpy as np
import os
from sys import version_info
import pytest
import warnings

import aacgmv2

class TestConvertLatLon:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.ddate = dt.date(2015, 1, 1)
        self.in_args = [60, 0, 300, self.dtime, 'TRACE']
        self.out = None
        self.ref = [58.2258, 81.1685, 1.0457]
        self.rtol = 1.0e-4

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.out, self.in_args, self.ref, self.rtol, self.dtime, self.ddate

    def test_convert_latlon(self):
        """Test single value latlon conversion"""
        self.out = aacgmv2.convert_latlon(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    def test_convert_latlon_badidea(self):
        """Test single value latlon conversion with a bad flag"""
        self.in_args[2] = 3000.0
        self.in_args[-1] = "G2A|BADIDEA"
        self.ref = [64.3568, 83.3027, 1.4694]
        self.out = aacgmv2.convert_latlon(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    def test_convert_latlon_trace_badidea(self):
        """Test single value latlon conversion with a bad flag for trace"""
        self.in_args[2] = 7000.0
        self.in_args[-1] = "G2A|TRACE|BADIDEA"
        self.ref = [69.3174, 85.0995, 2.0973]
        self.out = aacgmv2.convert_latlon(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    @pytest.mark.skipif(version_info.major == 2,
                        reason='Not raised in Python 2')
    def test_convert_latlon_location_failure(self):
        """Test single value latlon conversion with a bad location"""
        self.out = aacgmv2.convert_latlon(0, 0, 0, self.dtime, self.in_args[-1])
        assert np.all(np.isnan(np.array(self.out)))

    def test_convert_latlon_time_failure(self):
        """Test single value latlon conversion with a bad datetime"""
        self.in_args[3] = None
        with pytest.raises(ValueError):
            self.out = aacgmv2.convert_latlon(*self.in_args)

    def test_convert_latlon_datetime_date(self):
        """Test single latlon conversion with date and datetime input"""
        self.in_args[3] = self.ddate
        self.out = aacgmv2.convert_latlon(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    def test_convert_latlon_maxalt_failure(self):
        """test convert_latlon failure for an altitude too high for coeffs"""
        self.in_args[2] = 2001
        self.in_args[-1] = ""
        self.out = aacgmv2.convert_latlon(*self.in_args)
        assert np.all(np.isnan(np.array(self.out)))

    def test_convert_latlon_lat_high_failure(self):
        """Test error return for co-latitudes above 90 for a single value"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon(91, 0, 300, self.dtime)

    def test_convert_latlon_lat_low_failure(self):
        """Test error return for co-latitudes below -90 for a single value"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon(-91, 0, 300, self.dtime)

class TestConvertLatLonArr:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.ddate = dt.date(2015, 1, 1)
        self.lat_in = [60.0, 61.0]
        self.lon_in = [0.0, 0.0]
        self.alt_in = [300.0, 300.0]
        self.method = 'TRACE'
        self.out = None
        self.ref = [[58.22474610, 59.31648007], [81.17611033, 81.62281360],
                    [1.04566346, 1.04561304]]
        self.rtol = 1.0e-4

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.lat_in, self.lon_in, self.alt_in, self.dtime, self.ddate
        del self.method, self.out, self.ref, self.rtol

    def test_convert_latlon_arr_single_val(self):
        """Test array latlon conversion for a single value"""
        self.out = aacgmv2.convert_latlon_arr(self.lat_in[0], self.lon_in[0],
                                              self.alt_in[0], self.dtime,
                                              self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_convert_latlon_arr_list_single(self):
        """Test array latlon conversion for list input of single values"""
        self.out = aacgmv2.convert_latlon_arr([self.lat_in[0]],
                                              [self.lon_in[0]],
                                              [self.alt_in[0]], self.dtime,
                                              self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_convert_latlon_arr_list(self):
        """Test array latlon conversion for list input"""
        self.out = aacgmv2.convert_latlon_arr(self.lat_in, self.lon_in,
                                              self.alt_in, self.dtime,
                                              self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.ref[i])
                for i, oo in enumerate(self.out)]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_convert_latlon_arr_arr_single(self):
        """Test array latlon conversion for array input of shape (1,)"""
        self.out = aacgmv2.convert_latlon_arr(np.array([self.lat_in[0]]),
                                              np.array([self.lon_in[0]]),
                                              np.array([self.alt_in[0]]),
                                              self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_convert_latlon_arr_arr(self):
        """Test array latlon conversion for array input"""
        self.out = aacgmv2.convert_latlon_arr(np.array(self.lat_in),
                                              np.array(self.lon_in),
                                              np.array(self.alt_in),
                                              self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.ref[i])
                for i, oo in enumerate(self.out)]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_convert_latlon_arr_list_mix(self):
        """Test array latlon conversion for mixed types with list"""
        self.out = aacgmv2.convert_latlon_arr(self.lat_in, self.lon_in[0],
                                              self.alt_in[0], self.dtime,
                                              self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.ref[i])
                for i, oo in enumerate(self.out)]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_convert_latlon_arr_arr_mix(self):
        """Test array latlon conversion for mixed type with an array"""
        self.out = aacgmv2.convert_latlon_arr(np.array(self.lat_in),
                                              self.lon_in[0], self.alt_in[0],
                                              self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.ref[i])
                for i, oo in enumerate(self.out)]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_convert_latlon_arr_mult_failure(self):
        """Test array latlon conversion for mix type with multi-dim array"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon_arr(np.full(shape=(3,2), fill_value=50.0),
                                       0, 300, self.dtime)


    def test_convert_latlon_arr_badidea(self):
        """Test array latlon conversion for BADIDEA"""
        self.method = "G2A | BADIDEA"
        self.ref = [64.35677791, 83.30272053, 1.46944431]
        self.out = aacgmv2.convert_latlon_arr(self.lat_in[0], self.lon_in[0],
                                              [3000], self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i]], rtol=self.rtol)

    def test_convert_latlon_arr_badidea_trace(self):
        """Test array latlon conversion for BADIDEA with trace"""
        self.method = "G2A | BADIDEA | TRACE"
        self.ref = [69.317391, 85.099499, 2.09726]
        self.out = aacgmv2.convert_latlon_arr(self.lat_in[0], self.lon_in[0],
                                              [7000], self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i]], rtol=self.rtol)

    @pytest.mark.skipif(version_info.major == 2,
                        reason='Not raised in Python 2')
    def test_convert_latlon_arr_location_failure(self):
        """Test array latlon conversion with a bad location"""

        with warnings.catch_warnings():
            # Causes all warnings to be surpressed
            warnings.simplefilter("ignore")

            # Trigger a warning
            self.out = aacgmv2.convert_latlon_arr([0], [0], [0], self.dtime, "")

            # Test the output
            assert len(self.out) == len(self.ref)
            assert np.any(~np.isfinite(np.array(self.out)))

    def test_convert_latlon_arr_mult_arr_unequal_failure(self):
        """Test array latlon conversion for unequal sized arrays"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon_arr(np.array([[60, 61, 62], [63, 64, 65]]),
                                       np.array([0, 1]), 300, self.dtime)

    def test_convert_latlon_arr_time_failure(self):
        """Test array latlon conversion with a bad time"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon_arr(self.lat_in, self.lon_in, self.alt_in,
                                       None, self.method)

    def test_convert_latlon_arr_datetime_date(self):
        """Test array latlon conversion with date and datetime input"""
        self.out = aacgmv2.convert_latlon_arr(self.lat_in, self.lon_in,
                                              self.alt_in, self.ddate,
                                              self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.ref[i])
                for i, oo in enumerate(self.out)]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_convert_latlon_arr_maxalt_failure(self):
        """test convert_latlon_arr failure for altitudes too high for coeffs"""
        self.method = ""
        self.out = aacgmv2.convert_latlon_arr(self.lat_in[0], self.lon_in[0],
                                              [2001], self.dtime, self.method)
        assert np.all(np.isnan(np.array(self.out)))

    def test_convert_latlon_arr_lat_failure(self):
        """Test error return for co-latitudes above 90 for an array"""
        with pytest.raises(ValueError):
            aacgmv2.convert_latlon_arr([91, 60, -91], 0, 300, self.dtime)

class TestGetAACGMCoord:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.ddate = dt.date(2015, 1, 1)
        self.in_args = [60, 0, 300, self.dtime, 'TRACE']
        self.out = None
        self.ref = [58.22474610, 81.17611033, 0.18892]
        self.rtol = 1.0e-4

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.out, self.in_args, self.ref, self.rtol, self.dtime, self.ddate

    def test_get_aacgm_coord(self):
        """Test single value AACGMV2 calculation, defaults to TRACE"""
        self.out = aacgmv2.get_aacgm_coord(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    def test_get_aacgm_coord_badidea(self):
        """Test single value AACGMV2 calculation with a bad flag"""
        self.in_args[-1] = "BADIDEA"
        self.in_args[2] = 3000
        self.ref = [64.3568, 83.3027, 0.3307]
        self.out = aacgmv2.get_aacgm_coord(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    @pytest.mark.skipif(version_info.major == 2,
                        reason='Not raised in Python 2')
    def test_get_aacgm_coord_location_failure(self):
        """Test single value AACGMV2 calculation with a bad location"""

        self.in_args[0] = 0.0
        self.in_args[2] = 0.0
        self.out = aacgmv2.get_aacgm_coord(*self.in_args)
        np.all(np.isnan(np.array(self.out)))

    def test_get_aacgm_coord_time_failure(self):
        """Test single value AACGMV2 calculation with a bad datetime"""
        self.in_args[3] = None
        with pytest.raises(ValueError):
            self.out = aacgmv2.get_aacgm_coord(*self.in_args)

    def test_get_aacgm_coord_mlat_high_failure(self):
        """Test error return for co-latitudes above 90 for a single value"""
        self.in_args[0] = 91.0
        with pytest.raises(ValueError):
            aacgmv2.get_aacgm_coord(*self.in_args)

    def test_get_aacgm_coord_mlat_low_failure(self):
        """Test error return for co-latitudes below -90 for a single value"""
        self.in_args[0] = -91.0
        with pytest.raises(ValueError):
            aacgmv2.get_aacgm_coord(*self.in_args)

    def test_get_aacgm_coord_datetime_date(self):
        """Test single AACGMV2 calculation with date and datetime input"""
        self.in_args[3] = self.ddate
        self.out = aacgmv2.get_aacgm_coord(*self.in_args)
        np.testing.assert_allclose(self.out, self.ref, rtol=self.rtol)

    def test_get_aacgm_coord_maxalt_failure(self):
        """test get_aacgm_coord failure for an altitude too high for coeffs"""
        self.in_args[2] = 2001
        self.in_args[-1] = ""
        self.out = aacgmv2.get_aacgm_coord(*self.in_args)
        assert np.all(np.isnan(np.array(self.out)))

class TestGetAACGMCoordArr:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.ddate = dt.date(2015, 1, 1)
        self.lat_in = [60.0, 61.0]
        self.lon_in = [0.0, 0.0]
        self.alt_in = [300.0, 300.0]
        self.method = 'TRACE'
        self.out = None
        self.ref = [[58.22474610, 59.31648007], [81.17611033, 81.62281360],
                    [0.18891995, 0.21870017]]
        self.rtol = 1.0e-4

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.out, self.ref, self.lat_in, self.dtime, self.ddate
        del self.lon_in, self.alt_in, self.method, self.rtol

    def test_get_aacgm_coord_arr_single_val(self):
        """Test array AACGMV2 calculation for a single value"""
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in[0], self.lon_in[0],
                                               self.alt_in[0], self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_get_aacgm_coord_arr_list_single(self):
        """Test array AACGMV2 calculation for list input of single values"""
        self.out = aacgmv2.get_aacgm_coord_arr([self.lat_in[0]],
                                               [self.lon_in[0]],
                                               [self.alt_in[0]], self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_get_aacgm_coord_arr_list(self):
        """Test array AACGMV2 calculation for list input"""
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in,self.lon_in,
                                               self.alt_in, self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_get_aacgm_coord_arr_arr_single(self):
        """Test array AACGMV2 calculation for array with a single value"""
        self.out = aacgmv2.get_aacgm_coord_arr(np.array([self.lat_in[0]]),
                                               np.array([self.lon_in[0]]),
                                               np.array([self.alt_in[0]]),
                                               self.dtime, self.method)


        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, [self.ref[i][0]], rtol=self.rtol)

    def test_get_aacgm_coord_arr_arr(self):
        """Test array AACGMV2 calculation for an array"""
        self.out = aacgmv2.get_aacgm_coord_arr(np.array(self.lat_in),
                                               np.array(self.lon_in),
                                               np.array(self.alt_in),
                                               self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_get_aacgm_coord_arr_list_mix(self):
        """Test array AACGMV2 calculation for a list and floats"""
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in[0],
                                               self.alt_in[0], self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)  

    def test_get_aacgm_coord_arr_arr_mix(self):
        """Test array AACGMV2 calculation for an array and floats"""
        self.out = aacgmv2.get_aacgm_coord_arr(np.array(self.lat_in),
                                               self.lon_in[0], self.alt_in[0],
                                               self.dtime, self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_get_aacgm_coord_arr_mult_failure(self):
        """Test aacgm_coord_arr failure with multi-dim array input"""

        with pytest.raises(ValueError):
            (self.mlat_out, self.mlon_out,
             self.mlt_out) = aacgmv2.get_aacgm_coord_arr(
                 np.array([[60, 61, 62], [63, 64, 65]]), 0, 300, self.dtime)

    def test_get_aacgm_coord_arr_badidea(self):
        """Test array AACGMV2 calculation for BADIDEA"""
        self.method = "|".join([self.method, "BADIDEA"])
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in[0], self.lon_in[0],
                                               [3000.0], self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]

        self.ref = [64.34650424987989, 83.30339395305012, 0.3307388620896745]
        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    @pytest.mark.skipif(version_info.major == 2,
                        reason='Not raised in Python 2')
    def test_get_aacgm_coord_arr_location_failure(self):
        """Test array AACGMV2 calculation with a bad location"""
        self.out = aacgmv2.get_aacgm_coord_arr([0], [0], [0], self.dtime,
                                               self.method)

        
        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == 1 for oo in self.out]
        assert np.any([np.isnan(oo) for oo in self.out])

    def test_get_aacgm_coord_arr_time_failure(self):
        """Test array AACGMV2 calculation with a bad time"""
        with pytest.raises(ValueError):
            aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in, self.alt_in,
                                        None, self.method)

    def test_get_aacgm_coord_arr_mlat_failure(self):
        """Test error return for co-latitudes above 90 for an array"""

        self.lat_in = [91, 60, -91]
        with pytest.raises(ValueError):
            self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in[0],
                                                   self.alt_in[0], self.dtime,
                                                   self.method)

    def test_get_aacgm_coord_arr_datetime_date(self):
        """Test array AACGMV2 calculation with date and datetime input"""
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in,
                                               self.alt_in, self.ddate,
                                               self.method)
        self.ref = aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in,
                                               self.alt_in, self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]

        for i, oo in enumerate(self.out):
            np.testing.assert_allclose(oo, self.ref[i], rtol=self.rtol)

    def test_get_aacgm_coord_arr_maxalt_failure(self):
        """test aacgm_coord_arr failure for an altitude too high for coeff"""
        self.method = ""
        self.alt_in = [2001 for ll in self.lat_in]
        self.out = aacgmv2.get_aacgm_coord_arr(self.lat_in, self.lon_in,
                                               self.alt_in, self.dtime,
                                               self.method)

        assert len(self.out) == len(self.ref)
        assert [isinstance(oo, np.ndarray) and len(oo) == len(self.lat_in)
                for oo in self.out]
        assert np.all(np.isnan(np.array(self.out)))


class TestConvertCode:
    @classmethod
    def test_convert_str_to_bit_g2a(self):
        """Test conversion from string code to bit G2A"""
        if aacgmv2.convert_str_to_bit("G2A") != aacgmv2._aacgmv2.G2A:
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_a2g(self):
        """Test conversion from string code to bit A2G"""
        if aacgmv2.convert_str_to_bit("A2G") != aacgmv2._aacgmv2.A2G:
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_trace(self):
        """Test conversion from string code to bit TRACE"""
        if aacgmv2.convert_str_to_bit("TRACE") != aacgmv2._aacgmv2.TRACE:
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_allowtrace(self):
        """Test conversion from string code to bit ALLOWTRACE"""
        if(aacgmv2.convert_str_to_bit("ALLOWTRACE") !=
           aacgmv2._aacgmv2.ALLOWTRACE):
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_badidea(self):
        """Test conversion from string code to bit BADIDEA"""
        if(aacgmv2.convert_str_to_bit("BADIDEA") !=
           aacgmv2._aacgmv2.BADIDEA):
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_geocentric(self):
        """Test conversion from string code to bit GEOCENTRIC"""
        if(aacgmv2.convert_str_to_bit("GEOCENTRIC") !=
           aacgmv2._aacgmv2.GEOCENTRIC):
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_lowercase(self):
        """Test conversion from string code to bit for a lowercase code"""
        if aacgmv2.convert_str_to_bit("g2a") != aacgmv2._aacgmv2.G2A:
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_spaces(self):
        """Test conversion from string code to bit for a code with spaces"""
        if(aacgmv2.convert_str_to_bit("G2A | trace") !=
           aacgmv2._aacgmv2.G2A + aacgmv2._aacgmv2.TRACE):
            raise AssertionError()

    @classmethod
    def test_convert_str_to_bit_invalid(self):
        """Test conversion from string code to bit for an invalid code"""
        if aacgmv2.convert_str_to_bit("ggoogg|") != aacgmv2._aacgmv2.G2A:
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_g2a(self):
        """Test conversion from string code to bit G2A"""
        if aacgmv2.convert_bool_to_bit() != aacgmv2._aacgmv2.G2A:
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_a2g(self):
        """Test conversion from string code to bit A2G"""
        if aacgmv2.convert_bool_to_bit(a2g=True) != aacgmv2._aacgmv2.A2G:
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_trace(self):
        """Test conversion from string code to bit TRACE"""
        if aacgmv2.convert_bool_to_bit(trace=True) != aacgmv2._aacgmv2.TRACE:
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_allowtrace(self):
        """Test conversion from string code to bit ALLOWTRACE"""
        if(aacgmv2.convert_bool_to_bit(allowtrace=True) !=
           aacgmv2._aacgmv2.ALLOWTRACE):
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_badidea(self):
        """Test conversion from string code to bit BADIDEA"""
        if(aacgmv2.convert_bool_to_bit(badidea=True) !=
           aacgmv2._aacgmv2.BADIDEA):
            raise AssertionError()

    @classmethod
    def test_convert_bool_to_bit_geocentric(self):
        """Test conversion from string code to bit GEOCENTRIC"""
        if(aacgmv2.convert_bool_to_bit(geocentric=True) !=
           aacgmv2._aacgmv2.GEOCENTRIC):
            raise AssertionError()

class TestMLTConvert:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.dtime2 = dt.datetime(2015, 1, 1, 10, 0, 0)
        self.ddate = dt.date(2015, 1, 1)
        self.mlon_out = None
        self.mlt_out = None
        self.mlt_diff = None
        self.mlon_list = [270.0, 80.0, -95.0]
        self.mlt_list = [12.0, 25.0, -1.0]
        self.mlon_comp = [-101.657689, 93.34231102, 63.34231102]
        self.mlt_comp = [12.77717927, 0.1105126, 12.44384593]
        self.diff_comp = np.ones(shape=(3,)) * -10.52411552

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.mlon_out, self.mlt_out, self.mlt_list, self.mlon_list
        del self.mlon_comp, self.mlt_comp, self.mlt_diff, self.diff_comp

    def test_date_input(self):
        """Test to see that the date input works"""
        self.mlt_out = aacgmv2.convert_mlt(self.mlon_list, self.ddate,
                                           m2a=False)
        np.testing.assert_allclose(self.mlt_out, self.mlt_comp, rtol=1.0e-4)

    def test_datetime_exception(self):
        """Test to see that a value error is raised with bad time input"""
        with pytest.raises(ValueError):
            self.mlt_out = aacgmv2.wrapper.convert_mlt(self.mlon_list, 1997)

    def test_inv_convert_mlt_single(self):
        """Test MLT inversion for a single value"""
        for i,mlt in enumerate(self.mlt_list):
            self.mlon_out = aacgmv2.convert_mlt(mlt, self.dtime, m2a=True)
            np.testing.assert_almost_equal(self.mlon_out, self.mlon_comp[i],
                                           decimal=4)

    def test_inv_convert_mlt_list(self):
        """Test MLT inversion for a list"""
        self.mlon_out = aacgmv2.convert_mlt(self.mlt_list, self.dtime, m2a=True)
        np.testing.assert_allclose(self.mlon_out, self.mlon_comp, rtol=1.0e-4)

    def test_inv_convert_mlt_arr(self):
        """Test MLT inversion for an array"""
        self.mlon_out = aacgmv2.convert_mlt(np.array(self.mlt_list), self.dtime,
                                            m2a=True)

        np.testing.assert_allclose(self.mlon_out, self.mlon_comp, rtol=1.0e-4)

    def test_inv_convert_mlt_wrapping(self):
        """Test MLT wrapping"""
        self.mlon_out = aacgmv2.convert_mlt(np.array([1, 25, -1, 23]),
                                            self.dtime, m2a=True)

        np.testing.assert_almost_equal(self.mlon_out[0], self.mlon_out[1],
                                       decimal=6)
        np.testing.assert_almost_equal(self.mlon_out[2], self.mlon_out[3],
                                       decimal=6)

    def test_mlt_convert_mlon_wrapping(self):
        """Test mlon wrapping"""
        self.mlt_out = aacgmv2.convert_mlt(np.array([270, -90, 1, 361]),
                                           self.dtime, m2a=False)

        np.testing.assert_almost_equal(self.mlt_out[0], self.mlt_out[1],
                                       decimal=6)
        np.testing.assert_almost_equal(self.mlt_out[2], self.mlt_out[3],
                                       decimal=6)

    def test_mlt_convert_single(self):
        """Test MLT calculation for a single value"""
        for i,mlon in enumerate(self.mlon_list):
            self.mlt_out = aacgmv2.convert_mlt(mlon, self.dtime, m2a=False)
            np.testing.assert_almost_equal(self.mlt_out, self.mlt_comp[i],
                                           decimal=4)

    def test_mlt_convert_list(self):
        """Test MLT calculation for a list"""
        self.mlt_out = aacgmv2.convert_mlt(self.mlon_list, self.dtime,
                                           m2a=False)
        np.testing.assert_allclose(self.mlt_out, self.mlt_comp, rtol=1.0e-4)

    def test_mlt_convert_arr(self):
        """Test MLT calculation for an array"""
        self.mlt_out = aacgmv2.convert_mlt(np.array(self.mlon_list),
                                           self.dtime, m2a=False)
        np.testing.assert_allclose(self.mlt_out, self.mlt_comp, rtol=1.0e-4)

    def test_mlt_convert_list_w_times(self):
        """Test MLT calculation for data and time arrays"""
        self.dtime = [self.dtime for dd in self.mlon_list]
        self.mlt_out = aacgmv2.convert_mlt(self.mlon_list, self.dtime,
                                           m2a=False)
        np.testing.assert_allclose(self.mlt_out, self.mlt_comp, rtol=1.0e-4)

    def test_mlt_convert_change(self):
        """Test that MLT changes with UT"""
        self.mlt_out = aacgmv2.convert_mlt(self.mlon_list, self.dtime)
        self.mlt_diff = np.array(self.mlt_out) \
            - np.array(aacgmv2.convert_mlt(self.mlon_list, self.dtime2))

        np.testing.assert_allclose(self.mlt_diff, self.diff_comp, rtol=1.0e-4)

    def test_mlt_convert_multidim_failure(self):
        """Test MLT calculation failure for multi-dimensional arrays"""
        self.mlon_list = np.full(shape=(3,2), fill_value=50.0)
        with pytest.raises(ValueError):
            aacgmv2.convert_mlt(self.mlon_list, self.dtime, m2a=False)

    def test_mlt_convert_mismatch_failure(self):
        """Test MLT calculation failure for mismatched array input"""
        with pytest.raises(ValueError):
            aacgmv2.convert_mlt(self.mlon_list, [self.dtime, self.dtime2],
                                m2a=False)

class TestCoeffPath:

    def setup(self):
        """Runs before every method to create a clean testing setup"""
        os.environ['IGRF_COEFFS'] = "default_igrf"
        os.environ['AACGM_v2_DAT_PREFIX'] = "default_coeff"
        self.default_igrf = os.environ['IGRF_COEFFS']
        self.default_coeff = os.environ['AACGM_v2_DAT_PREFIX']

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.default_igrf, self.default_coeff

    def test_set_coeff_path_default(self):
        """Test the coefficient path setting using default values"""
        aacgmv2.wrapper.set_coeff_path()

        if os.environ['IGRF_COEFFS'] != self.default_igrf:
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != self.default_coeff:
            raise AssertionError()

    @classmethod
    def test_set_coeff_path_string(self):
        """Test the coefficient path setting using two user specified values"""
        aacgmv2.wrapper.set_coeff_path("hi", "bye")

        if os.environ['IGRF_COEFFS'] != "hi":
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != "bye":
            raise AssertionError()

    @classmethod
    def test_set_coeff_path_true(self):
        """Test the coefficient path setting using the module values"""
        aacgmv2.wrapper.set_coeff_path(True, True)

        if os.environ['IGRF_COEFFS'] != aacgmv2.IGRF_COEFFS:
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != aacgmv2.AACGM_v2_DAT_PREFIX:
            raise AssertionError()

    def test_set_only_aacgm_coeff_path(self):
        """Test the coefficient path setting using a mix of input"""
        aacgmv2.wrapper.set_coeff_path(coeff_prefix="hi")

        if os.environ['IGRF_COEFFS'] != self.default_igrf:
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != "hi":
            raise AssertionError()

    def test_set_only_igrf_coeff_path(self):
        """Test the coefficient path setting using a mix of input"""
        aacgmv2.wrapper.set_coeff_path(igrf_file="hi")

        if os.environ['IGRF_COEFFS'] != "hi":
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != self.default_coeff:
            raise AssertionError()

    @classmethod
    def test_set_both_mixed(self):
        """Test the coefficient path setting using a mix of input"""
        aacgmv2.wrapper.set_coeff_path(igrf_file=True, coeff_prefix="hi")

        if os.environ['IGRF_COEFFS'] != aacgmv2.IGRF_COEFFS:
            raise AssertionError()
        if os.environ['AACGM_v2_DAT_PREFIX'] != "hi":
            raise AssertionError()

class TestHeightReturns:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.code = aacgmv2._aacgmv2.A2G
        self.bad_code = aacgmv2._aacgmv2.BADIDEA
        self.trace_code = aacgmv2._aacgmv2.TRACE
        
    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.code, self.bad_code

    def test_low_height_good(self):
        """ Test to see that a very low height is still accepted"""

        assert aacgmv2.wrapper.test_height(-1, self.code)

    def test_high_coeff_bad(self):
        """ Test to see that a high altitude for coefficent use fails"""

        assert not aacgmv2.wrapper.test_height(aacgmv2.high_alt_coeff+10.0,
                                               self.code)

    def test_high_coeff_good(self):
        """ Test a high altitude for coefficent use with badidea """

        assert aacgmv2.wrapper.test_height(aacgmv2.high_alt_coeff+10.0,
                                           self.bad_code)

    def test_low_coeff_good(self):
        """ Test that a normal height succeeds"""
        assert aacgmv2.wrapper.test_height(aacgmv2.high_alt_coeff*0.5,
                                           self.code)

    def test_high_trace_bad(self):
        """ Test that a high trace height fails"""
        assert not aacgmv2.wrapper.test_height(aacgmv2.high_alt_trace+10.0,
                                               self.code)

    def test_low_trace_good(self):
        """ Test that a high coefficient height succeeds with trace"""
        assert aacgmv2.wrapper.test_height(aacgmv2.high_alt_coeff+10.0,
                                           self.trace_code)

    def test_high_trace_good(self):
        """ Test that a high trace height succeeds with badidea"""
        assert aacgmv2.wrapper.test_height(aacgmv2.high_alt_trace+10.0,
                                           self.bad_code)


class TestPyLogging:
    def setup(self):
        """Runs before every method to create a clean testing setup"""

        self.lwarn = u""
        self.lout = u""
        self.log_capture = StringIO()
        aacgmv2.logger.addHandler(logging.StreamHandler(self.log_capture))
        aacgmv2.logger.setLevel(logging.INFO)

    def teardown(self):
        """Runs after every method to clean up previous testing"""
        self.log_capture.close()
        del self.lwarn, self.lout, self.log_capture


    def test_warning_below_ground(self):
        """ Test that a warning is issued if height < 0 for height test """
        self.lwarn = u"conversion not intended for altitudes < 0 km"

        aacgmv2.wrapper.test_height(-1, 0)
        self.lout = self.log_capture.getvalue()
        if self.lout.find(self.lwarn) < 0:
            raise AssertionError()

    def test_warning_magnetosphere(self):
        """ Test that a warning is issued if altitude is very high"""
        self.lwarn = u"coordinates are not intended for the magnetosphere"

        aacgmv2.wrapper.test_height(70000, aacgmv2._aacgmv2.TRACE)
        self.lout = self.log_capture.getvalue()
        if self.lout.find(self.lwarn) < 0:
            raise AssertionError()

    def test_warning_high_coeff(self):
        """ Test that a warning is issued if altitude is very high"""
        self.lwarn = u"must either use field-line tracing (trace=True"

        aacgmv2.wrapper.test_height(3000, 0)
        self.lout = self.log_capture.getvalue()
        if self.lout.find(self.lwarn) < 0:
            raise AssertionError()

    def test_warning_single_loc_in_arr(self):
        """ Test that user is warned they should be using simpler routine"""
        self.lwarn = u"for a single location, consider using"

        aacgmv2.convert_latlon_arr(60, 0, 300, dt.datetime(2015,1,1,0,0,0))
        self.lout = self.log_capture.getvalue()
        if self.lout.find(self.lwarn) < 0:
            raise AssertionError()

class TestTimeReturns:
    def setup(self):
        """Runs before every method to create a clean testing setup"""
        self.dtime = dt.datetime(2015, 1, 1, 0, 0, 0)
        self.dtime2 = dt.datetime(2015, 1, 1, 10, 10, 10)
        self.ddate = dt.date(2015, 1, 1)
        
    def teardown(self):
        """Runs after every method to clean up previous testing"""
        del self.dtime, self.ddate, self.dtime2

    def test_good_time(self):
        """ Test to see that a good datetime is accepted"""

        assert self.dtime == aacgmv2.wrapper.test_time(self.dtime)

    def test_good_time_with_nonzero_time(self):
        """ Test to see that a good datetime with h/m/s is accepted"""

        assert self.dtime2 == aacgmv2.wrapper.test_time(self.dtime2)

    def test_good_date(self):
        """ Test to see that a good date has a good datetime output"""

        assert self.dtime == aacgmv2.wrapper.test_time(self.dtime)

    def test_bad_time(self):
        """ Test to see that a warning is raised with a bad time input"""
        with pytest.raises(ValueError):
            aacgmv2.wrapper.test_time(2015)
