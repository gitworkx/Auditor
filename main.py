import discord
from discord.ext import commands
import asyncio
import os
import sys

# 1. Configuração de Intents
intents = discord.Intents.default()
intents.message_content = True 

# 2. Inicialização do Bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logado como {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # --- FILTRO NSFW/GORE BÁSICO ---
    # Se o canal NÃO estiver marcado como NSFW
    if not message.channel.nsfw:
        # Se a mensagem contiver anexos (imagens, vídeos, etc)
        if message.attachments:
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, não envie mídias em canais comuns. Use canais NSFW.", delete_after=5)
            return

        # Filtro básico de links (geralmente onde gore/nsfw reside)
        if "http://" in message.content.lower() or "https://" in message.content.lower():
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, links não são permitidos aqui.", delete_after=5)
            return
    # -------------------------------

    await bot.process_commands(message)

    # Deleção automática após 24h
    async def delete_later(msg):
        await asyncio.sleep(86400)
        try:
            await msg.delete()
        except:
            pass

    bot.loop.create_task(delete_later(message))

# 3. Comandos
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def panic(ctx):
    await ctx.send('Panic!')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello there!')

@bot.command()
@commands.is_owner()
async def reload(ctx):
    await ctx.send("🔄 Reiniciando...")
    os.execv(sys.executable, ['python'] + sys.argv)

# 4. Rodar o Bot
token = os.environ.get('TOKEN')
bot.run(token)
