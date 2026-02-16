import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Auto-load all files from /cogs directory
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')
        
        await self.tree.sync()
        print(f"✅ Logged in as {self.user} | Commands synced.")

bot = AuditorBot()

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("🚫 **Error:** You need `Manage Channels` permission.", ephemeral=True)
    else:
        print(f"Command Error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("⚠️ An unexpected error occurred.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
