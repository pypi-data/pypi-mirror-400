"""
Load from the set of my currated NR waveforms 
or LALSimulation into a consistent frame
"""

import sys
from pathlib import Path
import numpy as np
from scipy.interpolate import make_interp_spline
from prim.waveform_generator import generate_waveform

class Waveform:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

def set_lal_surrogate_data_path(path=None):
    """
    set path to e.g NRHybSur3dq8 data
    """
    if path is None:
        path="/Users/sebastian.khan/personal/data/"

    if path not in sys.path:
        sys.path.append(path)

def peak_align(times, hlms):
    """
    shift times so that the peak of the total amplitude
    is at t=0
    """
    amp_squared = np.zeros_like(times)
    for mode in hlms.keys():
        amp_squared += np.abs(hlms[mode])**2

    peak_idx = np.argmax(amp_squared)
    peak_time = times[peak_idx]
    return peak_time


def add_start_time_to_cat(df, cat_dir):
    """
    add start_time column to the catalogue (after applying peak_align)
    """
    df=df.copy()
    sim_names = list(df['sim_name'])
    start_times = []
    for sim_name in sim_names:
        wf = {}
        p = Path(str(cat_dir / sim_name) + ".npy")
        wf = np.load(p, allow_pickle=True).item()
        times = wf['times']
        hlms = wf['hlms']
        peak_time = peak_align(times, hlms)
        times = times - peak_time
        
        start_times.append(times[0])
    df['start_time'] = start_times
    return df

def add_q_rounded_to_cat(df, sf=1):
    """
    add the rounded mass-ratio column
    """
    df = df.copy()
    df['q_rounded'] = df['q'].round(sf)
    return df

def get_arg_Alm(mode):
    """
    Leading order imaginary component of PN amplitude
    can get most of these easily from arXiv:2012.11923 (eq. 13)
    """
    return {
        (2,2):0,
        (2,1):np.pi/2,
        (3,3):-np.pi/2,
        (3,2):0,
        (4,4):np.pi,
        (4,3):-np.pi/2,
        (5,5):np.pi/2,
        (5,4):np.pi,
    }[mode]


def get_start_and_end_times(times, start_time, end_time):
    
    if start_time is None:
        start_time = times[0]
    if end_time is None:
        end_time = times[-1]

    return start_time, end_time

def chop(times, hlms, start_time, end_time):
    modes = hlms.keys()
    idxs = np.where( (times >= start_time) & (times <= end_time) )[0]
    times = times[idxs]
    for mode in modes:
        hlms[mode] = hlms[mode][idxs]

    return times, hlms


def reinterp_hlms(times, hlms, new_times):
    new_hlms={}
    for mode in hlms.keys():
        re = make_interp_spline(times, hlms[mode].real)(new_times)
        im = make_interp_spline(times, hlms[mode].imag)(new_times)
        new_hlms[mode] = re + 1.j*im
    return new_hlms


def reinterp_y(times, y, new_times):
    new_y={}
    for mode in y.keys():
        new_y[mode] = make_interp_spline(times, y[mode])(new_times)
    return new_y


def compute_amplitudes(hlms):
    modes = hlms.keys()
    amps = {}
    for mode in modes:
        amps[mode] = np.abs(hlms[mode])
    return amps

def compute_phases(times, hlms, tol=1.6, return_phase_sub=True, verbose=True):
    """
    taking care to try and account for inaccuracies in unwraping and 2pi ambiguities

    tol, float:
        the abs tolerance in order to add 2pi to the mode due to unwrapping errors
    """
    modes = hlms.keys()
    phases = {}
    phases_sub = {}

    
    for mode in modes:
        phases[mode] = np.unwrap(np.angle(hlms[mode]))

        # if early enough in the waveform, i.e. inspiral
        # then this quantitiy should be close to zero.
        # it can be non-zero if the NR waveform has noise
        # it can be non-zero and near -2pi due to unwrap errors
        # if it is near -2pi then we add 2pi
        p_sub = phases[mode] - get_arg_Alm(mode)
        # print(mode, p_sub[0], np.abs(p_sub[0] - (-2*np.pi)))
        if np.abs(p_sub[0] - (-2*np.pi)) < tol:
            if verbose:
                print(f"{mode = } broke tol. {p_sub[0]} {-2*np.pi} {np.abs(p_sub[0] - (-2*np.pi))}")
            phases[mode] = phases[mode] + 2*np.pi

        # now sub leading order
        phases_sub[mode] = phases[mode] - get_arg_Alm(mode)

    if return_phase_sub:
        return phases, phases_sub
    else:
        return phases


def compute_frequency(times, phases):
    freq={}
    for mode in phases.keys():
        freq[mode] = make_interp_spline(times, phases[mode]).derivative(1)(times)
    return freq

def apply_phase_shift(hlms, phi):
    hlms = hlms.copy()
    for mode in hlms.keys():
        l, m = mode
        hlms[mode] = hlms[mode] * np.exp(1.j * m * phi)
    return hlms

def apply_polarisation_shift(hlms, psi):
    hlms = hlms.copy()
    for mode in hlms.keys():
        l, m = mode
        hlms[mode] = hlms[mode] * np.exp(1.j * psi)
    return hlms

def set_phase_to_zero_at_start(hlms):
    hlms = hlms.copy()
    
    phi0 = np.angle(hlms[2,2])[0]/2
    # not sure if need the mod 2pi
    phi0 = phi0 % (2*np.pi)
    hlms = apply_phase_shift(hlms, -phi0)
    
    phi0 = np.angle(hlms[2,1])[0]
    # phi0 = phi0 % (2*np.pi)
    if phi0 < 0:
        hlms = apply_phase_shift(hlms, np.pi)
    return hlms

def generate_lal_waveform(approximant, q, modes, start_time=None, end_time=100, M=100, f_min=10, deltaT=1/4096., verbose=True, new_times=None, S1z=0, S2z=0):
    """
    generate LAL modes
    using either `SimInspiralChooseTDModes` or `pyseobnr.generate_waveform.GenerateWaveform`

    Returns
    -------
    Waveform instance
    """
    if verbose:
        print(approximant)
    wf_dict = generate_waveform(
        q,
        modes,
        M=M,
        f_min=f_min,
        S1z=S1z,
        S2z=S2z,
        approximant=approximant,
        deltaT=deltaT,
        phiRef=0,
        f_ref=None,
    )
    times = wf_dict["t"]

    hlms = {}
    for mode in modes:
        hlms[mode] = wf_dict["hlm"][mode]

    start_time, end_time = get_start_and_end_times(times, start_time, end_time)
    times, hlms = chop(times, hlms, start_time, end_time)



    hlms = set_phase_to_zero_at_start(hlms)

    phases, phases_sub = compute_phases(times, hlms, verbose=verbose)

    amplitudes = compute_amplitudes(hlms)

    frequencies = compute_frequency(times, phases)


    if new_times is not None:
        hlms = reinterp_hlms(times, hlms, new_times)
        
        amplitudes = reinterp_y(times, amplitudes, new_times)
        phases = reinterp_y(times, phases, new_times)
        phases_sub = reinterp_y(times, phases_sub, new_times)
        frequencies = reinterp_y(times, frequencies, new_times)

        times = new_times

    hlms_real = {mode:hlms[mode].real for mode in modes}
    hlms_imag = {mode:hlms[mode].imag for mode in modes}
    
    return Waveform(times=times, hlms=hlms, phases=phases, phases_sub=phases_sub, name=approximant, code=approximant, amplitudes=amplitudes, frequencies=frequencies, hlms_real=hlms_real, hlms_imag=hlms_imag)

def generate_nr_waveform(sim_name, df, cat_dir, start_time=None, end_time=100, junk_time=0, verbose=True, new_times=None, set_inital_phase_to_zero=True):
    """
    summary of conventions:
    
    - maya and rit have the convention as used in LAL
    - sxs: polarisation angle shift by pi
    - bam: very strange, polarisation angle shift by pi, tetrad multiplication (-i^m) AND conjugate the modes (but NOT (-1^l))
    
    Parameters
    ----------
    sim_name
        name of simulation to load
    df
        dataframe of catalogue
    cat_dir
        base path to the data directory

    Returns
    -------
    Waveform instance
    """
    if verbose:
        print(sim_name)
    code_name = df.set_index('sim_name').loc[sim_name, 'code']
    
    wf = {}
    p = Path(str(cat_dir / sim_name) + ".npy")
    wf = np.load(p, allow_pickle=True).item()
    times = wf['times']
    hlms_ = wf['hlms']

    if code_name == 'rit':
        modes = [(2,2), (2,1), (3,3), (3,2), (4,4), (4,3)]
        hlms={}
        for mode in modes:
            hlms[mode] = hlms_[mode].copy()
    else:
        hlms=hlms_.copy()
    del hlms_
        
    modes = hlms.keys()
    
    peak_time = peak_align(times, hlms)
    times = times - peak_time

    start_time, end_time = get_start_and_end_times(times, start_time, end_time)
    start_time += junk_time

    times, hlms = chop(times, hlms, start_time, end_time)



    # # swap (l,+m) -> (l,-m)
    # if code_name == 'bam':
    #     for l,m in modes:
    #         mode = (l,m)
    #         hlms[mode] = (-1)**l * hlms[mode].conj()

    if code_name == 'bam':
        # multiple by -1 i.e. psi=pi, however, in https://arxiv.org/abs/1501.00918 they say BAM and SXS differ by this so I don't know why I'm finding this.
        hlms = apply_polarisation_shift(hlms, np.pi)
        for l,m in modes:
            mode = (l,m)
            hlms[mode] = (-1.j)**m * hlms[mode].conj()

    if code_name in ['sxs']:
        hlms = apply_polarisation_shift(hlms, np.pi)

    if set_inital_phase_to_zero:
        hlms = set_phase_to_zero_at_start(hlms)
    
    phases, phases_sub = compute_phases(times, hlms, verbose=verbose)

    amplitudes = compute_amplitudes(hlms)

    frequencies = compute_frequency(times, phases)
    

    # re-sample after computing things like phase so that we don't calulate phase on coarse grid.
    if new_times is not None:
        hlms = reinterp_hlms(times, hlms, new_times)
        
        amplitudes = reinterp_y(times, amplitudes, new_times)
        phases = reinterp_y(times, phases, new_times)
        phases_sub = reinterp_y(times, phases_sub, new_times)
        frequencies = reinterp_y(times, frequencies, new_times)

        times = new_times

    hlms_real = {mode:hlms[mode].real for mode in modes}
    hlms_imag = {mode:hlms[mode].imag for mode in modes}
    
    return Waveform(times=times, hlms=hlms, phases=phases, phases_sub=phases_sub, name=sim_name, code=code_name, amplitudes=amplitudes, frequencies=frequencies, hlms_real=hlms_real, hlms_imag=hlms_imag)