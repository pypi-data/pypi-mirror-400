#!/usr/bin/env python3
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
TRAEFIK_API_PORT = 8087
CONFIG_FILE = os.path.join(Path.home(), ".consulcli_config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_config(key, value):
    config = load_config()
    config[key] = value
    config["saved_on"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"Configuration saved to {CONFIG_FILE}.")

def get_consul_ip(public_ip):
    config = load_config()
    aliases = config.get("aliases", {})
    internal_ip = aliases.get(public_ip)
    if not internal_ip:
        print(f"No alias found for '{public_ip}'. Use `alias add {public_ip} <ip>` to define one.")
        sys.exit(1)
    return internal_ip

# ------------------------------------------------------------------------------
# Register service in Consul
# ------------------------------------------------------------------------------
def register_service(public_ip, service_id, service_name, address, port, domains, middlewares=None, https_insecure=False):
    internal_ip = get_consul_ip(public_ip)
    domain_rules = " || ".join([f"Host(`{d}`)" for d in domains])
    tags = [
        "traefik.enable=true",
        f"traefik.http.routers.{service_id}.rule={domain_rules}",
        f"traefik.http.routers.{service_id}.entrypoints=websecure",
        f"traefik.http.routers.{service_id}.tls=true",
        f"traefik.http.routers.{service_id}.tls.certresolver=myresolver"
    ]

    if https_insecure:
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.server.scheme=https")
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.serverstransport={service_id}-transport@file")

    if middlewares:
        tags.append(f"traefik.http.routers.{service_id}.middlewares=" + ",".join(middlewares))

    if https_insecure:
        servers_transport_payload = {
            "Name": f"{service_id}-transport",
            "TLS": {
                "InsecureSkipVerify": True
            }
        }
        transport_url = f"http://{internal_ip}:8500/v1/agent/config/traefik/transport/{service_id}-transport"
        try:
            requests.put(transport_url, json=servers_transport_payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not register serversTransport for {service_id}: {e}")

    payload = {
        "ID": service_id,
        "Name": service_name,
        "Address": address,
        "Port": int(port),
        "Tags": tags
    }

    url = f"http://{internal_ip}:8500/v1/agent/service/register"
    try:
        resp = requests.put(url, json=payload, timeout=10)
        if resp.status_code == 200:
            mw_info = f" with middlewares: {', '.join(middlewares)}" if middlewares else ""
            print(f"Service '{service_name}' (ID: {service_id}) registered in Consul{mw_info}.")
        else:
            print(f"Failed to register service. HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def deregister_service(public_ip, service_id):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:8500/v1/agent/service/deregister/{service_id}"
    try:
        resp = requests.put(url, timeout=10)
        if resp.status_code == 200:
            print(f"Service with ID '{service_id}' deregistered.")
        else:
            print(f"Failed to deregister service. HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def list_services(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:8500/v1/agent/services"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            services = resp.json()
            if not services:
                print(f"No services found on Consul at {internal_ip}.")
                return
            print(f"Services on Consul at {internal_ip}:")
            print("-------------------------------------------------------------------")
            for srv_id, srv_data in services.items():
                name = srv_data.get("Service", "")
                addr = srv_data.get("Address", "")
                port = srv_data.get("Port", "")
                tags = srv_data.get("Tags", [])
                print(f"ID: {srv_id}")
                print(f"  Name: {name}")
                print(f"  Address: {addr}")
                print(f"  Port: {port}")
                print(f"  Tags: {', '.join(tags)}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list services. HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def list_traefik(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/routers"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            routers = resp.json()
            if not routers:
                print(f"No routers found in Traefik at {internal_ip}.")
                return
            print(f"Routers in Traefik at {internal_ip}:")
            print("-------------------------------------------------------------------")
            router_items = routers.items() if isinstance(routers, dict) else [
                (r.get("name", "unknown"), r) for r in routers
            ]
            for router_name, router_data in router_items:
                print(f"Router: {router_name}")
                print(f"  Rule: {router_data.get('rule', '')}")
                print(f"  Service: {router_data.get('service', '')}")
                middlewares = router_data.get("middlewares", [])
                if middlewares:
                    print(f"  Middlewares: {', '.join(middlewares)}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list Traefik routers. HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Traefik at {internal_ip}: {e}")
        sys.exit(1)

def list_middlewares(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/middlewares"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            middlewares = resp.json()
            if not middlewares:
                print(f"No middlewares found in Traefik at {internal_ip}.")
                return
            print(f"Middlewares in Traefik at {internal_ip}:")
            print("-------------------------------------------------------------------")
            for mw in middlewares:
                for key, value in mw.items():
                    print(f"{key}: {json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value}")
                print("-------------------------------------------------------------------")
        else:
            print(f"Failed to list Traefik middlewares. HTTP {resp.status_code}: {resp.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Traefik at {internal_ip}: {e}")
        sys.exit(1)

def main():
    epilog_text = """
Examples:
  tf5.py config mykey myvalue
  tf5.py alias add jim 192.168.19.7
  tf5.py alias list
  tf5.py register jim mysvc MyService 192.168.19.4 3000 my.example.com
  tf5.py register jim mysvc MyService 192.168.19.4 3000 my.example.com --middlewares auth@file
  tf5.py register jim proxmox Proxmox 192.168.19.10 8006 prox.example.com --https-insecure
  tf5.py deregister jim mysvc
  tf5.py list jim
  tf5.py list-traefik jim
  tf5.py list-middlewares jim
"""
    parser = argparse.ArgumentParser(
        description="Consul-Traefik Management CLI.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    config_parser = subparsers.add_parser("config", help="Set a config key")
    config_parser.add_argument("key")
    config_parser.add_argument("value")

    reg_parser = subparsers.add_parser("register", help="Register a service")
    reg_parser.add_argument("public_ip")
    reg_parser.add_argument("service_id")
    reg_parser.add_argument("service_name")
    reg_parser.add_argument("address")
    reg_parser.add_argument("port")
    reg_parser.add_argument("domains", nargs="*")
    reg_parser.add_argument("--middlewares", nargs="*")
    reg_parser.add_argument("--https-insecure", action="store_true")

    dereg_parser = subparsers.add_parser("deregister", help="Deregister a service")
    dereg_parser.add_argument("public_ip")
    dereg_parser.add_argument("service_id")

    list_parser = subparsers.add_parser("list", help="List services")
    list_parser.add_argument("public_ip")

    list_traefik_parser = subparsers.add_parser("list-traefik", help="List Traefik routers")
    list_traefik_parser.add_argument("public_ip")

    list_middlewares_parser = subparsers.add_parser("list-middlewares", help="List Traefik middlewares")
    list_middlewares_parser.add_argument("public_ip")

    alias_parser = subparsers.add_parser("alias", help="Manage IP aliases")
    alias_subparsers = alias_parser.add_subparsers(dest="alias_command")

    alias_add = alias_subparsers.add_parser("add", help="Add an alias")
    alias_add.add_argument("name")
    alias_add.add_argument("ip")

    alias_remove = alias_subparsers.add_parser("remove", help="Remove an alias")
    alias_remove.add_argument("name")

    alias_list = alias_subparsers.add_parser("list", help="List aliases")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "config":
        save_config(args.key, args.value)

    elif args.command == "alias":
        config = load_config()
        aliases = config.get("aliases", {})

        if args.alias_command == "add":
            aliases[args.name] = args.ip
            config["aliases"] = aliases
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"Alias '{args.name}' set to {args.ip}")

        elif args.alias_command == "remove":
            if args.name in aliases:
                del aliases[args.name]
                config["aliases"] = aliases
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
                print(f"Alias '{args.name}' removed.")
            else:
                print(f"No such alias: {args.name}")

        elif args.alias_command == "list":
            if aliases:
                print("Configured aliases:")
                for name, ip in aliases.items():
                    print(f"  {name}: {ip}")
            else:
                print("No aliases configured.")
        else:
            print("Invalid alias subcommand.")

    elif args.command == "register":
        register_service(
            args.public_ip,
            args.service_id,
            args.service_name,
            args.address,
            args.port,
            args.domains,
            middlewares=args.middlewares,
            https_insecure=args.https_insecure
        )

    elif args.command == "deregister":
        deregister_service(args.public_ip, args.service_id)

    elif args.command == "list":
        list_services(args.public_ip)

    elif args.command == "list-traefik":
        list_traefik(args.public_ip)

    elif args.command == "list-middlewares":
        list_middlewares(args.public_ip)

if __name__ == "__main__":
    main()

