from datetime import datetime
from typing import List

from discord import Embed
from nucypher.blockchain.eth import domains
from nucypher.blockchain.eth.domains import ChainInfo, PolygonChain, TACoDomain
from nucypher.blockchain.eth.models import Coordinator, SigningCoordinator

from models import RitualState, SigningRitualState


def _short_form(address: str):
    return address[:8]


def make_etherscan_explorer_link(domain: TACoDomain, address: str, short_form: bool = False) -> str:
    address_to_use = _short_form(address) if short_form else address
    if domain == domains.MAINNET:
        return f"[{address_to_use}](https://etherscan.io/address/{address})"
    else:
        return f"[{address_to_use}](https://sepolia.etherscan.io/address/{address})"


def make_polygon_explorer_link(domain: TACoDomain, address: str, short_form: bool = False) -> str:
    address_to_use = _short_form(address) if short_form else address
    if domain == domains.MAINNET:
        return f"[{address_to_use}](https://polygonscan.com/address/{address})"
    else:
        return f"[{address_to_use}](https://amoy.polygonscan.com/address/{address})"


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


def add_participants(embed: Embed,
                     domain: TACoDomain,
                     chain_info: ChainInfo,
                     participant_addresses: List[str]) -> None:
    """Format a list of participants into a string."""
    make_link = make_polygon_explorer_link if isinstance(chain_info, PolygonChain) else make_etherscan_explorer_link

    num_participants = len(participant_addresses)
    i = 0
    while i < num_participants:
        block_end = min(i + 10, num_participants)  # 10 at a time
        pretty_participants = ", ".join(
            make_link(domain, participant, True) for participant in
            participant_addresses[i:block_end]
        )
        embed.add_field(name=f"Participants[{i}-{block_end}]", value=pretty_participants,
                        inline=False)
        i = block_end


#
# DKG Ritual
#
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
    participant_addresses = ritual.providers
    add_participants(embed, domain, domain.polygon_chain, participant_addresses)

    return embed


#
# Network Status
#
def format_network_status_embed(total_nodes: int, results: list) -> Embed:
    """Format the network status for Discord as an embed."""
    embed = Embed(title=f"Network Status", description=f"Number of nodes: {total_nodes}", color=0x3498db)

    for version, count in results:
        percentage = count * 100 / total_nodes
        embed.add_field(name=f"Version {version}", value=f"{count} nodes ({percentage:.1f}%)", inline=False)

    return embed


#
# Signing Ritual
#
def make_signing_cohort_title_from_state(state: SigningRitualState) -> str:
    if state == SigningRitualState.ACTIVE:
        return "✅ Active"
    return state.name.lower().title()


def format_signing_ritual_embed(
        domain: TACoDomain,
        signing_cohort: SigningCoordinator.SigningCohort,
        state: SigningRitualState
) -> Embed:
    color_map = {
        'ACTIVE': 0x00FF00,
        'EXPIRED': 0xFF0000,
        'PENDING': 0xFFA500
    }
    pretty_state = make_signing_cohort_title_from_state(state)

    embed = Embed(title=f"Cohort ID# {signing_cohort.id} {pretty_state}", description="",
                  color=color_map.get(state.name, 0x3498db))

    embed.add_field(name="\nTime Info", value="---", inline=False)
    embed.add_field(name="Init Timestamp",
                    value=datetime.fromtimestamp(signing_cohort.init_timestamp).strftime(
                        '%B %d, %Y at %H:%M:%S UTC'), inline=True)
    embed.add_field(name="End Timestamp",
                    value=datetime.fromtimestamp(signing_cohort.end_timestamp).strftime(
                        '%B %d, %Y at %H:%M:%S UTC'), inline=True)
    time_remaining = signing_cohort.end_timestamp - int(datetime.now().timestamp())
    embed.add_field(name="Time Remaining", value=format_countdown(time_remaining), inline=True)

    embed.add_field(name="\nAuthority Info", value="---", inline=False)
    embed.add_field(name="Initiator", value=make_etherscan_explorer_link(domain, signing_cohort.initiator),
                    inline=False)
    embed.add_field(name="Authority", value=make_etherscan_explorer_link(domain, signing_cohort.authority),
                    inline=False)
    embed.add_field(name="\nTechnical Info", value="---", inline=False)
    embed.add_field(name="M/N", value=f"{signing_cohort.threshold}/{signing_cohort.num_signers}", inline=True)
    embed.add_field(name="Signatures Count", value=signing_cohort.total_signatures, inline=True)
    embed.add_field(name="Chain(s)", value=", ".join(str(c) for c in signing_cohort.chains), inline=True)

    # Too much text with links, so break-up participants
    # into blocks of 10 and use short form addresses
    participant_addresses = [p.provider for p in signing_cohort.signers]
    add_participants(embed, domain, domain.eth_chain, participant_addresses)

    return embed
