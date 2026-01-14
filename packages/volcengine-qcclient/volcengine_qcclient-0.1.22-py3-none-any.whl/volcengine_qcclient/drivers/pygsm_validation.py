import warnings


# Default configuration for `pygsm` tasks.
#
# This is aligned with the example config in
# `volcengine-qcworker/test_configs/pygsm/config.yaml`.
default_config = {
    'mode': 'DE_GSM',  # "DE_GSM" or "SE_GSM"
    'calc': 'PySCF',  # "XTB", "PySCF"
    'ID': 1,  # Integer identifier for this job
    'isomers': None,  # For SE_GSM: path to driving coordinate file

    'num_nodes': 11,  # If null, defaults: 9 for DE_GSM, 20 for SE_GSM

    'optimizer': 'eigenvector_follow',  # "eigenvector_follow" or "lbfgs"
    'opt_print_level': 1,
    'gsm_print_level': 1,
    'xyz_output_format': 'molden',
    'linesearch': 'NoLineSearch',  # "NoLineSearch" or "backtrack"

    'coordinate_type': 'TRIC',  # "TRIC", "DLC", or "HDLC"

    'ADD_NODE_TOL': 0.1,
    'DQMAG_MAX': 0.8,
    'BDIST_RATIO': 0.5,
    'CONV_TOL': 0.005,
    'growth_direction': 0,

    'reactant_geom_fixed': False,
    'product_geom_fixed': False,

    'nproc': 1,
    'max_gsm_iters': 50,
    'max_opt_steps': 5,  # If null, defaults: 3 for DE_GSM, 20 for SE_GSM

    'only_drive': False,  # SE-GSM only: only generate interpolated string
    'restart_file': None,  # Path to restart XYZ/molden file, or null

    'conv_Ediff': 100.0,
    'conv_dE': 1.0,
    'conv_gmax': 100.0,
    'DMAX': 0.1,
    'reparametrize': True,
    'interp_method': 'TRIC',
    'start_climb_immediately': False,

    'charge': 0,
    'multiplicity': 1,
    'device': 'cpu',  # For MLFF calculations: "cpu", "cuda", "cuda:0", ...

    'solvent': None,  # For implicit solvation (XTB: solvent name; PySCF: see solvation_model/solvent_eps)
    'solvation_model': 'IEF-PCM',  # XTB: "alpb"/"gbsa"; PySCF: "IEF-PCM"/"C-PCM"/"DDCOSMO"/"SMD", etc.

    'functional': 'pbe0',  # PySCF DFT functional
    'basis': 'def2-svpd',  # PySCF basis set
    'auxbasis': 'def2-universal-jkfit',  # PySCF auxiliary basis for density fitting
    'solvent_eps': 29.0,  # Dielectric constant (default is water 78.3553)
    'use_gpu': False,  # Use GPU acceleration for PySCF (requires gpu4pyscf)
    'grid_level': 5,  # PySCF DFT grid level
    'pyscf_verbose': 0,  # 0: silent, 1: quiet, 2: normal, 3: verbose, 4: debug
}


def _warn(msg: str):
    warnings.warn(msg, stacklevel=2)


def validate(task_config, xyz=None):
    """Validate `pygsm` task configuration.

    Notes:
    - qcclient currently does not support uploading extra files. Therefore,
      `isomers` and `restart_file` must be absent or set to null/None.
    - `xyz` is not used. (pyGSM input geometries are typically read from files
      inside the worker container.)
    """
    saved_keys = ["versions"]
    saved_map = {}
    for key in saved_keys:
        if key in task_config:
            saved_map[key] = task_config[key]
            del task_config[key]

    unknown_keys = set(task_config).difference(default_config)
    if unknown_keys:
        raise ValueError(f'Configuration keys {unknown_keys} are not supported')

    # Basic type checks using defaults as references.
    for key, val in task_config.items():
        if key in ('isomers', 'restart_file'):
            continue
        default_val = default_config[key]
        if default_val is None:
            continue
        if type(val) is not type(default_val):
            raise TypeError(f'The value for {key} must be of type {type(default_val)}')

    # Enforce no file-upload related fields.
    for key in ('isomers', 'restart_file'):
        if key in task_config and task_config[key] is not None:
            raise ValueError(
                f'qcclient does not support uploading files; `{key}` must be null/None or not set.'
            )

    mode = task_config.get('mode', default_config['mode'])
    calc = task_config.get('calc', default_config['calc'])
    if isinstance(mode, str) and mode not in ('DE_GSM', 'SE_GSM'):
        raise ValueError('`mode` must be "DE_GSM" or "SE_GSM"')
    if isinstance(calc, str) and calc not in ('XTB', 'PySCF'):
        raise ValueError('`calc` must be "XTB" or "PySCF"')

    if mode == 'SE_GSM':
        # SE_GSM requires isomers file.
        _warn('SE_GSM typically requires `isomers`; qcclient cannot upload it. Consider using worker-side paths.')

    task_config.update(saved_map)
    return task_config