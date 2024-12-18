import os
import socket
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor

# List of common server ports
SERVER_PORTS = [22, 80, 443, 21, 3306, 8080]

def ping_sweep(ip_range):
    """
    Scan a range of IPs by sending ping requests.

    :param ip_range: Base subnet (e.g., "10.10.10") for scanning devices.
    :return: List of active devices with their IPs and hostnames.
    """
    active_hosts = []
    print(f"Scanning network: {ip_range}.0/24...")
    for i in range(1, 255):  # Iterate through the range 1-254 for a typical subnet
        ip = f"{ip_range}.{i}"
        try:
            # Ping the IP
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "200", ip] if os.name == "nt" else ["ping", "-c", "1", "-W", "200", ip],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            if result.returncode == 0:  # If the ping was successful
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except socket.herror:
                    hostname = "Unknown"
                active_hosts.append({"ip": ip, "hostname": hostname})
        except Exception as e:
            pass

    return active_hosts

def check_port(ip, port):
    """Check if a port is open on a given IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Timeout after 1 second
            result = s.connect_ex((ip, port))
            if result == 0:
                return True
            else:
                return False
    except socket.error:
        return False

def get_service_name(port):
    """Map common ports to their respective services."""
    services = {
        22: 'SSH',
        80: 'HTTP',
        443: 'HTTPS',
        21: 'FTP',
        3306: 'MySQL',
        8080: 'HTTP Proxy'
    }
    return services.get(port, "Unknown Service")

def grab_banner(ip, port):
    """Try to grab a service banner (if available)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, port))
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024).decode().strip()
            if banner:
                return banner
            else:
                return "No banner"
    except:
        return "No banner"

def scan_ports(ip):
    """Scan for common server ports on the given IP."""
    open_ports = []
    services = {}
    for port in SERVER_PORTS:
        if check_port(ip, port):
            open_ports.append(port)
            service = get_service_name(port)
            services[port] = service
    return open_ports, services

def scan_for_servers(ip_range):
    active_devices = ping_sweep(ip_range)
    servers = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for device in active_devices:
            futures.append(executor.submit(scan_ports, device["ip"]))

        for i, future in enumerate(futures):
            open_ports, services = future.result()
            if open_ports:
                active_devices[i]["open_ports"] = open_ports
                active_devices[i]["services"] = services
                active_devices[i]["banner"] = {}
                # Grab banners for HTTP or other services
                for port in open_ports:
                    if services[port] in ["HTTP", "HTTPS"]:
                        banner = grab_banner(active_devices[i]["ip"], port)
                        active_devices[i]["banner"][port] = banner
                servers.append(active_devices[i])

    return servers

if __name__ == "__main__":
    # Specify the base subnet (first three octets of your network)
    subnet = "10.10.10"  # Replace with your network's subnet
    servers = scan_for_servers(subnet)

    # Display the results
    print("\nServers found on the network:")
    print(f"{'IP Address':<15} {'Hostname':<20} {'Open Ports'} {'Services'} {'Banners'}")
    print("-" * 100)
    for server in servers:
        print(f"{server['ip']:<15} {server['hostname']:<20} {', '.join(map(str, server['open_ports']))} "
              f"{', '.join([server['services'][port] for port in server['open_ports']])} "
              f"{' | '.join([f'{port}: {server['banner'].get(port, 'No banner')}' for port in server['open_ports']])}")
