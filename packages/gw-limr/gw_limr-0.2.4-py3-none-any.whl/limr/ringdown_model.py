import phenom
import qnm
import numpy as np
import logging
logger = logging.getLogger(__name__)


def get_mixing_coefficient(remnant_spin, lp, l, m, n=0):
    """

    mixing coefficient
    ------------------
    
    refs: https://arxiv.org/abs/1212.5553v2 eq 14 (and around there)
    should double check this more carefully


    lp = l' (spherical l?)

    for the 32 mode we have
    h32_S = s_l' h32_Y + h22_Y

    https://qnm.readthedocs.io/en/latest/README.html#spherical-spheroidal-decomposition
    Here ℓmin=max(|m|,|s|) and ℓmax can be chosen at run time. The C coefficients are returned as a complex ndarray,
    with the zeroth element corresponding to ℓmin. To
    avoid indexing errors, you can get the ndarray of ℓ values by calling qnm.angular.ells, e.g.

    ells = qnm.angular.ells(s=-2, m=2, l_max=mc.l_max)



    Returns
    -------
    mixing coefficient
        with a length equal to the number of input samples
    """
    mc = qnm.modes_cache(s=-2, l=l, m=m, n=n)
    ells = qnm.angular.ells(s=-2, m=m, l_max=mc.l_max)
    C = np.zeros(shape=(len(remnant_spin), len(ells)), dtype=np.complex128)
    for i, a in enumerate(remnant_spin):
        _, _, C[i] = mc(a=a)
        
    rho = np.zeros(shape=len(remnant_spin), dtype=np.complex128)
    for n in range(len(remnant_spin)):
        C_dict = {ells[i]:C[n,i] for i in range(len(ells))}
    
        slp = C_dict[lp]
        sl = C_dict[l]
    
        rho[n] = slp/sl
        
    return rho



def get_ringdown_params_from_samples(remnant_mass, remnant_spin, l, m, lp=None, n=0):
    """
    if lp is None then doesn't calculate the mixing coefficient
    
    Parameters
    ----------
    remnant_mass
        array of samples, can be length 1
    remnant_spin
        array of samples, can be length 1


    Returns
    -------
    2-tuple
        (ringdown freq, ringdown damping time)
        they each of a length equal to the number of input samples

    """
    mc = qnm.modes_cache(s=-2, l=l, m=m, n=n)
    
    omega = np.zeros(shape=len(remnant_spin), dtype=np.complex128)
    for i, a in enumerate(remnant_spin):
        omega[i], _, _ = mc(a=a)
    
    # (angular?) ringdown freq
    ringdown_freq = -np.real(omega) / remnant_mass

    # (angular?) damping time
    damping_time = -np.imag(omega) / remnant_mass

    return ringdown_freq, damping_time



def ComplexExponentiallyDampedSinusoid(x, t0, phi0, amp, omega, decay):
    """
    x: time coord, the output time array
    t0: time shift (the start time of the ringdown)
    phi0: phase at t0
        can be array of samples
    amp: amplitude at t0
        can be array of samples
    omega: angular frequency
    decay: decay constant i.e. angular damping time == 1/angular damping frequency

    Returns
    -------
    complex array of the generated ringdown
    the shape is (n_samples, n_times)
    """
    # amp, phi0, omega and decay are arrays of length the number of samples
    # we add a dimension so that broadcasting works properly
    assert len(amp) == len(phi0) == len(omega) == len(decay), 'something wrong with number of samples'
    amp = amp[:,np.newaxis]
    phi0 = phi0[:,np.newaxis]
    omega = omega[:,np.newaxis]
    decay = decay[:,np.newaxis]
    n_samples = amp.shape[0]
    n_times = len(x)
    y = np.zeros(shape=(n_samples, n_times), dtype=np.complex128)

    sigma = omega + 1.j*decay
    # y[:,:] ensures that we have the dimensions correct as we are populating the above array that we allocated
    y[:,:] = amp * np.exp(1.j * (sigma*(x-t0) + phi0))
    
    return y
    
def hlm_ringdown_no_mixing(hlm, times, omega, decay, t_rd_start):
    """
    hlm: value of `mode` at the time `t_rd_start`
    times: times to evaluate the ringdown waveform on
        the first time should be t_rd_start
    """
    assert times[0] == t_rd_start, 'inital time seems wrong'

    amp = np.abs(hlm)
    phase = np.angle(hlm)

    hlm_rd = ComplexExponentiallyDampedSinusoid(times, t_rd_start, phase, amp, omega, decay)

    return hlm_rd



def hlm_ringdown_with_mixing(hlm2, times, omega2, decay2, rho, t_rd_start, hlm1):
    """
    hlm2 comes from the merger model so we need the time `t_rd_start` as is `mode2`
        it is a single complex number
    hlm1 comes from the ringdown as is for `mode1`
        is an array of complex numbers
        it is the output from `hlm_ringdown_no_mixing`
    omega2: array
    decay2: array
    rho: array
        these three have length equal to the number of samples
    """

    assert len(omega2) == len(decay2) == len(rho) == len(hlm2) == len(hlm1), 'something wrong with inputs'

    # shape of hlm2 is (n_samples) i.e. it is for a single mode and a single time (the start of the ringdown / end of merger), comes from the merger model
    # shape of hlm1 is (n_samples, n_times) i.e. it is for a single mode on the output time grid, is a ringdown waveform
        
    # initial conditions
    # undo mix
    h_spherical = hlm2 - rho*hlm1[:,0]
    amp2 = np.abs(h_spherical)
    phase2 = np.angle(h_spherical)

    hlm2_rd_no_mix = ComplexExponentiallyDampedSinusoid(times, t_rd_start, phase2, amp2, omega2, decay2)

    # mix it up
    hlm_rd = hlm2_rd_no_mix + rho[:,np.newaxis]*hlm1
    return hlm_rd



def extrapolate_hlm_with_ringdown(mrg_times, mrg_hlms, rd_end_time, mode_to_index, remnant_mass, remnant_spin):
    modes = list(mode_to_index.keys())
    
    rd_start_time = mrg_times[-1]
    rd_dt = mrg_times[1] - mrg_times[0]
    rd_times = np.arange(rd_start_time, rd_end_time, rd_dt)

    n_modes, n_samples, _ = mrg_hlms.shape
    n_times = len(rd_times)
    rd_hlms = np.zeros(shape=(n_modes, n_samples, n_times), dtype=np.complex128)

    # get the non-mixed modes
    non_mix_modes = [(2,2), (2,1), (3,3), (4,4), (5,5)]
    for mode in non_mix_modes:
        if mode not in modes:
            continue
        mode_idx = mode_to_index[mode]
        l, m = mode
        omega, decay = get_ringdown_params_from_samples(remnant_mass, remnant_spin, l, m)
        rd_hlms[mode_idx] = hlm_ringdown_no_mixing(mrg_hlms[mode_idx,:,-1], rd_times, omega, decay, rd_start_time)

    # get the mixed modes
    mix_modes = [((2,2),(3,2)), ((3,3),(4,3)), ((4,4),(5,4))]
    for mode1, mode2 in mix_modes:
        if mode2 not in modes:
            continue
        assert mode1 in modes, f'{mode1} is not in {modes = }'
        mode1_idx = mode_to_index[mode1]
        mode2_idx = mode_to_index[mode2]


        lp = mode2[0]
        l = mode1[0]
        m = mode1[1]
        omega2, decay2 = get_ringdown_params_from_samples(remnant_mass, remnant_spin, mode2[0], mode2[1])
        rho = get_mixing_coefficient(remnant_spin, lp, l, m)

        rd_hlms[mode2_idx] = hlm_ringdown_with_mixing(mrg_hlms[mode2_idx,:,-1], rd_times, omega2, decay2, rho, rd_start_time, rd_hlms[mode1_idx])

    # don't need the first time and that comes from the merger
    return rd_times[1:], rd_hlms[:,:,1:]