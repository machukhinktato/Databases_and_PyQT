"""
Write a host_range_ping_tab () function, the capabilities of which
are based on the function from Example 2. But in this case, the result
should be total for all ip-addresses presented in a table format
(use the tabulate module). The table should consist of two columns
"""
from task_2 import host_range_ping
from tabulate import tabulate


def host_range_ping_tab():
    """
    function to request and check availability
     of requested range of ip addresses
               tabulate view
    """
    result_dict = diaposon_ip_checker(True)
    print(tabulate([result_dict], headers='keys', tablefmt="pipe", stralign="center"))


if __name__ == "__main__":
    host_range_ping_tab()
