"""
LIMR: late-inspiral, merger, ringdown
"""
from typing import Literal
import numpy as np
from scipy.interpolate import make_interp_spline
import phenom
from lal import SpinWeightedSphericalHarmonic
from pathlib import Path

from limr import late_inspiral_model
from limr import merger_model
from limr import ringdown_model
from limr import fitter
from limr import utils
from limr import model_versions

import logging
logger = logging.getLogger(__name__)


class LIMR:
    def __init__(self, model_version:Literal["prod", "test"]="prod", modes=None):

        if model_version == "prod":
            model_map = model_versions.PROD_MODEL_MAP
        elif model_version == "test":
            model_map = model_versions.TEST_MODEL_MAP
        else:
            raise ValueError(f"{model_version = } unknown, only 'prod' or 'test' available.")


        self.merger_model_save_path = Path(model_map['merger'])
        self.lateinspiral_model_save_path = Path(model_map['late-inspiral'])
        self.remnant_model_save_path = Path(model_map['remnant'])

        self.setup(modes)

    def setup(self, modes):
        self.gp_final_mass = fitter.TinyGPModel.load(self.remnant_model_save_path / 'final_mass_tinygp_model.pkl')
        self.gp_final_spin = fitter.TinyGPModel.load(self.remnant_model_save_path / 'final_spin_tinygp_model.pkl')

        self.lateinspiral_gp = late_inspiral_model.load_late_inspiral_gp_amp_phase(model_save_path=self.lateinspiral_model_save_path, modes=modes)
        self.merger_gp = merger_model.load_merger_gp_hlm(model_save_path=self.merger_model_save_path, modes=modes)

        self.mode_to_index = self.merger_gp.mode_to_index
        self.index_to_mode = self.merger_gp.index_to_mode
        self.modes = list(self.mode_to_index.keys())

        # should make these parameters
        self.t_connect_ins_mrg = -30
        self.t_connect_rd = 30
        
        # for now we use a fixed time array
        self.late_ins_times = np.arange(-300, -29, 1)
        # dt for mrg_times has to be small enough to capture the highest mode's frequency
        self.mrg_times = np.arange(-30, self.t_connect_rd+1, 0.5)
                
    def predict(self, times, q):
        rd_end_time = times[-1] + 1
        eta = phenom.eta_from_q(q)

        assert times[0] >= -300, f'start time must be >= -300M, got {times[0]}'
        assert times[-1] <= rd_end_time, f'end time must be <= {rd_end_time} M'

        late_ins_hlms = self.lateinspiral_gp.predict(self.late_ins_times, eta)
        mrg_hlms = self.merger_gp.predict(self.mrg_times, eta)
        
        remnant_mass = self.gp_final_mass.predict(np.array([[eta]]), return_std=False)
        remnant_spin = self.gp_final_spin.predict(np.array([[eta]]), return_std=False)
        
        rd_times, rd_hlms = ringdown_model.extrapolate_hlm_with_ringdown(self.mrg_times, mrg_hlms, rd_end_time, mode_to_index=self.mode_to_index, remnant_mass=remnant_mass, remnant_spin=remnant_spin)
        

        limr_hlms = connect_limr(times, self.late_ins_times, late_ins_hlms, self.mrg_times, mrg_hlms, rd_times, rd_hlms, self.mode_to_index, self.t_connect_ins_mrg, self.t_connect_rd)

        return limr_hlms


    def sample(self, times, q, n_samples, prngkey=None):
        rd_end_time = times[-1] + 1
        eta = phenom.eta_from_q(q)

        assert times[0] >= -300, f'start time must be >= -300M, got {times[0]}'
        assert times[-1] <= rd_end_time, f'end time must be <= {rd_end_time} M'

        late_ins_hlms = self.lateinspiral_gp.sample(self.late_ins_times, eta, n_samples, prngkey)
        mrg_hlms = self.merger_gp.sample(self.mrg_times, eta, n_samples, prngkey)
        
        remnant_mass = self.gp_final_mass.sample(np.array([[eta]]), n_samples, prngkey)[0]
        remnant_spin = self.gp_final_spin.sample(np.array([[eta]]), n_samples, prngkey)[0]
        
        rd_times, rd_hlms = ringdown_model.extrapolate_hlm_with_ringdown(self.mrg_times, mrg_hlms, rd_end_time, mode_to_index=self.mode_to_index, remnant_mass=remnant_mass, remnant_spin=remnant_spin)
        
        limr_hlms = connect_limr(times, self.late_ins_times, late_ins_hlms, self.mrg_times, mrg_hlms, rd_times, rd_hlms, self.mode_to_index, self.t_connect_ins_mrg, self.t_connect_rd)

        return limr_hlms
        

    def get_strain(self, hlm, theta, phi):
        """
        Take the output from etiher `.sample` or `.predict`
        which is an array of hlm modes compute and return
        the plus and cross polarisations evaluated at
        (theta, phi) coodinates.
        """
        n_modes, n_samples, n_times = hlm.shape
        h = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)
        for mode, mode_index in self.mode_to_index.items():
            l, m = mode
            # h_{l,m}*Y_{l,m} + h_{l,-m}*Y_{l,-m}
            Ylm = SpinWeightedSphericalHarmonic(theta=theta, phi=phi, s=-2, l=l, m=m)
            negYlm = SpinWeightedSphericalHarmonic(theta=theta, phi=phi, s=-2, l=l, m=-m)
            h[:,:] += hlm[mode_index] * Ylm + (-1)**l * np.conj(hlm[mode_index]) * negYlm
            
        hp = np.real(h)
        hc = np.imag(h)
        return hp, -hc





def connect_limr(imr_times, late_ins_times, late_ins_hlms, mrg_times, mrg_hlms, rd_times, rd_hlms, mode_to_index, t_connect_ins_mrg, t_connect_rd):
    # input shapes for _hlms are (n_modes, n_samples, n_times)
    
    # copy so we don't modify the input late_ins_hlms
    late_ins_hlms = late_ins_hlms.copy()

    # first we find the phase shift to align the inspiral with the merger at t_connect_ins_mrg
    n_modes, n_samples, _ = late_ins_hlms.shape
    d_phis = np.zeros(shape=(n_modes, n_samples))

    # only need to interpolate +/- 10M around t_connect_ins_mrg
    buf = 10
    ins_mask_con = (late_ins_times > t_connect_ins_mrg - buf) & (late_ins_times < t_connect_ins_mrg + buf)
    mrg_mask_con = (mrg_times > t_connect_ins_mrg - buf) & (mrg_times < t_connect_ins_mrg + buf)

    for mode, mode_idx in mode_to_index.items():
        for n in range(n_samples):
            i_ins = make_interp_spline(late_ins_times[ins_mask_con], np.unwrap(np.angle(late_ins_hlms[mode_idx,n,ins_mask_con])))
            i_mrg = make_interp_spline(mrg_times[mrg_mask_con], np.unwrap(np.angle(mrg_hlms[mode_idx,n,mrg_mask_con])))
            
            ins_phi_t_connect = i_ins(t_connect_ins_mrg)
            mrg_phi_t_connect = i_mrg(t_connect_ins_mrg)
            
            d_phis[mode_idx,n] = ins_phi_t_connect - mrg_phi_t_connect
    
    # rotate inspiral phase so that they match at t_connect with mrg
    for mode, mode_idx in mode_to_index.items():
        late_ins_hlms[mode_idx] = late_ins_hlms[mode_idx] * np.exp(-1.j * d_phis[mode_idx,:,np.newaxis])
    
    # concat ins and mrg-rd and re-interpolate onto final time grid
    n_imr_times = len(imr_times)
    limr_hlms = np.zeros(shape=(n_modes, n_samples, n_imr_times), dtype=np.complex128)

    # very important the type of inequality
    ins_mask = late_ins_times < t_connect_ins_mrg
    mrg_mask = (mrg_times >= t_connect_ins_mrg) & (mrg_times < t_connect_rd)
    rd_mask = rd_times >= t_connect_rd


    times_concat = np.concatenate((
        late_ins_times[ins_mask], 
        mrg_times[mrg_mask],
        rd_times[rd_mask],
    ))

    hlms_concat = np.concatenate((
        late_ins_hlms[:,:,ins_mask],
        mrg_hlms[:,:,mrg_mask],
        rd_hlms[:,:,rd_mask],
    ), axis=-1)

    
    for mode, mode_idx in mode_to_index.items():

        for n in range(n_samples):
        
            ire = make_interp_spline(times_concat, hlms_concat[mode_idx,n].real)
            iim = make_interp_spline(times_concat, hlms_concat[mode_idx,n].imag)
        
            limr_hlms[mode_idx,n,:] = ire(imr_times) + 1.j * iim(imr_times)



    # set phase to zero at beginning
    limr_hlms = utils.set_phase_to_zero_at_start(limr_hlms, mode_to_index)

    
    
    return limr_hlms






