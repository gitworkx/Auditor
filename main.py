import discord
from discord.ext import commands
from discord import app_commands # Import necessário para Slash Commands
import asyncio
import os
import sys

TOKEN = os.getenv('DISCORD_TOKEN') 

intents = discord.Intents.default()
intents.message_content = True 

auditor = commands.Bot(command_prefix='!', intents=intents)

@auditor.event
async def on_ready():
    print(f'🕵️‍♂️ Auditor pronto para serviço!')
    await auditor.change_presence(activity=discord.Game(name="Monitorando protocolos"))
    
    # Sincroniza os comandos de barra com o servidor do Discord
    try:
        synced = await auditor.tree.sync()
        print(f"📡 {len(synced)} comandos de barra sincronizados!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

# --- COMANDO HÍBRIDO (PREFIXO E BARRA) ---

# Comando de Texto (!ping)
@auditor.command(name="ping")
async def ping_prefix(ctx):
    latencia = round(auditor.latency * 1000)
    embed = discord.Embed(
        title="📡 Latência de Rede",
        description=f"O Auditor está operando a **{latencia}ms**",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed)

# Comando de Barra (/ping)
@auditor.tree.command(name="ping", description="Verifica a latência do Auditor")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(auditor.latency * 1000)
    embed = discord.Embed(
        title="📡 Latência de Rede",
        description=f"O Auditor está operando a **{latencia}ms**",
        color=discord.Color.blue()
    )
    # Em comandos de barra, usamos 'interaction.response.send_message'
    await interaction.response.send_message(embed=embed)

# --- RESTANTE DO CÓDIGO (on_message, etc) ---
@auditor.event
async def on_message(message):
    if message.author.bot:
        return

    if hasattr(message.channel, "is_nsfw") and not message.channel.is_nsfw():
        if message.attachments or "http" in message.content.lower():
            try:
                await message.delete()
                embed = discord.Embed(
                    description=f"⚠️ {message.author.mention}, links e mídias são restritos aos canais **NSFW**.",
                    color=discord.Color.red()
                )
                await message.channel.send(embed=embed, delete_after=7)
                return 
            except:
                pass

    await auditor.process_commands(message)

if __name__ == "__main__":
    if TOKEN:
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: TOKEN não encontrado.")
