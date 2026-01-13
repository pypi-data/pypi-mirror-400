# tfcommander

**tfcommander** is a simple CLI tool for managing services in [Consul](https://www.consul.io/) and [Traefik](https://traefik.io/) using metadata tags. It supports service registration, deregistration, alias mapping for internal IPs, and querying Traefik routers and middlewares.

After installing via `pip`, you can use it via the `tf` command.

---

Examples:

tf alias add jim 192.168.19.7
tf alias list
tf alias remove jim

tf register jim grafana Grafana 192.168.19.5 3000 grafana.example.com

tf register jim grafana Grafana 192.168.19.5 3000 grafana.example.com \
  --middlewares authHeader@file \
  --https-insecure

tf deregister jim grafana

tf list jim

tf list-traefik jim

tf list-middlewares jim