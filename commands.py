from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.agents import CoordinatorAgent

from agents import get_agent
from embeds import format_ritual_status_embed
from models import RitualState


async def ritual_command(message):
    try:
        _, domain_name, ritual_id = message.content.split()
    except ValueError:
        await message.channel.send("Invalid command. Usage: !ritual <domain> <ritual_id>")
        return

    try:
        domain = domains.get_domain(domain_name)
        agent: CoordinatorAgent = get_agent(contract_name="coordinator", domain=domain)
        status = agent.get_ritual(int(ritual_id), with_participants=True)
        state = RitualState(agent.get_ritual_status(int(ritual_id)))
        embed = format_ritual_status_embed(domain, ritual_id, status, state)
        embed.set_footer(text=f"Ritual Info requested by {message.author.display_name}")
        await message.channel.send(embed=embed)
    except Exception as e:
        await message.channel.send(f"Error: {e}")
        return


_COMMANDS = {
    'ritual': ritual_command,
}
