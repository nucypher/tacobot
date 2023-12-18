import os

import discord
from dotenv import load_dotenv

from agents import cache_agents
from commands import _COMMANDS

load_dotenv()
_intents = discord.Intents.all()
client = discord.Client(intents=_intents)


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    action = message.content.split()[0].lstrip('!')
    if action in _COMMANDS:
        await _COMMANDS[action](message)
        return
    else:
        # let the bot ignore messages that may not be commands.
        pass


if __name__ == "__main__":
    infura_api_key = os.getenv('INFURA_API_KEY')
    endpoints = {
        137: f"https://polygon-mainnet.infura.io/v3/{infura_api_key}",
        80001: f"https://polygon-mumbai.infura.io/v3/{infura_api_key}"
    }
    cache_agents(endpoints)
    client.run(os.getenv('DISCORD_TOKEN'))
