#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 18 14:45:53 2021

@author: carl
"""

import numpy as np
import scipy
import sklearn
import sklearn.metrics
import time

def simplisma(d, nr, f):
    """
    The SIMPLISMA algorithm for finding a set of 'pure' spectra to serve
    as starting point for MCR-ALS etc.
    Reference Matlab Code:
        J. Jaumot, R. Gargallo, A. de Juan, R. Tauler,
        Chemometrics and Intelligent Laboratoty Systems, 76 (2005) 101-110

    Parameters
    ----------
    d : array(nspectra, nwavenums)
        input spectra.
    nr : int
        number of output components.
    f : float
        noise threshold.

    Returns
    -------
    spout: array(nr, nspectra)
        concentration profiles of 'purest' spectra.
    imp : array(nr, dtype=int)
        indexes of the 'purest' spectra.
    """

    nrow = d.shape[0]
    ncol = d.shape[1]
    s = d.std(axis=0)
    m = d.mean(axis=0)
    mf = m + m.max() * f
    p = s / mf

    # First Pure Spectral/Concentration profile
    imp = np.empty(nr, dtype=int)
    imp[0] = p.argmax()

    #Calculation of correlation matrix
    l2 = s**2 + mf**2
    dl = d / np.sqrt(l2)
    c = (dl.T @ dl) / nrow

    #calculation of the first weight
    w = (s**2 + m**2) / l2
    p *= w
    #calculation of following weights
    dm = np.zeros((nr+1, nr+1))
    for i in range(1, nr):
        dm[1:i+1, 1:i+1] = c[imp[:i], :][:, imp[:i]]
        for j in range(ncol):
            dm[0, 0] = c[j, j]
            dm[0, 1:i+1] = c[j, imp[:i]]
            dm[1:i+1, 0] = c[imp[:i], j]
            w[j] = np.linalg.det(dm[0:i+1, 0:i+1])
        imp[i] = (p * w).argmax()

    ss = d[:,imp]
    spout = ss / np.sqrt(np.sum(ss**2, axis=0))
    return spout.T, imp

# import pymcr


# def pymcr_als(sp, initial_components, maxiters, reltol,
#             callback_iter):

#     mcr = pymcr.mcr.McrAR(max_iter=maxiters,
#                           tol_err_change=reltol,
#                           tol_increase=1., tol_n_increase=10,
#                           tol_n_above_min=30)
#     mcr.fit(sp, ST=initial_components, post_iter_fcn=callback_iter)

#     return mcr.n_iter, mcr.C_opt_.T, mcr.ST_opt_, np.asarray(mcr.err)


def mcr_als(sp, initial_components, maxiters, nonnegative=(True, True),
            tol_abs_error=0, tol_rel_improv=None, tol_ups_after_best=None,
            maxtime=None, callback=None, acceleration=None,
            return_time=False, **kwargs):
    """
    Perform MCR-ALS nonnegative matrix decomposition on the matrix sp

    Parameters
    ----------
    sp : array(nsamples, nfeatures)
        Spectra to be decomposed.
    initial_components : array(ncomponents, nfeatures)
        Initial concentrations.
    maxiters : int
        Maximum number of iterations.
    nonnegative : pair of bool
        True if (initial, other) components must be non-negative
    tol_abs_error : float, optional
        Error target (mean square error).
    tol_rel_improv : float, optional
        Stop when relative improvement is less than this over 10 iterations.
    tol_ups_after_best : int, optional
        Stop after error going net up this many times since best error.
    maxtime : float, optional
        Stop after this many seconds of process time have elapsed
    callback : func(it : int, err : float, A : array, B : array)
        Callback for every iteration.
    acceleration : str
        None, 'Anderson', 'AdaptiveOverstep'.
        Use one of two stabilized acceleration schemes.
        Anderson acceleration operates on whole iterations (A+B updates),
        mixing earlier directions to step towards the fixed point. This
        implementation temporarily falls back to basic updates if those
        would be much better.
        The AdaptiveOverstep algorithm attempts to gradually modify the
        step length, picking the best of a shorter or longer step.
    m : int, >1
        For Anderson acceleration: the number of earlier steps to consider.
    return_time : bool
        Measure and return process_time at each iteration.

    Returns
    -------
    A : array(ncomponents, nfeatures)
        Spectra (at lowest error)
    B : array(ncomponents, nsamples)
        Concentrations at lowest error
    error : list(float)
        Mean square error at every iteration
    process_time : list(float)
        Time relative start at each iteration, only if return_time is True.
    """
    nrow, ncol = np.shape(sp)
    nr = initial_components.shape[0]
    A = initial_components.T.copy()
    B = np.empty((nr, nrow))
    errors = []
    errorbest = None # Avoid spurious warning
    prevA, prevB = (None, None)

    unknown_args = kwargs.keys() - {'m', 'aosettings'}
    if unknown_args:
        raise TypeError('Unknown arguments: {}'.format(unknown_args))

    if acceleration == 'AndersonOld':
        ason_m = kwargs.get('m', 2)
        ason_g = None
        ason_G = []
        ason_X = []
    elif acceleration == 'Anderson':
        ason_m = kwargs.get('m', 2)
        ason_g = None
        ason_G = []
        ason_X = []
    elif acceleration:
        raise ValueError("acceleration must be None or 'Anderson'")

    starttime = time.process_time()
    if return_time:
        times = []
    tol_rel_iters = 10

    aerror = berror = saveA = 0 # Avoid warnings
    for it in range(maxiters):
        # print('strides', it, A.strides, B.strides)
        # Update B
        while(True):
            prevB = B
            if nonnegative[1]:
                error = 0
                B = np.empty_like(B)
                for i in range(nrow):
                    B[:, i], res = scipy.optimize.nnls(A, sp[i, :])
                    error = error + res * res
            else:
                B, res, _, _ = np.linalg.lstsq(A, sp.T, rcond=-1)
                error = res.sum()

            if acceleration == 'Anderson' and len(ason_X) > 1 \
                and error > aerror:
                print('restart', it, error-aerror, error-berror)
                print('gamma', gamma, np.linalg.norm(ason_g))
                ason_X = []
                ason_G = []
                A = saveA
            else:
                if acceleration == 'Anderson' and len(ason_X) < 1:
                    print('Bstep', it, error-aerror, error-berror)
                break
        berror = error

        prevA = A
        if nonnegative[0]:
            error = 0
            A = np.empty_like(A)
            for i in range(ncol):
                A[i, :], res = scipy.optimize.nnls(B.T, sp[:, i])
                error = error + res * res
        else:
            A, res, _, _ = np.linalg.lstsq(B.T, sp, rcond=-1)
            A = A.T
            error = res.sum()

        if acceleration == 'Anderson':
            aerror = error
            prevg = ason_g
            ason_g = (A - prevA).flatten()
            if len(ason_X) < 1:
                ason_X.append(ason_g)
            else:
                ason_G.append(ason_g - prevg)
                while(len(ason_G) > ason_m):
                    ason_G.pop(0)
                    ason_X.pop(0)
                Garr = np.asarray(ason_G)
                try:
                    gamma = np.linalg.lstsq(Garr.T, ason_g, rcond=-1)[0]
                    # print('gamma', gamma, np.linalg.norm(ason_g))
                except np.linalg.LinAlgError:
                    print('lstsq failed to converge; restart at iter %d' % it)
                    print('nans', np.isnan(Garr).sum(), np.isnan(ason_g).sum())
                    ason_X = []
                    ason_G = []
                else:
                    dx = ason_g - gamma @ (np.asarray(ason_X) + Garr)
                    ason_X.append(dx)
                    saveA = A
                    # A = prevA + dx.reshape(A.shape)
                    if nonnegative[0]:
                        A = np.maximum(0, A)

        error = error / sp.size

        # Anderson
        # A0 -> B0   errb0
        # B0 -> A1   erra1:E  A1-A0: X0,g0
        # A1 -> B1   errb1
        # B1 -> A2   erra2:E  A2-A1: g1  g1-g0: G0   g1=v0G: v0
        #            g1-v0(X+G): X1   A1+X1: A'2
        # A'2 -> B2  errb2  if errb2>erra2:  XG=[]  A2 -> B2   (seed??)
        # B2 -> A3   erra3:E  A3-A2: g2  g2-g1: G1   g2=v1G: v1
        #            g2-v1(X+G): X2   A2+X2: A'3
        # A'3 -> B3  errb3  if errb3>erra3:  XG=[]  A3 -> B3   (seed??)

        if acceleration == 'AndersonOld' and it > 2:
            prevg = ason_g
            ason_g = np.empty(A.size + B.size)
            ason_g[:A.size] = (A - prevA).flatten()
            ason_g[A.size:] = (B - prevB).flatten()
            if len(ason_X) < 1:
                ason_X.append(ason_g)
            else:
                ason_G.append(ason_g - prevg)
                while(len(ason_G) > ason_m):
                    ason_G.pop(0)
                    ason_X.pop(0)
                Garr = np.asarray(ason_G)
                try:
                    gamma = np.linalg.lstsq(Garr.T, ason_g, rcond=-1)[0]
                except np.linalg.LinAlgError:
                    print('lstsq failed to converge; restart at iter %d' % it)
                    print('nans', np.isnan(Garr).sum(), np.isnan(ason_g).sum())
                    ason_X = []
                    ason_G = []
                else:
                    # print('gamma', gamma, np.linalg.norm(ason_g))
                    xstep = ason_g - gamma @ (np.asarray(ason_X) + Garr)
                    ason_X.append(xstep)
                    nA = prevA + xstep[:A.size].reshape(A.shape)
                    if nonnegative[0]:
                        nA = np.maximum(0, nA)
                    nB = prevB + xstep[A.size:].reshape(B.shape)
                    if nonnegative[1]:
                        nB = np.maximum(0, nB)
                    nerror = np.linalg.norm(sp - nB.T @ nA.T)**2 / sp.size
                    # Reject changes that are much worse than the basic step
                    de = error - errors[-1]
                    nde = nerror - errors[-1]
                    if nde > .5 * de or (de > 0 and nde > 2 * de):
                        ason_X = []
                        ason_G = []
                        print('aold restart',it)
                    else:
                        A, B, error = (nA, nB, nerror)


        curtime = time.process_time() - starttime
        if return_time:
            times.append(curtime)
        errors.append(error)
        if not it or error < errorbest:
            errorbest = error
            Abest = A
            Bbest = B
            netups = 0
        if it:
            if error < tol_abs_error:
                break
            if tol_rel_improv and it > tol_rel_iters:
                emax = max(errors[-tol_rel_iters-1:-2])
                if (emax - errors[-1]) * tol_rel_iters <= \
                    tol_rel_improv * emax:
                    break
            if tol_ups_after_best is not None:
                if error < errors[-2]:
                    netups = max(0, netups - 1)
                else:
                    netups = netups + 1
                    if netups > tol_ups_after_best:
                        break
        if it and maxtime and curtime >= maxtime:
            break
        if callback is not None:
            callback(it, errors, A.T, B)

    if return_time:
        return Abest.T, Bbest, errors, times
    return Abest.T, Bbest, errors

