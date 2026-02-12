import discord
from discord.ext import commands
import asyncio
import os
import sys

# --- CONFIGURAÇÃO ---
# Cole seu token entre as aspas abaixo:
TOKEN = "MTQ3MTUwMDI3NDUxNzY3MjExOA.GglrVv.vRSc3QoxOeVsE1rwaAmkE3gwHwSX-QvhTR3roQ" 

intents = discord.Intents.default()
intents.message_content = True 

auditor = commands.Bot(command_prefix='!', intents=intents)

@auditor.event
async def on_ready():
    print(f'🕵️‍♂️ Auditor pronto para serviço!')
    await auditor.change_presence(activity=discord.Game(name="Monitorando canais"))

async def auto_delete_24h(msg):
    await asyncio.sleep(86400)
    try:
        await msg.delete()
    except:
        pass

@auditor.event
async def on_message(message):
    if message.author.bot:
        return

    # Filtro de Segurança com Interface Melhorada
    if hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
        if message.attachments or "http" in message.content.lower():
            try:
                await message.delete()
                embed = discord.Embed(
                    description=f"⚠️ {message.author.mention}, links e mídias só são permitidos em canais **NSFW**.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=7)
                return 
            except discord.Forbidden:
                pass

    auditor.loop.create_task(auto_delete_24h(message))
    await auditor.process_commands(message)

# --- COMANDOS COM VISUAL MELHORADO ---

@auditor.command()
async def ping(ctx):
    embed = discord.Embed(
        title="📡 Status de Conexão",
        description=f"Latência: **{round(auditor.latency * 1000)}ms**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@auditor.command()
async def status(ctx):
    embed = discord.Embed(
        title="🛡️ Auditor",
        description="Sistema operacional.\n• Filtro de links/mídia: **Ativo**\n• Limpeza 24h: **Ativa**",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@auditor.command()
@commands.is_owner()
async def reload(ctx):
    await ctx.send("🔄 **Auditor:** Reiniciando módulos...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

# Inicialização
if __name__ == "__main__":
    if TOKEN != "SEU_TOKEN_AQUI":
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: Você esqueceu de colocar o TOKEN no código!")
