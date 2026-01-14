from pathlib import Path
import numpy as np
import logging
import phenom
from scipy.interpolate import make_interp_spline

from limr import fitter
from limr import utils

logger = logging.getLogger(__name__)

class LateInspiralGP:
    def __init__(self, gp_amp_models:dict, gp_phi_models:dict):
        self.gp_amp_models = gp_amp_models
        self.gp_phi_models = gp_phi_models

        assert (
            list(self.gp_amp_models.keys())
            == list(self.gp_phi_models.keys())
        ), "modes from amp and phase models are not consistent"

        self.gp_amp_models = {k: v for k, v in sorted(list(self.gp_amp_models.items()))}
        self.gp_phi_models = {k: v for k, v in sorted(list(self.gp_phi_models.items()))}
        self.modes = list(self.gp_amp_models.keys())

        self.index_to_mode = dict(zip(np.arange(len(self.modes)), self.modes))
        self.mode_to_index = dict(zip(self.modes, np.arange(len(self.modes))))


    def get_hlm_interp(self, times, gpr_eval_times, amp, phi):
        amp = make_interp_spline(gpr_eval_times, amp)(times)
        phi = make_interp_spline(gpr_eval_times, phi)(times)
        return amp * np.exp(1.j * phi)
    
    def setup(self, times, eta, dt_gpr):
        # construct time array to evaluate the GP
        # because we use min/max of times you may need
        # to add a buffer depending on the sampling
        gpr_eval_times = np.arange(times[0], times[-1], dt_gpr)

        # build input feature grid for GP
        Xgrid = utils.cartesian_prod(gpr_eval_times, [eta])
        return gpr_eval_times, Xgrid

    def predict(self, times, eta, dt_gpr=10):
        """
        times: array,
            this is the time array, in units of M, you want the inspiral waveform on
            the data gets interpolated onto this
        eta: float,
            symmetric mass ratio
        dt_gpr, float,
            time spacing, in units of M, to eval gpr model on. this can be relatively
            high to reduce the cost of waveform evaluation because
            evaluating a gp is expensive.
            This could be mode dependend in the future to optimise waveform gen.
        """
        gpr_eval_times, Xgrid = self.setup(times, eta, dt_gpr)

        # store the mean waveform as an array with shape (n_modes, n_samples, n_times)
        # we don't use the std, only the mean
        n_modes = len(self.modes)
        n_samples = 1
        n_times = len(times)
        hlms = np.zeros(shape=(n_modes, n_samples, n_times), dtype=np.complex128)
        for i, mode in self.index_to_mode.items():
            l, m = mode
            fac = utils.leading_order_amp(eta, m)
            amp = fac * self.gp_amp_models[mode].predict(Xgrid, return_std=False)
            phi = self.gp_phi_models[mode].predict(Xgrid, return_std=False)
            hlms[i,0] = self.get_hlm_interp(times, gpr_eval_times, amp, phi)
        return hlms


    def sample(self, times, eta, n_samples, dt_gpr=10, prngkey=None):
        # for each mode have a dict of numpy array
        gpr_eval_times, Xgrid = self.setup(times, eta, dt_gpr)

        # store the mean waveform as an array with shape (n_modes, n_samples, n_times)
        # we don't use the std, only the mean
        n_modes = len(self.modes)
        n_times = len(times)
        hlms = np.zeros(shape=(n_modes, n_samples, n_times), dtype=np.complex128)
        for i, mode in self.index_to_mode.items():
            l, m = mode
            fac = utils.leading_order_amp(eta, m)
            # output shape is (num_times, n_samples)
            # i prefer (n_samples, num_times) so I transpose
            amps = fac * self.gp_amp_models[mode].sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
            phis = self.gp_phi_models[mode].sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T

            # interpolate onto output grid
            for n in range(n_samples):
                hlms[i,n] = self.get_hlm_interp(times, gpr_eval_times, amps[n], phis[n])
                
        return hlms
        
        
        

def load_late_inspiral_gp_amp_phase(model_save_path, modes=None):
    logger.info(f"late-inspiral model: {model_save_path = }")
    if not modes:
        logger.info("using default modes")
        modes = [(2,2),(2,1),(3,3),(3,2),(4,4),(4,3),(5,5),(5,4)]

    gp_amp_models = {}
    gp_phi_models = {}
    for mode in modes:
        l, m = mode
        logger.info(f"loading mode: {mode}")
        hlms_amp_file = model_save_path / f"gp_amplitudes__{l}_{m}.pkl"
        hlms_phi_file = model_save_path / f"gp_phases__{l}_{m}.pkl"
        logger.info(f"reading {hlms_amp_file}")
        gp_amp_models[mode] = fitter.TinyGPModel.load(hlms_amp_file)
        logger.info(f"reading {hlms_phi_file}")
        gp_phi_models[mode] = fitter.TinyGPModel.load(hlms_phi_file)

    logger.info(f"instantiating class")
    lateinspiral_gp = LateInspiralGP(gp_amp_models, gp_phi_models)
    return lateinspiral_gp