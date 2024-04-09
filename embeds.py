from datetime import datetime
from typing import Sequence

from discord import Embed
from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.domains import TACoDomain
from nucypher.blockchain.eth.models import Coordinator

from models import RitualState


def make_polygon_explorer_link(domain: TACoDomain, address: str, short_form: bool = False) -> str:
    address_to_use = address[:8] if short_form else address
    if domain == domains.MAINNET:
        return f"[{address_to_use}](https://polygonscan.com/address/{address})"
    else:
        return f"[{address_to_use}](https://oklink.com/amoy/address/{address})"


def format_duration(seconds: int) -> str:
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"


def format_countdown(seconds: int) -> str:
    if seconds < 0:
        return "Expired"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f"{days}d {hours}h {minutes}m {seconds}s"


def make_title_from_state(state: RitualState) -> str:
    if state == RitualState.ACTIVE:
        return "✅ Active"
    else:
        return state.name.lower().title()


def format_ritual_status_embed(domain: TACoDomain, ritual: Coordinator.Ritual, state: RitualState) -> Embed:
    """Format the ritual status for Discord as an embed."""

    # Change color based on ritual state
    color_map = {
        'ACTIVE': 0x00FF00,
        'EXPIRED': 0xFF0000,
        'PENDING': 0xFFA500
    }
    pretty_state = make_title_from_state(state)

    embed = Embed(title=f"Ritual ID# {ritual.id} {pretty_state}", description="",
                  color=color_map.get(state.name, 0x3498db))

    embed.add_field(name="\nTime Info", value="---", inline=False)
    embed.add_field(name="Init Timestamp",
                    value=datetime.fromtimestamp(ritual.init_timestamp).strftime('%B %d, %Y at %H:%M:%S UTC'), inline=True)
    embed.add_field(name="End Timestamp",
                    value=datetime.fromtimestamp(ritual.end_timestamp).strftime('%B %d, %Y at %H:%M:%S UTC'), inline=True)
    time_remaining = ritual.end_timestamp - int(datetime.now().timestamp())
    embed.add_field(name="Time Remaining", value=format_countdown(time_remaining), inline=True)

    embed.add_field(name="\nAuthority Info", value="---", inline=False)
    embed.add_field(name="Initiator", value=make_polygon_explorer_link(domain, ritual.initiator), inline=False)
    embed.add_field(name="Authority", value=make_polygon_explorer_link(domain, ritual.authority), inline=False)
    embed.add_field(name="Access Controller", value=make_polygon_explorer_link(domain, ritual.access_controller), inline=False)

    embed.add_field(name="\nTechnical Info", value="---", inline=False)
    embed.add_field(name="M/N", value=f"{ritual.threshold}/{ritual.dkg_size}", inline=True)
    embed.add_field(name="Transcripts Count", value=ritual.total_transcripts, inline=True)
    embed.add_field(name="Aggregation Mismatch", value=ritual.aggregation_mismatch, inline=True)

    # Too much text with links, so break-up participants
    # into blocks of 10 and use short form addresses
    participants: Sequence[Coordinator.Participant] = ritual.participants
    i = 0
    num_participants = len(participants)
    while i < num_participants:
        block_end = min(i + 10, num_participants)  # 10 at a time
        pretty_participants = ", ".join(
            make_polygon_explorer_link(domain, participant.provider, True)
            for participant in participants[i:block_end]
        )
        embed.add_field(name=f"Participants[{i}-{block_end}]", value=pretty_participants, inline=False)

    return embed
