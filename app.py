from __future__ import print_function
import sys
import os
import shutil
import time
import traceback
import json
from datetime import datetime
import copy
import re, base64
from binascii import a2b_base64

# logging
import logging

# adjust the datetime variables from ISO strings to python compatible variables
def fix(query):
    if "$and" not in query.keys():
        return query

    for obj in query["$and"]:
        if "CrimeDate" in obj.keys():
            for date_range in obj["CrimeDate"]["$in"]:
                date_range = datetime.strptime(date_range, '%Y-%m-%dT%H:%M:%S.%fZ')

        if "CrimeTime" in obj.keys():
            for time_range in obj["CrimeTime"]["$in"]:
                time_range = datetime.strptime(time_range, '%Y-%m-%dT%H:%M:%S.%fZ')

        if "$or" in obj.keys():
            for obj2 in obj["$or"]:
                if "CrimeDate" in obj2.keys():
                    obj2["CrimeDate"]["$gte"] = datetime.strptime(obj2["CrimeDate"]["$gte"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    obj2["CrimeDate"]["$lte"] = datetime.strptime(obj2["CrimeDate"]["$lte"], '%Y-%m-%dT%H:%M:%S.%fZ')

                if "CrimeTime" in obj2.keys():
                    obj2["CrimeTime"]["$gte"] = datetime.strptime(obj2["CrimeTime"]["$gte"], '%Y-%m-%dT%H:%M:%S.%fZ')
                    obj2["CrimeTime"]["$lte"] = datetime.strptime(obj2["CrimeTime"]["$lte"], '%Y-%m-%dT%H:%M:%S.%fZ')

        # recursive
        if "$and" in obj.keys():
            for obj2 in obj["$and"]:
                obj2 = fix(copy.deepcopy(obj2))

    return query

# Combine database queries to create set combinations
def combine(queries, operator):
    if len(queries) == 1:
        return queries[0].query

    final_query = {}
    serialized_query = {}
    final_query[operator] = []
    serialized_query[operator] = []

    for q in queries:
        query = q["query"]
        final_query[operator].append(fix(copy.deepcopy(query)))
        serialized_query[operator].append(copy.deepcopy(query))

    return final_query, serialized_query
