#!/usr/bin/pypy
import cProfile
import time
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(filename)s:%(funcName)s:%(lineno)s %(message)s')
from datalogger import DataLogger as DataLogger
from commons import *

def get_mse(series1, series2):
    """
    the series as is
    """
    assert len(series1) == len(series2)
    mse = 0.0
    for index, data1 in enumerate(series1):
        diff = (data1 - series2[index])
        mse += diff * diff
    mse /= len(series1)
    return mse

def get_mse_sorted(series1, series2):
    """
    sorted but not normalized values
    """
    assert len(series1) == len(series2)
    mse = 0.0
    series2_s = sorted(series2)
    for index, data1 in enumerate(sorted(series1)):
        diff = (data1 - series2_s[index])
        mse += diff * diff
    mse /= len(series1)
    return mse

def get_mse_norm(series1, series2):
    """
    normalized values
    """
    assert len(series1) == len(series2)
    mse = 0.0
    max_v = max(max(series1), max(series2))
    s1 = tuple((value/max_v for value in series1))
    s2 = tuple((value/max_v for value in series2))
    for index, data1 in enumerate(s1):
        diff = (data1 - s2[index])
        mse += diff * diff
    mse /= len(series1)
    return mse

def get_mse_sorted_norm(series1, series2):
    """
    sorted and normalized
    """
    assert len(series1) == len(series2)
    mse = 0.0
    max_v = max(series1)
    if max_v == 0.0:
        # difference is equa series2
        return sum((value * value for value in series2))/len(series1)
    s1 = tuple((value/max_v for value in sorted(series1)))
    s2 = tuple((value/max_v for value in sorted(series2)))
    for index, data1 in enumerate(s1):
        diff = (data1 - s2[index])
        mse += diff * diff
    mse /= len(series1)
    return mse

def get_mse_sorted_norm_missing(series1, series2):
    """
    sorted and normalized
    """
    mse = 0.0
    max_v = max(series1)
    if max_v == 0.0:
        # difference is equa series2
        return sum((value * value for value in series2))/len(series1)
    s1 = tuple((value/max_v for value in sorted(series1, reverse=True)))
    s2 = tuple((value/max_v for value in sorted(series2, reverse=True)))
    assert abs(len(s1) - len(s2)) / max(len(s1), len(s2)) < 0.1 # not more than 10% length difference
    for index, data1 in enumerate(s1):
        try:
            diff = (data1 - s2[index])
            mse += diff * diff
        except IndexError:
            break
    mse /= len(series1)
    return mse


class CorrelationMatrixArray(object):

    def __init__(self, tsa):
        self.__data = {}
        for value_key in tsa.value_keys:
            print "calculating value_key %s" % value_key
            self.__data[value_key] = CorrelationMatrix(tsa, value_key)

    def __eq__(self, other):
        try:
            assert self.__data.keys() == other.keys()
            for key in self.__data.keys():
                assert self.__data[key] == other[key]
            return True
        except AssertionError as exc:
            logging.exception(exc)
            print self.__data.keys(), other.keys()
        return False

    def __getitem__(self, key):
        return self.__data[key]

    def keys(self):
        return self.__data.keys()

    def dump(self, filehandle):
        data = dict(((key, self.__data[key].dumps()) for key in self.__data.keys()))
        json.dump(data, filehandle)

    @staticmethod
    def load(filehandle):
        cma = CorrelationMatrixArray.__new__(CorrelationMatrixArray)
        data = json.load(filehandle)
        cma.__data = dict(((key, CorrelationMatrix.loads(data)) for key, data in data.items()))
        return cma


class CorrelationMatrixTime(object):

    def __init__(self, tsa1, tsa2, value_key):
        self.__data = self.__get_correlation_matrix(tsa1, tsa2, value_key)

    @property
    def data(self):
        return self.__data

    def __eq__(self, other):
        try:
            assert self.__data == other.data
            return True
        except AssertionError as exc:
            logging.exception(exc)
            print self.__data.keys(), other.data.keys()
        return False

    def __getitem__(self, key):
        return self.__data[key]

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def items(self):
        return self.__data.items()

    @staticmethod
    def __get_correlation_matrix(tsa1, tsa2, value_key):
        """
        search for corelating series in all other series available
        """
        print "Searching for correlation in value_key %s)" % value_key
        matrix = {}
        keylist = tsa1.keys()
        for key in keylist:
            other = None
            try:
                other = tsa2[key][value_key]
            except KeyError:
                print "key %s is not in older tsa, skipping" % str(key)
                continue
            series = tsa1[key][value_key]
            matrix[key] = get_mse_sorted_norm_missing(series, other)
            print key, matrix[key]
        return matrix

    def dumps(self):
        return json.dumps(str(self.__data))

    @staticmethod
    def loads(data):
        cm = CorrelationMatrix.__new__(CorrelationMatrix)
        cm.__data = eval(json.loads(data))
        return cm

def report(datalogger, datestring):
    # get data, from datalogger, or dataloggerhelper
    print "loading data"
    starttime = time.time()
    tsa1 = datalogger.load_tsa("2015-10-13")
    tsa2 = datalogger.load_tsa("2015-10-06")
    print "Duration load %f" % (time.time() - starttime)
    starttime = time.time()
    cm = CorrelationMatrixTime(tsa1, tsa2, "cpu.used.summation")
    for key, coefficient in sorted(cm, key=lambda items: items[1]):
        print key, coefficient

def main():
    project = "vicenter"
    tablename = "virtualMachineCpuStats"
    datalogger = DataLogger(BASEDIR, project, tablename)
    datestring = get_last_business_day_datestring()
    report(datalogger, datestring)

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
