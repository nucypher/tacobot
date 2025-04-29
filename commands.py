from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.agents import CoordinatorAgent, SigningCoordinatorAgent

from agents import get_agent
from embeds import (
    format_ritual_status_embed, format_network_status_embed,
    format_signing_ritual_embed,
)
from models import RitualState, SigningRitualState
from network import get_network_versions


async def ritual_command(message):
    try:
        _, domain_name, ritual_id = message.content.split()
    except ValueError:
        await message.channel.send("Invalid command. Usage: !ritual <domain> <ritual_id>")
        return

    try:
        domain = domains.get_domain(domain_name)
        agent: CoordinatorAgent = get_agent(contract_name="coordinator", domain=domain)
        ritual = agent.get_ritual(int(ritual_id), transcripts=False)
        state = RitualState(agent.get_ritual_status(int(ritual_id)))
        embed = format_ritual_status_embed(domain, ritual, state)
        embed.set_footer(text=f"Ritual Info requested by {message.author.display_name}")
        await message.channel.send(embed=embed)
    except Exception as e:
        await message.channel.send(f"Error: {e}")
        return


async def signing_ritual_command(message):
    try:
        _, domain_name, cohort_id = message.content.split()
    except ValueError:
        await message.channel.send("Invalid command. Usage: !signing-ritual <domain> <cohort_id>")
        return

    try:
        domain = domains.get_domain(domain_name)
        agent: SigningCoordinatorAgent = get_agent(contract_name="signingcoordinator", domain=domain)
        signing_cohort = agent.get_signing_cohort(int(cohort_id))
        state = SigningRitualState(agent.get_signing_cohort_status(int(cohort_id)))
        embed = format_signing_ritual_embed(domain, signing_cohort, state)
        embed.set_footer(text=f"Signing Cohort Info requested by {message.author.display_name}")
        await message.channel.send(embed=embed)
    except Exception as e:
        await message.channel.send(f"Error: {e}")
        return


async def network_status_command(message):
    total_nodes, results = await get_network_versions()
    embed = format_network_status_embed(total_nodes, results)
    await message.channel.send(embed=embed)


_COMMANDS = {
    'ritual': ritual_command,
    'signing-ritual': signing_ritual_command,
    'network-status': network_status_command,
}
