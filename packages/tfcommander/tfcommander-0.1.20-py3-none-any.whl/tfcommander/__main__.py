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

# ------------------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------------------
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

def get_consul_ip(public_ip_or_alias):
    config = load_config()
    aliases = config.get("aliases", {})
    internal_ip = aliases.get(public_ip_or_alias)
    if not internal_ip:
        print(f"No alias found for '{public_ip_or_alias}'. Use `tf alias add {public_ip_or_alias} <ip>` to define one.")
        sys.exit(1)
    return internal_ip

# ------------------------------------------------------------------------------
# Consul / Traefik Operations
# ------------------------------------------------------------------------------
def register_service(public_ip, service_id, service_name, address, port, domains,
                     middlewares=None, https_insecure=False, custom_rule=None,
                     disable_tls=False, servers_transport=None, resolver=None):

    internal_ip = get_consul_ip(public_ip)

    resolver_name = resolver if resolver else "myresolver"

    if custom_rule:
        domain_rules = custom_rule
    else:
        if not domains:
            print("Error: You must specify at least one domain or provide --custom-rule support.")
            sys.exit(2)
        domain_rules = " || ".join([f"Host(`{d}`)" for d in domains])

    tags = ["traefik.enable=true"]

    if disable_tls:
        tags.append(f"traefik.http.routers.{service_id}.rule={domain_rules}")
        tags.append(f"traefik.http.routers.{service_id}.entrypoints=web")
        tags.append(f"traefik.http.routers.{service_id}.service={service_id}")
    else:
        tags.append(f"traefik.http.routers.{service_id}.rule={domain_rules}")
        tags.append(f"traefik.http.routers.{service_id}.entrypoints=websecure")
        tags.append(f"traefik.http.routers.{service_id}.tls=true")
        tags.append(f"traefik.http.routers.{service_id}.tls.certResolver={resolver_name}")

    tags.append(f"traefik.http.services.{service_id}.loadbalancer.server.port={int(port)}")

    if https_insecure:
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.server.scheme=https")
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.serverstransport=insecure-transport@file")

    if middlewares:
        tags.append(f"traefik.http.routers.{service_id}.middlewares=" + ",".join(middlewares))

    if servers_transport:
        tags.append(f"traefik.http.services.{service_id}.loadbalancer.serversTransport={servers_transport}")

    if https_insecure:
        servers_transport_payload = {
            "Name": "insecure-transport",
            "TLS": {"InsecureSkipVerify": True}
        }
        transport_url = f"http://{internal_ip}:8500/v1/agent/config/traefik/transport/insecure-transport"
        try:
            requests.put(transport_url, json=servers_transport_payload, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"Warning: Could not register serversTransport: {e}")

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
            st_info = f" and serversTransport={servers_transport}" if servers_transport else ""
            resolver_info = f" (resolver: {resolver_name})" if resolver else ""
            print(f"Service '{service_name}' (ID: {service_id}) registered in Consul{resolver_info}{mw_info}{st_info}.")
        else:
            print(f"Failed to register service. HTTP {resp.status_code}: {resp.text}")
            sys.exit(3)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Consul at {internal_ip}: {e}")
        sys.exit(1)

def deregister_service(public_ip, service_id):
    internal_ip = get_consul_ip(public_ip)

    transport_url = f"http://{internal_ip}:8500/v1/agent/config/traefik/transport/{service_id}-transport"
    try:
        resp_t = requests.delete(transport_url, timeout=10)
        if resp_t.status_code in (200, 204):
            print(f"Removed serversTransport '{service_id}-transport'.")
    except requests.exceptions.RequestException:
        pass

    url = f"http://{internal_ip}:8500/v1/agent/service/deregister/{service_id}"
    try:
        resp = requests.put(url, timeout=10)
        if resp.status_code == 200:
            print(f"Service ID '{service_id}' deregistered from Consul at {internal_ip}.")
        else:
            print(f"Failed to deregister service. HTTP {resp.status_code}: {resp.text}")
            sys.exit(4)
    except:
        sys.exit(1)

# ------------------------------------------------------------------------------
# List Services / Middlewares / Routers
# ------------------------------------------------------------------------------
def list_services(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:8500/v1/agent/services"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            services = resp.json()
            if not services:
                print("No services found.")
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
    except:
        sys.exit(1)

def list_traefik(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/routers"
    try:
        resp = requests.get(url, timeout=10)
        routers = resp.json()
        print(f"Routers in Traefik at {internal_ip}:")
        print("-------------------------------------------------------------------")
        router_items = routers.items() if isinstance(routers, dict) else [
            (r.get("name", "unknown"), r) for r in routers
        ]
        for router_name, router_data in router_items:
            print(f"Router: {router_name}")
            print(f"  Rule: {router_data.get('rule', '')}")
            print(f"  Service: {router_data.get('service', '')}")
            m = router_data.get("middlewares", [])
            if m:
                print(f"  Middlewares: {', '.join(m)}")
            print("-------------------------------------------------------------------")
    except:
        sys.exit(1)

def list_middlewares(public_ip):
    internal_ip = get_consul_ip(public_ip)
    url = f"http://{internal_ip}:{TRAEFIK_API_PORT}/api/http/middlewares"
    try:
        resp = requests.get(url, timeout=10)
        middlewares = resp.json()
        print(f"Middlewares in Traefik at {internal_ip}:")
        print("-------------------------------------------------------------------")
        for mw in middlewares:
            for key, value in mw.items():
                print(f"{key}: {json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value}")
            print("-------------------------------------------------------------------")
    except:
        sys.exit(1)

# ------------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------------
def main():
    epilog_text = """
Examples:
  tf alias list
  tf alias add jim 192.168.19.7

  tf register jim mysvc MyService 192.168.19.4 3000 my.example.com
  tf register jim mysvc MyService 192.168.19.4 3000 my.example.com --middlewares auth@file
  tf register jim proxmox Proxmox 192.168.19.10 8006 prox.example.com --https-insecure
  tf register jim proxmox Proxmox 192.168.19.10 8006 prox.example.com --disable-tls
  tf register jim uploads Chibisafe 192.168.6.3 24424 files.domain.tld --servers-transport long-upload@file
  tf register jim mysvc MyService 192.168.19.4 3000 my.example.com --resolver letsencrypt
"""

    parser = argparse.ArgumentParser(
        description="Consul-Traefik Management CLI.",
        epilog=epilog_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command")

    # register
    reg_parser = subparsers.add_parser("register", help="Register a service")
    reg_parser.add_argument("public_ip")
    reg_parser.add_argument("service_id")
    reg_parser.add_argument("service_name")
    reg_parser.add_argument("address")
    reg_parser.add_argument("port")
    reg_parser.add_argument("domains", nargs="*")
    reg_parser.add_argument("--middlewares", nargs="*")
    reg_parser.add_argument("--https-insecure", action="store_true")
    reg_parser.add_argument("--disable-tls", action="store_true")
    reg_parser.add_argument("--servers-transport",
                            help="Traefik serversTransport ref, e.g. large-upload-transport@file")
    reg_parser.add_argument("--resolver",
                            help="TLS cert resolver name. Defaults to 'myresolver' if not specified.")

    # deregister
    dereg_parser = subparsers.add_parser("deregister", help="Deregister a service")
    dereg_parser.add_argument("public_ip")
    dereg_parser.add_argument("service_id")

    # list services
    list_parser = subparsers.add_parser("list", help="List services")
    list_parser.add_argument("public_ip")

    # list traefik routers
    list_tr_parser = subparsers.add_parser("list-traefik")
    list_tr_parser.add_argument("public_ip")

    # list middlewares
    list_mw_parser = subparsers.add_parser("list-middlewares")
    list_mw_parser.add_argument("public_ip")

    # alias block unchanged
    alias_parser = subparsers.add_parser("alias")
    alias_sub = alias_parser.add_subparsers(dest="alias_command")
    alias_add = alias_sub.add_parser("add")
    alias_add.add_argument("name")
    alias_add.add_argument("ip")
    alias_rm = alias_sub.add_parser("remove")
    alias_rm.add_argument("name")
    alias_sub.add_parser("list")

    subparsers.add_parser("version")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "alias":
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
                print("No such alias.")
                sys.exit(1)

        elif args.alias_command == "list":
            if aliases:
                print("Configured aliases:")
                for name, ip in aliases.items():
                    print(f"  {name}: {ip}")
            else:
                print("No aliases configured.")

        else:
            print("Invalid alias subcommand.")
            sys.exit(1)

    elif args.command == "version":
        print("version: 0.1.20")
        sys.exit(0)

    elif args.command == "register":
        if not args.domains:
            print("Error: Must provide at least one domain.")
            sys.exit(2)

        register_service(
            args.public_ip,
            args.service_id,
            args.service_name,
            args.address,
            args.port,
            args.domains,
            middlewares=args.middlewares,
            https_insecure=args.https_insecure,
            disable_tls=args.disable_tls,
            servers_transport=args.servers_transport,
            resolver=args.resolver
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