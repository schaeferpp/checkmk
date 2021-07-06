#!/usr/bin/python

from .agent_based_api.v1.type_defs import (
    DiscoveryResult,
    CheckResult,
    StringTable
)

from .agent_based_api.v1 import (
    register,
    Service,
    check_levels,
    render
)

from pprint import pprint
from typing import Mapping, Dict, List, Tuple

Section = Dict[str, float]


squid_default_levels = {
    "client_reqs" : (600, 800),
    "client_hits" : (600, 800),
    "server_reqs" : (600, 800),
    "dns_time"    : (2, 4),
    "cpu_time"    : (60, 80)
} 


def parse_check_squid(string_table) -> Section:
    parsed = {}
    for line in string_table:
        if len(line) >= 2 and line[0] == 'cpu_usage':
            parsed['cpu_time'] = float(line[2][:-1])
        if len(line) >= 2 and line[0] == 'dns.median_svc_time':
            parsed['dns_time'] = float(line[2]) 
        if len(line) >= 2 and line[0] == 'client_http.hits':
            parsed['client_hits'] = float(line[2][:-4])
        if len(line) >= 2 and line[0] == 'client_http.requests':
            parsed['client_reqs'] = float(line[2][:-4])
        if len(line) >= 2 and line[0] == 'server.http.requests':
            parsed['server_reqs'] = float(line[2][:-4])

    return parsed

register.agent_section(
        name = 'check_squid',
        parse_function = parse_check_squid,
)

def discover_squid(section) -> DiscoveryResult:
    if 'cpu_time' in section:
        yield Service(item="CPU usage")
    if 'dns_time' in section:
        yield Service(item="DNS response time")
    if 'client_hits' in section:
        yield Service(item="client hits")
    if 'client_reqs' in section:
        yield Service(item="client requests")
    if 'server_reqs' in section:
        yield Service(item="server requests")

def check_squid(item: str, params: Mapping[str, Tuple[float, float]],
                    section: Section) -> CheckResult:
    if item == 'CPU usage':
        cpu_upper = params['cpu_time']
        cpu = section['cpu_time']
        yield from check_levels(
                cpu, levels_upper=cpu_upper, metric_name='squid_cpu_time', label='Squid CPU time', render_func=render.percent,
        )
    elif item == 'DNS response time':
        dns_upper = params['dns_time']
        dns = section['dns_time']
        yield from check_levels(
                dns, levels_upper=dns_upper, metric_name='squid_dns_time', label='DNS response time (avg)', render_func=render.timespan,
        )
    elif item == 'client hits':
        client_hits_upper = params['client_hits']
        client_hits = section['client_hits']
        yield from check_levels(
                client_hits, levels_upper=client_hits_upper, metric_name='squid_client_hits', render_func=lambda x: f'{x} per second',
        )
    elif item == 'client requests':
        client_reqs_upper = params['client_reqs']
        client_reqs = section['client_reqs']
        yield from check_levels(
                client_reqs, levels_upper=client_reqs_upper, metric_name='squid_client_reqs', render_func=lambda x: f'{x} per second',
        )
    elif item == 'server requests':
        server_reqs_upper = params['server_reqs']
        server_reqs = section['server_reqs']
        yield from check_levels(
                server_reqs, levels_upper=server_reqs_upper, metric_name='squid_server_reqs', render_func=lambda x: f'{x} per second',
        )



register.check_plugin(
        name = 'check_squid',
        service_name = 'Squid %s',
        discovery_function = discover_squid,
        check_function = check_squid,
        check_default_parameters = squid_default_levels,
        check_ruleset_name = 'check_squid',
)

# def discover_squid_dns(section) -> DiscoveryResult:
#     yield Service(item='Squid DNS response time')
# 
# def check_squid_dns(section):
#     dns_upper = params['dns_time']
#     dns = section['dns_time']
#     yield from check_levels(
#             cpu, levels_upper=cpu_upper, metric_name='squid_dns_time', label='Squid DNS response time', render_func=lambda v: v,
#     )
# 
# 
# register.check_plugin(
#         name = 'check_squid',
#         service_name = 'Squid %s DNS time',
#         discovery_function = discover_squid_dns,
#         check_function = check_squid_dns,
#         check_default_parameters = squid_default_levels,
#         check_ruleset_name = 'check_squid',
# )
