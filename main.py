import discord
from discord.ext import commands

# Ensure you have enabled 'Message Content Intent' in the Discord Dev Portal
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run('MTQ3MTUwMDI3NDUxNzY3MjExOA.GglrVv.vRSc3QoxOeVsE1rwaAmkE3gwHwSX-QvhTR3roQ')