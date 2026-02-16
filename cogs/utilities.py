import discord
from discord import app_commands
from discord.ext import commands
import os

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rules_pt = os.getenv('REGRAS_PT', '❌ Não configurado.').replace('\\n', '\n')
        self.rules_en = os.getenv('REGRAS_EN', '❌ Not configured.').replace('\\n', '\n')

    @app_commands.command(
        name="rules", 
        description="View the server rules / Ver as regras do servidor"
    )
    # Define as traduções do NOME do comando na lista do /
    @app_commands.rename(rules="regras")
    async def rules(self, interaction: discord.Interaction):
        is_pt = str(interaction.locale).startswith("pt")
        
        embed = discord.Embed(
            title="📜 " + ("Regras do Servidor" if is_pt else "Server Rules"),
            description=self.rules_pt if is_pt else self.rules_en,
            color=0x2b2d31 # Cor elegante (Dark Mode Grey)
        )
        
        embed.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"Requested by: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Check bot stability / Ver estabilidade")
    @app_commands.rename(ping="latencia")
    async def ping(self, interaction: discord.Interaction):
        is_pt = str(interaction.locale).startswith("pt")
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="📡 " + ("Status da Conexão" if is_pt else "Connection Status"),
            description=f"**Latency:** `{latency}ms`" if not is_pt else f"**Latência:** `{latency}ms`",
            color=0x2ecc71 if latency < 150 else 0xf1c40f
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utilities(bot))
