import asyncio
from collections import Counter
from contextlib import suppress

import aiohttp
import requests

TIMEOUT = 5
SEED_NODE = "mainnet.nucypher.network:9151"
UNKNOWN_VERSION = "unknown"

template = "https://{host}/status?json=true"

requests.packages.urllib3.disable_warnings()


async def _fetch(session, url):
    with suppress(Exception):
        async with session.get(url, ssl=False, timeout=TIMEOUT) as response:
            response = await response.json()
            return response["version"]
    return UNKNOWN_VERSION


async def get_network_versions():

    seed_url = template.format(host=SEED_NODE)
    async with aiohttp.ClientSession() as session:
        async with session.get(seed_url, ssl=False, timeout=TIMEOUT) as response:
            seed_status_data = await response.json()

        nodes = seed_status_data.get("known_nodes", [])
        total_nodes = len(nodes) + 1  # don't forget about the seed node itself
        print(f"Number of nodes: {total_nodes}")

        results = Counter()

        # get version of seed node itself; already in status data
        results[seed_status_data.get("version", UNKNOWN_VERSION)] += 1

        # account for all other nodes
        tasks = set()
        for node in nodes:
            url = template.format(host=node["rest_url"])
            tasks.add(_fetch(session, url))

        for task in asyncio.as_completed(tasks):
            if task:
                result = await task
                results[result] += 1

        results = sorted(results.items(), key=lambda r: r[1], reverse=True)
        return total_nodes, results
