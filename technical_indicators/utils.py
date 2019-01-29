# -*- coding: utf-8 -*-

"""utilities"""

__author__ = """Rajesh Rao"""
__email__ = 'rajeshmprao@gmail.com'
__version__ = '0.1.0'

from datetime import timedelta, datetime
import json

def list_dict_to_list(list_dict):
    result = []
    for d in list_dict:
        result.extend(list(d.values()))
    return result 

def daterange(start_date, end_date): # includes end
    for n in range(int ((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

class DateTimeAwareEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)

def get_closest_date(date, data):
    correct_date_list =  data.index[data.index <= date]
    if len(correct_date_list) == 0:
        return None
    else:
        return correct_date_list[-1]

    

