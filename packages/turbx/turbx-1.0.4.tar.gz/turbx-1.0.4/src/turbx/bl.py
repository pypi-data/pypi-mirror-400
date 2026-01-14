import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import PchipInterpolator, interp1d
from scipy.optimize import least_squares

# ======================================================================

def _check_validity_yx(y,x):
    '''
    Check 1D coordinate [y] and generic 1D variable [x]
    '''
    if not isinstance(y,np.ndarray):
        raise ValueError('y must be type np.ndarray')
    if not isinstance(x,np.ndarray):
        raise ValueError('x must be type np.ndarray')
    if y.ndim != 1 or x.ndim != 1:
        raise ValueError('.ndim != 1')
    if y.shape[0] != x.shape[0]:
        raise ValueError('y,x shapes not equal')
    if not np.all(np.diff(y) > 0): ## check (+) monotonicity
        raise ValueError("y must be monotonically increasing")
    if y[0] < -1e-4:
        raise ValueError("y[0] < 0")
    if not np.isclose(y[0], 0., atol=1e-4):
        raise ValueError("y[0] not sufficiently close to 0")
    return

def calc_d1(y, u, rho=None, j_edge=-1, u_edge=None, rho_edge=None, **kwargs):
    '''
    Displacement (mass-flux deficit) thickness δ1 = δ*
    -----
    δ1 = ∫ ( 1 - ρu / (ρe·ue) ) dy
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    # ===
    
    integrand = 1. - (rho*u)/(rho_edge*u_edge) ## δ1 integrand
    
    d1 = cumulative_trapezoid(y=integrand, x=y, initial=0.)[j_edge] ## δ1
    
    return d1

def calc_d2(y, u, rho=None, j_edge=-1, u_edge=None, rho_edge=None, **kwargs):
    '''
    Momentum deficit thickness δ2 = θ
    -----
    δ2 = ∫ ( ρu / (ρe·ue) ) ( 1 - u / ue ) dy
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    # ===
    
    integrand = (rho*u)/(rho_edge*u_edge) * (1. - u/u_edge) ## δ2 integrand
    
    d2 = cumulative_trapezoid(y=integrand, x=y, initial=0.)[j_edge] ## δ2
    
    return d2

def calc_d3(y, u, rho=None, j_edge=-1, u_edge=None, rho_edge=None, **kwargs):
    '''
    Kinetic energy deficit thickness δ3
    -----
    δ3 = ∫ ( ρu / (ρe·ue) ) ( 1 - (u / ue)^2 ) dy
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    # ===
    
    integrand = (rho*u)/(rho_edge*u_edge) * (1. - (u/u_edge)**2) ## δ3 integrand
    
    d3 = cumulative_trapezoid(y=integrand, x=y, initial=0.)[j_edge] ## δ3
    
    return d3

def calc_dRC(y, u, u_tau, rho=None, j_edge=-1, u_edge=None, rho_edge=None, rho_wall=None, **kwargs):
    '''
    Rotta-Clauser Δ = ∫W+dy = ∫(ρe+ue+ - ρ+u+) dy
    -----
    W  = (ρe·ue - ρ·u)/(ρe·ue) = 1 - (ρu/(ρe·ue))
    W+ = (ρe·ue - ρ·u)/(ρw·uτ) = ρe+ue+ - ρ+u+
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    if not isinstance(u_tau,(float,np.floating)):
        raise ValueError('u_tau must be type float')
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Get/check rho_wall
    if rho_wall is None:
        rho_wall = rho[0]
    np.testing.assert_allclose(rho_wall, rho[0], rtol=1e-4)
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    Wplus = (rho_edge*u_edge - rho*u) / (rho_wall*u_tau) ## W+
    
    dRC = cumulative_trapezoid(y=Wplus, x=y, initial=0.)[j_edge] ## Δ = ∫W+dy
    
    return dRC

def calc_I2(y, u, u_tau, rho=None, j_edge=-1, u_edge=None, rho_edge=None, rho_wall=None, **kwargs):
    '''
    Second moment of the velocity defect
    I2 = ∫ (W+)^2 d(y/Δ) = ∫ (W+)^2 dη
    W+ = (ρe·ue - ρ·u)/(ρw·uτ) = ρe+ue+ - ρ+u+
    Δ  = ∫W+dy = ∫(ρe+ue+ - ρ+u+) dy
    -----
    Monkewitz Chauhan Nagib (2007) : https://doi.org/10.1063/1.2780196
    Nagib Chauhan Monkewitz (2007) : https://doi.org/10.1098/rsta.2006.1948
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    if not isinstance(u_tau,(float,np.floating)):
        raise ValueError('u_tau must be type float')
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Get/check rho_wall
    if rho_wall is None:
        rho_wall = rho[0]
    np.testing.assert_allclose(rho_wall, rho[0], rtol=1e-4)
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    ## W+
    Wplus = (rho_edge*u_edge - rho*u) / (rho_wall*u_tau)
    
    dRC = cumulative_trapezoid(y=Wplus, x=y, initial=0.)[j_edge] ## Δ = ∫W+dy
    
    ## I2 = ∫ (W+)^2 d(y/Δ) = ∫ (W+)^2 dη = (1/Δ) ∫ (W+)^2 dy
    I2_dRC = cumulative_trapezoid(y=Wplus**2, x=y, initial=0.)[j_edge]
    
    I2 = I2_dRC / dRC
    
    return I2

def calc_I3(y, u, u_tau, rho=None, j_edge=-1, u_edge=None, rho_edge=None, rho_wall=None, **kwargs):
    '''
    Third moment of the velocity defect
    -----
    I3 = ∫ (W+)^3 d(y/Δ) = ∫ (W+)^3 dη
    W+ = (ρe·ue - ρ·u)/(ρw·uτ) = ρe+ue+ - ρ+u+
    Δ  = ∫W+dy = ∫(ρe+ue+ - ρ+u+) dy
    '''
    check = kwargs.get('check',True)
    rtol  = kwargs.get('rtol',1e-4)
    
    if not isinstance(u_tau,(float,np.floating)):
        raise ValueError('u_tau must be type float')
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    if rho is None: ## Assume ρ=const.
        rho = np.ones_like(u)
    rho = np.asarray(rho)
    
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Get/check rho_wall
    if rho_wall is None:
        rho_wall = rho[0]
    np.testing.assert_allclose(rho_wall, rho[0], rtol=1e-4)
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Determine rho_edge
    if rho_edge is not None: ## rho_edge was passed
        rho_edge = float(rho_edge)
        if check:
            np.testing.assert_allclose(rho[j_edge], rho_edge, rtol=rtol)
    else:
        rho_edge = rho[j_edge]
    
    ## W+
    Wplus = (rho_edge*u_edge - rho*u) / (rho_wall*u_tau)
    
    dRC = cumulative_trapezoid(y=Wplus, x=y, initial=0.)[j_edge] ## Δ = ∫W+dy
    
    ## I3 = ∫ (W+)^3 d(y/Δ) = (1/Δ) ∫ (W+)^3 dy
    I3_dRC = cumulative_trapezoid(y=Wplus**3, x=y, initial=0.)[j_edge]
    
    I3 = I3_dRC / dRC
    
    return I3

# ======================================================================

def calc_wake_parameter_1d(yplus, uplus, dplus, uplus_delta=None, **kwargs):
    '''
    Calculate the Coles wake parameter Π (1D kernel)
    
    Π = (κ/2)·[u+(δ) - (1/κ)·ln(δ+) - B]
    
    Coles profile:
      u+ = (1/κ)·ln(y+) + B + (2Π/κ)·W(y/δ)
        at y=δ, W(y/δ)==1
    
    Within the scope of this function, δ is generic i.e. not necessarily δ99
    
    Refs:
    -----
    Coles (1956)            : https://doi.org/10.1017/S0022112056000135
    Pirozzoli (2004)        : https://doi.org/10.1063/1.1637604
    Smits & Dussauge (2006) : https://doi.org/10.1007/b137383
    Chauhan et al. (2009)   : https://doi.org/10.1088/0169-5983/41/2/021404
    Nagib et al. (2007)     : https://doi.org/10.1098/rsta.2006.1948
    '''
    
    ## Von Kármán constant (κ)
    k = kwargs.get('k',0.384)
    
    ## Log-law intercept (B) : u+ = (1/κ)·ln(y+) + B
    ## see Nagib et al. (2007)
    B = kwargs.get('B',4.173)
    
    interp_kind = kwargs.get('interp_kind','cubic') ## 'linear','cubic'
    
    ## Check input y+,u+
    if (yplus.ndim!=1):
        raise ValueError('yplus must be 1D')
    if (uplus.ndim!=1):
        raise ValueError('uplus must be 1D')
    if (uplus.shape[0]!=yplus.shape[0]):
        raise ValueError("u,y shapes don't match")
    if not np.all(np.diff(yplus) > 0): ## check (+) monotonicity
        raise ValueError("y must be monotonically increasing")
    
    ## Check input δ+ and optional input u+(δ)
    if not isinstance(dplus,(float,np.floating)):
        raise ValueError('dplus must be type float')
    if uplus_delta is not None and not isinstance(uplus_delta,(float,np.floating)):
        raise ValueError('uplus_delta must be type float')
    
    ## u_{log}^+(δ) : Extrapolated u^+(δ) of log-law
    uplus_delta_loglaw = (1/k)*np.log(dplus) + B
    
    ## u+(δ)
    uplus_delta_func = interp1d(yplus, uplus, kind=interp_kind, bounds_error=True)
    uplus_delta_sol  = uplus_delta_func(dplus)
    
    ## If 'uplus_delta' was supplied, perform consistency check
    if uplus_delta is not None:
        np.testing.assert_allclose(uplus_delta_sol, uplus_delta, rtol=1e-5)
        uplus_delta = uplus_delta_sol
    
    Π = (k/2)*( uplus_delta - uplus_delta_loglaw )
    
    return Π

def calc_profile_edge_1d(y, ddy_u, **kwargs):
    '''
    Determine the edge index of a 1D boundary-layer profile
    
    The edge is defined as the first location where |du/dy|<ϵ
    
    Note: |-ωz|<ϵ can be found (instead of |du/dy|<ϵ) by 
      passing -ωz as ddy_u
    
    Note: '+' is used in notation here, but since the ddy_u arg
      is automatically normalized by ddy_u[0], effectively any
      du/dy is transformed to pseudo '+' units.
    
    Parameters
    ----------
    y : np.ndarray
        1D wall-normal coordinate (units arbitrary)
    ddy_u : np.ndarray
        Precomputed du/dy
    
    Keyword Arguments
    -----------------
    epsilon : float, default=5e-5
        Edge-detection threshold for |du/dy| (or |ωz|)
    check_eps : bool, default=True
        Abort when no point satisfies |du/dy|<ϵ
    
    Returns
    -------
    y_edge : float
        Wall-normal location of the boundary-layer edge
    j_edge : int
        Index of boundary-layer edge
    '''
    
    epsilon   = kwargs.get('epsilon',5e-5)
    check_eps = kwargs.get('check_eps',True)
    
    ## Checks
    if not isinstance(y,np.ndarray):
        raise ValueError('y should be a numpy array')
    if (y.ndim!=1):
        raise ValueError
    if not isinstance(ddy_u,np.ndarray):
        raise ValueError
    if (ddy_u.ndim!=1):
        raise ValueError
    if (ddy_u.shape[0]!=y.shape[0]):
        raise ValueError
    
    ny = y.shape[0]
    
    ## !!! Normalize such that |du/dy|_w == 1 !!!
    ## This is required for ϵ to be consistent
    ddy_u = np.copy( ddy_u/ddy_u[0] )
    
    ## Static ϵ
    j_edge = ny-1
    for j in range(ny):
        if np.abs(ddy_u[j]) < epsilon: ## |d□/dy|<ϵ
            j_edge = j
            break
    
    # ## Variable ϵ
    # keep_going = True
    # while keep_going:
    #     j_edge = ny-1
    #     for j in range(ny):
    #         if np.abs(ddy_u[j]) < epsilon: ## |d□/dy|<ϵ
    #             j_edge = j
    #             break
    #     if j_edge==ny-1: ## Got to end, recalibrate ϵ & keep going
    #         epsilon *= 1.05
    #         msg = f'[WARNING] Recalibrating: ϵ={epsilon:0.3e}'
    #         #print(msg)
    #         tqdm.write(msg)
    #     else:
    #         keep_going = False
    
    if j_edge<3: ## Less than 3 points in profile
        raise ValueError('j_edge<3')
    if np.abs(ddy_u[j_edge])>=epsilon and check_eps:
        print('\n')
        print(f'[ERROR] j_edge={j_edge:d}')
        print(f'[ERROR] abs(ddy_u[{j_edge:d}])={np.abs(ddy_u[j_edge])}, ϵ={epsilon:0.3e}')
        print('\n')
        raise ValueError
    
    ## First point satisfying |d□/dy|<ϵ
    y_edge = float( y[j_edge] )
    
    if False: ## LEGACY: Find interpolated |d□/dy|==ϵ
        
        intrp_func = PchipInterpolator(y, ddy_u, axis=0, extrapolate=False)
        
        def __f_opt_edge_locator(y_test, intrp_func, epsilon):
            ddy_u_test = intrp_func(y_test)
            root = np.abs( ddy_u_test ) - epsilon
            return root
        
        sol = least_squares(
                    fun=__f_opt_edge_locator,
                    args=(intrp_func,epsilon,),
                    x0 = y[0] + 0.99*(y[j_edge]-y[0]),
                    xtol=1e-12,
                    ftol=1e-12,
                    gtol=1e-12,
                    method='trf',
                    bounds=(y[0], y[j_edge]),
                    )
        if not sol.success:
            raise ValueError
        if ( sol.x.shape[0] != 1 ):
            raise ValueError
        
        y_edge = float(sol.x[0])
        
        if ( y_edge > y[j_edge] ):
            raise ValueError
    
    ## Debug plot
    # import matplotlib.pyplot as plt
    # plt.close('all')
    # fig1 = plt.figure(figsize=(2*(16/9),2), dpi=300)
    # ax1 = plt.gca()
    # ax1.set_xscale('log', base=10)
    # ax1.plot(ddy_u, y, lw=0.8, )
    # #ax1.set_xlim(1e-30, 1e1)
    # ax1.axhline(y=y_edge, linestyle='dashed', c='gray', zorder=1, lw=0.5)
    # ax1.axvline(x=epsilon, linestyle='dashed', c='gray', zorder=1, lw=0.5)
    # fig1.tight_layout(pad=0.25)
    # plt.show()
    
    return y_edge, j_edge

def calc_d99_1d(y, u, j_edge=-1, u_edge=None, **kwargs):
    '''
    Determine δ99 location of 1D profile
    - y : 1D coordinate vector
    - u : some profile variable (streamwise velocity, pseudovelocity, etc.)
    - j_edge : (optional) edge index
    - u_edge : (optional) edge value
    '''
    interp_kind = kwargs.get('interp_kind','cubic')
    check = kwargs.get('check',True)
    rtol = kwargs.get('rtol',1e-4)
    
    y = np.asarray(y)
    u = np.asarray(u)
    
    _check_validity_yx(y,u)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    y_edge = y[j_edge]
    
    ## Determine u_edge
    if u_edge is not None: ## u_edge was passed
        u_edge = float(u_edge)
        if check:
            np.testing.assert_allclose(u[j_edge], u_edge, rtol=rtol)
    else:
        u_edge = u[j_edge]
    
    ## Index vs slice semantics
    if j_edge == -1:
        sl = slice(None) ## take everything
    else:
        sl = slice(j_edge+1) ## inclusive semantics
    
    ## Primary u(y) interpolation callable
    intrp_func = interp1d(
        x=y[sl],
        y=u[sl],
        kind=interp_kind,
        bounds_error=True,
        )
    
    ## Does the solution actually exist?
    if u[sl].max() < u_edge*0.99:
        print('\n')
        print(f'[ERROR] u.max()     = {u[sl].max():0.12f}')
        print(f'[ERROR] u_edge*0.99 = {u_edge*0.99:0.12f}')
        print('[ERROR] No solution exists: u.max() < u_edge*0.99')
        print('\n')
        raise RuntimeError
    
    ## Root function for δ99
    def __f_opt_d99_locator(y_test, intrp_func, u_edge):
        #root = np.abs( 0.99*u_edge - intrp_func(y_test) )
        root = 0.99*u_edge - intrp_func(y_test)
        return root
    
    ## Perform solve
    sol = least_squares(
            fun=__f_opt_d99_locator,
            args=(intrp_func,u_edge),
            x0=0.1*y_edge,
            xtol=1e-12,
            ftol=1e-12,
            gtol=1e-12,
            method='trf',
            bounds=(y.min(), y_edge),
            )
    if not sol.success:
        raise ValueError
    
    d99 = float(sol.x[0]) ## δ99
    
    if d99 > y_edge:
        raise ValueError('δ99 > y_edge')
    
    ## Assert u(δ99)=0.99·u_edge
    u99 = intrp_func(d99)
    np.testing.assert_allclose(0.99*u_edge, u99, rtol=1e-5)
    
    return d99

def calc_bl_integral_quantities_1d(
    y,
    u,
    rho,
    u_tau,
    d99,
    rho_edge,
    nu_edge,
    u_edge,
    rho_wall,
    nu_wall,
    j_edge=-1,
    **kwargs,
    ):
    '''
    For 1D profile, get [δ1=δ*, δ2=θ, Reθ, Reτ] etc.
    '''
    
    rtol = kwargs.get('rtol',1e-4)
    
    y = np.asarray(y)
    u = np.asarray(u)
    _check_validity_yx(y,u)
    _check_validity_yx(y,rho)
    n = y.shape[0]
    
    ## Check j_edge
    if not isinstance(j_edge,(int,np.integer)):
        raise ValueError("j_edge must be int")
    if j_edge>=n:
        raise ValueError("j_edge>=n")
    if j_edge==0:
        raise RuntimeError('j_edge==0')
    
    ## Assert 0D scalars
    for val in (u_tau, d99, rho_edge, nu_edge, u_edge, rho_wall, nu_wall):
        if not isinstance(val, (float,np.floating)):
            raise ValueError
    
    ## Consistency checks for edge quantities
    np.testing.assert_allclose(u_edge   , u[j_edge]   , rtol=rtol)
    np.testing.assert_allclose(rho_edge , rho[j_edge] , rtol=rtol)
    
    # === Compressible integrals (root names)
    
    d1 = calc_d1(
        y, u,
        rho=rho,
        j_edge=j_edge,
        u_edge=u_edge,
        rho_edge=rho_edge,
        )
    dstar = d1
    
    d2 = calc_d2(
        y, u,
        rho=rho,
        j_edge=j_edge,
        u_edge=u_edge,
        rho_edge=rho_edge,
        )
    theta = d2
    
    d3 = calc_d3(
        y, u,
        rho=rho,
        j_edge=j_edge,
        u_edge=u_edge,
        rho_edge=rho_edge,
        )
    
    dRC = calc_dRC(
        y, u,
        u_tau=u_tau,
        rho=rho,
        j_edge=j_edge,
        u_edge=u_edge,
        rho_edge=rho_edge,
        rho_wall=rho_wall,
        )
    
    # === Kinetic (u-only) integrals
    
    d1_k = calc_d1(
        y, u,
        rho=None,
        j_edge=j_edge,
        u_edge=u_edge,
        )
    dstar_k = d1_k
    
    d2_k = calc_d2(
        y, u,
        rho=None,
        j_edge=j_edge,
        u_edge=u_edge,
        )
    theta_k = d2_k
    
    d3_k = calc_d3(
        y, u,
        rho=None,
        j_edge=j_edge,
        u_edge=u_edge,
        )
    
    dRC_k = calc_dRC(
        y, u,
        u_tau=u_tau,
        rho=None,
        j_edge=j_edge,
        u_edge=u_edge,
        )
    
    ## Shape factors
    H12    = d1   / d2
    H12_k  = d1_k / d2_k
    H32    = d3   / d2
    H32_k  = d3_k / d2_k
    
    ## Reynolds numbers
    Re_tau   = d99   * u_tau  / nu_wall
    Re_theta = theta * u_edge / nu_edge
    Re_d99   = d99   * u_edge / nu_edge
    
    ## Dictionary to return
    dd = {
        'd1': d1,
        'd1_k': d1_k,
        'dstar': dstar,
        'dstar_k': dstar_k,
        
        'd2': d2,
        'd2_k': d2_k,
        'theta': theta,
        'theta_k': theta_k,
        
        'd3': d3,
        'd3_k': d3_k,
        
        'dRC': dRC,
        'dRC_k': dRC_k,
        
        'H12': H12,
        'H12_k': H12_k,
        'H32': H32,
        'H32_k': H32_k,
        
        'Re_tau': Re_tau,
        'Re_theta': Re_theta,
        'Re_d99': Re_d99,
        }
    
    return dd
