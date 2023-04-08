# created on Mar 29, 2023
# last edited Mar 29, 2023
import math
import pandas as pd
import datetime
import numpy as np

##### variable definitions #####
"""
t_el: thickness of metal top electrode
t_m: thickness of the membrane
t_i: thickness of the insulator
t_v: thickness of vibration film (t_m + t_el)
a: radius of vibration film
E: Young's modulus of vibration film (YM_m*t_m/t_v + YM_el*t_el/t_v)
rho_v: density of vibration film (rho_m*t_m/t_v + rho_el*t_el/t_v)
v_v: poisson's ratio of the vibration film (v_m*t_m/t_v + v_el*t_el/t_v)
g_eff: effective gap height
g_o: the original gap height
eps_o: permittivity of free space
f_o: resonant frequency
V_pullin: pull-in voltage
"""

##### CONSTANTS #####
eps_o = 8.85418782*(10**-12) # m^-3 kg^-1 s^4 A^2, electric constant

##### INPUTS #####

# variables to change: t_m, a, g_o, t_i, t_el
# t_m: the membrane thickness is usually 0.5-2 µm
# a: the membrane radius is 20-100 µm
# t_i = g_o: 0.2-1.2 µm 
# t_el: 1-5 µm

length = 10 # change this
membranes = ['Si3N4', 'polySi'] 
insulators = ['SiO2'] # SOI is a layer of SiO2 on Si wafer
metals = ['Al', 'Cr']

t_m_list = np.arange(0.5, 2, (2-0.5)/length).tolist()
t_m_list = [round(elem, 4) for elem in t_m_list]
a_list = np.arange(20, 100, (100-2)/length).tolist()
a_list = [round(elem, 4) for elem in a_list]
t_i_list = np.arange(0.2, 1.2, (1.2-0.2)/length).tolist()
t_i_list = [round(elem, 4) for elem in t_i_list]
t_el_list = np.arange(1, 5, (5-1)/length).tolist()
t_el_list = [round(elem, 4) for elem in t_el_list]


##### FUNCTIONS #####
def combinations_materials(membranes, insulators, metals):
    combos_materials = []
    for membrane in membranes:
        for insulator in insulators:
            for metal in metals:
                current = [membrane, insulator, metal]
                combos_materials.append(current)
    return combos_materials    

def combination_dimensions(t_m_list, a_list, t_i_list, t_el_list):
    combos_dimensions = []
    for t_m in t_m_list:
        for a in a_list:
            for t_i in t_i_list:
                for t_el in t_el_list:
                    current = [t_m, a, t_i, t_el]
                    combos_dimensions.append(current)
    return combos_dimensions

def insulator_selected(insulator):
    if insulator == 'SiO2':
        epsr_i = 4.2
    return epsr_i

def membrane_selected(membrane):
    if membrane == 'Si3N4':
        E_m = ((250+325.04)/2 * (10**9)) # Pa, ceramic, hot pressed 
        v_m = 0.24 # ceramic
        rho_m = 3184 # kg/m^3, ceramic, alpha silicon nitride
        epsr_m = (8+10)/2 # between 8.0 and 10.0
        return [E_m, v_m, rho_m, epsr_m]
    elif membrane == 'polySi':
        E_m = 160*(10**9) # Pa
        v_m = 0.22
        rho_m = 2330 # kg/m^3
        epsr_m = 11.7 
        return [E_m, v_m, rho_m, epsr_m]

def electrode_selected(metal):
    if metal == 'Cr':
        E_el = ((245+285)/2) * (10**9) # Pa
        v_el = 0.21
        rho_el = 7140 # kg/m^3
        return [E_el, v_el, rho_el]
    elif metal == 'Al':
        E_el = 69*(10**9) # Pa
        v_el = (0.31+0.34)/2
        rho_el = 2699 # kg/m³
        return [E_el, v_el, rho_el]

def g_effective(t_m, t_i, epsr_m, epsr_i, g_o):
    g_eff = t_m/epsr_m + t_i/epsr_i + g_o # eq1
    return g_eff

def resonant_frequency(t_v, a, E_v, rho_v, v_v):
    term1 = (0.47*t_v)/(a**2)
    term2 = math.sqrt(E_v/(rho_v*(1-(v_v**2))))
    f_o = term1*term2
    return f_o


# pull_in_voltage_new_eqn comes from (Park et al., 2018)
def pull_in_voltage_Park(E_eq, t_eq, g_eff, eps_o, a, v_eq):
    numerator = E_eq*(t_eq**3)*(g_eff**3)
    denominator = eps_o*(a**4)*(1-(v_eq**2))
    V_pullin = 1.56*math.sqrt(numerator/denominator)
    return V_pullin

##### MAIN FUNCTION CALL #####

# create empty dataframe
df = pd.DataFrame(columns=[
    'membrane',
	'insulator',
	'metal',
	'membrane_radius',
	'gap_height_original',
	'membrane_thickness',
	'insulator_thickness',
	'metal_thickness',
	'gap_height_effective',
	'resonant_frequency',
	'V_pullin',
	'freq_within_range',
])

# loop through the different inputs
    # combos: membrane, insulator, metal
    # membrane
    # insulator
    # metal
    # membrane radius
    # gap height
    # membrane thickness
    # insulator thickness
    # metal thickness

combos_materials = combinations_materials(membranes, insulators, metals)
for materials in combos_materials:
    membrane = materials[0]
    insulator = materials[1]
    metal = materials[2]
    epsr_i = insulator_selected(insulator)
    [E_m, v_m, rho_m, epsr_m] = membrane_selected(membrane)
    [E_el, v_el, rho_el] = electrode_selected(metal)

    combos_dimensions = combination_dimensions(t_m_list, a_list, t_i_list, t_el_list)
    for dimensions in combos_dimensions:
        t_m = dimensions[0]*(10**-6) # µm
        a = dimensions[1]*(10**-6) # µm
        g_o = dimensions[2]*(10**-6) # µm
        t_i = dimensions[2]*(10**-6) # µm
        t_el = dimensions[3]*(10**-6) # µm

        t_v = t_m + t_el
        E_v = E_m*(t_m/t_v) + E_el*(t_el/t_v)
        rho_v = rho_m*(t_m/t_v) + rho_el*(t_el/t_v)
        v_v = v_m*(t_m/t_v) + v_el*(t_el/t_v)
        # epsr = epsr_m*(t_m/(t_m+t_i)) + epsr_i*(t_i/(t_m+t_i))

        # for the effective gap, just use the dielectric of the insulator
        g_eff = g_effective(t_m, t_i, epsr_m, epsr_i, g_o)
        f_o = resonant_frequency(t_v, a, E_v, rho_v, v_v)
        V_pullin = pull_in_voltage_Park(E_v, t_v, g_eff, eps_o, a, v_v)

        # calculate the following:
        # effective gap height
        # resonant frequency
        # pull-in voltage
        # check if the resonant frequency is within the range
            # the desired range is 10-60 MHz 
        if (f_o > 10*(10**6)) and (f_o < 40*(10**6)):
            freq_within_range = True
        else:
            freq_within_range = False

        # paste values into new line of the dataframe
        new_line = {
            'membrane': membrane,
            'insulator': insulator,
            'metal': metal,
            'membrane_radius': a,
            'gap_height_original': g_o,
            'membrane_thickness': t_m,
            'insulator_thickness': t_i,
            'metal_thickness': t_el,
            'gap_height_effective': g_eff,
            'resonant_frequency': f_o,
            'V_pullin': V_pullin,
            'freq_within_range': freq_within_range,
        }
        df = df.append(new_line, ignore_index=True)

# outside of the loop, save the dataframe to a csv
now = datetime.datetime.now()
string = now.strftime('%Y%m%d_%H%M')
output_path = '/Users/hannah/Documents/4B/NE 459/design_%s.csv' % (string)
df.to_csv(output_path, index=False)
print('Outputted to %s' %output_path)
print(df)