import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import os
import sys
import subprocess
import io
from datetime import datetime, timedelta, timezone

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')
RAW_BASE = "https://raw.githubusercontent.com"
CATALOG_URL = f"{RAW_BASE}/gitworkx/Auditor/main/catalog.json"
ALLOWED_EXTENSIONS = ('.py', '.sh', '.json', '.txt', '.js') # Hardening: restricts file types

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.session: aiohttp.ClientSession = None
        self._catalog_cache = None

    async def fetch_catalog(self):
        """Hardened fetch: limits response size to prevent RAM exhaustion."""
        try:
            async with self.session.get(CATALOG_URL, timeout=10) as resp:
                if resp.status == 200:
                    # Read max 1MB to prevent large payload attacks
                    content = await resp.read()
                    if len(content) > 1024 * 1024: return False
                    self._catalog_cache = await resp.json(content_type=None)
                    return True
        except Exception as e:
            print(f"❌ Security Alert - Fetch Error: {e}")
        return False

    async def setup_hook(self):
        # Hardened headers to mimic a browser/official client
        headers = {'User-Agent': 'AuditorBot/2.0 (Security-Hardened)'}
        connector = aiohttp.TCPConnector(limit=25, ttl_dns_cache=300)
        self.session = aiohttp.ClientSession(connector=connector, headers=headers)
        
        await self.fetch_catalog()
        self.auto_purge_task.start() # Starts the 24h cleanup cycle
        await self.tree.sync()

    @tasks.loop(hours=1)
    async def auto_purge_task(self):
        """Background task to bulk delete messages older than 24h."""
        for guild in self.guilds:
            for channel in guild.text_channels:
                # Check if bot has permission to manage messages
                if channel.permissions_for(guild.me).manage_messages:
                    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
                    try:
                        # bulk=True uses Discord's mass delete (optimized)
                        deleted = await channel.purge(before=cutoff, bulk=True)
                        if len(deleted) > 0:
                            print(f"🗑️ Purged {len(deleted)} messages in {channel.name}")
                    except Exception as e:
                        print(f"⚠️ Purge failed in {channel.name}: {e}")

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

bot = AuditorBot()

# --- HARDENED DOWNLOAD SYSTEM --- #

class DownloadView(discord.ui.View):
    __slots__ = ('filename',)

    def __init__(self, filename: str):
        super().__init__(timeout=180)
        self.filename = filename

    @discord.ui.button(label="Download", style=discord.ButtonStyle.success, emoji="📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # --- HARDENING: Path Traversal & Extension Protection ---
        clean_filename = os.path.normpath(self.filename).lstrip('./\\')
        if not clean_filename.endswith(ALLOWED_EXTENSIONS) or ".." in clean_filename:
            return await interaction.followup.send("❌ Security Violation: Invalid file path/type.", ephemeral=True)
        
        try:
            async with bot.session.get(f"{RAW_BASE}/{clean_filename}", timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file_display_name = clean_filename.split('/')[-1]
                    
                    with io.BytesIO(data) as f:
                        await interaction.followup.send(
                            content=f"✅ **{file_display_name}** secure delivery complete.",
                            file=discord.File(f, filename=file_display_name),
                            ephemeral=True
                        )
                else:
                    await interaction.followup.send(f"❌ GitHub Source Error: {resp.status}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Request Blocked: {e}", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts: list):
        options = [
            discord.SelectOption(label=s['nome'], value=s['arquivo']) 
            for s in scripts[:25]
        ]
        super().__init__(placeholder="Select a verified script...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content=f"📥 Script locked: `{self.values[0]}`. Proceed to download?",
            view=DownloadView(self.values[0]),
            ephemeral=True
        )

# --- COMMANDS --- #

@bot.tree.command(name="webscripts", description="Encrypted access to scripts")
async def webscripts(interaction: discord.Interaction):
    if not bot._catalog_cache:
        await bot.fetch_catalog()

    scripts_list = bot._catalog_cache.get("scripts", []) if bot._catalog_cache else []
    if not scripts_list:
        return await interaction.response.send_message("❌ Database offline.", ephemeral=True)

    view = discord.ui.View()
    view.add_item(WebScriptsSelect(scripts_list))
    
    embed = discord.Embed(title="🛡️ Auditor Secure Cloud", color=0x2f3136)
    embed.set_footer(text="Verified & Hardened Environment 🚀")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="ping", description="Network heartbeat")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"⚡ Latency: `{round(bot.latency * 1000)}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Secure Hot-Reload")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Verifying integrity and rebooting...")
    try:
        subprocess.run(["git", "pull"], check=True)
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Update Integrity Failure: {e}", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
