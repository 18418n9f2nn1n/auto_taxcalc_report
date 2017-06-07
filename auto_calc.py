import re
import os
import sys
import math
import copy
import locale
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from taxcalc import *
from decimal import *
from pylatex.utils import italic, NoEscape
from pylatex.base_classes import Container, Command
from pylatex import Document, PageStyle, Head, Foot, MiniPage, Section, \
                    Command, StandAloneGraphic, MultiColumn, MultiRow, Tabu, \
                    LongTabu, LargeText, MediumText, LineBreak, NewPage, \
                    Tabularx, Tabular, TextColor, simple_page_number, Figure, \
                    Subsection, Math, TikZ, Axis, Plot, Figure, Matrix, Itemize


def make_baseline(start_year, records_url):
    """
    Generates a baseline calculator using current law.
    """
    policy_cl = Policy()
    behavior_cl = Behavior()
    records_cl = Records(records_url)
    calc_cl = Calculator(policy_cl, records_cl, behavior_cl)
    for i in range(start_year - 2013):
        calc_cl.increment_year()
    assert calc_cl.current_year == start_year
    calc_cl.calc_all()
    return(calc_cl)


def make_calculator(calc_cl, ref_dict, start_year, beh_dict, records_url):
    """
    Makes a calculator, implimenting each behavioral reform in beh_dict.
    """
    policy1 = Policy()
    behavior1 = Behavior()
    records1 = Records(records_url)
    policy1.implement_reform(ref_dict)
    calc1 = Calculator(records=records1, policy=policy1, behavior=behavior1)
    for i in range(start_year - 2013):
        calc1.increment_year()
    assert calc1.current_year == start_year
    calc1.calc_all()
    global calc_beh_dict
    calc_beh_dict = beh_dict.copy()
    for key in beh_dict:
        behavior1.update_behavior(beh_dict[key])
        calc_beh_dict[key] = Behavior.response(calc_cl, calc1)
    return(calc_beh_dict)


def dict_calculator(ref_dict, start_year, beh_dict, records_url):
    """
    Generate a dictionary of calculators for all policy reforms,
    across all behavirors.
    """
    global calc_dict
    calc_dict = ref_dict.copy()
    for key in ref_dict:
        calc_dict[key] = make_calculator(make_baseline(start_year,
                                                       records_url),
                                         ref_dict[key],
                                         start_year,
                                         beh_dict,
                                         records_url)
        print('Done')
    return(calc_dict)


def ten_year_cost(calc_base, calc_ref):
    """
    Calculate the ten-year-cost of thereform without behavorial dynamics.
    """
    path = [0] * 10
    calc1 = copy.deepcopy(calc_base)
    calc2 = copy.deepcopy(calc_ref)
    for i in range(10):
        calc1.calc_all()
        calc2.calc_all()
        calc1_combined = (calc1.records.combined * calc1.records.s006)
        calc2_combined = (calc2.records.combined * calc2.records.s006)
        path[i] = (calc2_combined - calc1_combined).sum() / 10**9
        if calc1.current_year < 2026:
            calc1.increment_year()
            calc2.increment_year()
    return sum(path)


def dict_ten_year_cost(calc_dict, calc_cl):
    """
    Calculate a dictionary of ten-year-costs without behavorial dynamics.
    """
    global cost_dict
    cost_dict = copy.deepcopy(calc_dict)
    for key in calc_dict:
        key1 = key
        for key in calc_dict[key1]:
            key2 = key
            cost_dict[key1][key2] = ten_year_cost(calc_cl,
                                                  cost_dict[key1][key2])
            print(cost_dict[key1][key2])
    print('Done')


def ten_year_cost_PE(calc_base, calc_ref, tyc_beh):
    """
    Calculate the ten year cost with behavioral dynamics.
    """
    path = [0] * 10
    calc1 = copy.deepcopy(calc_base)
    calc2 = copy.deepcopy(calc_ref)
    calc2.behavior.update_behavior(tyc_beh)
    calc2b = Behavior.response(calc1, calc2)
    for i in range(10):
        calc1_combined = (calc1.records.combined * calc1.records.s006)
        calc2b_combined = (calc2b.records.combined * calc2b.records.s006)
        path[i] = (calc2b_combined - calc1_combined).sum() / 10**9
        if calc1.current_year < 2026:
            calc1.increment_year()
            calc2b.increment_year()
            calc1.calc_all()
            calc2b.calc_all()
    return sum(path)


def dict_ten_year_cost_PE(calc_cl, tyc_beh, calc_dict):
    """
    Calculate a dictionary with the ten-year-costs with behavioral dynamics.
    """
    global cost_PE_dict
    cost_PE_dict = copy.deepcopy(calc_dict)
    for key in calc_dict:
        key1 = key
        for key in calc_dict[key1]:
            key2 = key
            cost_PE_dict[key1][key2] = ten_year_cost_PE(calc_cl,
                                                        calc_dict[key1][key2],
                                                        tyc_beh)
            print(cost_PE_dict[key1][key2])
    print('Done')


# baseline (current law)
policy_cl = Policy()
behavior_cl = Behavior()
records_cl = Records(records_url)
calc_cl = Calculator(policy_cl, records_cl, behavior_cl)
for i in range(start_year - 2013):
    calc_cl.increment_year()
assert calc_cl.current_year == start_year
calc_cl.calc_all()
print("Done")


dict_calculator(ref_dict, start_year, beh_dict, records_url)
dict_ten_year_cost(calc_dict, calc_cl)
dict_ten_year_cost_PE(calc_cl, tyc_beh, calc_dict)
