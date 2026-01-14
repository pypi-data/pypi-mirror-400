#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2023 Yang
# ararpy - smp - table
# ==========================================
#
#
#
"""
import ast
import re
import copy
import numpy as np
from .. import calc
from . import (sample as samples, basic)

Sample = samples.Sample
Table = samples.Table


# Table functions
def update_table_data(smp: Sample, only_table: str = None):
    """
    Update table data
    Parameters
    ----------
    smp
    only_table

    Returns
    -------

    """
    for key, comp in basic.get_components(smp).items():
        if not isinstance(comp, Table):
            continue
        if only_table is not None and key != only_table:
            continue
        if key == '1':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.SampleIntercept]
        elif key == '2':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.BlankIntercept]
        elif key == '3':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.CorrectedValues]
        elif key == '4':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.DegasValues]
        elif key == '5':
            data = np.array(smp.CorrectedValues)
            data[1:10:2] = np.abs(np.divide(data[1:10:2], data[0:10:2])) * 100
            smp.PublishValues[0:10] = copy.deepcopy(data.tolist())
            smp.PublishValues[10:14] = copy.deepcopy(smp.ApparentAgeValues[0:4])
            smp.PublishValues[14:16] = copy.deepcopy(smp.ApparentAgeValues[6:8])
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.PublishValues]
        elif key == '6':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.ApparentAgeValues]
        elif key == '7':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.IsochronValues]
        elif key == '8':
            data = [smp.SequenceName, smp.SequenceValue, smp.IsochronMark, *smp.TotalParam]
        else:
            raise KeyError(f"Invalid table id")

        data = _normalize_data(
            data, len(comp.header), smp.Info.experiment.step_num, text_col_indexes=comp.text_indexes)

        try:
            params_to_check = {
                comp.name: [
                    {'data': [data[i] for i in comp.text_indexes], 'dtype': str, 'class': 'k1', },
                    {'data': [data[i] for i in range(len(data)) if i not in comp.text_indexes], 'dtype': float, 'class': 'k1', },
                ],
                'step num': {'data': len(smp.SequenceName), 'dtype': int,
                             'func': lambda x: x == smp.Info.experiment.step_num >= 0, 'class': 'k2', },
            }
        except (IndexError, AttributeError) as e:
            raise ValueError(f"{type(e).__name__}, {str(e)}")
        if not basic.validate_params(**params_to_check):
            return

        comp.set_colcount(len(data))
        # calc.arr.replace(data, pd.isnull, None)
        setattr(comp, 'data', calc.arr.transpose(data))


def update_handsontable(smp: Sample, data: list, id: str):
    """
    Parameters
    ----------
    smp : sample instance
    data : list
    id : str, table id

    Returns
    -------

    """


    try:
        col3 = _normalize_data(data[0:3], cols=3, rows=len(data[0]), text_col_indexes=[0, 1, 2])
    except IndexError:
        raise

    update_all_table = False
    try:
        if col3[0] != smp.SequenceName or col3[1] != smp.SequenceValue or col3[2] != smp.IsochronMark:
            update_all_table = True
            smp.SequenceName = col3[0]
            smp.SequenceValue = col3[1]
            smp.IsochronMark = col3[2]
    except IndexError:
        print(f"Check sequence value / isochron mark failed")
        raise
    n = len(data[0])
    if id == '1':  # 样品值
        data = _normalize_data(data, len(samples.SAMPLE_INTERCEPT_HEADERS), n, 3)
        smp.SampleIntercept = _digitize_data(data)
    elif id == '2':  # 本底值
        data = _normalize_data(data, len(samples.BLANK_INTERCEPT_HEADERS), n, 3)
        smp.BlankIntercept = _digitize_data(data)
    elif id == '3':  # 校正值
        data = _normalize_data(data, len(samples.CORRECTED_HEADERS), n, 3)
        smp.CorrectedValues = _digitize_data(data)
    elif id == '4':  # Degas table
        data = _normalize_data(data, len(samples.DEGAS_HEADERS), n, 3)
        smp.DegasValues = _digitize_data(data)
    elif id == '5':  # 发行表
        data = _normalize_data(data, len(samples.PUBLISH_TABLE_HEADERS), n, 3)
        smp.PublishValues = _digitize_data(data)
    elif id == '6':  # 年龄谱
        data = _normalize_data(data, len(samples.SPECTRUM_TABLE_HEADERS), n, 3)
        smp.ApparentAgeValues = _digitize_data(data)
    elif id == '7':  # 等时线
        data = _normalize_data(data, len(samples.ISOCHRON_TABLE_HEADERS), n, 3)
        smp.IsochronValues = _digitize_data(data)
    elif id == '8':  # 总参数
        data = _normalize_data(data, len(samples.TOTAL_PARAMS_HEADERS), n, 3)
        data = _digitize_data(data)
        data[101: 112] = [_strToBool(i) for i in data[101: 112]]
        smp.TotalParam = data
    else:
        raise ValueError(f"{id = }, The table id is not supported.")
    smp.sequence()
    if update_all_table:
        update_table_data(smp)
    else:
        update_table_data(smp, only_table=id)  # Update data of tables after changes of a table


def update_data_from_table(smp: Sample, only_table: str = None):
    """
    Update table data
    Parameters
    ----------
    smp
    only_table

    Returns
    -------

    """
    for key, comp in basic.get_components(smp).items():
        if not isinstance(comp, Table):
            continue
        if only_table is not None and key != only_table:
            continue
        if key == '1':
            smp.SampleIntercept = calc.arr.transpose(comp.data)[3:]
        elif key == '2':
            smp.BlankIntercept = calc.arr.transpose(comp.data)[3:]
        elif key == '3':
            smp.CorrectedValues = calc.arr.transpose(comp.data)[3:]
        elif key == '4':
            smp.DegasValues = calc.arr.transpose(comp.data)[3:]
        elif key == '5':
            smp.PublishValues = calc.arr.transpose(comp.data)[3:]
        elif key == '6':
            smp.ApparentAgeValues = calc.arr.transpose(comp.data)[3:]
        elif key == '7':
            smp.IsochronValues = calc.arr.transpose(comp.data)[3:]
        elif key == '8':
            smp.TotalParam = calc.arr.transpose(comp.data)[3:]
        else:
            pass


def _normalize_data(a, cols, rows, start_col=0, start_row=0, text_col_indexes=[]):
    if isinstance(a, np.ndarray):
        a = a.tolist()
    if not isinstance(a, list):
        raise ValueError(f"List required, but {type(a)} given.")
    if len(a) >= cols:
        a = a[start_col:cols]
    else:
        a = a[start_col:] + [[] for j in range(cols - len(a))]

    def f(_, _i):
        if _i in text_col_indexes:
            if isinstance(_, type(None)):
                return ""
            if isinstance(_, float) and np.isnan(_):
                return ""
            return str(_)
        else:
            if _ in ["", None, np.nan]:
                return np.nan
            elif isinstance(_, str):
                if _.lower() == 'true':
                    return 1
                elif _.lower() == 'false':
                    return 0
            return float(_)

    for i in range(cols - start_col):
        if len(a[i]) >= rows:
            a[i] = [f(each, i + start_col) for each in a[i][start_row:rows]]
        else:
            a[i] = [f(each, i + start_col) for each in a[i][start_row:]] + [f("", i + start_col) for j in range(rows - len(a[i]))]

    return a


def _digitize_data(a):
    # pattern = r'^[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?$'
    # return [[ast.literal_eval(str(cell)) if re.fullmatch(pattern, str(cell)) else np.nan if str(cell) == "" else cell for cell in row] for row in a]
    return a


def _strToBool(cols):
    bools_dict = {
        'true': True, 'false': False, 'True': True, 'False': False, '1': True, '0': False, 'none': False,
    }
    return [bools_dict.get(str(col).lower(), False) for col in cols]
