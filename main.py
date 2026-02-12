import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- TRUQUE PARA FICAR ONLINE ---
app = Flask('')

@app.route('/')
def home():
    return "Bot está vivo!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# --------------------------------

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logado como {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Liga o servidor web e depois o bot
keep_alive()
token = os.getenv('DISCORD_TOKEN')
bot.run(token)
