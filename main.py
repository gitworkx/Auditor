from flask import Flask
import os

app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Pong!"

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def hello(ctx):
    await ctx.send('Hello, World!')

if __name__ == '__main__':
    # Start Discord bot
    bot.loop.create_task(app.run_async(host='0.0.0.0', port=os.getenv('PORT', 5000)))
    bot.run(os.getenv('TOKEN'))
