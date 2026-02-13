import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import sys
import subprocess
import io

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')
RAW_BASE = "https://raw.githubusercontent.com"
# Repositório oficial fornecido: WebScripts
CATALOG_URL = "https://raw.githubusercontent.com"
ALLOWED_EXTENSIONS = ('.py', '.sh', '.json', '.txt', '.js', '.lua')

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.session: aiohttp.ClientSession = None
        self._catalog_cache = None

    async def fetch_catalog(self):
        """Fetches the catalog and stores it in memory."""
        try:
            async with self.session.get(CATALOG_URL, timeout=10) as resp:
                if resp.status == 200:
                    self._catalog_cache = await resp.json(content_type=None)
                    print(f"✅ Catalog loaded from WebScripts: {len(self._catalog_cache.get('scripts', []))} items.")
                    return True
                else:
                    print(f"❌ Catalog error: Status {resp.status}")
        except Exception as e:
            print(f"❌ Connection error: {e}")
        return False

    async def setup_hook(self):
        connector = aiohttp.TCPConnector(limit=50)
        self.session = aiohttp.ClientSession(connector=connector)
        await self.fetch_catalog()
        await self.tree.sync()

bot = AuditorBot()

# --- FASTEST CLEANUP METHOD (NUKE) --- #

async def nuke_channel(channel: discord.TextChannel):
    """Clones the channel and deletes the old one for instant wiping."""
    if not channel.permissions_for(channel.guild.me).manage_channels:
        return None
    
    # Clone permissions, slowmode, category, etc.
    new_channel = await channel.clone(reason="Nuke/Instant Wipe")
    await new_channel.edit(position=channel.position)
    await channel.delete(reason="Nuke/Instant Wipe")
    return new_channel

# --- COMMANDS --- #

@bot.tree.command(name="nuke_channel", description="Instantly wipes THIS channel (Cloning method)")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke_this(interaction: discord.Interaction):
    # Cannot be ephemeral because the channel will be destroyed
    await interaction.response.send_message("☢️ **NUKING CHANNEL...**")
    await nuke_channel(interaction.channel)

@bot.tree.command(name="nuke_server", description="Instantly wipes ALL OTHER text channels")
@app_commands.checks.has_permissions(administrator=True)
async def nuke_all(interaction: discord.Interaction):
    await interaction.response.send_message("🚨 **SERVER WIPE INITIATED...**", ephemeral=True)
    
    current_id = interaction.channel_id
    for channel in interaction.guild.text_channels:
        if channel.id != current_id:
            try:
                await nuke_channel(channel)
            except:
                continue
    
    await interaction.followup.send("🛡️ All secondary channels have been reset.", ephemeral=True)

# --- SCRIPTS SYSTEM --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename: str):
        super().__init__(timeout=180)
        self.filename = filename

    @discord.ui.button(label="Download", style=discord.ButtonStyle.success, emoji="📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        # Security hardening: ensure we only get the file from the WebScripts repo
        file_url = f"https://raw.githubusercontent.com{self.filename}"
        
        try:
            async with bot.session.get(file_url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file_name = self.filename.split('/')[-1]
                    with io.BytesIO(data) as f:
                        await interaction.followup.send(
                            content=f"✅ **{file_name}** delivered from WebScripts.",
                            file=discord.File(f, filename=file_name),
                            ephemeral=True
                        )
                else:
                    await interaction.followup.send(f"❌ File not found (Status {resp.status})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {e}", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts: list):
        options = [
            discord.SelectOption(label=s['nome'], description=s.get('descricao', '')[:50], value=s['arquivo']) 
            for s in scripts[:25]
        ]
        super().__init__(placeholder="Select a verified script...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            content=f"📥 **Script:** `{self.values[0]}`",
            view=DownloadView(self.values[0]),
            ephemeral=True
        )

@bot.tree.command(name="webscripts", description="Access the WebScripts catalog")
async def webscripts(interaction: discord.Interaction):
    if not bot._catalog_cache:
        await bot.fetch_catalog()

    if not bot._catalog_cache:
        return await interaction.response.send_message("❌ Database offline. Verify GitHub RAW link.", ephemeral=True)

    scripts_list = bot._catalog_cache.get("scripts", [])
    view = discord.ui.View()
    view.add_item(WebScriptsSelect(scripts_list))
    
    embed = discord.Embed(title="🛡️ WebScripts Secure Cloud", color=0x2b2d31)
    embed.set_footer(text="Verified Repository: gitworkx/WebScripts")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# --- ADMIN --- #

@bot.tree.command(name="ping", description="Check latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"⚡ Latency: `{round(bot.latency * 1000)}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Git Pull & Cache Reset")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Synchronizing with WebScripts...")
    subprocess.run(["git", "pull"], check=True)
    await bot.fetch_catalog() # Força recarga do JSON após o update
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot.run(TOKEN)
