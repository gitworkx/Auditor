import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import subprocess
from datetime import datetime

# --- CONFIGURAÇÃO --- #
TOKEN = os.getenv('DISCORD_TOKEN')
# Puxa as regras das variáveis de ambiente (injetadas pelo Workflow)
REGRAS_PT = os.getenv('REGRAS_PT', 'Regras em português não configuradas.')
REGRAS_EN = os.getenv('REGRAS_EN', 'English rules not configured.')

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

@bot.tree.command(name="regras", description="Exibe as regras do servidor")
@app_commands.describe(idioma="Escolha o idioma das regras")
@app_commands.choices(idioma=[
    app_commands.Choice(name="Português", value="pt"),
    app_commands.Choice(name="English", value="en")
])
async def regras(interaction: discord.Interaction, idioma: app_commands.Choice[str]):
    # Seleciona o conteúdo baseado na escolha
    conteudo = REGRAS_PT if idioma.value == "pt" else REGRAS_EN
    titulo = "📜 Regras do Servidor" if idioma.value == "pt" else "📜 Server Rules"
    
    # Substitui eventuais '\n' literais por quebras de linha reais
    conteudo_formatado = conteudo.replace('\\n', '\n')
    
    embed = discord.Embed(
        title=titulo,
        description=conteudo_formatado,
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Solicitado por {interaction.user.name}")
    
    # Enviamos como ephemeral=True para manter a privacidade ou False para todos verem
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Verifica latência")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message
