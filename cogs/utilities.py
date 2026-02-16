import discord
from discord import app_commands
from discord.ext import commands
import os

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Load and clean environment variables
        self.rules_pt = os.getenv('REGRAS_PT', 'Regras não configuradas.').replace('\\n', '\n')
        self.rules_en = os.getenv('REGRAS_EN', 'Rules not configured.').replace('\\n', '\n')

    @app_commands.command(name="rules", description="Shows server rules / Exibe as regras do servidor")
    async def rules(self, interaction: discord.Interaction):
        # interaction.locale identifies the user's language
        # pt-BR and pt-PT both start with 'pt'
        is_portuguese = str(interaction.locale).startswith("pt")

        if is_portuguese:
            title = "📜 Regras do Servidor"
            content = self.rules_pt
            footer = f"Solicitado por {interaction.user.display_name}"
        else:
            title = "📜 Server Rules"
            content = self.rules_en
            footer = f"Requested by {interaction.user.display_name}"

        embed = discord.Embed(
            title=title,
            description=content,
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_footer(text=footer)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Check bot latency / Verifica latência")
    async def ping(self, interaction: discord.Interaction):
        is_portuguese = str(interaction.locale).startswith("pt")
        latency = round(self.bot.latency * 1000)
        
        if is_portuguese:
            await interaction.response.send_message(f"🏓 Pong! Latência: **{latency}ms**")
        else:
            await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

async def setup(bot):
    await bot.add_cog(Utilities(bot))
