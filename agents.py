from collections import defaultdict

import aiohttp
from nucypher.blockchain.eth.agents import ContractAgency, CoordinatorAgent, SigningCoordinatorAgent
from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.domains import TACoDomain
from nucypher.blockchain.eth.registry import ContractRegistry

from typing import Dict

from constants import BASE_URL

__AGENTS = defaultdict(defaultdict)

_TRACK = {
    domains.LYNX: [
        (CoordinatorAgent, domains.LYNX.polygon_chain),
        (SigningCoordinatorAgent, domains.LYNX.eth_chain.chain),
    ],
    domains.TAPIR: [
        (CoordinatorAgent, domains.TAPIR.polygon_chain),
    ],
    domains.MAINNET: [
        (CoordinatorAgent, domains.MAINNET.polygon_chain),
    ]
}


def get_agent(contract_name: str, domain: TACoDomain):
    """Get the agent by domain name."""
    return __AGENTS[domain][contract_name]


async def fetch_registry(domain):
    """Fetch contract ABIs from GitHub."""
    url = BASE_URL.format(domain=domain)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json(content_type=None)


def cache_agents(endpoints: Dict[int, str]):
    """Cache agents."""
    registries = {domain: ContractRegistry.from_latest_publication(domain=domain) for domain in _TRACK}

    for domain, registry in registries.items():
        for agent_class, chain in _TRACK[domain]:
            endpoint = endpoints[chain.id]
            if not endpoint:
                raise ValueError(
                    f"No endpoint provided for domain {domain}:{agent_class}:{chain.id}"
                )

            _agent = ContractAgency.get_agent(
                agent_class=agent_class,
                registry=registry,
                blockchain_endpoint=endpoint,
            )
            __AGENTS[domain][_agent.contract_name.lower()] = _agent
    return __AGENTS
