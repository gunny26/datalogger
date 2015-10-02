#!/usr/bin/python
import json
import urllib
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(filename)s:%(funcName)s:%(lineno)s %(message)s')
from datalogger import DataLogger as DataLogger
from commons import *

def report(datalogger, datestring):
    # get data, from datalogger, or dataloggerhelper
    #tsa1 = datalogger.read_tsa_full(datestring, force=True)
    tsa = datalogger.load_tsa(datestring, cleancache=False)
    tsa.add_per_s_col('vrsclKBRead64', 'vrsclKBRead64_s')
    tsa.add_per_s_col('vrsclKBWritten64', 'vrsclKBWritten64_s')
    tsa.add_per_s_col('vrsclSCSIReadCmd', 'vrsclSCSIReadCmd_s')
    tsa.add_per_s_col('vrsclSCSIWriteCmd', 'vrsclSCSIWriteCmd_s')
    tsa.remove_col('vrsclKBRead64')
    tsa.remove_col('vrsclKBWritten64')
    tsa.remove_col('vrsclSCSIReadCmd')
    tsa.remove_col('vrsclSCSIWriteCmd')
    tsa_grouped = tsa.slice(('vrsclKBRead64_s', 'vrsclKBWritten64_s'))
    standard_wiki_report(datalogger, datestring, tsa, tsa_grouped)

def main():
    project = "ipstor"
    tablename = "vrsClientTable"
    datalogger = DataLogger(BASEDIR, project, tablename)
    datestring = get_last_business_day_datestring()
    report(datalogger, datestring)

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
