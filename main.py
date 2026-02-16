import discord
from discord.ext import commands
from discord import app_commands
import os

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')

class AuditorBot(commands.Bot):
    def __init__(self):
        # Intents are required for message content and guild interactions
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        """
        Executed when the bot starts. 
        Automatically loads all Cogs from the /cogs directory.
        """
        if os.path.exists('./cogs'):
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    try:
                        await self.load_extension(f'cogs.{filename[:-3]}')
                        print(f"📦 Extension loaded: {filename}")
                    except Exception as e:
                        print(f"❌ Failed to load extension {filename}: {e}")
        
        # Important: Syncs the tree to apply @app_commands.rename (localization)
        await self.tree.sync()
        print(f"✅ Logged in as {self.user} | Commands & Translations synced.")

bot = AuditorBot()

# --- GLOBAL ERROR HANDLING (Bilingual) --- #
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """
    Handles errors globally and responds in the user's language.
    """
    is_pt = str(interaction.locale).startswith("pt")

    if isinstance(error, app_commands.MissingPermissions):
        msg = (
            "🚫 **Erro:** Você não tem a permissão `Gerenciar Canais` para usar este comando." 
            if is_pt else 
            "🚫 **Error:** You lack `Manage Channels` permission to use this command."
        )
        await interaction.response.send_message(msg, ephemeral=True)
    
    elif isinstance(error, app_commands.CommandOnCooldown):
        msg = (
            f"⏳ **Cooldown:** Tente novamente em {error.retry_after:.2f}s." 
            if is_pt else 
            f"⏳ **Cooldown:** Try again in {error.retry_after:.2f}s."
        )
        await interaction.response.send_message(msg, ephemeral=True)

    else:
        # Logs the specific error for you to see in GitHub Actions
        print(f"Command Error: {error}")
        
        if not interaction.response.is_done():
            err_msg = (
                "⚠️ **Erro Crítico:** Algo deu errado na execução." 
                if is_pt else 
                "⚠️ **Critical Error:** Something went wrong during execution."
            )
            await interaction.response.send_message(err_msg, ephemeral=True)

# --- BOT INITIALIZATION --- #
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ CRITICAL: DISCORD_TOKEN not found in environment variables.")
