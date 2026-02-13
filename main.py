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
        await self.tree.sync()
        print(f"✅ Comandos sincronizados para {self.user}")

bot = AuditorBot()

# --- COMANDOS --- #

@bot.tree.command(name="nuke", description="Limpa e reseta o canal atual")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    """Clona o canal atual, deleta o antigo e recria na mesma posição."""
    await interaction.response.send_message("☢️ Iniciando limpeza...", ephemeral=True)
    
    channel = interaction.channel
    pos = channel.position
    
    # Operação de clonagem
    new_channel = await channel.clone(reason=f"Nuke por {interaction.user}")
    await channel.delete()
    await new_channel.edit(position=pos)
    
    embed = discord.Embed(
        title="☣️ Canal Resetado",
        description=f"Este canal foi purificado por **{interaction.user.name}**.",
        color=0xff4747,
        timestamp=datetime.now()
    )
    await new_channel.send(embed=embed)

@bot.tree.command(name="ping", description="Verifica a latência do sistema")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    color = 0x43b581 if latency < 100 else 0xfaa61a
    
    embed = discord.Embed(
        description=f"📡 **Latência do Gateway:** `{latency}ms`", 
        color=color
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="update", description="Puxa atualizações do Git e reinicia")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Atualizando arquivos e reiniciando...", ephemeral=True)
    
    try:
        subprocess.run(["git", "pull"], check=True)
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro ao atualizar: {e}", ephemeral=True)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Erro: DISCORD_TOKEN não encontrado nas variáveis de ambiente.")
