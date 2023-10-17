from datetime import datetime
from typing import Sequence

from discord import Embed
from nucypher.blockchain.eth.agents import CoordinatorAgent

from models import RitualState


def make_polygonscan_link(address: str) -> str:
    return f"[{address}](https://mumbai.polygonscan.com/address/{address})"


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
    if state == RitualState.FINALIZED:
        return "✅ Finalized"
    else:
        return state.name.lower().title()


def format_ritual_status_embed(_id: int, ritual: CoordinatorAgent.Ritual, state: RitualState) -> Embed:
    """Format the ritual status for Discord as an embed."""

    # Change color based on ritual state
    color_map = {
        'ACTIVE': 0x00FF00,
        'EXPIRED': 0xFF0000,
        'PENDING': 0xFFA500
    }
    pretty_state = make_title_from_state(state)

    embed = Embed(title=f"Ritual ID# {_id} {pretty_state}", description="",
                  color=color_map.get(state.name, 0x3498db))

    embed.add_field(name="\nTime Info", value="---", inline=False)
    embed.add_field(name="Init Timestamp",
                    value=datetime.fromtimestamp(ritual.init_timestamp).strftime('%B %d, %Y at %H:%M:%S UTC'), inline=True)
    embed.add_field(name="End Timestamp",
                    value=datetime.fromtimestamp(ritual.end_timestamp).strftime('%B %d, %Y at %H:%M:%S UTC'), inline=True)
    time_remaining = ritual.end_timestamp - int(datetime.now().timestamp())
    embed.add_field(name="Time Remaining", value=format_countdown(time_remaining), inline=True)

    embed.add_field(name="\nAuthority Info", value="---", inline=False)
    embed.add_field(name="Initiator", value=make_polygonscan_link(ritual.initiator), inline=False)
    embed.add_field(name="Authority", value=make_polygonscan_link(ritual.authority), inline=False)
    embed.add_field(name="Access Controller", value=make_polygonscan_link(ritual.access_controller), inline=False)

    embed.add_field(name="\nTechnical Info", value="---", inline=False)
    embed.add_field(name="M/N", value=f"{ritual.threshold}/{ritual.dkg_size}", inline=True)
    embed.add_field(name="Transcripts Count", value=ritual.total_transcripts, inline=True)
    embed.add_field(name="Aggregation Mismatch", value=ritual.aggregation_mismatch, inline=True)

    # Create links for each participant address
    participants: Sequence[CoordinatorAgent.Ritual.Participant] = ritual.participants
    pretty_participants = ", ".join(make_polygonscan_link(participant.provider) for participant in participants)
    embed.add_field(name="Participants", value=pretty_participants, inline=False)

    return embed
