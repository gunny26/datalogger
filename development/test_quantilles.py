#!/usr/bin/pypy
import cProfile
import time
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(filename)s:%(funcName)s:%(lineno)s %(message)s')
import datalogger
from datalogger import DataLogger as DataLogger
from datalogger import QuantillesArray as QuantillesArray
from commons import *

def report(datalogger, datestring):
    # get data, from datalogger, or dataloggerhelper
    print "Loading data"
    tsa = datalogger.load_tsa(datestring)
    print "calculating quantilles"
    # tsa_test = tsa.slice(("cpu.used.summation", ))
    starttime = time.time()
    qa = QuantillesArray(tsa)
    print "Duration Quantilles: %f" % (time.time()-starttime)
    starttime = time.time()
    qa.dump(open("/tmp/test_quantilles.json", "wb"))
    print "Duration dump: %f" % (time.time()-starttime)
    starttime = time.time()
    qa2 = QuantillesArray.load(open("/tmp/test_quantilles.json", "rb"))
    print "Duration load: %f" % (time.time()-starttime)
    assert qa == qa2
    qa3 = datalogger.load_quantilles(datestring)
    assert qa3 == qa
    print "Output"
    print qa2[("srvarthur1.tilak.cc","0")]
    #quantilles = Quantilles(tsa, "cpu.used.summation", maxx=None)
    quantilles = qa2["cpu.used.summation"]
    #quantilles = Quantilles(tsa, "datastore.read.average", maxx=None)
    quantilles.sort(2)
    print "most demanding CPU Cores"
    print quantilles.head(20)
    print "least demanding CPU Cores"
    print quantilles.tail(20)

def main():
    project = "vicenter"
    tablename = "virtualMachineCpuStats"
    datalogger = DataLogger(BASEDIR, project, tablename)
    datestring = get_last_business_day_datestring()
    report(datalogger, datestring)

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
