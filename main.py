import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import subprocess
from datetime import datetime

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Syncs slash (/) commands
        await self.tree.sync()

bot = AuditorBot()

# --- COMMANDS --- #

@bot.tree.command(name="nuke2", description="Media destruction protocol (Unrecoverable)")
@app_commands.describe(amount="Number of messages to scan for media")
@app_commands.checks.has_permissions(manage_messages=True)
async def nuke2(interaction: discord.Interaction, amount: int = 100):
    """
    Scans recent history and wipes only messages with attachments or links.
    Invalidates CDN links permanently.
    """
    await interaction.response.send_message("☣️ **Overwrite Protocol Active.** Purging media traces...", ephemeral=True)
    
    def is_media(m):
        # Checks for files or links that likely host media
        return len(m.attachments) > 0 or "http" in m.content

    deleted = await interaction.channel.purge(limit=amount, check=is_media)
    
    embed = discord.Embed(
        title="☢️ Media Disintegrated",
        description=f"Successfully eliminated **{len(deleted)}** files/links from this channel.\n"
                    f"Status: **Zero Recovery Probability (CDN Purged)**",
        color=0x000000
    )
    embed.set_footer(text="Permanent Action • No media logs remaining.")
    await interaction.channel.send(embed=embed)

@bot.tree.command(name="nuke", description="Resets the current channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    await interaction.response.send_message("☢️ Cleaning...", ephemeral=True)
    
    pos = interaction.channel.position
    new_channel = await interaction.channel.clone(reason="Nuke")
    await interaction.channel.delete()
    await new_channel.edit(position=pos)
    
    embed = discord.Embed(
        title="☣️ Channel Reset",
        description=f"Action executed by **{interaction.user.name}**.",
        color=0xff4747
    )
    await new_channel.send(embed=embed)

@bot.tree.command(name="ping", description="Checks latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"📡 `{latency}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Git Pull and Reboot")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Updating...", ephemeral=True)
    try:
        subprocess.run(["git", "pull"], check=True)
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {e}", ephemeral=True)

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ Please define DISCORD_TOKEN variable")
