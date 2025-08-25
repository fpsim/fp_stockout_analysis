"""
Script to create a model of Senegal, modify some parameters, run the model and generate plots showing the
discrepancies between the model and data.
"""
import numpy as np
import fpsim as fp
import sciris as sc
from fpsim import plotting as plt

# Settings
country = 'senegal'
plt.Config.set_figs_directory('figures/')
plt.Config.do_save = True
plt.Config.do_show = False
plt.Config.show_rmse = False


def make_pars():
    pars = fp.make_fp_pars()  # For default pars
    pars.update_location(country)

    # Modify individual fecundity and exposure parameters
    # These adjust each woman's probability of conception and exposure to pregnancy.
    pars['exposure_factor'] = 1

    # Adjust contraceptive choice parameters
    pars['prob_use_year'] = 2020  # Base year
    pars['prob_use_trend_par'] = 0.01  # Time trend in contraceptive use
    pars['prob_use_intercept'] = -1  # Intercept for the probability of using contraception

    # Weights assigned to dictate preferences between methods:
    method_weights = dict(
        pill=1,
        iud=1,
        inj=2.2,
        cond=1.5,
        btl=1,
        wdraw=1,
        impl=1,
        othtrad=1,
        othmod=1,
    )
    pars['method_weights'] = np.array([*method_weights.values()])  # Weights for the methods in method_list in methods.py (excluding 'none', so starting with 'pill' and ending in 'othmod').

    return pars


def make_sim(pars=None, stop=2021):
    if pars is None:
        pars = make_pars()

    # Run the sim
    sim = fp.Sim(
        start=2000,
        stop=stop,
        n_agents=1000,
        location=country,
        pars=pars,
        analyzers=[fp.cpr_by_age(), fp.method_mix_by_age()],
    )

    return sim


if __name__ == '__main__':
    do_run = True  # Whether to run the sim or load from file
    if do_run:
        # Create simulation with parameters
        sim = make_sim()
        sim.run()
        sc.saveobj(f'results/{country}_calib.sim', sim)
    else:
        sim = sc.loadobj(f'results/{country}_calib.sim')

    # Set options for plotting
    sc.options(fontsize=20)
    plt.plot_calib(sim, single_fig=True)
