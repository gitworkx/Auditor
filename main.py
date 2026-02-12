import discord
from discord.ext import commands
import asyncio
import os

# 1. Configuração de Intents (Importante: Ative "Message Content Intent" no Discord Developer Portal)
intents = discord.Intents.default()
intents.message_content = True 

# 2. Uso do commands.Bot para os comandos funcionarem
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot está online como {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # IMPORTANTE: Permite que os comandos (!ping, etc) funcionem junto com o on_message
    await bot.process_commands(message)

    # Deletar após 24h em segundo plano (sem travar o bot)
    async def delayed_delete(msg):
        await asyncio.sleep(86400)
        try:
            await msg.delete()
        except Exception as e:
            print(f"Erro ao deletar: {e}")

    bot.loop.create_task(delayed_delete(message))

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def panic(ctx):
    await ctx.send('Panic!')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello there!')

# 3. Rodando o bot com a variável de ambiente do Replit
# No Replit, vá em "Secrets" (ícone do cadeado) e adicione:
# Key: TOKEN
# Value: seu_token_aqui
token = os.environ.get('TOKEN')
bot.run(token)
