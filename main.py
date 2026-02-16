import discord
from discord.ext import commands
from discord import app_commands
import os

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')

class AuditorBot(commands.Bot):
    def __init__(self):
        # Setting up intents for full functionality
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        """
        Executed when the bot starts. 
        Automatically loads all Cogs from the /cogs directory.
        """
        # Ensure the 'cogs' directory exists before iterating
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"📦 Extension loaded: {filename}")
                    except Exception as e:
                        print(f"❌ Failed to load extension {filename}: {e}")
        
        # Syncs Slash Commands globally
        await self.tree.sync()
        print(f"✅ Logged in as {self.user} | Commands synced.")

bot = AuditorBot()

# --- GLOBAL ERROR HANDLING --- #
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
    Global error handler that detects user locale (PT/EN).
    """
    is_portuguese = str(interaction.locale).startswith("pt")

    if isinstance(error, app_commands.MissingPermissions):
        msg = (
            "🚫 **Erro:** Você precisa da permissão `Gerenciar Canais` para usar isso." 
            if is_portuguese else 
            "🚫 **Error:** You need `Manage Channels` permission to use this."
        )
        await interaction.response.send_message(msg, ephemeral=True)
    
    else:
        # Logs the error to the console for debugging
        print(f"Command Error: {error}")
        
        if not interaction.response.is_done():
            err_msg = (
                "⚠️ Ocorreu um erro inesperado." 
                if is_portuguese else 
                "⚠️ An unexpected error occurred."
            )
            await interaction.response.send_message(err_msg, ephemeral=True)

# --- INITIALIZATION --- #
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN environment variable not found.")
