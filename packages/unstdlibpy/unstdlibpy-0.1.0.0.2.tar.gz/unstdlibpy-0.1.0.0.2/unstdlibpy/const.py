
"""
Module for defining constants that cannot be changed once set.
Includes common mathematical and physical constants.
"""

from typing import Any

__all__ = ['Const', 'const', 'function_const', 'class_const', 'num_const']

class Const:
    """A class to define constants. Once a constant is set, it cannot be changed."""
    def __setattr__(self, name: str, value: Any) -> None:
        """
        Set a constant value. Raises an AttributeError if the constant is already set.
        :param name: The name of the constant.
        :param value: The value of the constant.
        """

        if name in self.__dict__:
            raise AttributeError(f"Cannot reassign constant '{name}'")
        self.__dict__[name] = value

const = Const()
function_const = Const()
class_const = Const()
num_const = Const()

# Defining some common mathematical and physical constants

num_const.pi = 3.141592653589793 # Pi
num_const.e = 2.718281828459045 # Euler's number
num_const.phi = 1.618033988749895 # Golden ratio
num_const.gravity = 9.80665  # m/s^2
num_const.speed_of_light = 299792458  # m/s
num_const.avogadro_number = 6.02214076e23  # 1/mol
num_const.boltzmann_constant = 1.380649e-23  # J/K
num_const.planck_constant = 6.62607015e-34  # J·s
num_const.gas_constant = 8.314462618  # J/(mol·K)
num_const.elementary_charge = 1.602176634e-19  # C
num_const.fine_structure_constant = 7.2973525693e-3  # dimensionless
num_const.hubble_constant = 67.4  # km/s/Mpc
num_const.universal_gravitational_constant = 6.67430e-11  # m^3/(kg·s^2)
num_const.stefan_boltzmann_constant = 5.670374419e-8  # W/(m^2·K^4)
num_const.electron_mass = 9.10938356e-31  # kg
num_const.proton_mass = 1.67262192369e-27  # kg
num_const.neutron_mass = 1.67492749804e-27  # kg
num_const.water_density = 997  # kg/m^3 at 25 °C
num_const.standard_temperature = 273.15  # K
num_const.standard_pressure = 101325  # Pa
num_const.light_year = 9.4607e15  # meters
num_const.astronomical_unit = 1.495978707e11  # meters
num_const.parsec = 3.0857e16  # meters
num_const.electron_volt = 1.602176634e-19  # Joules
num_const.coulomb_constant = 8.9875517923e9  # N·m²/C²
num_const.magnetic_constant = 1.25663706212e-6  # N/A²
num_const.electric_constant = 8.854187817e-12  # F/m
num_const.permeability_of_free_space = 4e-7 * 3.141592653589793  # H/m
num_const.impedance_of_free_space = 376.730313668  # Ohms
num_const.rydberg_constant = 10973731.568160  # 1/m
num_const.solar_mass = 1.98847e30  # kg
num_const.jupiter_mass = 1.898e27  # kg
num_const.earth_mass = 5.97237e24  # kg
num_const.moon_mass = 7.342e22  # kg
num_const.solar_radius = 6.9634e8  # meters
num_const.earth_radius = 6.371e6  # meters
num_const.universe_age = 13.8e9  # years
num_const.planck_length = 1.616255e-35  # meters
num_const.planck_time = 5.391247e-44  # seconds
num_const.planck_mass = 2.176434e-8  # kg
num_const.planck_temperature = 1.416784e32  # Kelvin
num_const.bohr_radius = 5.29177210903e-11  # meters
num_const.classical_electron_radius = 2.8179403262e-15  # meters
num_const.thomson_cross_section = 6.6524587321e-29  # m²
num_const.faraday_constant = 96485.33212  # C/mol
num_const.universal_molar_volume = 22.414  # L/mol at STP
