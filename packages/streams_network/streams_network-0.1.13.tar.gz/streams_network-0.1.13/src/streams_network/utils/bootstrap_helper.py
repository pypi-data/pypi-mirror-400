from streams_network import BootstrapNetwork, ConnectionInfo
from functools import lru_cache
import psutil
import socket
import ipaddress
import stun
from .filter_constants import FILTER_SUBNETS


def is_filtered(ip_str: str) -> bool:
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        for entry in FILTER_SUBNETS:
            network = ipaddress.ip_network(entry["subnet"])
            if ip_obj in network:
                return entry["filter_out"]
        return False
    except ValueError:
        return True


def get_local_ips():
    lan_ips = []
    vpn_ips = []

    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ip = addr.address

                if is_filtered(ip):
                    continue

                ip_obj = ipaddress.IPv4Address(ip)

                if ip_obj in ipaddress.IPv4Network("100.64.0.0/10"):
                    vpn_ips.append(ip)
                else:
                    lan_ips.append(ip)

    return lan_ips, vpn_ips


def get_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def get_public_ip_and_port(stun_host="stun.l.google.com", stun_port=19302):
    try:
        nat_type, external_ip, external_port = stun.get_ip_info(
            stun_host=stun_host, stun_port=stun_port
        )
        if external_ip and not is_filtered(external_ip):
            return external_ip, external_port
    except Exception:
        pass
    return None, None


def get_all_ips_with_ports(stun_host="stun.l.google.com", stun_port=19302):
    lan_ips, vpn_ips = get_local_ips()
    os_port = get_port()

    all_conns = {
        "LAN": [{"ip": ip, "port": os_port} for ip in lan_ips],
        "VPN": [{"ip": ip, "port": os_port} for ip in vpn_ips],
    }

    public_ip, public_port = get_public_ip_and_port(
        stun_host=stun_host, stun_port=stun_port
    )
    if public_ip:
        all_conns["Public"] = [{"ip": public_ip, "port": public_port}]

    return all_conns


def get_bootstrap_config(
    email: str,
    token: str,
    url: str = "https://stream.plotune.net",
) -> BootstrapNetwork:
    connections = []

    ip_data = get_all_ips_with_ports()

    for con_type, addrs in ip_data.items():
        for addr in addrs:
            connections.append(
                ConnectionInfo(
                    con_type=con_type, address=addr["ip"], port=str(addr["port"])
                )
            )

    return BootstrapNetwork(
        bearer_token=token, owner=email, bootstrap_url=url, connections=connections
    )
