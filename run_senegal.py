"""
Script to create a model of Senegal, modify some parameters, run the model and generate plots showing the
discrepancies between the model and data.

PRIOR TO RUNNING:
1. Be sure to set the plotting config variables in the first section below (country, figs directory, save option) as well as
any sim parameters and free params (for calibration) in the 'run_sim' function

2. Ensure that fpsim/locations contains both a directory for the country being calibrated, and ensure this location directory
 contains a corresponding location file (i.e. 'ethiopia.py') and 'data/' subdirectory

3. In order to run this script, the country data must be stored in the country directory mentioned above and with the
following naming conventions:

ageparity.csv' # Age-parity distribution file
use.csv' # Dichotomous contraceptive method use
birth_spacing_dhs.csv'  # Birth-to-birth interval data
afb.table.csv'  # Ages at first birth in DHS for women age 25-50
cpr.csv'  # Contraceptive prevalence rate data; from UN Data Portal
asfr.csv'  # Age-specific data fertility rate data
mix.csv'  # Contraceptive method mix
tfr.csv'  # Total fertility rate data
popsize.csv'  # Population by year

4. Ensure that the data in the aforementioned files are formatted properly (see files in locations/kenya/data for reference)
"""
import numpy as np
import fpsim as fp
from fpsim import plotting as plt

# Name of the country being calibrated. To note that this should match the name of the country data folder
country = 'senegal'

plt.Config.set_figs_directory('./figs_manual_calib')
plt.Config.do_save = True
plt.Config.show_rmse = True


def run_sim():
    # Set up sim for country
    pars = fp.make_fp_pars()  # For default pars
    pars.update_location('senegal')

    # Modify individual fecundity and exposure parameters
    # These adjust each woman's probability of conception and exposure to pregnancy.
    pars['fecundity_var_low'] = .8
    pars['fecundity_var_high'] = 3.25
    pars['exposure_factor'] = 3.5

    # Last free parameter, postpartum sexual activity correction or 'birth spacing preference'.
    # Pulls values from {location}/data/birth_spacing_pref.csv by default
    # Set all to 1 to reset.
    pars['spacing_pref']['preference'][:3] =  1  # Spacing of 0-6 months
    pars['spacing_pref']['preference'][3:6] = 1  # Spacing of 9-15 months
    pars['spacing_pref']['preference'][6:9] = 1  # Spacing of 18-24 months
    pars['spacing_pref']['preference'][9:] =  1  # Spacing of 27-36 months

    # Adjust contraceptive choice parameters
    pars['prob_use_year'] = 2020,         # Time trend intercept
    pars['prob_use_trend_par'] = 0.03,    # Time trend parameter
    pars['force_choose'] = False,         # Whether to force non-users to choose a method ('False' by default)
    # Weights assigned to dictate preferences between methods:
    method_weights = dict(
        pill=1,
        iud=1,
        inj=1,
        cond=1,
        btl=1,
        wdraw=1,
        impl=1,
        othtrad=1,
        othmod=1,
    )
    pars['method_weights'] = np.array([*method_weights.values()])  # Weights for the methods in method_list in methods.py (excluding 'none', so starting with 'pill' and ending in 'othmod').

    # Print out free params being used
    print("PARAMETERS BEING SET:")
    print(f"Fecundity range: {pars['fecundity_var_low']}-{pars['fecundity_var_high']}")
    print(f"Exposure factor: {pars['exposure_factor']}")
    print(f"Birth spacing preference: {pars['spacing_pref']['preference']}")
    print(f"Age-based exposure and parity-based exposure can be adjusted manually in {country}.py")
    print(f"Contraceptive choice baseline year: {pars['prob_use_year']}")
    print(f"Contraceptive choice time trend parameter: {pars['prob_use_trend_par']}")
    print(f"Contraceptive method weights: {pars['method_weights']}")

    # Run the sim
    sim = fp.Sim(start=2000, n_agents=1000, pars=pars, analyzers=fp.cpr_by_age())
    sim.run()

    return sim


if __name__ == '__main__':
    # Run the simulation
    sim = run_sim()
    sim.plot()

    # Set options for plotting
    plt.plot_calib(sim)     # Function to plot the primary calibration targets (method mix, use, mcpr, tfr, birth spacing, afb, and asfr)
    plt.plot_cpr_by_age(sim)    # Function to plot cpr by age when this analyzer is used (useful for analysis and debugging)
