# -*- coding: utf-8 -*-
"""
Created on Tue Jan  6 10:23:49 2026

@author: S.T.Hwang
"""

# HYOTC/Equity/American.py
# -*- coding: utf-8 -*-

from __future__ import annotations

import numpy as np
from math import log, sqrt, exp, isfinite
from scipy.stats import norm, multivariate_normal
from scipy.optimize import brentq
import math


# ============================================================
# 0) Helpers: 입력/옵션 플래그
# ============================================================

def _opt_flag(option: str | None = None, is_call: bool | None = None) -> str:
    """
    내부 통일용: 'call'/'put' 반환
    - option="call"/"put" 우선
    - is_call=True/False도 지원
    """
    if option is not None:
        opt = option.lower().strip()
        if opt not in ("call", "put"):
            raise ValueError("option must be 'call' or 'put'")
        return opt
    if is_call is None:
        return "call"
    return "call" if bool(is_call) else "put"


def _assert_pos(name: str, x: float):
    if not (x > 0 and isfinite(x)):
        raise ValueError(f"{name} must be positive and finite. got {x}")


# ============================================================
# 1) Black–Scholes (European) price/delta
# ============================================================

def bs_price(S: float, K: float, T: float, r: float, q: float, sigma: float, option: str = "call") -> float:
    """
    Black-Scholes European option price with continuous dividend yield q.
    """
    option = _opt_flag(option=option)

    if T <= 0:
        intrinsic = max(S - K, 0.0) if option == "call" else max(K - S, 0.0)
        return intrinsic

    _assert_pos("S", S)
    _assert_pos("K", K)
    _assert_pos("sigma", sigma)

    vsqrt = sigma * sqrt(T)
    d1 = (log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / vsqrt
    d2 = d1 - vsqrt

    if option == "call":
        return S * exp(-q * T) * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    else:
        return K * exp(-r * T) * norm.cdf(-d2) - S * exp(-q * T) * norm.cdf(-d1)


def bs_delta(S: float, K: float, T: float, r: float, q: float, sigma: float, option: str = "call") -> float:
    """
    Black-Scholes European delta with continuous dividend yield q.
    """
    option = _opt_flag(option=option)

    if T <= 0:
        if option == "call":
            return 1.0 if S > K else 0.0
        else:
            return -1.0 if S < K else 0.0

    _assert_pos("S", S)
    _assert_pos("K", K)
    _assert_pos("sigma", sigma)

    d1 = (log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))

    if option == "call":
        return exp(-q * T) * norm.cdf(d1)
    else:
        return exp(-q * T) * (norm.cdf(d1) - 1.0)


# ============================================================
# 2) Barone-Adesi & Whaley (1987) Approximation
# ============================================================

def _baw_params(T: float, r: float, q: float, sigma: float):
    """
    BAW common parameters.
    b = r - q  (cost of carry)
    """
    b = r - q
    sig2 = sigma * sigma
    M = 2.0 * r / sig2
    N = 2.0 * b / sig2
    kappa = 1.0 - exp(-r * T)  # 1 - e^{-rT}
    return b, M, N, kappa


def _baw_q1_q2(T: float, r: float, q: float, sigma: float):
    """
    Exponents used in BAW.
    q2 (call) > 0, q1 (put) < 0
    """
    b, M, N, kappa = _baw_params(T, r, q, sigma)
    # 보호: r≈0이면 kappa≈0가 되어 발산 가능 → 작은 값 바닥
    kappa = max(kappa, 1e-12)

    sqrt_term = sqrt((N - 1.0) ** 2 + 4.0 * M / kappa)
    q2 = 0.5 * (-(N - 1.0) + sqrt_term)  # call exponent
    q1 = 0.5 * (-(N - 1.0) - sqrt_term)  # put exponent
    return q1, q2


def american_baw(S: float, K: float, T: float, r: float, q: float, sigma: float, option: str = "call") -> float:
    """
    American option price by Barone-Adesi & Whaley approximation.

    Notes:
    - Call with dividend (q>0) may have early exercise.
    - For non-dividend call (q=0), American call = European call (no early exercise).
    """
    option = _opt_flag(option=option)

    if T <= 0:
        return max(S - K, 0.0) if option == "call" else max(K - S, 0.0)

    _assert_pos("S", S)
    _assert_pos("K", K)
    _assert_pos("sigma", sigma)

    # Non-dividend call: no early exercise in BSM world
    if option == "call" and q <= 0.0:
        return bs_price(S, K, T, r, q, sigma, option="call")

    b, M, N, kappa = _baw_params(T, r, q, sigma)
    q1, q2 = _baw_q1_q2(T, r, q, sigma)

    # choose exponent and sign by option
    if option == "call":
        qn = q2
        # 초기 guess: K 근처에서 시작
        S_guess = max(K, 1e-8)
        # S* 찾기 방정식
        def f(Sstar: float) -> float:
            c = bs_price(Sstar, K, T, r, q, sigma, option="call")
            d1 = (log(Sstar / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
            A2 = (Sstar / qn) * (1.0 - exp((b - r) * T) * norm.cdf(d1))
            return (Sstar - K) - (c + A2)

        # Root bracket (실무 안전범위)
        lo = 1e-12
        hi = max(5.0 * K, 5.0 * S)
        # brentq가 실패하면 bracket 확장
        for _ in range(10):
            if f(lo) * f(hi) < 0:
                break
            hi *= 2.0

        S_star = brentq(f, lo, hi, maxiter=200)

        # Price
        if S >= S_star:
            return S - K
        c = bs_price(S, K, T, r, q, sigma, option="call")
        d1 = (log(S_star / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
        A2 = (S_star / qn) * (1.0 - exp((b - r) * T) * norm.cdf(d1))
        return c + A2 * (S / S_star) ** qn

    else:
        qn = q1  # negative
        def f(Sstar: float) -> float:
            p = bs_price(Sstar, K, T, r, q, sigma, option="put")
            d1 = (log(Sstar / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
            A1 = -(Sstar / qn) * (1.0 - exp((b - r) * T) * norm.cdf(-d1))
            return (K - Sstar) - (p + A1)

        lo = 1e-12
        hi = max(5.0 * K, 5.0 * S)
        for _ in range(10):
            if f(lo) * f(hi) < 0:
                break
            hi *= 2.0

        S_star = brentq(f, lo, hi, maxiter=200)

        if S <= S_star:
            return K - S
        p = bs_price(S, K, T, r, q, sigma, option="put")
        d1 = (log(S_star / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt(T))
        A1 = -(S_star / qn) * (1.0 - exp((b - r) * T) * norm.cdf(-d1))
        return p + A1 * (S / S_star) ** qn
    
    
# ============================================================
# BS2002 (2002)
# ============================================================

# 이변량 정규분포 CDF
def _M(a, b, rho):
    cov = [[1.0, rho], [rho, 1.0]]
    return multivariate_normal.cdf([a, b], mean=[0.0, 0.0], cov=cov)


def phi_bs2002(S, T, gamma, H, I, r, b, sigma):
    if T <= 0 or sigma <= 0:
        return 0.0

    sig2 = sigma * sigma
    vs = sigma * math.sqrt(T)

    lam = (-r + gamma * b + 0.5 * gamma * (gamma - 1.0) * sig2)
    kappa = 2.0 * b / sig2 + (2.0 * gamma - 1.0)

    d = (math.log(S / H) + (b + (gamma - 0.5) * sig2) * T) / vs
    d2 = (math.log((I * I) / (S * H)) + (b + (gamma - 0.5) * sig2) * T) / vs

    return math.exp(lam*T) * (S ** gamma) * (norm.cdf(-d) - (I / S) ** kappa * norm.cdf(-d2))



# -----------------------------
# 3) Ψ (BS2002; 이미지의 가격식에 등장)
#    표준 구현 형태(Φ 정의가 N(-d)인 경우에도 -e,-f 형태로 일관되게 작성)
# -----------------------------
def psi_bs2002(S, T, gamma, H, I2, I1, t1, r, b, sigma):

    if T <= 0 or t1 <= 0 or sigma <= 0:
        return 0.0

    sig2 = sigma * sigma
    vsT = sigma * math.sqrt(T)
    vst1 = sigma * math.sqrt(t1)

    # λT 
    lamT = (-r + gamma * b + 0.5 * gamma * (gamma - 1.0) * sig2) * T

    # κ
    kappa = 2.0 * b / sig2 + (2.0 * gamma - 1.0)

    rho = math.sqrt(t1 / T)

    drift_T  = (b + (gamma - 0.5) * sig2) * T
    drift_t1 = (b + (gamma - 0.5) * sig2) * t1

    # ----- e_i : t1 기반 (I1, I2, S)
    e1 = (math.log(S / I1) + drift_t1) / vst1
    e2 = (math.log((I2 * I2) / (S * I1)) + drift_t1) / vst1
    e3 = (math.log(S / I1) - drift_t1) / vst1
    e4 = (math.log((I2 * I2) / (S * I1)) - drift_t1) / vst1

    # ----- f_i : T 기반 (H, I1, I2, S)
    f1 = (math.log(S / H) + drift_T) / vsT
    f2 = (math.log((I2 * I2) / (S * H)) + drift_T) / vsT
    f3 = (math.log((I1 * I1) / (S * H)) + drift_T) / vsT
    f4 = (math.log((S * I1 * I1) / (H * I2 * I2)) + drift_T) / vsT

    term = (
        _M(-e1, -f1,  rho)
        - (I2 / S) ** kappa * _M(-e2, -f2,  rho)
        - (I1 / S) ** kappa * _M(-e3, -f3, -rho)
        + (I1 / I2) ** kappa * _M(-e4, -f4, -rho)
    )

    return math.exp(lamT) * (S ** gamma) * term

# -----------------------------
# BS(2002) American Call 
# -----------------------------
def american_call_bs2002(S, K, T, r, q, sigma):
    if T <= 0:
        return max(S - K, 0.0)

    b = r - q  # cost of carry

    # 무배당(q=0) => American Call = European Call (B0=r/q 발산 방지)
    if abs(q) < 1e-12:
        return bs_price(S, K, T, r, q, sigma, "call")

    if sigma <= 0:
        immediate = max(S - K, 0.0)
        ST = S * math.exp((r - q) * T)
        hold = math.exp(-r * T) * max(ST - K, 0.0)
        return max(immediate, hold)

    sig2 = sigma * sigma

    # beta
    beta = (0.5 - b / sig2) + math.sqrt((b / sig2 - 0.5) ** 2 + 2.0 * r / sig2)
    if abs(beta - 1.0) < 1e-12:
        return bs_price(S, K, T, r, q, sigma, "call")

    # 트리거 I1, I2 계산(표준 BS2002 설정)
    B_inf = (beta / (beta - 1.0)) * K
    # r-b = q 이므로 q가 아주 작으면 불안정 -> 위에서 q=0 방어
    B0 = max(K, (r / (r - b)) * K)

    t1 = 0.5 * (math.sqrt(5.0) - 1.0) * T  # BS2002 추천값

    h1 = -(b*t1 + 2.0*sigma*math.sqrt(t1)) * (K*K / ((B_inf - B0)*B0))
    h2 = -(b*T  + 2.0*sigma*math.sqrt(T )) * (K*K / ((B_inf - B0)*B0))

    I1 = B0 + (B_inf - B0) * (1.0 - math.exp(h1))
    I2 = B0 + (B_inf - B0) * (1.0 - math.exp(h2))

    # alpha1, alpha2
    alpha1 = (I1 - K) * (I1 ** (-beta))
    alpha2 = (I2 - K) * (I2 ** (-beta))

    # 콜옵션 가격식 (Φ는 t1에서 평가 / Ψ는 (S,T,...) 형태)
    C = (
        alpha2 * (S ** beta)
        - alpha2 * phi_bs2002(S, t1, beta, I2, I2, r, b, sigma)
        + phi_bs2002(S, t1, 1.0,  I2, I2, r, b, sigma)
        - phi_bs2002(S, t1, 1.0,  I1, I2, r, b, sigma)
        - K * phi_bs2002(S, t1, 0.0, I2, I2, r, b, sigma)
        + K * phi_bs2002(S, t1, 0.0, I1, I2, r, b, sigma)
        + alpha1 * phi_bs2002(S, t1, beta, I1, I2, r, b, sigma)
        - alpha1 * psi_bs2002(S, T,  beta, I1, I2, I1, t1, r, b, sigma)
        + psi_bs2002(S, T,  1.0,  I1, I2, I1, t1, r, b, sigma)
        - psi_bs2002(S, T,  1.0,  K,  I2, I1, t1, r, b, sigma)
        - K * psi_bs2002(S, T,  0.0, I1, I2, I1, t1, r, b, sigma)
        + K * psi_bs2002(S, T,  0.0, K,  I2, I1, t1, r, b, sigma)
    )

    # 안전장치(수치적으로 말도 안되게 낮게 나오는 경우 방지)
    return max(C, bs_price(S, K, T, r, q, sigma, "call"))

# -----------------------------
# American Put: duality (swap S<->K, r<->q)
# -----------------------------
def american_put_bs2002(S, K, T, r, q, sigma):
    return american_call_bs2002(S=K, K=S, T=T, r=q, q=r, sigma=sigma)