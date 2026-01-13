# -*- coding: utf-8 -*-
"""
Components that require PyWake.

@author: ricriv
"""

# %% Import.

import jax.numpy as jnp
import xarray as xr
from autograd.scipy.special import erf
from py_wake import np as anp  # Autograd numpy
from py_wake.utils import gradients
from py_wake.utils.numpy_utils import Numpy32
from py_wake.wind_farm_models.engineering_models import (
    All2AllIterative,
    PropagateDownwind,
    PropagateUpDownIterative,
)

from wind_farm_loads.tool_agnostic import (
    _arg2ilk,
    rotate_grid_multiple_angles,
)

# %% Pot functions.


def pot_tanh(r, R, exponent=20):
    r"""
    Smooth pot function based on tanh.

    .. math::
      y = \mathrm{tanh}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`r < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r \ge 0`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 20.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return anp.tanh((r / R) ** exponent)


def pot_arctan(r, R, exponent=100):
    r"""
    Smooth pot function based on arctan.

    .. math::
      y = \frac{2}{\pi} \mathrm{arctan}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`r < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r \ge 0`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 100.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return 2.0 / anp.pi * anp.arctan((r / R) ** exponent)


def pot_erf(r, R, exponent=20):
    r"""
    Smooth pot function based on the error function.

    .. math::
      y = \mathrm{erf}\left(\left(\frac{r}{R}\right)^{a}\right)

    Values where :math:`r < R` are mapped to 0, while values outside of it are mapped to 1.

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r \ge 0`.
    R : ndarray
        Distance at which to clip :math:`R`.
    exponent : int, optional
        Exponent :math:`a`. The default is 20.

    Returns
    -------
    y : ndarray
        Smooth pot of radius :math:`R`.

    """
    # Uses Autograd numpy and Scipy because it is meant to work with PyWake.
    return erf((r / R) ** exponent)


def pot_sharp(r, R):
    r"""
    Sharp pot function.
    
    .. math::
      y = \begin{cases}
              0  &  r < R,    \\
              1  &  r \ge R
          \end{cases}

    Parameters
    ----------
    r : ndarray
        Radial distance :math:`r \ge 0`.
    R : ndarray
        Distance at which to clip :math:`R`.

    Returns
    -------
    y : ndarray
        Sharp pot of radius :math:`R`.

    """
    # Uses Autograd numpy because it is meant to work with PyWake.
    return anp.where(r < R, 0.0, 1.0)


# %% Classes to avoid self wake and self blockage.


class PropagateDownwindNoSelfInduction(PropagateDownwind):
    """Same as `PropagateDownwind`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        PropagateDownwind.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateDownwind._calc_deficit(
            self, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(
            deficit, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


class PropagateUpDownIterativeNoSelfInduction(PropagateUpDownIterative):
    """Same as `PropagateUpDownIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        PropagateUpDownIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = PropagateUpDownIterative._calc_deficit(
            self, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight

        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(
            deficit, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


class All2AllIterativeNoSelfInduction(All2AllIterative):
    """Same as `All2AllIterative`, but the wake, added turbulence and blockage are set to 0 in a sphere that surrounds each rotor.

    The objective of this class is to obtain a flow map that does not measure
    the induction of the current turbine, while keeping the same wind farm power.
    """

    def __init__(self, *args, pot=pot_sharp, **kwargs):
        All2AllIterative.__init__(self, *args, **kwargs)
        self.pot = pot

    def _calc_deficit(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, blockage = All2AllIterative._calc_deficit(
            self, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, blockage

    def _calc_deficit_convection(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        deficit, uc, sigma_sqr = self.wake_deficitModel.calc_deficit_convection(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        deficit, blockage = self._add_blockage(
            deficit, dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        deficit = deficit * weight
        if blockage is not None:
            blockage = blockage * weight
        return deficit, uc, sigma_sqr, blockage

    def _calc_added_turbulence(self, dw_ijlk, cw_ijlk, D_src_il, **kwargs):
        added_ti = self.turbulenceModel.calc_added_turbulence(
            dw_ijlk=dw_ijlk, cw_ijlk=cw_ijlk, D_src_il=D_src_il, **kwargs
        )
        r = gradients.hypot(dw_ijlk, cw_ijlk)
        weight = self.pot(r, 0.75 * D_src_il[:, anp.newaxis, :, anp.newaxis])
        added_ti = added_ti * weight
        return added_ti


# %% Functions to extract the inflow.


def get_rotor_averaged_wind_speed_and_turbulence_intensity(sim_res):
    """
    Get rotor-averaged effective wind speed and turbulence intensity.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        A simulation result from PyWake. Must follow a call to the wind farm model.

    Returns
    -------
    ws_eff : xarray DataArray
        Effective wind speed.
    ti_eff : xarray DataArray
        Effective turbulence intensity.

    """
    return sim_res["WS_eff"], sim_res["TI_eff"]


def compute_flow_map(
    sim_res,
    grid,
    align_in_yaw=True,
    align_in_tilt=True,
    axial_wind=False,
    wt=None,
    wd=None,
    ws=None,
    time=None,
    dtype=jnp.float32,
    save_grid=False,
    use_single_precision=False,
    memory_GB=1,
    n_cpu=1,
):
    r"""
    Compute the effective wind speed and Turbulence Intensity over a rotor.

    This function receives a grid, and then rotates it by the wind direction. Optionally,
    the grid is also rotated by the yaw and tilt of each turbine to align it with the rotor plane.
    Finally, the grid is translated to each rotor center and the flow map is computed.

    Parameters
    ----------
    sim_res : py_wake SimulationResult
        Simulation result computed by PyWake. Must follow a call to the wind farm model.
    grid : (M, N, 3) or (M, N, 3, Type) ndarray
        x, y and z coordinate of the grid points, before rotation by yaw and tilt.
        Typically generated by `make_rectangular_grid` or `make_polar_grid`.
        The first 2 dimensions cover the rotor, then there are x, y, z and finally (optionally) the turbine type.
        If the user passes a 3D array, the grid is assumed to be the same for all turbine types.
    align_in_yaw : bool, optional
        If `True` (default) the grid is aligned in yaw with the rotor plane.
    align_in_tilt : bool, optional
        If `True` (default) the grid is aligned in tilt with the rotor plane.
    axial_wind : bool, optional
        If `True` the axial wind speed and TI are returned. That is, the downstream wind speed computed by PyWake
        is multiplied by :math:`\cos(\mathrm{yaw}) \cos(\mathrm{tilt})`. The default is `False`.
    wt : int, (I) array_like, optional
        Wind turbines. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind turbines.
    wd : float, (L) array_like, optional
        Wind direction, in deg. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind directions.
    ws : float, (K) array_like, optional
        Wind speed. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available wind speeds.
    time : float, (Time) array_like, optional
        Time. Must be a subset of the one contained in `sim_res`.
        The default is `None`, which means to use all available time instants.
    dtype : data-type, optional
        The desired data-type for the result and some intermediate computations.
        The default is single precision, which should be enough for all outputs.
        The properties of each type can be checked with `np.finfo(np.float32(1.0))`.
    save_grid : bool, optional
        If `True` the grid will be saved for all inflow conditions. Since this comes at a significant
        memory cost, it is recommended to switch it on only for debug purposes.
        The default is `False`.
    use_single_precision : bool, optional
        If `True`, the PyWake flow map is computed in single precision.
        This leads to reduced memory and run time, but also to a loss of precision.
        The default is `False`.
    memory_GB : int or float, optional
        If the additional memory needed to compute the flow map is assumed to exceed `memory_GB` GB using
        simple models, then the flow map is split into a number of wind direction and/or point chunks to
        reduce the memory consumption.
        The default is 1 GB.
    n_cpu : int or None, optional
        Number of CPUs used to compute the flow map.
        If `None`, all available CPUs are used.
        The default is 1, since often it is the fastest option.

    Returns
    -------
    flow_map : xarray DataSet
        Effective wind speed, effective turbulence intensity and corresponding grid points
        for each turbine and flow case.

    """
    # Get the number of turbine types.
    # This is faster than jnp.unique(sim_res["type"].data).
    n_types = len(sim_res.windFarmModel.windTurbines._names)

    # The grid must be an array with 3 or 4 dimensions.
    # The first 2 cover the rotor, while the third is x, y and z.
    # The 4th dimension, if present, is over the types.
    # If the grid is a 3D array, then all turbine types share the same grid.
    if grid.ndim == 3:
        grid_t = jnp.broadcast_to(
            jnp.astype(grid[:, :, :, jnp.newaxis], dtype), (*grid.shape, n_types)
        )
    elif grid.ndim == 4:
        grid_t = jnp.astype(grid, dtype)
        # Check that there is 1 grid per turbine type.
        if grid_t.shape[3] != n_types:
            raise ValueError(
                f"{grid_t.shape[3]} grid types provided, but {n_types} were expected."
            )
    else:
        raise ValueError("The grid must be a 3D or 4D array.")

    # The default value of wt, wd, ws and time is the one in sim_res.
    wt_ = sim_res["wt"].data if wt is None else jnp.atleast_1d(jnp.asarray(wt))
    wd_ = sim_res["wd"].data if wd is None else jnp.atleast_1d(jnp.asarray(wd))
    ws_ = sim_res["ws"].data if ws is None else jnp.atleast_1d(jnp.asarray(ws))

    # Compute the list of turbines for each type. The list is also filtered by wt_.
    # The dict is in the form turbine_type_index: list_of_turbines.
    # It is used later to rotate the grids.
    wt_by_type = {
        t: sim_res["wt"].data[wt_][sim_res["type"].data[wt_] == t]
        for t in range(n_types)
    }

    # Convert yaw and tilt to arrays.
    # If time is not present the result has shape (I, L, K), i.e. (turbines, wind directions, wind speeds).
    # Instead, if time is present, the result has shape (I, Time), i.e. (turbines, time).
    # These arrays are contained in sim_res, therefore all turbines, directions and speeds and times must be used.
    I = sim_res.sizes["wt"]
    if "time" in sim_res.dims:
        # We use L to store the time dimension.
        L = sim_res.sizes["time"]
        K = None  # Dummy dimension for wind speed.
        if time is None:
            time_ = sim_res["time"].data
        else:
            if isinstance(time, xr.DataArray):
                time_ = time.data
            else:
                time_ = jnp.atleast_1d(jnp.asarray(time))
        time_index = jnp.searchsorted(sim_res["time"].data, time_)
    else:
        L = sim_res.sizes["wd"]
        K = sim_res.sizes["ws"]
        wd_index = jnp.searchsorted(sim_res["wd"].data, wd_)
        ws_index = jnp.searchsorted(sim_res["ws"].data, ws_)
    yaw = sim_res["yaw"].data if align_in_yaw else 0.0
    tilt = sim_res["tilt"].data if align_in_tilt else 0.0
    yaw_turbines_ = _arg2ilk(yaw, I, L, K)
    tilt_turbines_ = _arg2ilk(tilt, I, L, K)

    # Conveniently access turbine position.
    # Coherently with the grid, the axis dimension is placed last.
    # The axes are ordered as: (I, L, K, direction), where direction is x, y or z.
    # When time is present, there is no K.
    position_turbines = jnp.stack(
        (
            _arg2ilk(sim_res["x"].data, I, L, K),
            _arg2ilk(sim_res["y"].data, I, L, K),
            _arg2ilk(sim_res["h"].data, I, L, K),
        ),
        axis=-1,
        dtype=dtype,
    )

    # Convert all angles from deg to rad.
    # Angles are always computed in double precision.
    wd_rad = jnp.deg2rad(jnp.astype(wd_, jnp.float64))
    yaw_turbines_ = jnp.deg2rad(jnp.astype(yaw_turbines_, jnp.float64))
    tilt_turbines_ = jnp.deg2rad(jnp.astype(tilt_turbines_, jnp.float64))

    # 90 deg.
    angle_ref = jnp.float64(jnp.pi) / 2.0

    # The following code computes the flow map, which depends if time is included or not.
    if "time" in sim_res.dims:
        # Preallocate arrays to store the flow and grid.
        # Each turbine type is allowed to have a different grid, but all grids must have the same number of points.
        # The dimension for the effective wind speed and TI, as well as the direction (x, y, z), is placed last for faster access.
        flow = jnp.empty(
            (
                wt_.size,
                time_.size,
                grid_t.shape[0],
                grid_t.shape[1],
                2,  # Effective wind speed and TI.
            ),
            dtype=dtype,
        )
        grid_all = jnp.empty(
            (
                wt_.size,
                time_.size,
                grid_t.shape[0],
                grid_t.shape[1],
                3,  # x, y, z
            ),
            dtype=dtype,
        )

        # Loop over the turbine types.
        for tt, wt_per_tt in wt_by_type.items():
            # Compute the grid for all ambient wind conditions.
            # Convert grid from downwind-crosswind-z to east-north-z.
            # While doing that, also rotate by yaw and tilt.
            # This can be done because the order of rotations is first yaw and then tilt.
            # It will NOT work for a floating turbine.
            # We rely on this function to create new arrays, so that the following
            # translation will not affect the original ones.
            # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
            id = jnp.ix_(wt_per_tt, time_index)
            grid_current = rotate_grid_multiple_angles(
                grid_t[:, :, :, tt],
                yaw=yaw_turbines_[id]
                - wd_rad[jnp.newaxis, time_index]
                + angle_ref,  # [rad]
                tilt=-tilt_turbines_[id],  # [rad]
                degrees=False,
            )
            grid_all = grid_all.at[wt_per_tt, ...].set(grid_current)

        # Translate grids to each rotor center. The turbine position is in east-north-z coordinates.
        # First, select the subset of turbines and time, and then add the 2 grid dimensions.
        id = jnp.ix_(wt_, time_index, jnp.arange(3))
        grid_all = grid_all.at[...].add(
            position_turbines[id][:, :, jnp.newaxis, jnp.newaxis, :]
        )

        # Now that the grid is available for all rotors and time instants, compute the flow map.
        # The public function sim_res.flow_map(), as well as Points, do not support time-dependent grids.
        # Therefore, we must repeat what sim_res.flow_map() does, with the only change related to the grid.

        # The _flow_map function requires a grid with shape (points, time).
        # Shape of the grid that depends on turbine and time, per axis (x, y, z).
        grid_jl_shape = (wt_.size * grid_t.shape[0] * grid_t.shape[1], time_.size)
        wd_for_flow_map, ws_for_flow_map, sim_res_for_flow_map = (
            sim_res._get_flow_map_args(wd_, ws_, time_)
        )
        if use_single_precision:
            with Numpy32():
                # Grid arrays are converted from JAX to AutoGrad before calling PyWake.
                # The time is moved to be the last dimension.
                # Alternative: move the time dimension before splitting by x, y, z.
                _, WS_eff_jlk, TI_eff_jlk = sim_res.windFarmModel._flow_map(
                    x_jl=anp.asarray(
                        grid_all[:, :, :, :, 0]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    y_jl=anp.asarray(
                        grid_all[:, :, :, :, 1]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    h_jl=anp.asarray(
                        grid_all[:, :, :, :, 2]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    lw=sim_res.localWind,
                    wd=wd_for_flow_map,
                    ws=ws_for_flow_map,
                    sim_res_data=sim_res_for_flow_map,
                    D_dst=0,
                    memory_GB=memory_GB,
                    n_cpu=n_cpu,
                )
        else:  # Double precision.
            # Grid arrays are converted from JAX to AutoGrad before calling PyWake.
            _, WS_eff_jlk, TI_eff_jlk = sim_res.windFarmModel._flow_map(
                x_jl=anp.asarray(
                    grid_all[:, :, :, :, 0].transpose(0, 2, 3, 1).reshape(grid_jl_shape)
                ),
                y_jl=anp.asarray(
                    grid_all[:, :, :, :, 1].transpose(0, 2, 3, 1).reshape(grid_jl_shape)
                ),
                h_jl=anp.asarray(
                    grid_all[:, :, :, :, 2].transpose(0, 2, 3, 1).reshape(grid_jl_shape)
                ),
                lw=sim_res.localWind,
                wd=wd_for_flow_map,
                ws=ws_for_flow_map,
                sim_res_data=sim_res_for_flow_map,
                D_dst=0,
                memory_GB=memory_GB,
                n_cpu=n_cpu,
            )
        # Save the effective wind speed and TI.
        flow = flow.at[:, :, :, :, 0].set(
            WS_eff_jlk[:, :, 0]  # Remove the dummy wind speed dimension.
            .reshape(wt_.size, grid_t.shape[0], grid_t.shape[1], time_.size)
            .transpose(0, 3, 1, 2)
            .astype(dtype)
        )
        flow = flow.at[:, :, :, :, 1].set(
            TI_eff_jlk[:, :, 0]  # Remove the dummy wind speed dimension.
            .reshape(wt_.size, grid_t.shape[0], grid_t.shape[1], time_.size)
            .transpose(0, 3, 1, 2)
            .astype(dtype)
        )
        # Project wind speed.
        if axial_wind:
            cos_yaw_cos_tilt = jnp.cos(yaw_turbines_) * jnp.cos(tilt_turbines_)
            flow = flow * cos_yaw_cos_tilt[:, :, jnp.newaxis, jnp.newaxis, jnp.newaxis]

    else:  # "time" not in sim_res.dims
        # Preallocate arrays to store the flow and grid.
        # Each turbine type is allowed to have a different grid, but all grids must have the same number of points.
        # The dimension for the effective wind speed and TI, as well as the direction (x, y, z), is placed last for faster access.
        flow = jnp.empty(
            (
                wt_.size,
                wd_.size,
                ws_.size,
                grid_t.shape[0],
                grid_t.shape[1],
                2,  # Effective wind speed and TI.
            ),
            dtype=dtype,
        )
        grid_all = jnp.empty(
            (
                wt_.size,
                wd_.size,
                ws_.size,
                grid_t.shape[0],
                grid_t.shape[1],
                3,  # x, y, z
            ),
            dtype=dtype,
        )

        # Loop over the turbine types.
        for tt, wt_per_tt in wt_by_type.items():
            # Compute the grid for all ambient wind conditions.
            # Convert grid from downwind-crosswind-z to east-north-z.
            # While doing that, also rotate by yaw and tilt.
            # This can be done because the order of rotations is first yaw and then tilt.
            # It will NOT work for a floating turbine.
            # We rely on this function to create new arrays, so that the following
            # translation will not affect the original ones.
            # The formula for the yaw is taken from py_wake.wind_turbines._wind_turbines.WindTurbines.plot_xy()
            id = jnp.ix_(wt_per_tt, wd_index, ws_index)
            grid_current = rotate_grid_multiple_angles(
                grid_t[:, :, :, tt],
                yaw=yaw_turbines_[id]
                - wd_rad[jnp.newaxis, wd_index, jnp.newaxis]
                + angle_ref,  # [rad]
                tilt=-tilt_turbines_[id],  # [rad]
                degrees=False,
            )
            grid_all = grid_all.at[wt_per_tt, ...].set(grid_current)

        # Translate grids to each rotor center. The turbine position is in east-north-z coordinates.
        # First, select the subset of turbines, wind direction and speeds, and then add the 2 grid dimensions.
        id = jnp.ix_(wt_, wd_index, ws_index, jnp.arange(3))
        grid_all = grid_all.at[...].add(
            position_turbines[id][:, :, :, jnp.newaxis, jnp.newaxis, :]
        )

        # Loop over wind speeds.
        for k in range(ws_.size):
            # Now that the grid is available for all rotors, wind directions and speeds, compute the flow map.
            # The public function sim_res.flow_map, as well as Points, do not support wd-dependent grids.
            # Therefore, we must repeat what sim_res.flow_map() does, with the only change related to the grid.

            # The _flow_map function requires a grid with shape (points, wd).
            # Shape of the grid that depends on turbine and wind direction, per axis (x, y, z).
            grid_jl_shape = (wt_.size * grid_t.shape[0] * grid_t.shape[1], wd_.size)
            wd_for_flow_map, ws_for_flow_map, sim_res_for_flow_map = (
                sim_res._get_flow_map_args(wd_, ws_[k], None)
            )
            if use_single_precision:
                with Numpy32():
                    # Grid arrays are converted from JAX to AutoGrad before calling PyWake.
                    # The wind direction is moved to be the last dimension.
                    # Alternative: move the wind direction dimension before splitting by x, y, z.
                    _, WS_eff_jlk, TI_eff_jlk = sim_res.windFarmModel._flow_map(
                        x_jl=anp.asarray(
                            grid_all[:, :, k, :, :, 0]
                            .transpose(0, 2, 3, 1)
                            .reshape(grid_jl_shape)
                        ),
                        y_jl=anp.asarray(
                            grid_all[:, :, k, :, :, 1]
                            .transpose(0, 2, 3, 1)
                            .reshape(grid_jl_shape)
                        ),
                        h_jl=anp.asarray(
                            grid_all[:, :, k, :, :, 2]
                            .transpose(0, 2, 3, 1)
                            .reshape(grid_jl_shape)
                        ),
                        lw=sim_res.localWind,
                        wd=wd_for_flow_map,
                        ws=ws_for_flow_map,
                        sim_res_data=sim_res_for_flow_map,
                        D_dst=0,
                        memory_GB=memory_GB,
                        n_cpu=n_cpu,
                    )
            else:  # Double precision.
                # Grid arrays are converted from JAX to AutoGrad before calling PyWake.
                _, WS_eff_jlk, TI_eff_jlk = sim_res.windFarmModel._flow_map(
                    x_jl=anp.asarray(
                        grid_all[:, :, k, :, :, 0]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    y_jl=anp.asarray(
                        grid_all[:, :, k, :, :, 1]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    h_jl=anp.asarray(
                        grid_all[:, :, k, :, :, 2]
                        .transpose(0, 2, 3, 1)
                        .reshape(grid_jl_shape)
                    ),
                    lw=sim_res.localWind,
                    wd=wd_for_flow_map,
                    ws=ws_for_flow_map,
                    sim_res_data=sim_res_for_flow_map,
                    D_dst=0,
                    memory_GB=memory_GB,
                    n_cpu=n_cpu,
                )
            # Save the effective wind speed and TI for the current wind speed.
            flow = flow.at[:, :, k, :, :, 0].set(
                WS_eff_jlk[:, :, 0]  # Remove the dummy wind speed dimension.
                .reshape(wt_.size, grid_t.shape[0], grid_t.shape[1], wd_.size)
                .transpose(0, 3, 1, 2)
                .astype(dtype)
            )
            flow = flow.at[:, :, k, :, :, 1].set(
                TI_eff_jlk[:, :, 0]  # Remove the dummy wind speed dimension.
                .reshape(wt_.size, grid_t.shape[0], grid_t.shape[1], wd_.size)
                .transpose(0, 3, 1, 2)
                .astype(dtype)
            )

        # Project wind speed.
        if axial_wind:
            cos_yaw_cos_tilt = jnp.cos(yaw_turbines_) * jnp.cos(tilt_turbines_)
            flow = (
                flow * cos_yaw_cos_tilt[:, :, :, jnp.newaxis, jnp.newaxis, jnp.newaxis]
            )

    # Store results into xarray Dataset.
    # The grid dimensions are labeled q0 and q1 because they might be either y and z or radius and azimuth.
    xr_dict = {}
    if "time" in sim_res.dims:
        # Set the independent coordinates: turbine, time and quantity.
        coords_flow = {
            "wt": wt_,
            "time": time_,
            "quantity": ["WS_eff", "TI_eff"],
        }
        # Set the dependent coordinates: wind direction and wind speed.
        coords_flow["wd"] = (["time"], wd_[time_index])
        coords_flow["ws"] = (["time"], ws_[time_index])

        xr_dict["flow"] = xr.DataArray(
            data=flow,
            coords=coords_flow,
            dims=("wt", "time", "q0", "q1", "quantity"),
        )
        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=grid_all,
                coords={
                    "wt": wt_,
                    "time": time_,
                    "axis": ["x", "y", "z"],
                },
                dims=("wt", "time", "q0", "q1", "axis"),
            )

    else:  # "time" not in sim_res.dims
        xr_dict["flow"] = xr.DataArray(
            data=flow,
            coords={
                "wt": wt_,
                "wd": wd_,
                "ws": ws_,
                "quantity": ["WS_eff", "TI_eff"],
            },
            dims=("wt", "wd", "ws", "q0", "q1", "quantity"),
        )
        if save_grid:
            xr_dict["grid"] = xr.DataArray(
                data=grid_all,
                coords={
                    "wt": wt_,
                    "wd": wd_,
                    "ws": ws_,
                    "axis": ["x", "y", "z"],
                },
                dims=("wt", "wd", "ws", "q0", "q1", "axis"),
            )
    ds = xr.Dataset(xr_dict)

    return ds
