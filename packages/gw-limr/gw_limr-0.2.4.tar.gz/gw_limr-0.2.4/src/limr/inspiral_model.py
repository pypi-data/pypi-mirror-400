"""
By default we use the PhenomT 22 mode as our inspiral model
and use PN scaling relations and a simple phenomenological
extention to approximate the higher order multipoles.
"""
import numpy as np
import phenom
import prim.waveform
import prim.spliced_pn
from limr import loader

def get_inspiral_hlm(approximant, modes, q, M, f_min, deltaT, verbose=False, S1z=0, S2z=0):
    eta = phenom.eta_from_q(q+1e-6)
    h22 = loader.generate_lal_waveform(
        approximant,
        q,
        modes=[(2,2), (2,1)], # need to change this as I don't need 2,1 mode by the current version of generate_lal_waveform requires this
        start_time=None,
        end_time=-298,
        M=M,
        f_min=f_min,
        deltaT=deltaT,
        verbose=verbose,
        new_times=None,
        S1z=S1z,
        S2z=S2z,
        )

    # compute frequency
    x = prim.spliced_pn.pn_x_fn(-h22.frequencies[2,2]/2)
    
    # compute PN amplitudes
    amp_pn={}
    for mode in modes:
        l,m = mode
        func=getattr(prim.spliced_pn, f'pn_h_{l}{m}')
        amp_pn[mode] = np.abs(func(x, eta, 0, S1z, S2z))
    
    # scale amp using PN ratios
    # and scale the phases
    # then combine into complex multipole hlm.
    insprial_hm_wf = {}
    for mode in modes:
        amp_lm = h22.amplitudes[2,2] * amp_pn[mode] / amp_pn[2,2]
        phase_lm = h22.phases[2,2] / 2 * mode[1]
        pn_amp_arg = loader.get_arg_Alm(mode)
        insprial_hm_wf[mode] = amp_lm * np.exp(1.j * (phase_lm + pn_amp_arg))

    insprial_hm_wf = prim.waveform.Waveform(h22.times, insprial_hm_wf)
    return insprial_hm_wf
    