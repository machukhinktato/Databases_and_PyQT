"""
Write a host_range_ping () function to iterate over ip addresses from
 a given range. Only the last octet of each address should change. Based
  on the results of the check, a corresponding message should
   be displayed.
"""
from task_1 import checker as checker, host_ping


def host_range_ping(getList=False):
    """
    function to request and check availability
     of requested range of ip addresses
    """
    while True:
        ip_choise = input('Enter necessity ip address: ')
        try:
            ipv4 = checker(ip_choise)
            octan_checker = int(ip_choise.split('.')[3])
            break
        except Exception as e:
            print(e)
    while True:
        ip_quantity = input('Quantity of address numbers to check: ')
        if not ip_quantity.isnumeric():
            print('Please, enter numeric symbols: ')
        else:
            if (octan_checker + int(ip_quantity)) > 254:
                print(f"Only last octet could be changed , \
                max numbers of octet: {254 - lastOct}")
            else:
                break
    list_of_hosts = []
    [list_of_hosts.append(str(ipv4 + x)) for x in range(int(ip_quantity))]
    if not getList:
        host_ping(list_of_hosts)
    else:
        return host_ping(list_of_hosts, True)


if __name__ == "__main__":
    host_range_ping()
