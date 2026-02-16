import discord
from discord import app_commands
from discord.ext import commands
import os

class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Loading environment variables with line break handling
        self.rules_pt = os.getenv('REGRAS_PT', 'Regras não configuradas.').replace('\\n', '\n')
        self.rules_en = os.getenv('REGRAS_EN', 'Rules not configured.').replace('\\n', '\n')

    @app_commands.command(name="rules", description="Displays server rules based on your locale")
    async def rules(self, interaction: discord.Interaction):
        lang = str(interaction.locale)
        
        if lang.startswith("pt"):
            title, content = "📜 Regras do Servidor", self.rules_pt
        else:
            title, content = "📜 Server Rules", self.rules_en
        
        embed = discord.Embed(title=title, description=content, color=discord.Color.blue())
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="ping", description="Checks bot latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: **{latency}ms**")

async def setup(bot):
    await bot.add_cog(Utilities(bot))
