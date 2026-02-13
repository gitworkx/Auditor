import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import subprocess
from datetime import datetime

# --- CONFIGURAÇÃO --- #
TOKEN = os.getenv('DISCORD_TOKEN')

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Sincroniza os comandos de barra (/)
        await self.tree.sync()

bot = AuditorBot()

# --- COMANDOS --- #

@bot.tree.command(name="nuke", description="Reseta o canal atual")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ Limpando...", ephemeral=True)
    
    pos = interaction.channel.position
    new_channel = await interaction.channel.clone(reason="Nuke")
    await interaction.channel.delete()
    await new_channel.edit(position=pos)
    
    embed = discord.Embed(
        title="☣️ Canal Resetado",
        description=f"Ação executada por **{interaction.user.name}**.",
        color=0xff4747
    )
    await new_channel.send(embed=embed)

@bot.tree.command(name="ping", description="Verifica latência")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"📡 `{latency}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Git Pull e Reboot")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Atualizando...", ephemeral=True)
    try:
        subprocess.run(["git", "pull"], check=True)
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro: {e}", ephemeral=True)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Defina a variável DISCORD_TOKEN")
