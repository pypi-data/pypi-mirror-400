#!/usr/bin/env python

import k3net

if __name__ == "__main__":

    # Check if an IP is valid IPv4
    print(k3net.is_ip4("192.168.0.1"))  # True
    print(k3net.is_ip4("invalid"))      # False

    # Check if IP is public or private (INN)
    print(k3net.is_pub("1.2.3.4"))      # True
    print(k3net.is_inn("192.168.0.1"))  # True

    # Get IP class
    print(k3net.ip_class("1.2.3.4"))      # PUB
    print(k3net.ip_class("192.168.0.1"))  # INN

    # Select IPs by class
    ips = ["1.2.3.4", "192.168.0.1", "10.0.0.1"]
    print(k3net.choose_pub(ips))  # ['1.2.3.4']
    print(k3net.choose_inn(ips))  # ['192.168.0.1', '10.0.0.1']

    # Prefer public or private IPs
    print(k3net.ips_prefer(ips, k3net.PUB))  # Public IPs first
    print(k3net.ips_prefer(ips, k3net.INN))  # Private IPs first

    # Get host IP addresses
    host_ips = k3net.get_host_ip4()
    print(host_ips)  # List of host IPv4 addresses

    # IP to number conversion
    num = k3net.ip_to_num("192.168.0.1")
    print(num)  # 3232235521
    print(k3net.num_to_ip(num))  # '192.168.0.1'
