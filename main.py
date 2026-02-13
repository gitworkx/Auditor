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
        except Exception: return False

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        await self.fetch_catalog()
        await self.tree.sync()

bot = AuditorBot()

# --- AUTOMATIC LOCALIZATION ENGINE --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename: str, locale: discord.Locale):
        super().__init__(timeout=180)
        self.filename = filename
        # Detecta se o usuário usa PT-BR, caso contrário, Inglês
        self.is_pt = locale == discord.Locale.brazil_portuguese

    @discord.ui.button(label="Get Script", style=discord.ButtonStyle.blurple)
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            async with bot.session.get(f"{RAW_BASE}/{self.filename}") as resp:
                if resp.status == 200:
                    data = await resp.read()
                    msg = "✅ Arquivo enviado!" if self.is_pt else "✅ File delivered!"
                    await interaction.followup.send(content=msg, file=discord.File(io.BytesIO(data), filename=self.filename), ephemeral=True)
                else:
                    msg = "❌ Erro no servidor." if self.is_pt else "❌ Server error."
                    await interaction.followup.send(msg, ephemeral=True)
        except Exception:
            await interaction.followup.send("⚠️ Error", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts: list, locale: discord.Locale):
        is_pt = locale == discord.Locale.brazil_portuguese
        options = [discord.SelectOption(label=s['nome'], value=s['arquivo']) for s in scripts[:25]]
        placeholder = "Selecione um script..." if is_pt else "Select a script..."
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        is_pt = interaction.locale == discord.Locale.brazil_portuguese
        msg = "📥 Script selecionado." if is_pt else "📥 Script selected."
        await interaction.response.send_message(content=msg, view=DownloadView(self.values, interaction.locale), ephemeral=True)

# --- COMMANDS WITH NATIVE TRANSLATION --- #

@bot.tree.command(
    name="webscripts", 
    description="Access the scripts library",
    description_localizations={discord.Locale.brazil_portuguese: "Acessar a biblioteca de scripts"}
)
async def webscripts(interaction: discord.Interaction):
    is_pt = interaction.locale == discord.Locale.brazil_portuguese
    if not bot._catalog_cache: await bot.fetch_catalog()

    embed = discord.Embed(
        title="🛡️ WebScripts Cloud",
        description="Select a tool below." if not is_pt else "Selecione uma ferramenta abaixo.",
        color=0x2b2d31
    )
    
    view = discord.ui.View()
    view.add_item(WebScriptsSelect(bot._catalog_cache.get("scripts", []), interaction.locale))
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(name="nuke", description="☢️ Reset this channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    # O nuke apaga o canal, então a resposta precisa ser rápida
    channel = interaction.channel
    new_channel = await channel.clone()
    await new_channel.edit(position=channel.position)
    await channel.delete()
    
    msg = "☢️ **Channel Reset**" if interaction.locale != discord.Locale.brazil_portuguese else "☢️ **Canal Resetado**"
    await new_channel.send(msg)

@bot.tree.command(name="update", description="Reboot system")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Synchronizing...")
    subprocess.run(["git", "pull"], check=True)
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot.run(TOKEN)
