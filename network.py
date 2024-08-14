import asyncio
from collections import Counter
from contextlib import suppress

import aiohttp
import requests

TIMEOUT = 5
template = "https://{host}/status?json=true"

requests.packages.urllib3.disable_warnings()


async def _fetch(session, url):
    with suppress(Exception):
        async with session.get(url, ssl=False, timeout=TIMEOUT) as response:
            response = await response.json()
            return response["version"]
    return "unknown"


async def get_network_versions():

    url = template.format(host="mainnet.nucypher.network:9151")
    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False, timeout=TIMEOUT) as response:
            status_data = await response.json()

        nodes = status_data.get("known_nodes", [])
        total_nodes = len(nodes)
        print(f"Number of nodes: {total_nodes}")

        tasks = set()
        for node in nodes:
            url = template.format(host=node["rest_url"])
            tasks.add(_fetch(session, url))

        results = Counter()
        for task in asyncio.as_completed(tasks):
            if task:
                result = await task
                results[result] += 1

        results = sorted(results.items(), key=lambda r: r[1], reverse=True)
        return total_nodes, results
