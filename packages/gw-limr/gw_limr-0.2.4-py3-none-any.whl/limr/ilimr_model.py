"""
I-LIMR: Inspiral-Late-Inspiral-Merger-Ringdown

Here we hybridise LIMR with an inspiral.
"""

import numpy as np

import limr.limr_model
import limr.inspiral_model
import limr.utils

class ILIMR:
    def __init__(self, limr_model:limr.limr_model.LIMR):
        self.limr_model = limr_model
        self.modes = self.limr_model.modes


    def get_inspiral(self, q, M, f_min, deltaT, approximant):
        # generate the base HM inspiral
        inspiral_hlm = limr.inspiral_model.get_inspiral_hlm(
            approximant=approximant,
            modes=self.modes,
            q=q,
            M=M,
            f_min=f_min,
            deltaT=deltaT,
            )
        
        inspiral_times = inspiral_hlm.times
        return inspiral_times, inspiral_hlm


    def predict(self, q, M=100, f_min=20, deltaT=1/4096., approximant='IMRPhenomTHM', end_time=100):
        inspiral_times, inspiral_hlm = self.get_inspiral(q, M=M, f_min=f_min, deltaT=deltaT, approximant=approximant)
        
        # generate the LIMR waveform
        deltaT_M = inspiral_times[1]-inspiral_times[0]
        # the first limr sample is going to be the last sample
        # from the inspiral
        # and when we join the two together we
        # will drop either the last inspiral and the first limr
        # sample to have a contiguous time series
        t_limr_start = inspiral_times[-1]
        limr_times = np.arange(t_limr_start, end_time, deltaT_M)
        limr_hlm = self.limr_model.predict(limr_times, q)

        ilimr_times, ilimr_hlm = self.connect_(inspiral_times, inspiral_hlm, limr_times, limr_hlm, t_limr_start)
        return ilimr_times, ilimr_hlm


    def sample(self, q, n_samples, M=100, f_min=20, deltaT=1/4096., approximant='IMRPhenomTHM', end_time=100, prngkey=None):
        inspiral_times, inspiral_hlm = self.get_inspiral(q, M=M, f_min=f_min, deltaT=deltaT, approximant=approximant)
        
        # generate the LIMR waveform
        deltaT_M = inspiral_times[1]-inspiral_times[0]
        # the first limr sample is going to be the last sample
        # from the inspiral
        # and when we join the two together we
        # will drop either the last inspiral and the first limr
        # sample to have a contiguous time series
        t_limr_start = inspiral_times[-1]
        limr_times = np.arange(t_limr_start, end_time, deltaT_M)

        limr_hlm = self.limr_model.sample(limr_times, q, n_samples=n_samples, prngkey=prngkey)

        ilimr_times, ilimr_hlm = self.connect_(inspiral_times, inspiral_hlm, limr_times, limr_hlm, t_limr_start)
        return ilimr_times, ilimr_hlm


    def connect_(self, inspiral_times, inspiral_hlm, limr_times, limr_hlm, t_limr_start):
        # determine amplitude and phase connection
        # of the type (1 + A * (t - T_0))
        # where A is the free parameter
        # and T_0 is the start of the inspiral waveform
        Amp_A0 = {}
        T_0 = inspiral_times[0]

        n_modes = limr_hlm.shape[0]
        n_samples = limr_hlm.shape[1]
        n_times = len(inspiral_times)
        inspiral_amp = np.zeros(shape=(n_modes, n_samples, n_times))
        inspiral_phase = np.zeros(shape=(n_modes, n_samples, n_times))

        # -1 because there is one sample that overlaps
        n_ilimr_times = len(inspiral_times) + len(limr_times) - 1
        ilimr_times = np.concatenate((inspiral_times[:-1], limr_times))
        ilimr_amp = np.zeros(shape=(n_modes, n_samples, n_ilimr_times))
        ilimr_phase = np.zeros(shape=(n_modes, n_samples, n_ilimr_times))
        ilimr_hlm = np.zeros(shape=(n_modes, n_samples, n_ilimr_times), dtype=np.complex128)

        limr_amp = np.abs(limr_hlm)
        limr_phase = np.unwrap(np.angle(limr_hlm))
        
        for mode, mode_index in self.limr_model.mode_to_index.items():
            B_ = np.abs(inspiral_hlm.hlms[mode])[-1]
            C_ = limr_amp[mode_index, :, 0]
            Amp_A0 = (C_/B_ - 1)/(t_limr_start-T_0)

            amp_correction = (1 + Amp_A0[:,np.newaxis] * (inspiral_times-T_0))
            inspiral_amp[mode_index,:,:] = np.abs(inspiral_hlm.hlms[mode]) * amp_correction

            # align phase
            inspiral_phase[mode_index] = np.unwrap(np.angle(inspiral_hlm.hlms[mode]))
            shift = inspiral_phase[mode_index,:,-1] - limr_phase[mode_index,:,0]

            # shift limr to match inspiral
            # phase_limr = phase_limr + shift
            # shift inspiral to match limr (this way make it easier to compare with limr)
            inspiral_phase[mode_index] = inspiral_phase[mode_index] - shift[:,np.newaxis]

            ilimr_amp[mode_index, :, :] = np.concatenate((inspiral_amp[mode_index, :, :-1], limr_amp[mode_index,:,:]), axis=1)
            ilimr_phase[mode_index, :, :] = np.concatenate((inspiral_phase[mode_index,:,:-1], limr_phase[mode_index,:,:]), axis=1)
            ilimr_hlm[mode_index, :, :] = ilimr_amp[mode_index, :, :] * np.exp(1.j * ilimr_phase[mode_index, :, :])

        # re-interpolate onto final time grid ... if i've done it correctly then i don't need to reinterpolate

        # set initial phase to zero?
        ilimr_hlm = limr.utils.set_phase_to_zero_at_start(ilimr_hlm, self.limr_model.mode_to_index)

        # output

        return ilimr_times, ilimr_hlm
    

