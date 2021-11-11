import discord
from discord.ext import commands
import os
from requests_html import AsyncHTMLSession
#from datetime import datetime, timedelta

import time
import datetime as dt

from decouple import config

start_time = time.time()

session = AsyncHTMLSession()
path = os.getcwd()
intents = discord.Intents().all()
client = commands.Bot(command_prefix = '!', intents=intents)
client.remove_command('status')

@client.event

async def on_ready():
    print("DataSci Bot is ready")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Crunching the Numbers..."))

@client.command()
async def ping(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    text = str(dt.timedelta(seconds=difference))
    await ctx.send(f"pong! {round(client.latency * 1000)}ms. Uptime: {text}")
    print(text)

@client.command(aliases=['rel'])
async def reload(ctx,extension):
    client.reload_extension(f"cogs.{extension}")
    embed = discord.Embed(title='Reload', description=f'{extension} successfully reloaded', color=0xff00c8)
    await ctx.send(embed=embed)


cogList = ['cogs.music']  # list of cogs

if __name__ == '__main__':
    for ext in cogList:
        client.load_extension(ext)

secret = config('bot')
client.run(secret)