# Copyright (C) 2014-2016 The BET Development Team

# Steven Mattis 04/07/2015
# Troy Butler 03/23/2016
"""
This module contains tests for :module:`bet.postProcess.postTools`.


Tests for correct post-processing.
"""
import unittest
import bet.calculateP.simpleFunP as simpleFunP
import bet.postProcess.postTools as postTools
import numpy as np
import scipy.spatial as spatial
import numpy.testing as nptest
import bet.util as util
from bet.Comm import comm
import bet.sample as sample

def test_in_high_prob():
    """

    Tests :meth:`bet.postProcess.postTools.in_high_prob`
    """
    def rho_D(my_data):
        return my_data/4.0
    data = np.array([0, 1, 0, 1, 1, 1])
    maximum = np.max(rho_D(data))
    print "maximum", maximum
    assert 4 == postTools.in_high_prob(data, rho_D, maximum)
    assert 3 == postTools.in_high_prob(data, rho_D, maximum, [3, 4, 5])
    assert 2 == postTools.in_high_prob(data, rho_D, maximum, [0, 1, 2, 3])
    assert 1 == postTools.in_high_prob(data, rho_D, maximum, [0, 2, 4])
    assert 0 == postTools.in_high_prob(data, rho_D, maximum, [0, 2])

def test_in_high_prob_multi():
    """

    Tests :meth:`bet.postProcess.postTools.in_high_prob_multi`
    
    """
    def rho_D(my_data):
        return my_data/4.0
    data1 = np.array([0, 1, 0, 1, 1, 0])
    data2 = np.ones(data1.shape)-data1
    maximum = np.max(rho_D(data1))

    print "maximum", maximum
    results_list = [[None, data1], [None, data2], [None, data1], [None, data2]]
    sample_nos_list = [[3, 4, 5], [3, 4, 5], [0, 2, 4], [0, 2, 4]]

    nptest.assert_array_equal(np.array([2, 1, 1, 2]),
            postTools.in_high_prob_multi(results_list, rho_D, maximum,
                sample_nos_list))
    nptest.assert_array_equal(np.array([3, 3, 3, 3]),
            postTools.in_high_prob_multi(results_list, rho_D, maximum))

def test_compare_yield_CH():
    """

    Tests :meth:`bet.postProcess.postTools.compare_yield` with column headings

    """
    sample_quality = np.random.random((10,))
    sort_ind = np.argsort(sample_quality)
    run_param = []
    for i in range(10):
        run_param.append(np.random.random((4,)))
    column_headings = ['swallow', 'coconut', 'ni', 'shrubbery']
    try:
        postTools.compare_yield(sort_ind, sample_quality, run_param,
                column_headings)
        go = True
    except (RuntimeError, TypeError, NameError):
        go = False
    nptest.assert_equal(go, True)

def test_compare_yield():
    """

    Tests :meth:`bet.postProcess.postTools.compare_yield` without column headings

    """
    sample_quality = np.random.random((10,))
    sort_ind = np.argsort(sample_quality)
    run_param = []
    for i in range(10):
        run_param.append(np.random.random((4,)))
    try:
        postTools.compare_yield(sort_ind, sample_quality, run_param)
        go = True
    except (RuntimeError, TypeError, NameError):
        go = False
    nptest.assert_equal(go, True)


class Test_PostTools(unittest.TestCase):
    """
    Test :mod:`bet.postProcess.postTools`.
    """
    def setUp(self):
        """
        Set up problem.
        """
        self.lam_domain=np.array([[0.0,1.0]])
        num_samples=1000
        self.samples = np.linspace(self.lam_domain[0][0], self.lam_domain[0][1], num_samples+1)
        self.P_samples = (1.0/float(self.samples.shape[0]))*np.ones((self.samples.shape[0],))
        self.P_samples[0] = 0.0
        self.P_samples[-1] *= 2.0

        self.data = self.samples[:]
        
    def test_sort_by_rho(self):
        """
        Test :meth:`bet.postProcess.postTools.sort_by_rho`.
        """
        (P_samples, samples, _ , data, _) = postTools.sort_by_rho(self.P_samples, self.samples,
                                                               lam_vol=None, data=self.data)
        self.assertGreater(np.min(P_samples),0.0)
        nptest.assert_almost_equal(np.sum(P_samples),1.0)

    def test_sample_prob(self):
        """
        Test :meth:`bet.postProcess.postTools.sample_prob`.
        """
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_prob(1.0,
                                                                           self.P_samples, 
                                                                           self.samples,
                                                                           lam_vol=None,
                                                                           data=self.data,
                                                                           sort=True,
                                                                           descending=True)
        nptest.assert_almost_equal(np.sum(P_samples),1.0)
        nptest.assert_equal(num_samples,1000)
        
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_prob(0.8,
                                                                           self.P_samples, 
                                                                           self.samples,
                                                                           lam_vol=None,
                                                                           data=self.data,
                                                                           sort=True,
                                                                           descending=True)
        nptest.assert_allclose(np.sum(P_samples),0.8,0.001)

        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_prob(1.0,
                                                                           self.P_samples, 
                                                                           self.samples,
                                                                           lam_vol=None,
                                                                           data=self.data,
                                                                           sort=True,
                                                                           descending=False)
        nptest.assert_almost_equal(np.sum(P_samples),1.0)
        nptest.assert_equal(num_samples,1000)
        
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_prob(0.8,
                                                                           self.P_samples, 
                                                                           self.samples,
                                                                           lam_vol=None,
                                                                           data=self.data,
                                                                           sort=True,
                                                                           descending=False)
        nptest.assert_allclose(np.sum(P_samples),0.8,0.001)
    
    def test_sample_highest_prob(self):
        """
        Test :meth:`bet.postProcess.postTools.sample_highest_prob`.
        """
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_highest_prob(1.0,
                                                                                  self.P_samples, 
                                                                                  self.samples,
                                                                                  lam_vol=None, data=self.data, sort=True)
        nptest.assert_almost_equal(np.sum(P_samples),1.0)
        nptest.assert_equal(num_samples,1000)
        
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_highest_prob(0.8,
                                                                                  self.P_samples, 
                                                                                  self.samples,
                                                                                  lam_vol=None, data=self.data, sort=True)
        nptest.assert_allclose(np.sum(P_samples),0.8,0.001)
    
    def test_sample_lowest_prob(self):
        """
        Test :meth:`bet.postProcess.postTools.sample_lowest_prob`.
        """
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_lowest_prob(1.0,
                                                                                  self.P_samples, 
                                                                                  self.samples,
                                                                                  lam_vol=None, data=self.data, sort=True)
        nptest.assert_almost_equal(np.sum(P_samples),1.0)
        nptest.assert_equal(num_samples,1000)
        
        (num_samples,P_samples, samples, _ , data, _) = postTools.sample_lowest_prob(0.8,
                                                                                  self.P_samples, 
                                                                                  self.samples,
                                                                                  lam_vol=None, data=self.data, sort=True)
        nptest.assert_allclose(np.sum(P_samples),0.8,0.001)
