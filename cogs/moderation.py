import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nuke", description="Purge all messages in this channel / Limpa o canal")
    @app_commands.rename(nuke="limpar")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def nuke(self, interaction: discord.Interaction):
        is_pt = str(interaction.locale).startswith("pt")
        
        # Resposta inicial discreta
        await interaction.response.send_message("⏳ ...", ephemeral=True)
        
        channel = interaction.channel
        pos = channel.position
        
        # Operação de Nuke
        new_channel = await channel.clone(reason=f"Nuke: {interaction.user}")
        await channel.delete()
        await new_channel.edit(position=pos)
        
        embed = discord.Embed(
            title="☢️ " + ("Canal Purificado" if is_pt else "Channel Purified"),
            description=(
                f"Toda a radiação foi removida por {interaction.user.mention}." if is_pt 
                else f"All radiation removed by {interaction.user.mention}."
            ),
            color=0xff4747
        )
        embed.set_image(url="https://i.imgur.com") # Gif de explosão (opcional)
        
        await new_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
