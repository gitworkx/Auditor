import discord
from discord.ext import commands
import asyncio
import os
import sys

# 1. Configuração de Intents
intents = discord.Intents.default()
intents.message_content = True  # Necessário para ler mensagens e comandos

# 2. Inicialização do Bot
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logado com sucesso como {bot.user}!')

@bot.event
async def on_message(message):
    # Ignora mensagens do próprio bot
    if message.author == bot.user:
        return

    # IMPORTANTE: Permite que os comandos (!ping, etc) funcionem
    await bot.process_commands(message)

    # Feature de deleção automática após 24h (sem travar o bot)
    async def delete_later(msg):
        await asyncio.sleep(86400)  # 24 horas
        try:
            await msg.delete()
        except Exception as e:
            print(f"Erro ao deletar mensagem: {e}")

    # Cria a tarefa em background
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
@commands.is_owner() # Apenas o dono do bot pode usar
async def reload(ctx):
    """Reinicia o bot para aplicar alterações de código"""
    await ctx.send("🔄 Reiniciando o bot... Aguarde.")
    os.execv(sys.executable, ['python'] + sys.argv)

@reload.error
async def reload_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.send("❌ Você não tem permissão para reiniciar o bot.")

# 4. Rodar o Bot usando o Secret do Replit
token = os.environ.get('TOKEN')
if token:
    bot.run(token)
else:
    print("ERRO: O Token não foi encontrado nos Secrets do Replit!")
