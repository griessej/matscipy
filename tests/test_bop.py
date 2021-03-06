#! /usr/bin/env python

# ======================================================================
# matscipy - Python materials science tools
# https://github.com/libAtoms/matscipy
#
# Copyright (2014) James Kermode, King's College London
#                  Lars Pastewka, Karlsruhe Institute of Technology
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ======================================================================

from __future__ import print_function

import unittest

import numpy as np

import ase

import matscipytest

from matscipy.calculators.bop import AbellTersoffBrenner 
from matscipy.calculators.bop.explicit_forms import KumagaiTersoff, TersoffIII
from ase import Atoms
import ase.io
from matscipy.hessian_finite_differences import fd_hessian

class TestAbellTersoffBrenner(matscipytest.MatSciPyTestCase):

    def test_kumagai_tersoff(self):
        d = 2.0  # Si2 bondlength
        small = Atoms([14]*4, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d)], cell=(100, 100, 100))
        small.center(vacuum=10.0)
        small2 = Atoms([14]*5, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d), (0, d, d)], cell=(100, 100, 100))
        small2.center(vacuum=10.0)
        self.compute_forces_and_hessian(small, KumagaiTersoff())

        self.compute_forces_and_hessian(small2, KumagaiTersoff())

        aSi = ase.io.read('aSi.cfg')
        self.compute_forces_and_hessian(aSi, KumagaiTersoff())

    def tersoffIII(self):
        # not marked as test yet. TersoffIII not vectorized yet.
        d = 2.0  # Si2 bondlength
        small = Atoms([14]*4, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d)], cell=(100, 100, 100))
        small.center(vacuum=10.0)
        small2 = Atoms([14]*5, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d), (0, d, d)], cell=(100, 100, 100))
        small2.center(vacuum=10.0)
        self.compute_forces_and_hessian(small, TersoffIII())

        self.compute_forces_and_hessian(small2, TersoffIII())

        aSi = ase.io.read('aSi.cfg')
        self.compute_forces_and_hessian(aSi, TersoffIII())


    def test_generic_potential_form(self):
        self.test_cutoff = 2.4
        d = 2.0  # Si2 bondlength
        small = Atoms([14]*4, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d)], cell=(100, 100, 100))
        small.center(vacuum=10.0)
        small2 = Atoms([14]*5, [(d, 0, d/2), (0, 0, 0), (d, 0, 0), (0, 0, d), (0, d, d)], cell=(100, 100, 100))
        small2.center(vacuum=10.0)
        self.compute_forces_and_hessian(small, self.term1())
        self.compute_forces_and_hessian(small, self.term4())
        self.compute_forces_and_hessian(small, self.d11_term5())
        self.compute_forces_and_hessian(small, self.d22_term5())

        self.compute_forces_and_hessian(small2, self.term1())
        self.compute_forces_and_hessian(small2, self.term4())
        self.compute_forces_and_hessian(small2, self.d11_term5())
        self.compute_forces_and_hessian(small2, self.d22_term5())

    # 0 - Tests Hessian term #4 (with all other terms turned off)
    def term4(self):
        return {'F': lambda x, y: x,
        'G': lambda x, y: np.ones_like(x[:, 0]),
        'd1F': lambda x, y: np.ones_like(x),
        'd11F': lambda x, y: np.zeros_like(x),
        'd2F': lambda x, y: np.zeros_like(y),
        'd22F': lambda x, y: np.zeros_like(y),
        'd12F': lambda x, y: np.zeros_like(y),
        'd1G': lambda x, y: np.zeros_like(y),
        'd2G': lambda x, y: np.zeros_like(y),
        'd1x2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd11G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3), #if beta <= 1 else beta*(beta-1)*x.**(beta-2) * y[:, 2]**gamma,
        'd12G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd22G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'cutoff': self.test_cutoff}
    
    # 1 - Tests Hessian term #1 (and #4, with all other terms turned off)
    def term1(self):
        return {'F': lambda x, y: x**2,
        'G': lambda x, y: np.ones_like(x[:, 0]),
        'd1F': lambda x, y: 2*x,
        'd11F': lambda x, y: 2*np.ones_like(x),
        'd2F': lambda x, y: np.zeros_like(y),
        'd22F': lambda x, y: np.zeros_like(y),
        'd12F': lambda x, y: np.zeros_like(y),
        'd1G': lambda x, y: np.zeros_like(x),
        'd2G': lambda x, y: np.zeros_like(y),
        'd1x2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd11G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd12G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd22G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd1y2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'cutoff': self.test_cutoff}

    # 2 - Tests D_11 parts of Hessian term #5
    def d11_term5(self):
        return {
        'F': lambda x, y: y,
        'G': lambda x, y: np.sum(x**2, axis=1),
        'd1F': lambda x, y: np.zeros_like(x),
        'd11F': lambda x, y: np.zeros_like(x),
        'd2F': lambda x, y: np.ones_like(x),
        'd22F': lambda x, y: np.zeros_like(x),
        'd12F': lambda x, y: np.zeros_like(x),
        'd1G': lambda x, y: 2*x,
        'd2G': lambda x, y: np.zeros_like(y),
        'd1x2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd11G': lambda x, y: np.array([2*np.eye(3)]*x.shape[0]),#np.ones_like(x).reshape(-1,3,1)*np.ones_like(y).reshape(-1,1,3), #if beta <= 1 else beta*(beta-1)*x.**(beta-2) * y[:, 2]**gamma,
        'd12G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd22G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'cutoff': self.test_cutoff}
    
    # 3 - Tests D_22 parts of Hessian term #5
    def d22_term5(self):
        return {
        'F': lambda x, y: y,
        'G': lambda x, y: np.sum(y**2, axis=1),
        'd1F': lambda x, y: np.zeros_like(x),
        'd11F': lambda x, y: np.zeros_like(x),
        'd2F': lambda x, y: np.ones_like(x),
        'd22F': lambda x, y: np.zeros_like(x),
        'd12F': lambda x, y: np.zeros_like(x),
        'd2G' : lambda x, y: 2*y,
        'd1G' : lambda x, y: np.zeros_like(x),
        'd1x2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2zG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1x2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2yG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1z2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd1y2xG': lambda x, y: np.zeros_like(x[:, 0]),
        'd22G': lambda x, y: np.array([2*np.eye(3)]*x.shape[0]),#np.ones_like(x).reshape(-1,3,1)*np.ones_like(y).reshape(-1,1,3), #if beta <= 1 else beta*(beta-1)*x.**(beta-2) * y[:, 2]**gamma,
        'd12G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'd11G': lambda x, y: 0*x.reshape(-1,3,1)*y.reshape(-1,1,3),
        'cutoff': self.test_cutoff}



    def compute_forces_and_hessian(self, a, par):
        """ function to test the bop AbellTersoffBrenner class on
            a potential given by the form defined in par

        Parameters
        ----------
        a : ase atoms object
            passes an atomic configuration as an ase atoms object
        par : bop explicit form
            defines the explicit form of the bond order potential
        
        """
        calculator = AbellTersoffBrenner(**par)
        a.set_calculator(calculator)

        print('FORCES')
        ana_forces = a.get_forces()
        num_forces = calculator.calculate_numerical_forces(a, d=1e-5)
        print('num\n', num_forces)
        print('ana\n', ana_forces)
        assert np.allclose(ana_forces, num_forces, rtol=1e-3)
        
        print('HESSIAN')
        ana_hessian = calculator.calculate_hessian_matrix(a).todense()
        num_hessian = fd_hessian(a, dx=1e-5, indices=None).todense()
        print('ana\n', ana_hessian)
        print('num\n', num_hessian)
        print('ana - num\n', (np.abs(ana_hessian - num_hessian) > 1e-6).astype(int))
        assert np.allclose(ana_hessian, ana_hessian.T, atol=1e-6)
        assert np.allclose(ana_hessian, num_hessian, atol=1e-3)