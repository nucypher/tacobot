from collections import defaultdict

import aiohttp
from nucypher.blockchain.eth.agents import ContractAgency, CoordinatorAgent
from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.domains import TACoDomain
from nucypher.blockchain.eth.registry import ContractRegistry

from typing import Dict

from constants import BASE_URL

__AGENTS = defaultdict(defaultdict)

_TRACK = {
    domains.LYNX: (
        CoordinatorAgent,
    ),
    domains.TAPIR: (
        CoordinatorAgent,
    ),
    domains.MAINNET: (
        CoordinatorAgent,
    )
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
        for _, agent_classes in _TRACK.items():
            endpoint = endpoints[domain.polygon_chain.id]
            if not endpoint:
                raise ValueError(f"No endpoint provided for domain {domain}")
            for agent_class in agent_classes:
                _agent = ContractAgency.get_agent(
                    agent_class=agent_class,
                    registry=registry,
                    blockchain_endpoint=endpoint,
                )
                __AGENTS[domain][_agent.contract_name.lower()] = _agent
    return __AGENTS
