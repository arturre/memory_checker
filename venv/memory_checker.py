#!/usr/bin/env python3
from argparse import ArgumentParser
import logging
import os
import statsd



def set_loglevel(loglevel="INFO"):
    #set logging for the script
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    logging.basicConfig(level=numeric_level)

def parse_input():
    #parse input arguments
    parser = ArgumentParser()
    parser.add_argument("-l", "--log", dest="loglevel",
                        help="set loglevel DEBUG|INFO|WARNING|ERROR|CRITICAL", default="INFO")
    parser.add_argument("-d", "--host", dest="host",
                        help="statsd server host", default="localhost")
    parser.add_argument("-p", "--port", dest="port",
                        help="statsd server port", default="8125")
    parser.add_argument("-m", "--prefix", dest="prefix", default="awesome_game.production.0.service",
                        help="prefix for metrics")
    result = parser.parse_args()

    return result.host, result.port, result.prefix, result.loglevel

def get_process_memory():
    #walks over /proc filessytem
    #retuns pid, name, virtual_memory_used in kb
    #we are not interested in physical memory used, but virtual memory
    memory_status=list()
    for pid in os.listdir("/proc"):
        if os.path.isdir(os.path.join("/proc",pid)) and pid.isnumeric() and os.path.isfile(os.path.join("/proc",pid,"status")):
            #read virtual memoryobject
            status_file=open(os.path.join("/proc",pid,"status"))
            status_data=status_file.readlines()
            logging.debug("Process found:" + pid)
            proc_vmsize=list(filter(lambda x: x.startswith("VmSize:"), status_data))
            proc_name=list(filter(lambda x: x.startswith("Name:"), status_data))
            if proc_vmsize and proc_name:object
                proc_vmsize=proc_vmsize[0].split()[1]
                proc_name=proc_name[0].split()[1]
                logging.debug("Pid:"+pid+" Name:" + proc_name + " VmSize:" + proc_vmsize)
                memory_status.append((pid,proc_name,proc_vmsize))
    return memory_status

def generate_metric(item):
    return item[1]+"."+item[0]

def extract_value(item):
    return item[2]

def main():
    #initialize
    host,port,prefix,loglevel = parse_input()
    statsd_client=statsd.StatsClient(host,port,prefix)
    set_loglevel(loglevel)
    logging.debug("Statsd destination: "+host+":"+port)
    logging.debug("Statsd prefix: "+prefix)
    #parse memory
    proc_memory=get_process_memory()
    logging.info("Memory data read for " + str(len(proc_memory)) + "processes")
    #send it to statsd using gauge
    for item in proc_memory:
        statsd_client.gauge(generate_metric(item),int(extract_value(item)))
        logging.debug("Sending with prefix " + prefix + " " +generate_metric(item)+"="+extract_value(item))


if __name__ == "__main__":
    main()