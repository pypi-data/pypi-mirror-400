import jax
jax.config.update("jax_enable_x64", True)
import numpy as np
import jax.numpy as jnp
from tinygp import GaussianProcess, kernels, transforms
import itertools

def cartesian_prod(*arrs):
    """
    https://docs.pytorch.org/docs/stable/generated/torch.cartesian_prod.html

    much easier that using meshgrids...

    Example
    -------
    cartesian_prod([1,2,3],[1], [2])
    array([[1, 1, 2],
       [2, 1, 2],
       [3, 1, 2]])
    """
    return np.array(list(itertools.product(*arrs)))



def leading_order_amp(eta, m):
    if m % 2 == 1:
        return eta * np.sqrt(1 - 4*eta)
    else:
        return eta


def apply_phase_shift(hlms, phi, mode_to_index):
    """
    hlms is an array with shape (n_mode, n_samples, n_times)
    phi is an array with shape (n_samples)
    """
    hlms = hlms.copy()
    for mode, mode_idx in mode_to_index.items():
        l, m = mode
        hlms[mode_idx] = hlms[mode_idx] * np.exp(1.j * m * phi[:,np.newaxis])
    return hlms


def set_phase_to_zero_at_start(hlms, mode_to_index):
    """
    hlms is an array with shape (n_mode, n_samples, n_times)
    """
    hlms = hlms.copy()
    n_mode, n_samples, n_times = hlms.shape

    mode_22 = mode_to_index[2,2]
    mode_21 = mode_to_index[2,1]
    
    phi0 = np.angle(hlms[mode_22])[:,0] / 2
    # not sure if need the mod 2pi
    phi0 = phi0 % (2*np.pi)
    hlms = apply_phase_shift(hlms, -phi0, mode_to_index)


    # for each sample need to change the state of the 21 mode, don't think this can be vectorised?
    # well the phase shift could be an array of 0 or pi i guess
    phi0 = np.angle(hlms[mode_21])[:,0]
    # phi0 = phi0 % (2*np.pi)
    mask = phi0 < 0
    if mask.sum() > 0:
        phi0_21 = np.zeros(shape=n_samples)
        phi0_21[mask] = np.pi
        hlms = apply_phase_shift(hlms, phi0_21, mode_to_index)
    

    return hlms

