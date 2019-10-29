# -*- coding: utf-8 -*-
"""
Created on Thu Mar 02 17:26:23 2017

@author: lansford
"""

"""Vibrational modes."""
from ase.data import covalent_radii as CR
import numpy as np

class Coordination:
    """Class for calculating coordination and generalized coordination number."""

    def __init__(self, atoms, exclude=[], cutoff=1.25, cutoff_type = 'percent'):
        self.atoms = atoms
        self.exclude = exclude
        self.cutoff = cutoff
        self.cutoff_type = cutoff_type
        
    def read(self):
        """Returns an array of coordination numbers and an array of existing bonds determined by
        distance and covalent radii.  By default a bond is defined as 120% of the combined radii
        or less. This can be changed by setting 'cutoff' to a float representing a 
        factor to multiple by (default = 1.2).
        If 'exclude' is set to an array,  these atomic numbers with be unable to form bonds.
        This only excludes them from being counted from other atoms,  the coordination
        numbers for these atoms will still be calculated,  but will be unable to form
        bonds to other excluded atomic numbers.
        """
    
        # Get all the distances
        distances = np.divide(self.atoms.get_all_distances(mic=True), self.cutoff)
        
        # Array of indices of bonded atoms.  len(bonded[x]) == cn[x]
        bonded = []
        indices = list(range(len(self.atoms)))
        
        # Atomic Numbers
        numbers = self.atoms.numbers
        # Coordination Numbers for each atom
        cn = []
        
        cr = np.take(CR, numbers)
        if self.cutoff_type == 'absolute':
            for i in indices:
                cr[i] = self.cutoff/2.
            distances = self.atoms.get_all_distances(mic=True)
                
        for i in indices:
            bondedi = []
            for ii in indices:
                # Skip if measuring the same atom
                if i == ii or ii in self.exclude:
                    continue
                if (cr[i] + cr[ii]) >= distances[i,ii]:
                    bondedi.append(ii)
            # Add this atoms bonds to the bonded list
            bonded.append(bondedi)
        for i in bonded:
            cn.append(len(i))
        self.cn = cn
        self.bonded = bonded
        
    def get_coordination_numbers(self):
        self.read()
        return self.cn, self.bonded    
    
    def get_gcn(self,site=[], surface_type="fcc"):
        """Returns the generalized coordination number of the site given.  To define
        A site,  just give a list containing the indices of the atoms forming the site.
        The calculated coordination numbers and bonding needs to be supplied, and the
        surface type also needs to be changed if the surface is not represented by bulk fcc.
        """
        # Define the types of bulk accepted
        gcn_bulk = {"fcc": [12., 18., 22., 26., 26.], "bcc": [14., 22., 28., 32.]}
        gcn = 0.
        if len(site) == 0:
            return 0
        counted = []
        for i in site:
            counted.append(i)
        for i in site:
            for ii in self.bonded[i]:
                if ii in counted:
                    continue
                counted.append(ii)
                gcn += self.cn[ii]
        return gcn / gcn_bulk[surface_type][len(site) - 1]