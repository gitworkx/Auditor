import discord
from discord.ext import commands
import asyncio
import os
import sys

# Puxa o token das variáveis de ambiente do sistema/hospedagem
TOKEN = os.getenv('MTQ3MTUwMDI3NDUxNzY3MjExOA.GglrVv.vRSc3QoxOeVsE1rwaAmkE3gwHwSX-QvhTR3roQ') 

intents = discord.Intents.default()
intents.message_content = True 

auditor = commands.Bot(command_prefix='!', intents=intents)

@auditor.event
async def on_ready():
    print(f'🕵️‍♂️ Auditor pronto para serviço!')
    await auditor.change_presence(activity=discord.Game(name="Monitorando protocolos"))

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

    # Filtro de Auditoria (Canais não-NSFW)
    if hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
        if message.attachments or "http" in message.content.lower():
            try:
                await message.delete()
                embed = discord.Embed(
                    description=f"⚠️ {message.author.mention}, links e mídias são restritos aos canais **NSFW**.",
                    color=discord.Color.from_rgb(255, 0, 0)
                )
                await message.channel.send(embed=embed, delete_after=7)
                return 
            except discord.Forbidden:
                pass

    auditor.loop.create_task(auto_delete_24h(message))
    await auditor.process_commands(message)

@auditor.command()
async def ping(ctx):
    embed = discord.Embed(
        title="📡 Latência de Rede",
        description=f"O Auditor está operando a **{round(auditor.latency * 1000)}ms**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

@auditor.command()
async def status(ctx):
    embed = discord.Embed(
        title="🛡️ Relatório do Auditor",
        color=discord.Color.gold()
    )
    embed.add_field(name="Monitoramento", value="✅ Ativo", inline=True)
    embed.add_field(name="Limpeza 24h", value="✅ Ativa", inline=True)
    embed.set_footer(text="Proteção de integridade do servidor")
    await ctx.send(embed=embed)

@auditor.command()
@commands.is_owner()
async def reload(ctx):
    await ctx.send("🔄 **Auditor:** Reiniciando módulos do sistema...")
    os.execv(sys.executable, [sys.executable] + sys.argv)

if __name__ == "__main__":
    if TOKEN:
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: DISCORD_TOKEN não configurado nas variáveis de ambiente.")
