#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - corr
# ==========================================
#
#
#
"""

import traceback
import numpy as np
import copy
import re

from .. import calc
from .sample import Sample
from . basic import validate_params


# =======================
# Corr Blank
# =======================
def corr_blank(sample: Sample):
    """Blank Correction"""
    try:
        params_to_check = {
            'unknown intercepts': {'data': sample.SampleIntercept[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            'blank intercepts': {'data': sample.BlankIntercept[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            'gain factors': {'data': sample.TotalParam[126:136], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    blank_corrected = np.zeros([10, sample.Info.experiment.step_num])
    try:
        for i in range(5):
            b, sb = np.array(sample.BlankIntercept[i * 2: i * 2 + 2])
            u, su = np.array(sample.SampleIntercept[i * 2: i * 2 + 2])
            f, sf = np.array(sample.TotalParam[126 + i * 2: 128 + i * 2])  # gain factors
            sf = f * sf / 100  # to absolute errors
            u, su = np.array(calc.corr.gain(u, su, f, sf))  # unknown intercepts gain corrected
            _b, _sb = np.array(calc.corr.gain(b, sb, f, sf))  # balnk intercepts gain corrected
            apply_gain_to_blank = np.array(sample.TotalParam[111], dtype=bool)
            b[~apply_gain_to_blank] = _b[~apply_gain_to_blank]
            sb[~apply_gain_to_blank] = _sb[~apply_gain_to_blank]
            blank_corrected[i * 2:2 + i * 2] = calc.corr.blank(u, su, b, sb)
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError(f'Blank correction error: {str(e)}')
    for i in range(0, 10, 2):
        blank_corrected[i] = [blank_corrected[i][index] if sample.TotalParam[102][index] else j for index, j in enumerate(sample.SampleIntercept[i])]
        blank_corrected[i + 1] = [blank_corrected[i + 1][index] if sample.TotalParam[102][index] else j for index, j in enumerate(sample.SampleIntercept[i + 1])]
    sample.BlankCorrected = blank_corrected


# =======================
# Mass Discrimination
# =======================
def corr_massdiscr(sample: Sample):
    """Mass Discrimination Correction"""
    try:
        params_to_check = {
            'blank corrected': {'data': sample.BlankCorrected[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            'masses': [
                {'data': sample.TotalParam[71:81:2], 'dtype': float, 'func': lambda x: x > 0, 'class': 'k2', },
                {'data': sample.TotalParam[72:81:2], 'dtype': float, 'class': 'k2', },
            ],
            'MDF values': {'data': sample.TotalParam[69:71], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            'mass discrimination correction method': {
                'data': sample.TotalParam[100], 'dtype': str, 'func': lambda x: str(x).lower()[0] in ['l', 'e', 'p'], 'class': 'k4',
            },
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    corrMassdiscr = sample.TotalParam[103][0]
    if not corrMassdiscr:
        sample.MassDiscrCorrected = copy.deepcopy(sample.BlankCorrected)
        return
    MASS = sample.TotalParam[71:81]
    mdf_corrected = np.zeros([10, sample.Info.experiment.step_num])
    try:
        for i in range(5):
            if len(sample.BlankCorrected[i * 2:2 + i * 2]) == 0:
                raise ValueError("sample.BlankCorrected is empty.")
            mdf_corrected[i * 2:2 + i * 2] = calc.corr.discr(
                *sample.BlankCorrected[i * 2:2 + i * 2],
                *sample.TotalParam[69:71], m=MASS[i * 2], m40=MASS[8], isRelative=True,
                method=sample.TotalParam[100])
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError(f'Mass discrimination correction error: {str(e)}')
    sample.MassDiscrCorrected = copy.deepcopy(mdf_corrected)


# =======================
# Decay correction
# =======================
def corr_decay(sample: Sample):
    """ Ar37 and Ar39 Decay Correction
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar37': {'data': sample.MassDiscrCorrected[2:4], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            'λAr37': {'data': sample.TotalParam[44:46], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            'Ar39': {'data': sample.MassDiscrCorrected[6:8], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            'λAr39': {'data': sample.TotalParam[42:44], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
            'irradiation cycles': [
                {'data': sample.TotalParam[27], 'dtype': str, 'func': lambda x: all(
                    [len(re.findall(r"\d+", item)) >= 5 for item in list(filter(None, re.split(r'[DS]', x)))[::2]]), 'class': 'k5', },
                {'data': sample.TotalParam[27], 'dtype': str, 'func': lambda x: all(
                    [isinstance(float(item), float) for item in list(filter(None, re.split(r'[DS]', x)))[1::2]]), 'class': 'k5', },
            ],
            'experiment datetime': {'data': sample.TotalParam[31], 'dtype': str, 'func': lambda x: len(re.findall(r"\d+", x)) >= 5, 'class': 'k6', },
            # 'apply Ar37 decay': {'data': sample.TotalParam[104], 'dtype': bool},
            # 'apply Ar39 decay': {'data': sample.TotalParam[105], 'dtype': bool},
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    decay_corrected = np.zeros([10, sample.Info.experiment.step_num])
    try:
        irradiation_cycles = [list(filter(None, re.split(r'[DS]', each_step))) for each_step in sample.TotalParam[27]]
        t1 = [re.findall(r"\d+", i) for i in sample.TotalParam[31]]  # t1: experiment time
        t2, t3 = [], []  # t2: irradiation time, t3: irradiation duration
        for each_step in irradiation_cycles:
            t2.append([re.findall(r"\d+", item) for item in each_step[::2]])
            t3.append([item for item in each_step[1::2]])
        decay_corrected[2:4] = calc.corr.decay(
            *sample.MassDiscrCorrected[2:4], t1, t2, t3, *sample.TotalParam[44:46], isRelative=True)
        decay_corrected[6:8] = calc.corr.decay(
            *sample.MassDiscrCorrected[6:8], t1, t2, t3, *sample.TotalParam[42:44], isRelative=True)
    except Exception as e:
        print(traceback.format_exc())
        raise ValueError(f'Decay correction error: {str(e)}')

    corrDecay37 = sample.TotalParam[104]
    corrDecay39 = sample.TotalParam[105]
    sample.CorrectedValues = copy.deepcopy(sample.MassDiscrCorrected)
    for idx in range(sample.Info.experiment.step_num):
        if corrDecay37[idx]:
            sample.CorrectedValues[2][idx] = decay_corrected[2][idx]
            sample.CorrectedValues[3][idx] = decay_corrected[3][idx]
        if corrDecay39[idx]:
            sample.CorrectedValues[6][idx] = decay_corrected[6][idx]
            sample.CorrectedValues[7][idx] = decay_corrected[7][idx]

    data = np.array(sample.CorrectedValues)
    data[1:10:2] = data[1:10:2] = np.abs(np.divide(data[1:10:2], data[0:10:2])) * 100
    sample.PublishValues[0:10] = copy.deepcopy(data.tolist())


# =======================
# Degas Calcium derived 37Ar 36Ar 38Ar 39Ar
# =======================
def calc_degas_ca(sample: Sample):
    """ Degas Pattern for Ca
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar37Ca': {'data': sample.TotalParam[106], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            '36/37Ca': {'data': sample.TotalParam[12:14], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            '38/37Ca': {'data': sample.TotalParam[10:12], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            '39/37Ca': {'data': sample.TotalParam[8:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
            # 'apply Ca degas': {'data': sample.TotalParam[106], 'dtype': bool},
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    set_negative_zero = sample.TotalParam[101]
    corrDegasCa = sample.TotalParam[106]
    ar37ca = copy.deepcopy(sample.CorrectedValues[2:4])
    ar37ca[0] = [0 if val < 0 and set_negative_zero[i] else val for i, val in enumerate(ar37ca[0])]
    ar39ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[8:10], isRelative=True)
    ar38ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[10:12], isRelative=True)
    ar36ca = calc.arr.mul_factor(ar37ca, sample.TotalParam[12:14], isRelative=True)
    sample.DegasValues[8:10] = copy.deepcopy(ar37ca)  # 37Ca
    sample.DegasValues[ 4] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar36ca[0])]  # 36Ca
    sample.DegasValues[ 5] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar36ca[1])]
    sample.DegasValues[18] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar38ca[0])]  # 38Ca
    sample.DegasValues[19] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar38ca[1])]
    sample.DegasValues[22] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar39ca[0])]  # 39Ca
    sample.DegasValues[23] = [val if corrDegasCa[idx] else 0 for idx, val in enumerate(ar39ca[1])]


# =======================
# Degas Potassium derived 39Ar 38Ar 40Ar
# =======================
def calc_degas_k(sample: Sample):
    """ Degas Pattern for K
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar39': {'data': sample.CorrectedValues[6:8], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            'Ar39Ca': {'data': sample.DegasValues[22:24], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            '38/39K': {'data': sample.TotalParam[16:18], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            '40/39K': {'data': sample.TotalParam[14:16], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
            # 'apply K degas': {'data': sample.TotalParam[107], 'dtype': bool},
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    corrDecasK = sample.TotalParam[107]
    set_negative_zero = sample.TotalParam[101]
    ar39k = calc.arr.sub(sample.CorrectedValues[6:8], sample.DegasValues[22:24])
    ar39k[0] = [0 if val < 0 and set_negative_zero[idx] else val for idx, val in enumerate(ar39k[0])]
    ar40k = calc.arr.mul_factor(ar39k, sample.TotalParam[14:16], isRelative=True)
    ar38k = calc.arr.mul_factor(ar39k, sample.TotalParam[16:18], isRelative=True)

    sample.DegasValues[20:22] = copy.deepcopy(ar39k)
    sample.DegasValues[16] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar38k[0])]
    sample.DegasValues[17] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar38k[1])]
    sample.DegasValues[30] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar40k[0])]
    sample.DegasValues[31] = [val if corrDecasK[idx] else 0 for idx, val in enumerate(ar40k[1])]


# =======================
# Degas Chlorine derived 36Ar 38Ar
# =======================
def calc_degas_cl(sample: Sample):
    """ Degas Pattern for Cl
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar36': [
                {'data': sample.CorrectedValues[0:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                {'data': sample.CorrectedValues[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                {'data': sample.DegasValues[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            ],
            'Ar38': [
                {'data': sample.DegasValues[16:18], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
                {'data': sample.DegasValues[18:20], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            ],
            '38/36t': {'data': sample.TotalParam[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            '36/38Cl productivity': {'data': sample.TotalParam[56:58], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
            'λCl36': {'data': sample.TotalParam[46:48], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k5', },
            'standing time': {'data': sample.TotalParam[32], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k6', },
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    n = sample.Info.experiment.step_num
    corrDecasCl = sample.TotalParam[108]
    decay_const = sample.TotalParam[46:48]
    cl36_cl38_p = sample.TotalParam[56:58]
    ar38ar36 = sample.TotalParam[4:6]
    stand_time_year = sample.TotalParam[32]
    set_negative_zero = sample.TotalParam[101]
    # ============
    decay_const[1] = [decay_const[0][i] * decay_const[1][i] / 100 for i in
                      range(len(decay_const[0]))]  # convert to absolute error
    cl36_cl38_p[1] = [cl36_cl38_p[0][i] * cl36_cl38_p[1][i] / 100 for i in
                      range(len(cl36_cl38_p[0]))]  # convert to absolute error
    ar38ar36[1] = [ar38ar36[0][i] * ar38ar36[1][i] / 100 for i in range(len(ar38ar36[0]))] # convert to absolute error
    # ============
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
    # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl
    ar38acl = calc.arr.sub(calc.arr.sub(
        sample.CorrectedValues[4:6], sample.DegasValues[16:18]), sample.DegasValues[18:20])
    for index, item in enumerate(ar36acl[0]):
        if set_negative_zero[index]:
            if item < 0:
                ar36acl[0][index] = 0
            if ar38acl[0][index] < 0:
                ar38acl[0][index] = 0
    # 36ArCl
    ar36cl = [[], []]
    # 38ArCl
    ar38cl = [[], []]
    for i in range(n):

        if not corrDecasCl[i]:
            v1 = s1 = v2 = s2 = 0
        else:
            vDecay = cl36_cl38_p[0][i] * (1 - np.exp(-1 * decay_const[0][i] * stand_time_year[i]))
            sDecay = pow(
                (cl36_cl38_p[1][i] * (1 - np.exp(-1 * decay_const[0][i] * stand_time_year[i]))) ** 2 +
                (cl36_cl38_p[0][i] * stand_time_year[i] * (np.exp(-1 * decay_const[0][i] * stand_time_year[i])) *
                 decay_const[1][i]) ** 2, 0.5)
            sDecay = calc.err.div((1, 0), (vDecay, sDecay))
            vDecay = 1 / vDecay

            a1 = sample.CorrectedValues[0][i]; s1 = sample.CorrectedValues[1][i]
            a2 = sample.DegasValues[4][i]; s2 = sample.DegasValues[5][i];
            a3 =  sample.DegasValues[16][i]; s3 = sample.DegasValues[17][i]
            a4 =  sample.DegasValues[18][i]; s4 = sample.DegasValues[19][i]
            a5 =  sample.CorrectedValues[4][i]; s5 = sample.CorrectedValues[5][i]
            a6 = vDecay; s6 = sDecay
            a7 = ar38ar36[0][i]; s7 = ar38ar36[1][i]

            d1 = 1 / (1 - a6 / a7)
            d2 = - 1 / (1 - a6 / a7)
            d3 = 1 / (a7 - a6)
            d4 = 1 / (a7 - a6)
            d5 = - 1 / (a7 - a6)
            d6 = (a1 - a2 + (a3 + a4) / a7 - a5 / a7) / a7 / (1 - a6 / a7) ** 2
            d7 = -(a1 - a2) * (a6) / (a7 - a6) ** 2 - (a3 + a4 - a5) / (a7 - a6) ** 2

            v1 = (a1 - a2 + (a3 + a4 - a5) / a7) / (1 - a6 / a7)
            s1 = (d1**2*s1**2 + d2**2*s2**2 + d3**2*s3**2 + d4**2*s4**2+ d5**2*s5**2 + d6**2*s6**2 + d7**2*s7**2) ** .5
            s2 = calc.err.mul((v1, s1), (a6, s6))
            v1 = 0 if (ar36acl[0][i] - v1 < 0 or v1 < 0) and set_negative_zero[i] else v1
            v2 = v1 * a6

        # Note: Ar36Cl uncertainty is differen with ArArCALC. All calculation was conducted separately considering they are independent
        # s1 = calc.err.div((a1 - a2 + (a3 + a4) / a7 - a5 / a7, calc.err.add(s1, s2, calc.err.div((a3 + a4, calc.err.add(s3, s4)), (a7, s7)), calc.err.div((a5, s5), (a7, s7)))), (1 - a6 / a7, calc.err.div((a6, s6), (a7, s7))))

        ar36cl[0].append(v1); ar36cl[1].append(s1)
        ar38cl[0].append(v2); ar38cl[1].append(s2)

    sample.DegasValues[6:8] = copy.deepcopy(ar36cl)
    sample.DegasValues[10:12] = copy.deepcopy(ar38cl)


# =======================
# Degas atmospheric 36Ar 38Ar 40Ar
# =======================
def calc_degas_atm(sample: Sample):
    """ Degas for Atmospheric Gas
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar36': [
                {'data': sample.CorrectedValues[0:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                {'data': sample.DegasValues[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                {'data': sample.DegasValues[6:8], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            ],
            '38/36t': {'data': sample.TotalParam[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            '40/36t': {'data': sample.TotalParam[0:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
            # 'apply atm degas': {'data': sample.TotalParam[109], 'dtype': bool},
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    corrDecasAtm = sample.TotalParam[109]
    set_negative_zero = sample.TotalParam[101]
    # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl
    ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
    ar36acl[0] = [0 if val < 0 and set_negative_zero[idx] else val for idx, val in enumerate(ar36acl[0])]
    # 36ArAir
    ar36a = calc.arr.sub(ar36acl, sample.DegasValues[6:8])
    # If ar36acl - ar36cl < 0, let ar36a = ar36 - ar36ca
    ar36a[0] = [ar36acl[index] if item < 0 and set_negative_zero[index] else item for index, item in enumerate(ar36a[0])]
    if sample.Info.sample.type == "Air":
        # Air shot: no chlorine related Ar38
        ar38a = copy.deepcopy(sample.CorrectedValues[4:6])
        ar40a = copy.deepcopy(sample.CorrectedValues[8:10])
    else:
        # 38ArAir, Ar36a × factor
        ar38a = calc.arr.mul_factor(ar36a, sample.TotalParam[4:6], isRelative=True)
        # 40ArAir, Ar36a × factor
        ar40a = calc.arr.mul_factor(ar36a, sample.TotalParam[0:2], isRelative=True)

    sample.DegasValues[ 0] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar36a[0])]  # Ar36a
    sample.DegasValues[ 1] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar36a[1])]
    sample.DegasValues[12] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar38a[0])]  # Ar38a
    sample.DegasValues[13] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar38a[1])]
    sample.DegasValues[26] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar40a[0])]  # Ar40a
    sample.DegasValues[27] = [val if corrDecasAtm[idx] else 0 for idx, val in enumerate(ar40a[1])]


# =======================
# Degas radiogenic 40Ar
# =======================
def calc_degas_r(sample: Sample):
    """ Degas for Radiogenic Ar40
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'Ar40': {'data': sample.CorrectedValues[8:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
            'Ar40K': {'data': sample.DegasValues[30:32], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            'Ar40a': {'data': sample.DegasValues[26:28], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    ar40ar = calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32])
    ar40r = calc.arr.sub(ar40ar, sample.DegasValues[26:28])
    ar40r[0] = [0 if item < 0 and sample.TotalParam[101][index] else item for index, item in enumerate(ar40r[0])]
    sample.DegasValues[24:26] = copy.deepcopy(ar40r)


def calc_degas_c(sample: Sample):
    """ Degas for residuals
    Parameters
    ----------
    sample

    Returns
    -------

    """
    n = sample.Info.experiment.step_num
    sample.DegasValues[ 2] = [0 for i in range(n)]  # 36Arc
    sample.DegasValues[ 3] = [0 for i in range(n)]
    sample.DegasValues[14] = [0 for i in range(n)]  # 38Arc
    sample.DegasValues[15] = [0 for i in range(n)]
    sample.DegasValues[28] = [0 for i in range(n)]  # 40Arc
    sample.DegasValues[29] = [0 for i in range(n)]


# =======================
# Calc ratio
# =======================
def calc_nor_inv_isochrons(sample: Sample):
    n = sample.Info.experiment.step_num
    try:
        isochron_1 = calc.isochron.get_data(
            *calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138]),
            *calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32]),
            *sample.DegasValues[0:2]
        )
        isochron_2 = calc.isochron.get_data(
            *calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138]),
            *sample.DegasValues[0:2],
            *calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32]))
    except (BaseException, Exception):
        return np.empty([5, n]), np.empty([5, n])
    else:
        return isochron_1, isochron_2


def calc_cl_isochrons(sample: Sample):
    n = sample.Info.experiment.step_num
    try:
        isochron_3 = calc.isochron.get_data(
            *calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138]),
            *sample.DegasValues[24:26],
            *calc.arr.mul(sample.DegasValues[10:12], sample.TotalParam[136:138]))
        isochron_4 = calc.isochron.get_data(
            *calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138]),
            *calc.arr.mul(sample.DegasValues[10:12], sample.TotalParam[136:138]),
            *sample.DegasValues[24:26])
        isochron_5 = calc.isochron.get_data(
            *calc.arr.mul(sample.DegasValues[10:12], sample.TotalParam[136:138]),
            *sample.DegasValues[24:26],
            *calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138]))
    except (BaseException, Exception):
        return np.empty([5, n]), np.empty([5, n]), np.empty([5, n])
    else:
        return isochron_3, isochron_4, isochron_5


def calc_3D_isochrons(sample: Sample):
    n = sample.Info.experiment.step_num
    try:
        # === Ar values ===
        # 3D ratio, 36Ar(a+cl)/40Ar(a+r), 38Ar(a+cl)/40Ar(a+r), 39Ar(k)/40Ar(a+r),
        ar40ar = calc.arr.sub(sample.CorrectedValues[8:10], sample.DegasValues[30:32])
        # 36Ar deduct Ca, that is sum of 36Ara and 36ArCl (and also 36Arc)
        ar36acl = calc.arr.sub(sample.CorrectedValues[0:2], sample.DegasValues[4:6])
        # 38Ar deduct K and Ca, that is sum of 38Ara and 38ArCl (and also 38Arc)
        ar38acl = calc.arr.sub(calc.arr.sub(sample.CorrectedValues[4:6], sample.DegasValues[16:18]),
                               sample.DegasValues[18:20])
        # 38ArCl
        ar38cl = sample.DegasValues[10:12]
        # 39ArK
        ar39k = sample.DegasValues[20:22]
        # isochron_6 = calc.isochron.get_3d_data(*ar36acl, *ar38acl, *ar40ar, *ar39k)
        isochron_6 = calc.isochron.get_3d_data(*ar36acl, *ar38acl, *ar39k, *ar40ar)  # Points on the plot will be more disperse than the above
    except:
        return np.empty([9, n])
    else:
        return isochron_6


def calc_ratio(sample: Sample):
    """ Calculate isochron ratio data, 40Arr/39ArK, Ar40r percentage,
        Ar39K released percentage, Ca/K
    Parameters
    ----------
    sample : Sample instance

    Returns
    -------
    None
    """

    try:
        if sample.Info.sample.type == "Air":
            params_to_check = {
                'corrected values': {'data': sample.CorrectedValues[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                'degas values': {'data': sample.DegasValues[0:32], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
            }
        else:
            params_to_check = {
                'corrected values': {'data': sample.CorrectedValues[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k1', },
                'degas values': {'data': sample.DegasValues[0:32], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k2', },
                'K/Ca factor': {'data': sample.TotalParam[20:22], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k3', },
                'normalizing factor': [
                    {'data': sample.TotalParam[136], 'dtype': float, 'func': lambda x: np.isfinite(x) and x > 0, 'class': 'k4', },
                    {'data': sample.TotalParam[137], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
                ],
                # 'apply monte carlo': {'data': sample.TotalParam[112][0], 'dtype': bool, },
            }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    n = sample.Info.experiment.step_num

    # assignation
    if sample.Info.sample.type == "Air":
        sum_ar36a = sum(sample.DegasValues[ 0])
        ar40aar36a = calc.arr.mul_factor(
            sample.DegasValues[26:28], calc.arr.rec_factor(sample.DegasValues[0:2], isRelative=False),
            isRelative=False)
        ar36a_percent = [item / sum_ar36a * 100 if sum_ar36a != 0 else 0 for item in sample.DegasValues[0]]
        sample.ApparentAgeValues[0:2] = ar40aar36a
        sample.ApparentAgeValues[7] = ar36a_percent
    else:
        ar39k, sar39k = calc.arr.mul(sample.DegasValues[20:22], sample.TotalParam[136:138])
        sum_ar39k = sum(ar39k)
        ar39k_percent = [item / sum_ar39k * 100 if sum_ar39k != 0 else 0 for item in ar39k]
        ar40rar39k = calc.arr.mul_factor(
            sample.DegasValues[24:26], calc.arr.rec_factor(sample.DegasValues[20:22], isRelative=False),
            isRelative=False)
        sample.ApparentAgeValues[0:2] = ar40rar39k
        sample.ApparentAgeValues[7] = ar39k_percent

    ar40r_percent = [item / sample.CorrectedValues[8][index] * 100 if sample.CorrectedValues[8][index] != 0 else 0
                     for index, item in enumerate(sample.DegasValues[24])]
    CaK = calc.arr.mul_factor(calc.arr.mul_factor(
        sample.DegasValues[8:10], calc.arr.rec_factor(sample.DegasValues[20:22], isRelative=False)),
        calc.arr.rec_factor(sample.TotalParam[20:22], isRelative=True))

    sample.ApparentAgeValues[6] = ar40r_percent
    sample.PublishValues[10:12] = copy.deepcopy(sample.ApparentAgeValues[0:2])
    sample.PublishValues[14:18] = copy.deepcopy([*sample.ApparentAgeValues[6:8], *CaK])

    sample.IsochronValues[0:5], sample.IsochronValues[6:11] = calc_nor_inv_isochrons(sample)
    sample.IsochronValues[12:17], sample.IsochronValues[18:23], sample.IsochronValues[24:29] = \
        calc_cl_isochrons(sample)
    sample.IsochronValues[5] = [np.nan] * n
    sample.IsochronValues[11] = [np.nan] * n
    sample.IsochronValues[17] = [np.nan] * n
    sample.IsochronValues[23] = [np.nan] * n
    sample.IsochronValues[29] = [np.nan] * n

    # === Cl-Atm-Correlation Plot ===
    sample.IsochronValues[30:39] = calc_3D_isochrons(sample)

    # Turner 1988 3D cake mix plots
    # ar40 = sample.CorrectedValues[8:10]  # ar40 = atm + r + k
    # ar36a = sample.DegasValues[0:2]  # ar36a
    # isochron_6 = calc.isochron.get_3d_data(*ar39k, *ar38cl, *ar40, *ar36a)
    # sample.IsochronValues[30:39] = isochron_6

    # Note that the difference between Turner 3D plots and our 3D plots.


def calc_ratio_monte_carlo(sample: Sample):
    monte_carlo = sample.TotalParam[112][0]
    if monte_carlo and sample.Info.sample.type != "Air":
        res = monte_carlo_f(sample=sample)
        # ages
        res = np.array(list(res)).T  # res is a generator for [*F, *age, iso, ...]
        sample.ApparentAgeValues[0:2] = res[0:2]
        sample.ApparentAgeValues[2] = [np.nan] * sample.Info.experiment.step_num
        sample.ApparentAgeValues[3] = [np.nan] * sample.Info.experiment.step_num
        sample.ApparentAgeValues[4] = [np.nan] * sample.Info.experiment.step_num
        sample.ApparentAgeValues[5] = [np.nan] * sample.Info.experiment.step_num
        # degas
        sample.DegasValues = res[2:2 + 32]
        # isochron data
        sample.IsochronValues = res[2 + 32:2 + 32 + 39]
        # corrected
        sample.CorrectedValues = res[2 + 32 + 39:2 + 32 + 39 + 10]
        # publish
        data = np.array(sample.CorrectedValues)
        data[1:10:2] = data[1:10:2] = np.abs(np.divide(data[1:10:2], data[0:10:2])) * 100
        sample.PublishValues[0:10] = copy.deepcopy(data.tolist())
        sample.PublishValues[10:14] = copy.deepcopy(sample.ApparentAgeValues[0:4])
        sample.PublishValues[14:16] = copy.deepcopy(sample.ApparentAgeValues[6:8])


def monte_carlo_f(sample: Sample):
    """
    Parameters
    ----------
    sample

    Returns
    -------

    """
    try:
        params_to_check = {
            'unknows': {'data': sample.SampleIntercept[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k5', },
            'blanks': {'data': sample.BlankIntercept[0:10], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k6', },
            'mass': [
                {'data': sample.TotalParam[71:81:2], 'dtype': float, 'func': lambda x: np.isfinite(x) and x > 0, 'class': 'k7', },
                {'data': sample.TotalParam[72:81:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k7', },
            ],
            'gain': [
                {'data': sample.TotalParam[126:136:2], 'dtype': float, 'func': lambda x: np.isfinite(x) and x > 0, 'class': 'k8', },
                {'data': sample.TotalParam[126:136:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k8', },
            ],
            'mdf': [
                {'data': sample.TotalParam[69], 'dtype': float, 'func': lambda x: np.isfinite(x) and x != 0, 'class': 'k9', },
                {'data': sample.TotalParam[70], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k9', },
            ],
            'decay consts': [
                {'data': sample.TotalParam[42:48:2], 'dtype': float, 'func': lambda x: np.isfinite(x) and x > 0, 'class': 'k10', },
                {'data': sample.TotalParam[43:48:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k10', },
            ],
            'normalization factor': [
                {'data': sample.TotalParam[136], 'dtype': float, 'func': lambda x: np.isfinite(x) and x > 0, 'class': 'k4', },
                {'data': sample.TotalParam[137], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k4', },
            ],
            'interference params': [
                {'data': sample.TotalParam[8:18], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k11', },
                {'data': sample.TotalParam[0:2], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k11', },
                {'data': sample.TotalParam[4:6], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k11', },
                {'data': sample.TotalParam[56:58], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k11', },
                {'data': sample.TotalParam[32], 'dtype': float, 'func': lambda x: np.isfinite(x), 'class': 'k11', },
                {'data': sample.TotalParam[27], 'dtype': str, 'func': lambda x: all(
                    [len(re.findall(r"\d+", item)) >= 5 for item in list(filter(None, re.split(r'[DS]', x)))[::2]]), 'class': 'k11', },
                {'data': sample.TotalParam[27], 'dtype': str, 'func': lambda x: all(
                    [isinstance(float(item), float) for item in list(filter(None, re.split(r'[DS]', x)))[1::2]]), 'class': 'k11', },
            ],
            'experiment datetime': {'data': sample.TotalParam[31], 'dtype': str, 'func': lambda x: len(re.findall(r"\d+", x)) >= 5, 'class': 'k12', },
        }
    except (IndexError, AttributeError) as e:
        raise
    if not validate_params(**params_to_check):
        return

    sequence_num = sample.Info.experiment.step_num

    ar40m = np.transpose(sample.SampleIntercept[8:10])
    ar39m = np.transpose(sample.SampleIntercept[6:8])
    ar38m = np.transpose(sample.SampleIntercept[4:6])
    ar37m = np.transpose(sample.SampleIntercept[2:4])
    ar36m = np.transpose(sample.SampleIntercept[0:2])
    ar40b = np.transpose(sample.BlankIntercept[8:10])
    ar39b = np.transpose(sample.BlankIntercept[6:8])
    ar38b = np.transpose(sample.BlankIntercept[4:6])
    ar37b = np.transpose(sample.BlankIntercept[2:4])
    ar36b = np.transpose(sample.BlankIntercept[0:2])

    M36 = np.transpose(sample.TotalParam[71:73])
    M37 = np.transpose(sample.TotalParam[73:75])
    M38 = np.transpose(sample.TotalParam[75:77])
    M39 = np.transpose(sample.TotalParam[77:79])
    M40 = np.transpose(sample.TotalParam[79:81])

    G36 = np.transpose(sample.TotalParam[126:128])  # gain correction factors
    G37 = np.transpose(sample.TotalParam[128:130])
    G38 = np.transpose(sample.TotalParam[130:132])
    G39 = np.transpose(sample.TotalParam[132:134])
    G40 = np.transpose(sample.TotalParam[134:136])

    MDF = np.transpose(sample.TotalParam[69:71])

    L39ar = np.transpose(sample.TotalParam[42:44])
    L37ar = np.transpose(sample.TotalParam[44:46])
    L36cl = np.transpose(sample.TotalParam[46:48])

    R39v37ca = np.transpose(sample.TotalParam[8:10])
    R38v37ca = np.transpose(sample.TotalParam[10:12])
    R36v37ca = np.transpose(sample.TotalParam[12:14])
    R40v39k = np.transpose(sample.TotalParam[14:16])
    R38v39k = np.transpose(sample.TotalParam[16:18])

    R40v36a = np.transpose(sample.TotalParam[0:2])
    R38v36a = np.transpose(sample.TotalParam[4:6])
    R36v38clp = np.transpose(sample.TotalParam[56:58])

    R36v38cl = np.transpose(sample.TotalParam[18:20])  # ?
    KCaFactor = np.transpose(sample.TotalParam[20:22])
    KClFactor = np.transpose(sample.TotalParam[22:24])

    stand_time_year = np.transpose(sample.TotalParam[32])
    JNFactor = np.transpose(sample.TotalParam[136:138])

    irradiation_cycles = [list(filter(None, re.split(r'[DS]', each_step))) for each_step in sample.TotalParam[27]]
    t1 = [re.findall(r"\d+", i) for i in sample.TotalParam[31]]  # t1: experimental times
    t2, t3 = [], []  # t2: irradiation times, t3: irradiation durations
    for each_step in irradiation_cycles:
        t2.append([re.findall(r"\d+", item) for i, item in enumerate(each_step) if i % 2 == 0])
        t3.append([float(item) for i, item in enumerate(each_step) if i % 2 == 1])

    # for i in range(sequence_num):
    #     P37Decay = calc.corr.get_decay_factor(t1[i], t2[i], t3[i], L37ar[i][0], L37ar[i][0] * L37ar[i][1] / 100)
    #     print(P37Decay)
    #
    # for i in range(sequence_num):
    #     P39Decay = calc.corr.get_decay_factor(t1[i], t2[i], t3[i], L39ar[i][0], L39ar[i][0] * L39ar[i][1] / 100)
    #     print(P39Decay)

    for i in range(sequence_num):

        res = calc.corr.Monte_Carlo_F(
            ar40m=ar40m[i], ar39m=ar39m[i], ar38m=ar38m[i], ar37m=ar37m[i], ar36m=ar36m[i],
            ar40b=ar40b[i], ar39b=ar39b[i], ar38b=ar38b[i], ar37b=ar37b[i], ar36b=ar36b[i],
            M40=M40[i], M39=M39[i], M38=M38[i], M37=M37[i], M36=M36[i],
            G40=G40[i], G39=G39[i], G38=G38[i], G37=G37[i], G36=G36[i],
            t1=t1[i], t2=t2[i], t3=t3[i],
            R40v36a=R40v36a[i], R38v36a=R38v36a[i],
            R39v37ca=R39v37ca[i], R36v37ca=R36v37ca[i], R38v37ca=R38v37ca[i],
            R40v39k=R40v39k[i], R38v39k=R38v39k[i],
            R36v38clp=R36v38clp[i],
            L37ar=L37ar[i], L39ar=L39ar[i], L36cl=L36cl[i],
            MDF=MDF[i], stand_time_year=stand_time_year[i],
            JNFactor=JNFactor[i],
            KCaFactor=KCaFactor[i],
            KClFactor=KClFactor[i],
            blank_gain_corr=sample.TotalParam[111][i],
            MDF_method=sample.TotalParam[100][i],
            force_to_zero=sample.TotalParam[101][i],
            monte_carlo_size=4000,
        )

        yield res
