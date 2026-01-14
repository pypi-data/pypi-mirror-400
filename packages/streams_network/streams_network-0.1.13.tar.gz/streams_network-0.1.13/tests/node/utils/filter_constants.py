FILTER_SUBNETS = [
    {
        "subnet": "127.0.0.0/8",
        "filter_out": True,
        "desc": "Loopback IPv4 - Localhost only",
    },
    {"subnet": "::1/128", "filter_out": True, "desc": "Loopback IPv6 - Localhost only"},
    {
        "subnet": "169.254.0.0/16",
        "filter_out": True,
        "desc": "Link-local IPv4 - No DHCP assigned",
    },
    {"subnet": "fe80::/10", "filter_out": True, "desc": "Link-local IPv6"},
    {"subnet": "172.17.0.0/16", "filter_out": True, "desc": "Docker Default Bridge"},
    {"subnet": "172.24.0.0/20", "filter_out": True, "desc": "WSL2 Default Network"},
    {
        "subnet": "10.0.0.0/8",
        "filter_out": False,
        "desc": "Private LAN A - Corporate/Internal Network",
    },
    {
        "subnet": "172.16.0.0/12",
        "filter_out": False,
        "desc": "Private LAN B - Internal Network",
    },
    {
        "subnet": "192.168.0.0/16",
        "filter_out": False,
        "desc": "Private LAN C - Home/Office Network",
    },
    {"subnet": "224.0.0.0/4", "filter_out": False, "desc": "Multicast Range"},
    {
        "subnet": "192.168.56.0/24",
        "filter_out": False,
        "desc": "VirtualBox Host-Only Network",
    },
]
