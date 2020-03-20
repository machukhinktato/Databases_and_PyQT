"""
Write the host_ping () function, in which the ping utility will check
 the availability of network nodes. The argument of the function is a list
  in which each network node must be represented by a host name or
   ip-address. In the function, it is necessary to sort through the
    IP addresses and check their availability with the corresponding
     message (“Host is available”, “Host is unavailable”). In this case,
     the IP address of the network node must be created using the
      ip_address () function.
"""
import os
import subprocess
from pprint import *
from ipaddress import *

LIST_OF_HOSTS = [
    '192.168.8.1', '8.8.8.8', 'localhost',
    'mail.ru', '127.0.0.1', '192.168.0.1'
]
FINAL_LIST = {
    'available hosts': "",
    'unavailable hosts': ""
}

DNULL = open(os.devnull, 'w')


def checker(value):
    """
      checks is data ip address or not
    """
    try:
        ip_addr = ip_address(value)
    except ValueError:
        raise Exception("Incorrect IP address")
    return ip_addr


def host_ping(LIST_OF_HOSTS, getList=False):
    """
       checking availability of the ports
    """
    print('Checking a hosts availability ...')
    for host in LIST_OF_HOSTS:
        try:
            ip_addr = checker(host)
        except Exception as e:
            print(f"{host} - {e}, it is a domain name")
            ip_addr = host
        response = subprocess.Popen(["ping", str(ip_addr)], stdout=DNULL)
        if response == 0:
            FINAL_LIST['available hosts'] += f"{str(ip_addr)} \n "
            res_out = f'{str(ip_addr)} - Host is available'
        else:
            FINAL_LIST['unavailable hosts'] += f"{ip_addr} \n "
            res_out = f'{str(ip_addr)} - Host is unavailable'
        if not getList:
            print(res_out)
    if getList:
        return FINAL_LIST


if __name__ == '__main__':
    host_ping(LIST_OF_HOSTS)
    pprint(FINAL_LIST)
