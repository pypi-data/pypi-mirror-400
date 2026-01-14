import logging
import re
import socket
import struct
import sys

import netifaces
import yaml

"""
It is string "PUB" that represents a public ip.
"""
PUB = "PUB"

"""
It is string "INN" that represents a internal ip.
"""
INN = "INN"

LOCALHOST = "127.0.0.1"
inner_ip_patterns = ["^172[.]1[6-9].*", "^172[.]2[0-9].*", "^172[.]3[0-1].*", "^10[.].*", "^192[.]168[.].*"]
logger = logging.getLogger(__name__)


class NetworkError(Exception):
    """
    Super class of all network exceptions.
    """

    pass


class IPUnreachable(NetworkError):
    """
    Exception for an unreachable ip.
    """

    pass


class InvalidIP4(Exception):
    """
    Exception for an invalidIP4 ip.
    """

    pass


class InvalidIP4Number(Exception):
    """
    Exception for an invalidIP4 number.
    """

    pass


def is_ip4(ip):
    """
    It checks if `ip` is a valid ipv4 string.
    :param ip: string or other type data.
    :return: `True` if `ip` is valid ipv4 address. Otherwise `False`.
    """
    if not isinstance(ip, (str, bytes)):
        return False

    ip = ip.split(".")

    for s in ip:
        if not s.isdigit():
            return False

        i = int(s)
        if i < 0 or i > 255:
            return False

    return len(ip) == 4


def ip_class(ip):
    """
    Return the class of `ip`: `net.PUB` or `net.INN`.
    :param ip:
    :return: `net.PUB` or `net.INN`.
    """
    if ip.startswith("127.0.0."):
        return INN

    for ptn in inner_ip_patterns:
        if re.match(ptn, ip):
            return INN

    else:
        return PUB


def is_ip4_loopback(ip):
    return is_ip4(ip) and ip.startswith("127.")


def ips_prefer(ips, preference):
    """
    Reorder `ip_list` according to `preference`.
    If `preference` is `net.PUB`, it returns a new list with public ips before
    internal ips.
    If `preference` is `net.INN`, it returns a new list with internal ips
    before public ips.
    :param ips: list of ip strings.
    :param preference: is one of `net.PUB` and `net.INN`, to specify what ip should be added into
    the list returned.
    :return: a new list of ips in `ip_list` reordered according to `preference`.
    """
    eips = choose_pub(ips)
    iips = choose_inn(ips)

    if preference == PUB:
        return eips + iips
    else:
        return iips + eips


def is_pub(ip):
    """
    Check if `ip` is a public ipv4 address.
    :param ip: string of ipv4 address
    :return: `True` or `False`
    """
    return ip_class(ip) == PUB


def is_inn(ip):
    """
    Check if `ip` is an internal ipv4 address.
    :param ip: string of ipv4 address
    :return: `True` or `False`
    """
    return ip_class(ip) == INN


def choose_ips(ips, ip_type=None):
    """
    :param ips: is a list of ips to choose from.
    :param ip_type:

    `net.PUB`: returns a list of public ip from `ips`.
    `net.INN`: returns a list of internal ip from `ips`.
    `None`: returns the original list.

     Other value: raise `ValueError`.

    :return: list of chosen ips.
    """
    if ip_type is None:
        return ips
    elif ip_type == INN:
        return choose_inn(ips)
    elif ip_type == PUB:
        return choose_pub(ips)
    else:
        raise ValueError("invalid ip_type: {ip_type}".format(ip_type=ip_type))


def choose_pub(ips):
    """
    Return a list of all public ip from `ip_list`.
    :param ips: is a list of ipv4 addresses.
    :return: a list of public ipv4 addresses.
    """
    return [x for x in ips if ip_class(x) == PUB]


def choose_inn(ips):
    """
    Return a list of all internal ip from `ip_list`.
    :param ips: is a list of ipv4 addresses.
    :return: a list of internal ipv4 addresses.
    """
    return [x for x in ips if ip_class(x) == INN]


def get_host_ip4(iface_prefix=None, exclude_prefix=None):
    """
    Get ipv4 addresses on local host.
    If `iface_prefix` is specified, it returns only those whose iface name
    starts with `iface_prefix`.
    If `exclude_prefix` is specified, it does not return those whose iface name
    starts with `exclude_prefix`.
    `127.0.0.1` will not be returned.
    :param iface_prefix: is a string or a list of string to specify what iface should be chosen.
    By default it is `""` thus it returns ips of all iface.
    :param exclude_prefix: is a string or a list of string to specify what iface should not be
    chosen.
    By default it is `None` thus no iface is excluded.
    :return: a list of ipv4 addresses.
    """
    if iface_prefix is None:
        iface_prefix = [""]

    if isinstance(iface_prefix, (str, bytes)):
        iface_prefix = [iface_prefix]

    if exclude_prefix is not None:
        if isinstance(exclude_prefix, (str, bytes)):
            exclude_prefix = [exclude_prefix]

    ips = []

    for ifacename in netifaces.interfaces():
        matched = False

        for t in iface_prefix:
            if ifacename.startswith(t):
                matched = True
                break

        if exclude_prefix is not None:
            for ex in exclude_prefix:
                if ifacename.startswith(ex):
                    matched = False
                    break

        if not matched:
            continue

        addrs = netifaces.ifaddresses(ifacename)

        if netifaces.AF_INET in addrs and netifaces.AF_LINK in addrs:
            for addr in addrs[netifaces.AF_INET]:
                ip = str(addr["addr"])

                if not is_ip4_loopback(ip):
                    ips.append(ip)

    return ips


def choose_by_idc(dest_idc, local_idc, ips):
    """
    net.choose_by_idc(dest_idc, my_idc, ip_list)
    :param dest_idc: is a string representing an IDC where the ips in `ip_list` is.
    :param local_idc: is a string representing the IDC where the function is running.
    :param ips: is a list of ip in the `dest_idc`.
    :return: a list of sub set of `ip_list`.
    """
    if dest_idc == local_idc:
        pref_ips = ips_prefer(ips, INN)
    else:
        pref_ips = ips_prefer(ips, PUB)

    return pref_ips


def get_host_devices(iface_prefix=""):
    """
        Returns a dictionary of all iface, and address information those are binded to it.

    {
        'en0': {
            'LINK': [{
                'addr': 'ac:bc:32:8f:e5:71'
        }],
            'INET': [{
                'broadcast': '172.18.5.255',
                'netmask': '255.255.255.0',
                'addr': '172.18.5.252'

            }]

        }

    }
        :param iface_prefix: is a string or `''` to specify what iface should be chosen.
        :return: a dictionary of iface and its address information.
    """
    rst = {}

    for ifacename in netifaces.interfaces():
        if not ifacename.startswith(iface_prefix):
            continue

        addrs = netifaces.ifaddresses(ifacename)

        if netifaces.AF_INET in addrs and netifaces.AF_LINK in addrs:
            ips = [addr["addr"] for addr in addrs[netifaces.AF_INET]]

            for ip in ips:
                if is_ip4_loopback(ip):
                    break
            else:
                rst[ifacename] = {"INET": addrs[netifaces.AF_INET], "LINK": addrs[netifaces.AF_LINK]}

    return rst


def parse_ip_regex_str(ip_regexs_str):
    """
    It splits a comma separated string into a list.
    Each one in the result list should be a regex string.
    :param ip_regexs_str: is a comma separated string, such as: `192[.]168[.],172[.]16[.]`.
    With this argument, it returns: `['192[.]168[.]', '172[.]16[.]']`.

    These two regex matches all ipv4 addresses those are started
    with `192.168.` or `172.16.`

    :return: a list of regex string.
    """
    ip_regexs_str = ip_regexs_str.strip()

    regs = ip_regexs_str.split(",")
    rst = []
    for r in regs:
        # do not choose ip if it matches this regex
        if r.startswith("-"):
            r = (r[1:], False)
        else:
            r = (r, True)

        if r[0] == "":
            raise ValueError("invalid regular expression: " + repr(r))

        if r[1]:
            r = r[0]

        rst.append(r)

    return rst


def choose_by_regex(ips, ip_regexs):
    """
    net.choose_by_regex(ip_list, regex_list)
    :param ips: is a list of ipv4 addresses.
    :param ip_regexs: is a list of regex.
    :return: a list of ipv4 addresses, in which every ip matches at least one regex from `regex_list`.
    """
    rst = []

    for ip in ips:
        all_negative = True
        for ip_regex in ip_regexs:
            # choose matched:
            #     '127[.]'
            #     ('127[.]', True)
            # choose unmatched:
            #     ('127[.], False)

            if type(ip_regex) in (type(()), type([])):
                ip_regex, to_choose = ip_regex
            else:
                ip_regex, to_choose = ip_regex, True

            all_negative = all_negative and not to_choose

            # when to choose it:
            #     match one of positive regex.
            #     and match none of negative regex.

            if re.match(ip_regex, ip):
                if to_choose:
                    rst.append(ip)

                break
        else:
            # if all regexs are for excluding ip, then choose it
            if all_negative:
                rst.append(ip)

    return rst


def ip_to_num(ip_str):
    """
    It converts the IP to 4-byte integer
    :param ip_str: ip
    :return: a 4-byte integer.
    """
    if not is_ip4(ip_str):
        raise InvalidIP4("IP is invalid: {s}".format(s=ip_str))

    return struct.unpack(">L", socket.inet_aton(ip_str))[0]


def num_to_ip(ip_num):
    """
    It converts the 4-byte integer to IP
    :param ip_num:
    :return: IP.
    """
    if isinstance(ip_num, bool) or not isinstance(ip_num, int):
        raise InvalidIP4Number("The type of IP4 number should be int or long :{t}".format(t=type(ip_num)))
    if ip_num > 0xFFFFFFFF or ip_num < 0:
        raise InvalidIP4Number("IP4 number should be between 0 and 0xffffffff :{s}".format(s=ip_num))

    return socket.inet_ntoa(struct.pack(">L", ip_num))


if __name__ == "__main__":
    args = sys.argv[1:]

    if args[0] == "ip":
        print(yaml.dump(get_host_ip4(), default_flow_style=False))

    elif args[0] == "device":
        print(yaml.dump(get_host_devices(), default_flow_style=False))

    else:
        raise ValueError("invalid command line arguments", args)
