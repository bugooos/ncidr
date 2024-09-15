#!/usr/bin/env python3

import ipaddress
import os
import subprocess
import platform
from concurrent.futures import ThreadPoolExecutor
from prompt_toolkit import prompt
from prompt_toolkit.completion import PathCompleter

def save_ips_to_file(ips, output_file):
    # Sort IP addresses
    sorted_ips = sorted(ips, key=ipaddress.ip_address)
    with open(output_file, 'w') as f:
        for ip in sorted_ips:
            f.write(f"{ip}\n")
    print(f"IP addresses saved to {output_file}")

def extract_ips_from_cidr(cidr_range):
    try:
        network = ipaddress.ip_network(cidr_range)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        print(f"Invalid CIDR range: {cidr_range}")
        return []

def ping_ip(ip):
    try:
        # Determine the platform and adjust ping command accordingly
        system = platform.system()
        if system == "Windows":
            result = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:  # Unix-like systems (Linux, macOS)
            result = subprocess.run(["ping", "-c", "1", "-W", "1", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ip if result.returncode == 0 else None
    except Exception as e:
        print(f"Error pinging {ip}: {e}")
        return None

def check_active_ips(ips):
    active_ips = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(ping_ip, ip) for ip in ips]
        for future in futures:
            result = future.result()
            if result is not None:
                active_ips.append(result)
    return active_ips

def test_ping_ip(ip):
    result = ping_ip(ip)
    if result is not None:
        print(f"Active IP: {result}")
    else:
        print(f"Inactive IP: {ip}")

def process_single_cidr():
    cidr_range = prompt("Enter CIDR range: ")
    output_file = prompt("Enter the output file: ", completer=PathCompleter())
    ips = extract_ips_from_cidr(cidr_range)
    if ips:
        # Remove duplicates and check for active IPs
        ips = list(set(ips))
        active_ips = check_active_ips(ips)
        if active_ips:
            save_ips_to_file(active_ips, output_file)

def process_cidr_file():
    input_file = prompt("Enter the file with CIDR ranges: ", completer=PathCompleter())
    output_file = prompt("Enter the output file: ", completer=PathCompleter())

    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' does not exist.")
        return

    all_ips = []
    with open(input_file, 'r') as f:
        cidr_ranges = f.readlines()
        for cidr_range in cidr_ranges:
            cidr_range = cidr_range.strip()
            if cidr_range:
                ips = extract_ips_from_cidr(cidr_range)
                all_ips.extend(ips)
    
    if all_ips:
        # Remove duplicates and check for active IPs
        all_ips = list(set(all_ips))
        active_ips = check_active_ips(all_ips)
        if active_ips:
            save_ips_to_file(active_ips, output_file)

def main():
    banner = """
    ========================
    |  Welcome to Nexu's  |
    |      World!         |
    ========================
    """
    print(banner)
    choice = prompt("For CIDR range Press (1) or File with CIDR ranges Press (2): ")

    if choice == '1':
        process_single_cidr()
    elif choice == '2':
        process_cidr_file()
    elif choice == '3':
        # Test ping functionality with a known IP
        test_ping_ip("8.8.8.8")  # Google's public DNS, should be active
    else:
        print("Invalid choice. Please enter '1', '2', or '3'.")

if __name__ == "__main__":
    main()
