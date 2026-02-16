import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nuke", description="Resets the current channel (deletes and recreates)")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.guild_only()
    async def nuke(self, interaction: discord.Interaction):
        await interaction.response.send_message("☢️ Executing total cleanup...", ephemeral=True)
        
        channel = interaction.channel
        pos = channel.position
        
        # Clone channel and delete old one
        new_channel = await channel.clone(reason=f"Nuke requested by {interaction.user}")
        await channel.delete()
        await new_channel.edit(position=pos)
        
        embed = discord.Embed(
            title="☣️ Channel Reset",
            description=f"This channel has been purified by **{interaction.user.mention}**.",
            color=0xff4747,
            timestamp=discord.utils.utcnow()
        )
        await new_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
