import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os
import sys
import subprocess
import io
from datetime import datetime

# --- CONFIGURATION --- #
TOKEN = os.getenv('DISCORD_TOKEN')
RAW_BASE = "https://raw.githubusercontent.com"
CATALOG_URL = f"{RAW_BASE}/catalog.json"

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.session: aiohttp.ClientSession = None
        self._catalog_cache = None

    async def fetch_catalog(self):
        try:
            async with self.session.get(CATALOG_URL, timeout=10) as resp:
                if resp.status == 200:
                    self._catalog_cache = await resp.json(content_type=None)
                    return True
        except Exception as e:
            print(f"❌ Connection error: {e}")
        return False

    async def setup_hook(self):
        connector = aiohttp.TCPConnector(limit=50)
        self.session = aiohttp.ClientSession(connector=connector)
        await self.fetch_catalog()
        await self.tree.sync()

bot = AuditorBot()

# --- STYLIZED UI COMPONENTS --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename: str):
        super().__init__(timeout=180)
        self.filename = filename

    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.blurple, emoji="<:download:1234567890> 📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        file_url = f"{RAW_BASE}/{self.filename}"
        
        try:
            async with bot.session.get(file_url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    file_name = self.filename.split('/')[-1]
                    with io.BytesIO(data) as f:
                        embed = discord.Embed(
                            description=f"✅ **{file_name}** successfully retrieved from the cloud.",
                            color=0x43b581 # Green
                        )
                        await interaction.followup.send(embed=embed, file=discord.File(f, filename=file_name), ephemeral=True)
                else:
                    await interaction.followup.send("❌ **Source Error:** File not found on GitHub.", ephemeral=True)
        except Exception:
            await interaction.followup.send("⚠️ **Network Error:** Could not reach the cloud.", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts: list):
        options = [
            discord.SelectOption(
                label=s['nome'], 
                description=s.get('descricao', 'No description provided.')[:50], 
                emoji="📄",
                value=s['arquivo']
            ) for s in scripts[:25]
        ]
        super().__init__(placeholder="📂 Browse our secure script library...", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📥 Ready to Download",
            description=f"You selected: `{self.values[0]}`\n\nClick the button below to receive your encrypted file.",
            color=0x5865f2 # Blurple
        )
        await interaction.response.send_message(embed=embed, view=DownloadView(self.values[0]), ephemeral=True)

# --- BEAUTIFIED COMMANDS --- #

@bot.tree.command(name="webscripts", description="Access the premium WebScripts library")
async def webscripts(interaction: discord.Interaction):
    if not bot._catalog_cache: await bot.fetch_catalog()

    if not bot._catalog_cache:
        return await interaction.response.send_message("❌ **System Offline:** Could not sync with database.", ephemeral=True)

    scripts_list = bot._catalog_cache.get("scripts", [])
    
    embed = discord.Embed(
        title="🛡️ WebScripts Cloud Storage",
        description="Welcome to the secure repository. Select a verified tool from the dropdown menu below to begin.",
        color=0x2b2d31 # Dark Mode Gray
    )
    embed.add_field(name="Total Scripts", value=f"📊 `{len(scripts_list)}` available", inline=True)
    embed.add_field(name="System Status", value="🟢 `Operational`", inline=True)
    embed.set_image(url="https://i.imgur.com") # Opcional: Adicione um banner
    embed.set_footer(text="Verified Repository: gitworkx/WebScripts • 2026", icon_url=bot.user.display_avatar.url)

    view = discord.ui.View()
    view.add_item(WebScriptsSelect(scripts_list))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="nuke", description="☢️ Instant wipe this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    channel = interaction.channel
    await interaction.response.send_message("☢️ **NUKING...**", ephemeral=True)
    
    new_channel = await channel.clone(reason="Manual Nuke")
    await new_channel.edit(position=channel.position)
    await channel.delete()
    
    # Envia mensagem estilizada no canal NOVO
    final_embed = discord.Embed(
        title="☣️ Channel Reset",
        description=f"This channel was wiped by **{interaction.user.name}**.\nAll traces have been removed.",
        color=0xff4747,
        timestamp=datetime.now()
    )
    final_embed.set_image(url="https://media.giphy.com")
    await new_channel.send(embed=final_embed)

@bot.tree.command(name="ping", description="Check system heartbeat")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    color = 0x43b581 if latency < 100 else 0xfaa61a
    embed = discord.Embed(description=f"📡 **Gateway Latency:** `{latency}ms`", color=color)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="update", description="Push updates and clear cache")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    embed = discord.Embed(description="🔄 **Synchronizing files and rebooting...**", color=0x5865f2)
    await interaction.response.send_message(embed=embed, ephemeral=True)
    
    subprocess.run(["git", "pull"], check=True)
    await bot.fetch_catalog()
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot.run(TOKEN)
