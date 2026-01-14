from pathlib import Path
import numpy as np
import logging
import phenom
from scipy.interpolate import make_interp_spline
from scipy.signal import hilbert
from scipy import signal
import glob

from limr import fitter
from limr import utils

logger = logging.getLogger(__name__)


def compute_hilbert_merger_times(start=-50, end=30, dt=1, buffer=40):
    """
    function to compute the times to evaluate the 'hilbert' gp model on
    because we take a hilbert transform we need to evaluate the gp
    on a wider stretch of data given by buffer.

    times in units of M
    """
    return np.arange(start - buffer, end + buffer, dt)


class HilbertMergerModeGP:
    """
    predict and sample that outputs h_lm for a single mode
    coming from a model for the real(hlm). We use
    a Hilbert transform to get the imag(hlm)
    """
    def __init__(self, gp_hlm_real_model, mode):
        self.gp_hlm_real_model = gp_hlm_real_model
        self.mode = mode
        self.ismixed = True
        
        # tukey window param
        self.alpha_by_mode = {
            (2,2):0.5,
            (2,1):0.3,
            (3,3):0.5,
            (3,2):0.5,
            (4,4):0.3,
            (4,3):0.3,
            (5,5):0.1,
            (5,4):0.3,
        }
        
    def hilbert_transform(self, y, alpha):
        """
        Returns
        -------
        z_taper: complex array of shape (n_samples, n_times)
            this is the tapered hilber transform of the input
        """
        # imag
        # taper
        y = np.atleast_2d(y)
        # the shape should be (n_samples, n_times)
        n, d = y.shape
        y_taper = y * signal.windows.tukey(d, alpha=alpha)
        # conj to get correct convention
        z_taper = hilbert(y_taper).conj()
        return z_taper

    
    def predict(self, times, eta):
        """
        compute gpr prediction of hilbert hlm modes on the gpr eval times
        which is typically coarser than required and the interpolation onto
        the final time grid happens in `MergerModel`

        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio

    
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean and so n_samples = 1
        n_samples = 1
        n_times = len(times)
        hlms_real = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)
        hlms_real[0,:] = fac * self.gp_hlm_real_model.predict(Xgrid, return_std=False)
        hlms[0,:] = self.hilbert_transform(hlms_real, self.alpha_by_mode[self.mode])[0]

        return hlms

    def sample(self, times, eta, n_samples, prngkey=None):
        """
        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio
        eta: float,
            symmetric mass ratio
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean
        n_times = len(times)
        hlms_real = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)
        hlms_real[:,:] = fac * self.gp_hlm_real_model.sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
        hlms[:,:] = self.hilbert_transform(hlms_real, self.alpha_by_mode[self.mode])

        return hlms


class AmpPhaseMergerModeGP:
    """
    predict and sample that outputs h_lm for a single mode
    coming from a model for the amplitude and phase.
    """
    def __init__(self, gp_amp_model, gp_phase_model, mode):
        self.gp_amp_model = gp_amp_model
        self.gp_phase_model = gp_phase_model
        self.mode = mode
        self.ismixed = False


    def predict(self, times, eta):
        """
        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean and so n_samples = 1
        n_samples = 1
        n_times = len(times)
        amp = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        phase = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)

        amp[0,:] = fac * self.gp_amp_model.predict(Xgrid, return_std=False)
        phase[0,:] = self.gp_phase_model.predict(Xgrid, return_std=False)
        
        hlms[:,:] = amp * np.exp(1.j * phase)

        return hlms

    def sample(self, times, eta, n_samples, prngkey=None):
        """
        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean and so n_samples = 1
        n_times = len(times)
        amp = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        phase = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)

        amp[:,:] = fac * self.gp_amp_model.sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
        phase[:,:] = self.gp_phase_model.sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
        
        hlms[:,:] = amp * np.exp(1.j * phase)

        return hlms

class ReImMergerModeGP:
    """
    predict and sample that outputs h_lm for a single mode
    coming from a model for the real and imag parts
    """
    def __init__(self, gp_real_model, gp_imag_model, mode):
        self.gp_real_model = gp_real_model
        self.gp_imag_model = gp_imag_model
        self.mode = mode


    def predict(self, times, eta):
        """
        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean and so n_samples = 1
        n_samples = 1
        n_times = len(times)
        hlm_real = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlm_imag = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)

        hlm_real[0,:] = fac * self.gp_real_model.predict(Xgrid, return_std=False)
        hlm_imag[0,:] = fac * self.gp_imag_model.predict(Xgrid, return_std=False)
        
        hlms[:,:] = hlm_real + 1.j * hlm_imag

        return hlms

    def sample(self, times, eta, n_samples, prngkey=None):
        """
        times: array
            times to evaluate the gpr model on
        eta: float,
            symmetric mass ratio
        """
        # this should probably be made as an input
        Xgrid = utils.cartesian_prod(times, [eta])

        # store the mean waveform as an array with shape (n_samples, n_times)
        # we don't use the std, only the mean and so n_samples = 1
        n_times = len(times)
        hlm_real = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlm_imag = np.zeros(shape=(n_samples, n_times), dtype=np.float64)
        hlms = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        l, m = self.mode
        fac = utils.leading_order_amp(eta, m)


        # need separate prngkey for real and imag
        hlm_real[:,:] = fac * self.gp_real_model.sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
        hlm_imag[:,:] = fac * self.gp_imag_model.sample(Xgrid, n_samples=n_samples, prngkey=prngkey).T
        
        hlms[:,:] = hlm_real + 1.j * hlm_imag

        return hlms


class MergerModel:
    """
    each mode has it's own predict, sample method
    """
    def __init__(self, gp_hlm_models):
        """
        gp_hlm_models: dict
            a dict of either HilbertMergerModeGP or AmpPhaseMergerModeGP or ReImMergerModeGP
        """
        self.gp_hlm_models = gp_hlm_models

        # let's sort the keys of the dict so that the order of the modes
        # is more interpretable
        self.gp_hlm_models = {k: v for k, v in sorted(list(self.gp_hlm_models.items()))}
        self.modes = list(self.gp_hlm_models.keys())

        self.index_to_mode = dict(zip(np.arange(len(self.modes)), self.modes))
        self.mode_to_index = dict(zip(self.modes, np.arange(len(self.modes))))

    def predict(self, times, eta, gpr_dt=0.5):
        """
        times: array
            the array of output times
            depending on the mode we evaluate the gpr on different times and interpolate
            onto these `times`.

        gpr_dt:
            has to be high enough
        """

        start = times[0] #- 1
        end = times[-1] #+ 1
        # times_mixed are the times we eval the gp on, it included a buffer because we use a Hilbert transform
        mrg_times = np.arange(start, end, gpr_dt)
        
        # store the mean waveform as an array with shape (n_modes, n_samples, n_times)
        # and just set n_samples = 1
        # we don't use the std, only the mean
        n_modes = len(self.modes)
        n_samples = 1
        n_times = len(times)
        hlms = np.zeros(shape=(n_modes, n_samples, n_times), dtype=np.complex128)

        # generate prediction
        for i, mode in self.index_to_mode.items():
            _mrg_hlms = self.gp_hlm_models[mode].predict(mrg_times, eta)
            # resample
            hlms[i,0,:] = self.interpolate_real_imag(times, mrg_times, _mrg_hlms[0])

        return hlms


    def sample(self, times, eta, n_samples, prngkey=None, gpr_dt=0.5):
        start = times[0] #- 1
        end = times[-1] #+ 1
        mrg_times = np.arange(start, end, gpr_dt)
        
        n_modes = len(self.modes)
        n_times = len(times)
        hlms = np.zeros(shape=(n_modes, n_samples, n_times), dtype=np.complex128)

        for i, mode in self.index_to_mode.items():
            _mrg_hlms_samples = self.gp_hlm_models[mode].sample(mrg_times, eta, n_samples, prngkey)

            # resample
            for n in range(n_samples):
                hlms[i,n,:] = self.interpolate_real_imag(times, mrg_times, _mrg_hlms_samples[n])
                
        return hlms    

    def interpolate_real_imag(self, times, gpr_eval_times, hlm):
        hlm_real = make_interp_spline(gpr_eval_times, hlm.real)(times)
        hlm_imag = make_interp_spline(gpr_eval_times, hlm.imag)(times)
        return hlm_real + 1.j*hlm_imag


def load_merger_gp_hlm(model_save_path, modes=None):
    logger.info(f"merger model: {model_save_path = }")

    if not modes:
        logger.info("using default modes")
        modes = [(2,2),(2,1),(3,3),(3,2),(4,4),(4,3),(5,5),(5,4)]
        

    # unmixed-modes are modelled as amp-phase
    # mixed-modes are modelled as real(hlm) 

    # unmixed_modes = [(2,2), (2,1), (3,3), (4,4), (5,5)]
    # mixed_modes = [(3,2), (4,3), (5,4)]

    # unmixed_modes = [(2,1), (3,3), (4,4), (5,5)]
    # mixed_modes = [(2,2), (3,2), (4,3), (5,4)]

    # mixed_modes = []
    # unmixed_modes = [(2,2),(2,1),(3,3),(3,2),(4,4),(4,3),(5,5),(5,4)]

    gp_hlm_models = {}

    # for mode in unmixed_modes:
    #     if mode not in modes:
    #         continue
    #     logger.info(f"loading {mode = }")
    #     l, m = mode
    #     amp_file = model_save_path / f"gp_amplitudes__{l}_{m}.pkl"
    #     amp_model_ = fitter.TinyGPModel.load(amp_file)
    #     phase_file = model_save_path / f"gp_phases__{l}_{m}.pkl"
    #     phase_model_ = fitter.TinyGPModel.load(phase_file)
    #     gp_hlm_models[mode] = AmpPhaseMergerModeGP(gp_amp_model=amp_model_, gp_phase_model=phase_model_, mode=mode)
    
    # for mode in mixed_modes:
    #     if mode not in modes:
    #         continue
    #     logger.info(f"loading {mode = }")
    #     l, m = mode
    #     hlms_real_file = model_save_path / f"gp_hlms_real__{l}_{m}.pkl"
    #     hlm_model_ = fitter.TinyGPModel.load(hlms_real_file)
    #     gp_hlm_models[mode] = HilbertMergerModeGP(gp_hlm_real_model=hlm_model_, mode=mode)

    for mode in modes:
        logger.info(f"loading {mode = }")
        l, m = mode


        hlms_real_file = model_save_path / f"gp_hlms_real__{l}_{m}.pkl"
        logger.info(f"loading real: {hlms_real_file}")
        hlm_real_model = fitter.TinyGPModel.load(hlms_real_file)

        hlms_imag_file = model_save_path / f"gp_hlms_imag__{l}_{m}.pkl"
        logger.info(f"loading imag: {hlms_imag_file}")
        hlm_imag_model = fitter.TinyGPModel.load(hlms_imag_file)

        gp_hlm_models[mode] = ReImMergerModeGP(gp_real_model=hlm_real_model, gp_imag_model=hlm_imag_model, mode=mode)

    merger_gp = MergerModel(gp_hlm_models)
    return merger_gp







