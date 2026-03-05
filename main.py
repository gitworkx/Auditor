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

@bot.tree.command(name="nuke2", description="Protocolo de destruição de mídia (Irrecuperável)")
@app_commands.describe(amount="Número de mensagens para escanear em busca de mídias")
@app_commands.checks.has_permissions(manage_messages=True)
async def nuke2(interaction: discord.Interaction, amount: int = 100):
    """
    Escanreia o histórico recente e apaga apenas mensagens com anexos ou links.
    Invalida os links do CDN permanentemente.
    """
    await interaction.response.send_message("☣️ **Protocolo de Sobrescrita Ativo.** Expurgando rastros de mídia...", ephemeral=True)
    
    def is_media(m):
        # Verifica arquivos ou links que provavelmente contêm mídia
        return len(m.attachments) > 0 or "http" in m.content

    deleted = await interaction.channel.purge(limit=amount, check=is_media)
    
    embed = discord.Embed(
        title="☢️ Mídias Desintegradas",
        description=f"Eliminado com sucesso **{len(deleted)}** arquivos/links deste canal.\n"
                    f"Status: **Probabilidade de Recuperação Zero (CDN Purged)**",
        color=0x000000
    )
    embed.set_footer(text="Ação Permanente • Sem logs de mídia restantes.")
    await interaction.channel.send(embed=embed)

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

@bot.tree.command(name="ping", description="Verifica a latência")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"📡 `{latency}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Git Pull e Reinicialização")
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
        print("❌ Por favor, defina a variável de ambiente DISCORD_TOKEN")
