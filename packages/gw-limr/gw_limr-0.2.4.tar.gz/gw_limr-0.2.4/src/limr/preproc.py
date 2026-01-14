import pandas as pd
import tqdm
from pathlib import Path
import numpy as np
import phenom
import itertools
import limr.loader

DEFAULT_CAT_PATH = "/Users/sebastian.khan/personal/data/nr-compiled-cat-2025/"

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

def prepare_input_dataframe(cat_dir=None, q_decimal=3, spin_decimal=4, max_q=21):
    """
    Load catalogue dataframe and augment with other things we need.
    Notable we had the column 'sim_group_id' which approximately enumerates
    duplicate simulations.
    
    Parameters
    ----------
    max_q
        only keep simulations with a mass-ratio less than this.

    Returns
    -------
    dataframe
    sim_group_id_map: dict
        maps mass-ratio to sim-group-id
    sim_group_id_inv_map: dict
        maps sim-group-id to mass-ratio
    """
    if not cat_dir:
        cat_dir = DEFAULT_CAT_PATH
    cat_dir = Path(cat_dir)
    df = pd.read_csv(cat_dir / "compiled_cat.csv")
    
    # using a rounding of 1 decimal place might be a bit too aggressive
    df = limr.loader.add_q_rounded_to_cat(df, q_decimal)

    #
    df = limr.loader.add_start_time_to_cat(df, cat_dir)
    
    df['spin1x'] = df['spin1x'].round(spin_decimal)
    df['spin1y'] = df['spin1y'].round(spin_decimal)
    df['spin1z'] = df['spin1z'].round(spin_decimal)
    
    df['spin2x'] = df['spin2x'].round(spin_decimal)
    df['spin2y'] = df['spin2y'].round(spin_decimal)
    df['spin2z'] = df['spin2z'].round(spin_decimal)
    
    # apply vetoes
    df_dq = pd.read_csv("data-quality.csv")
    df = pd.merge(
        df,
        df_dq[['sim_name', 'keep']],
        on='sim_name', how='outer'
    ).query("keep != False").drop(columns=['keep'])
    
    df = df.loc[df['q'] < max_q].reset_index(drop=True)
    
    # add a 'sim_group_id' so we can easily grab the set of simulations that
    # simulate the same system (approximately)
    try:
        unique_q = df['q_rounded'].value_counts().reset_index()['index']
    except:
        unique_q = df['q_rounded'].value_counts().reset_index()['q_rounded']
    unique_q_idx = df['q_rounded'].value_counts().reset_index().index
    
    sim_group_id_map = dict(zip(unique_q, unique_q_idx))
    sim_group_id_inv_map = dict(zip(unique_q_idx, unique_q))
    
    df['sim_group_id'] = df.apply(lambda x : sim_group_id_map[x['q_rounded']], axis=1)

    return df, sim_group_id_map, sim_group_id_inv_map



def add_generate_basic_train_test_idxs(
    df,
    remove_equal_mass_from_training=True,
    add_q234_to_train=False,
    add_q8910=False,
    add_q6_58=False,
    drop_duplicates_train=False,
    remove_q_gl_8=False,
    remove_q_4_to_6=False,
):
    """
    adds the 'set' column to the dataframe

    Parameters
    ----------
    df: pd.DataFrame
    remove_equal_mass_from_training: bool,
        if True then the equal mass simulations are moved to the test set

    Returns
    -------
    pd.DataFrame,
        updated dataframe
    list,
        list of train indices
    list,
        list of test indices
    """
    df = df.copy()
    # train sims are when we have more than one simulation
    # test is when we only have one sim
    mask_train = df['sim_group_id'].isin(df['sim_group_id'].value_counts().loc[lambda x: x > 1].index)
    train_idxs = list(df[mask_train].index)

    mask_test = df['sim_group_id'].isin(df['sim_group_id'].value_counts().loc[lambda x: x == 1].index)
    test_idxs = list(df[mask_test].index)

    df['set'] = ''
    df.loc[train_idxs,'set']='train'
    df.loc[test_idxs,'set']='test'

    if remove_equal_mass_from_training:
        # make q=1 part of the test set
        df.loc[df['q'] < 1.01, 'set'] = 'test'
        
        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)


    if add_q234_to_train:
        df.loc[(df['q'] > 2) & (df['q'] < 4), 'set'] = 'train'

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)

    if add_q8910:
        df.loc[(df['q'] > 8) & (df['q'] < 10), 'set'] = 'train'

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)

    if add_q6_58:
        df.loc[df['q_rounded'] == 6.58, 'set'] = 'train'

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)

    if drop_duplicates_train:
        df_train = df.loc[df['set']=='train']
        df_test = df.loc[df['set']=='test']
        df_train = df_train.drop_duplicates(subset=['sim_group_id'])

        df = pd.concat([df_train, df_test], axis=0).reset_index(drop=True)

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)


    if remove_q_gl_8:
        df.loc[(df['q'] > 7.9), 'set'] = 'test'

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)

    if remove_q_4_to_6:
        df.loc[(df['q'] > 3.9) & (df['q'] < 6.1), 'set'] = 'test'

        train_idxs = list(df[df['set']=='train'].index)
        test_idxs = list(df[df['set']=='test'].index)

    
    return df, train_idxs, test_idxs



def generate_new_times_coarse(start_time, end_time, boundary_time=0, dt_left=3, dt_right=3):
    new_times_left = np.arange(start_time, boundary_time, dt_left)
    new_times_right = np.arange(boundary_time, end_time, dt_right)
    new_times = np.concatenate((new_times_left, new_times_right))
    return new_times

def generate_new_times_fine(start_time, end_time, dt):
    return np.arange(start_time, end_time, dt)




def generate_all_nr_waveforms(df, cat_dir=None, start_time=None, end_time=100, verbose=False, new_times=None, set_inital_phase_to_zero=True):
    """
    Generate all nr waveforms in the given df dataframe catalogue
    
    Parameters
    ----------
    df: pd.DataFrame
    cat_dir: str
    start_time: float
    end_time: float
    verbose: bool
    new_times: array
        If given then interpolate waveform data onto this grid.

    Returns
    -------
    list[loader.Waveform]
    """
    if not cat_dir:
        cat_dir = Path(DEFAULT_CAT_PATH)
        
    wfs=[]
    for i, row in tqdm.tqdm(df.iterrows()):
        wf = limr.loader.generate_nr_waveform(
            sim_name=row['sim_name'],
            start_time=start_time,
            end_time=end_time,
            df=df,
            cat_dir=cat_dir,
            verbose=verbose,
            new_times=new_times,
            set_inital_phase_to_zero=set_inital_phase_to_zero,
        )
        wfs.append(wf)
    return wfs


def leading_order_amp(eta, m):
    if m % 2 == 1:
        return eta * np.sqrt(1 - 4*eta)
    else:
        return eta



def generate_grid_data(nr_wfs, df, target, mode, div_by_eta, idxs=None, eps=1e-4):
    """
    Generate cartesian product fit grids for nr waveforms
    
    Parameters
    ----------
    target:
        can be one of 'amplitudes', 'phases', 'frequencies', 'hlms_real', 'hlms_imag'
    div_by_eta:
        if True then depending on the mode will divide by eta (even m) or eta*sqrt(1-4eta) (odd m)

    Returns
    -------
    X: array
        grid of times and mass-ratios
    y: array
        array of targets
    """
    if idxs is None:
        idxs = range(len(nr_wfs))


    X = []
    y = []
    for i in idxs:
        times = getattr(nr_wfs[i], 'times')
        data = getattr(nr_wfs[i], target)
        if mode in data.keys():
            ell, m = mode
            q = df.loc[i, 'q']
            eta = phenom.eta_from_q(q)
            X.append(cartesian_prod(times, [eta]))

            if div_by_eta:
                # for odd-m modes
                if m % 2 == 1:
                    # https://arxiv.org/abs/1106.1021 (Table III)
                    fac = leading_order_amp(eta, m) + eps
                else:
                    fac = leading_order_amp(eta, m)
                y.append(data[mode] / fac)
            else:
                y.append(data[mode])
    
    X = np.concatenate(X)
    y = np.concatenate(y)
    
    return X, y







