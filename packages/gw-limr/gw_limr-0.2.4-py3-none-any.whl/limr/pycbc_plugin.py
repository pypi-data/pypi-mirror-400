"""
module to generate LIMR waveforms as a pycbc TimeSeries

https://pycbc.org/pycbc/latest/html/waveform_plugin.html#waveform-plugin
"""


import numpy
import lal
from pycbc.types import TimeSeries

import phenom
import limr.limr_model
import limr.ilimr_model


def td_amp_scale(mtot, distance):
    """
    Computes the amplitude pre-factor for time-domain signals
    given as M*G/c^2 * M_sun / dist

    Parameters
    ----------
    mtot
        Total mass in solar masses
    distance
        Distance to source in SI units (metres)

    Returns
    -------
    float
        The scale factor
    """
    return mtot * lal.MRSUN_SI / distance

def ilimr_waveform(**args):
    """
    pass in an instantiated limr_model otherwise you have to load it every time
    q, M=100, f_min=20, deltaT=1/4096., inspiral_approximant='IMRPhenomTHM', end_time=100
    """
    if 'limr_model' not in args:
        raise ValueError("'limr_model' not in args as is required for this approximant!")
    limr_model = args['limr_model'] # required
    mass1 = args['mass1']
    mass2 = args['mass2']
    flow = args['f_lower'] # Required parameter
    dt = args['delta_t']   # Required parameter
    theta = args.get('inclination', 0)
    phi = args.get('coa_phase', 0)
    distance = args.get('distance', 1)

    M, eta = phenom.M_eta_m1_m2(mass1, mass2)
    q = phenom.q_from_eta(eta)
    
    sample = args.get('sample', False)  # A new parameter for my model
    inspiral_approximant = args.get('inspiral_approximant', 'IMRPhenomTHM')  # A new parameter for my model
    end_time = args.get('end_time', 100)  # A new parameter for my model

    # limr_model = limr.limr_model.LIMR(model_version=model_version)
    ilimr_model = limr.ilimr_model.ILIMR(limr_model)
    
    if sample:
        ilimr_times, ilimr_hlms = ilimr_model.sample(q=q, n_samples=1, M=M, f_min=flow, deltaT=dt, approximant=inspiral_approximant, end_time=end_time)    
    else:
        ilimr_times, ilimr_hlms = ilimr_model.predict(q=q, M=M, f_min=flow, deltaT=dt, approximant=inspiral_approximant, end_time=end_time)

    ilimr_hp, ilimr_hc = ilimr_model.limr_model.get_strain(ilimr_hlms, theta, phi+numpy.pi/2)

    AMP_SCALE = td_amp_scale(M, distance * lal.PC_SI * 1e6)

    ilimr_hp = ilimr_hp * AMP_SCALE
    ilimr_hc = ilimr_hc * AMP_SCALE

    # find the peak
    peak_idx = numpy.abs(ilimr_hlms).sum(0).argmax(1)[0]
    epoch = phenom.MtoS(ilimr_times[0],M) - phenom.MtoS(ilimr_times[peak_idx],M)

    ilimr_hp_ts = TimeSeries(ilimr_hp[0], delta_t=dt, epoch=epoch)
    ilimr_hc_ts = TimeSeries(ilimr_hc[0], delta_t=dt, epoch=epoch)

    return ilimr_hp_ts, ilimr_hc_ts



def batch_ilimr_waveform(**args):
    """
    batch_ilimr_waveform: this returns a list of hp and hc
    this way is much faster at generating samples because it does it 'at the same time'
    but is incompatible with pycbc

    pass in an instantiated limr_model otherwise you have to load it every time
    q, M=100, f_min=20, deltaT=1/4096., inspiral_approximant='IMRPhenomTHM', end_time=100
    """
    if 'limr_model' not in args:
        raise ValueError("'limr_model' not in args as is required for this approximant!")
    limr_model = args['limr_model'] # required
    mass1 = args['mass1']
    mass2 = args['mass2']
    flow = args['f_lower'] # Required parameter
    dt = args['delta_t']   # Required parameter
    theta = args.get('inclination', 0)
    phi = args.get('coa_phase', 0)
    distance = args.get('distance', 1)

    M, eta = phenom.M_eta_m1_m2(mass1, mass2)
    q = phenom.q_from_eta(eta)
    
    n_samples = args.get('n_samples', None)  # A new parameter for my model
    inspiral_approximant = args.get('inspiral_approximant', 'IMRPhenomTHM')  # A new parameter for my model
    end_time = args.get('end_time', 100)  # A new parameter for my model

    # want to have this in here but how to only load it once if it hasn't been loaded?
    # maybe set an environment variable?
    # limr_model = limr.limr_model.LIMR(model_version=model_version)
    ilimr_model = limr.ilimr_model.ILIMR(limr_model)
    
    if n_samples:
        ilimr_times, ilimr_hlms = ilimr_model.sample(q=q, n_samples=n_samples, M=M, f_min=flow, deltaT=dt, approximant=inspiral_approximant, end_time=end_time)    
    else:
        ilimr_times, ilimr_hlms = ilimr_model.predict(q=q, M=M, f_min=flow, deltaT=dt, approximant=inspiral_approximant, end_time=end_time)

    ilimr_hp, ilimr_hc = ilimr_model.limr_model.get_strain(ilimr_hlms, theta, phi+numpy.pi/2)

    AMP_SCALE = td_amp_scale(M, distance * lal.PC_SI * 1e6)

    ilimr_hp = ilimr_hp * AMP_SCALE
    ilimr_hc = ilimr_hc * AMP_SCALE

    # find the peak
    peak_idx = numpy.abs(ilimr_hlms).sum(0).argmax(1)[0]
    epoch = phenom.MtoS(ilimr_times[0],M) - phenom.MtoS(ilimr_times[peak_idx],M)

    # if n_samples is -1 then we return the mean, if n_samples=1 then we return 1 sample
    # if n_samples is X then we return X samples
    N = ilimr_hp.shape[0]

    ilimr_hp_ts = [TimeSeries(ilimr_hp[i], delta_t=dt, epoch=epoch) for i in range(N)]
    ilimr_hc_ts = [TimeSeries(ilimr_hc[i], delta_t=dt, epoch=epoch) for i in range(N)]


    return ilimr_hp_ts, ilimr_hc_ts
