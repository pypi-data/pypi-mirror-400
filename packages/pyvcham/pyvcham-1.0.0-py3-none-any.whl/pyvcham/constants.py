"""
This module contains physical constants and conversion factors.

.. data:: H

   Planck's constant (J·s)

.. data:: C

   Speed of light in vacuum (m/s)

.. data:: AU_TO_J

   Hartree to Joule conversion factor (J)

.. data:: CM1_TO_AU

   Conversion factor from wavenumbers (cm^-1) to atomic units

.. data:: AU_TO_EV

   Conversion factor from atomic units to electron volts (eV)
"""

# Planck's constant in Joule seconds (J·s)
H = 6.62607015e-34

# Speed of light in vacuum in meters per second (m/s)
C = 299792458.0

# Hartree to Joule conversion factor (J)
AU_TO_J = 4.3597447222071e-18

# Conversion factor from wavenumbers (cm^-1) to atomic units
CM1_TO_AU = (H * C * 100.0) / AU_TO_J

# Conversion factor from atomic units to electron volts (eV)
AU_TO_EV = 27.211386245988

# Conversion factor from bohr to angstrom
BOHR_TO_ANGSTROM = 0.52917721067

# Conversion factor from angstrom to bohr
ANGSTROM_TO_BOHR = 1.0 / BOHR_TO_ANGSTROM

# Atomic weights
ATOMIC_WEIGHTS = {
            "H": 1.00782503223, 
            "He": 4.00260325413,
            "Li": 6.938,        
            "Be": 9.0121831,    
            "B": 10.806,        
            "C": 12.0096,       
            "N": 14.00643,      
            "O": 15.99903,      
            "F": 18.998403163,  
            "Ne": 20.1797,      
            "Na": 22.98976928,  
            "Mg": 24.304,       
            "Al": 26.9815385,   
            "Si": 28.084,       
            "P": 30.973761998,  
            "S": 32.059,        
            "Cl": 35.446,       
            "Ar": 39.792,
            "X" : 1.0,  # Placeholder for unknown elements
            "Ghost": 1.0,  # Placeholder for ghost atoms       
        }