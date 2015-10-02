#!/usr/bin/python
import logging
logging.basicConfig(level=logging.ERROR)
import os
#import tilak_snmp
import time
import datetime
import subprocess
import threading
import Queue
import tilak_centreon

def get_snmp_table(hostname, table_oid, community, index=False):
    """
    hostname : <str>
    table_oid : <str>
    community : <str>
    index : <bool> append index to every row, snmptable Option -Ci

    call snmptable command and get output

    ooutput will be transferred to list of dictionaries,
    key names are taken from output at line 3

    to function properly, the MIB of the mentioned table must be present and installed,
    under ubuntu  use user specific diectory under ~/.snmp/mibs to store vendor specific files

    every dataset - aka row of data - is prependet with key "hostname" and "ts" : timestamp of call
    """
    # field should be extra separated, not the default space
    cmd = ""
    if index is False:
        cmd = "snmptable -v2c -c %s -Cf \; %s %s" % (community, hostname, table_oid)
    else:
        cmd = "snmptable -v2c -c %s -Ci -Cf \; %s %s" % (community, hostname, table_oid)
    logging.info(cmd)
    output = subprocess.check_output((cmd, ), shell=True)
    lines_to_ignore = 1 # ignore first two line
    header_line = True # next is header line
    headers = [] # headers are stored in list
    data = [] # result
    keys = {
        "hostname" : hostname,
        "ts" : time.time()
    }
    for line in output.split("\n"):
        if line == "":
            continue # ignore blank lines
        if lines_to_ignore > 0:
            lines_to_ignore -= 1
            continue
        else:
            if header_line is True:
                headers = line.strip().split(";")
                header_line = False
            else:
                subindex = 0
                values = keys.copy()
                for col in line.strip().split(";"):
                    values[headers[subindex]] = col.replace("\"", "")
                    subindex += 1
                data.append(values)
    return data

def get_hrStorageTable(hostname, community):
    data = get_snmp_table(hostname, "HOST-RESOURCES-MIB::hrStorageTable" , community, index=False)
    # do some data correction
    for row in data:
        try:
            int(row["hrStorageAllocationFailures"]) # not applicable for shared memory
        except ValueError:
            row["hrStorageAllocationFailures"] = "0"
        try:
            int(row["hrStorageUsed"]) # not applicable for shared Memory
        except ValueError:
            row["hrStorageUsed"] =  "0"
        # remove " Bytes" suffix
        row["hrStorageAllocationUnits"] = row["hrStorageAllocationUnits"].split(" ")[0]
    return(data)

def save_data(filename, data):
    """
    save data to file
    input data should be a list, containing dictionaries of row data

    [
        { key1 : value1,
          key2 : value2,
        },
        { key1 : value1,
          key2 : value2,
        },
    ]

    if file already exists, the new data is appended.

    if the file will be created, the firstline will be header names, sorted

    all row data will be written in sorted keys ranking
    """
    if len(data) > 0:
        outfile = None
        outfile_sema.acquire()
        if not os.path.exists(filename):
            outfile = open(filename, "wb")
            outfile.write("\t".join(sorted(data[0].keys())))
            outfile.write("\n")
        else:
            outfile = open(filename, "ab")
        for row in data:
            outfile.write("\t".join((str(row[k]) for k in sorted(row.keys()))))
            outfile.write("\n")
        outfile.close()
        outfile_sema.release()
    else:
        print "No Data returned"

worklist = Queue.Queue()
outfile_sema = threading.BoundedSemaphore(value=1)

def worker():
    while not worklist.empty():
        hostname, community = worklist.get()
        logging.info("Getting Data from %s", hostname)
        try:
            data = get_hrStorageTable(hostname, community)
            save_data(csv_filename, data)
        except subprocess.CalledProcessError as exc:
            #logging.exception(exc)
            logging.error("Failure to get data from %s community %s", hostname, community)
        worklist.task_done()

if __name__ == "__main__":
    centreon = tilak_centreon.Centreon()
    project = "snmp"
    tablename = "hrStorageTable"
    nagios_group = "CMDB_SERVER"
    basedir = os.path.join("/var/rrd", project)
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    basedir_raw = os.path.join(basedir, "raw")
    if not os.path.exists(basedir_raw):
        os.mkdir(basedir_raw)
    datestring = datetime.date.today().isoformat()
    csv_filename = os.path.join(basedir_raw, "%s_%s.csv" % (tablename, datestring))
    # get switchnames from centreon database
    for row in centreon.getCentreonHostGroupMembersSnmp(nagios_group):
        hostname, community, version = row
        if hostname[0:3] in ("vmw", "nss"):
            continue
        if community is None:
            community = "tango97"
        worklist.put((hostname, community))
    q_size = worklist.qsize()
    starttime = time.time()
    for i in range(10):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    worklist.join()
    logging.error("Duration to fetch all %s hosts %s s", q_size, time.time() - starttime)
