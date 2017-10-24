#!/usr/bin/pypy
import cProfile
import time
import json
import socket
import urllib3
import time
import datetime
import requests
#import logging
#logging.basicConfig(level=logging.INFO, format='%(asctime)-15s %(levelname)s %(filename)s:%(funcName)s:%(lineno)s %(message)s')
#logging.getLogger("requests").setLevel(logging.WARNING)
#logging.getLogger("urllib3").setLevel(logging.CRITICAL)
# own modules
from datalogger import DataLoggerWeb as DataLoggerWeb
from commons import *


ca_certs = "/etc/ssl/certs/ca-certificates.crt"  # Or wherever it lives.

http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=ca_certs,         # Path to your certificate bundle.
    )

def decode_ip(encoded):
    ip_str = "%d.%d.%d.%d" % (int(encoded[0:2], 16) - 5, int(encoded[2:4], 16) - 5, int(encoded[4:6], 16) - 5, int(encoded[6:8], 16) - 5)
    return ip_str

def main():
    project = "haproxy"
    tablename = "http_host"
    datalogger = DataLoggerWeb(DATALOGGER_URL)
    datestring = datalogger.get_last_business_day_datestring()
    # two days back for haproxy logs
    datestring = (datetime.date.today() - datetime.timedelta(int(2))).isoformat()
    caches = datalogger.get_caches(project, tablename, datestring)
    vhosts = [eval(key)[0].split(":")[0] for key in caches["ts"]["keys"].keys()]
    index = 1
    out_data = []
    out_data.append(("index", "vhost", "fqdn", "ip", "ip_reverse_hostname", "status_code", "x_backend_server", "duration"))
    for vhost in vhosts:
        ip = "unknown"
        hostname = "unknown"
        duration = -1.0
        try:
            fqdn = socket.getfqdn(vhost)
            ip = socket.gethostbyname(vhost)
            hostname = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror):
            pass
        if (ip == "unknown") or (not ip.startswith("10.")):
            print "could not resolv hostname %s , probably fake" % vhost
            continue
        elif (not ip.startswith("10.")):
            print "%s is external, skipping" % vhost
            continue
        status_code = 0
        try:
            starttime = time.time()
            res = requests.request("GET", "http://%s/" % vhost, timeout=10, stream=False)
            duration = time.time()-starttime
            status_code = res.status_code
        except (requests.exceptions.ConnectionError, requests.exceptions.InvalidURL):
            pass
        x_backend_server = None
        try:
            x_backend_server = res.headers['x-backend-server']
            if len(x_backend_server) == 8:
                # TODO not exact, hack
                ip_backend_server = decode_ip(x_backend_server)
                x_backend_server = socket.gethostbyaddr(ip_backend_server)[0] # only hostname part
            else:
                x_backend_server = socket.getfqdn(x_backend_server)
        except KeyError:
            pass
        print "%40s : %40s : %15s : %40s : %d : %s : %02f" % (vhost, fqdn, ip, hostname, status_code, x_backend_server, duration)
        out_data.append((index, vhost, fqdn, ip, hostname, status_code, x_backend_server, duration))
        index += 1
    json.dump({"last_update_ts" : str(datetime.date.today()), "data" : out_data}, open("/var/www/webapps/webmap/webmap.json", "w"))

if __name__ == "__main__":
    main()
    #cProfile.run("main()")
