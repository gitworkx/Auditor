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
CATALOG_URL = f"{RAW_BASE}/user/repo/main/catalog.json"

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.session: aiohttp.ClientSession = None

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        print(f"📡 Synchronizing slash commands...")
        await self.tree.sync()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

bot = AuditorBot()

# --- DOWNLOAD SYSTEM --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename: str, locale: discord.Locale):
        super().__init__(timeout=180)
        self.filename = filename
        self.locale = locale

    @discord.ui.button(label="Download", style=discord.ButtonStyle.success, emoji="📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        is_pt = interaction.locale == discord.Locale.brazil_portuguese
        url = f"{RAW_BASE}/{self.filename}"
        
        try:
            async with bot.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.read()
                    with io.BytesIO(data) as file_data:
                        msg = f"✅ **{self.filename}** pronto!" if is_pt else f"✅ **{self.filename}** is ready!"
                        await interaction.followup.send(
                            content=msg,
                            file=discord.File(file_data, filename=self.filename.split('/')[-1]),
                            ephemeral=True
                        )
                else:
                    err = f"❌ Erro no GitHub: {resp.status}" if is_pt else f"❌ GitHub Error: {resp.status}"
                    await interaction.followup.send(err, ephemeral=True)
        except Exception as e:
            err_conn = f"⚠️ Falha na conexão: {e}" if is_pt else f"⚠️ Connection failure: {e}"
            await interaction.followup.send(err_conn, ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts: list, locale: discord.Locale):
        is_pt = locale == discord.Locale.brazil_portuguese
        options = [
            discord.SelectOption(label=s['nome'], description=s.get('descricao', '')[:100], value=s['arquivo']) 
            for s in scripts
        ]
        placeholder = "Escolha um script..." if is_pt else "Choose a script..."
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction: discord.Interaction):
        is_pt = interaction.locale == discord.Locale.brazil_portuguese
        msg = f"📥 Selecionado: `{self.values[0]}`. Clique abaixo." if is_pt else f"📥 Selected: `{self.values[0]}`. Click below."
        
        await interaction.response.send_message(
            content=msg,
            view=DownloadView(self.values[0], interaction.locale),
            ephemeral=True
        )

# --- COMMANDS WITH LOCALIZATION --- #

@bot.tree.command(
    name="webscripts",
    description="Show the script catalog",
    description_localizations={discord.Locale.brazil_portuguese: "Mostra o catálogo de scripts"}
)
async def webscripts(interaction: discord.Interaction):
    is_pt = interaction.locale == discord.Locale.brazil_portuguese
    
    try:
        async with bot.session.get(CATALOG_URL) as resp:
            if resp.status != 200:
                err = "❌ Erro ao acessar catálogo." if is_pt else "❌ Failed to reach catalog."
                return await interaction.response.send_message(err, ephemeral=True)
            
            data = await resp.json(content_type=None)
            scripts = data.get("scripts", [])

            view = discord.ui.View()
            view.add_item(WebScriptsSelect(scripts, interaction.locale))
            
            embed = discord.Embed(title="🌐 WebScripts Cloud", color=0x2b2d31)
            footer = "Modo Performance Ativo 🚀" if is_pt else "Performance Mode Active 🚀"
            embed.set_footer(text=footer)
            
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Error: {e}", ephemeral=True)

@bot.tree.command(
    name="ping",
    description="Check bot latency",
    description_localizations={discord.Locale.brazil_portuguese: "Verifica a latência do bot"}
)
async def ping(interaction: discord.Interaction):
    is_pt = interaction.locale == discord.Locale.brazil_portuguese
    label = "Latência" if is_pt else "Latency"
    await interaction.response.send_message(f"⚡ {label}: `{round(bot.latency * 1000)}ms`", ephemeral=True)

@bot.tree.command(
    name="update",
    description="Update and reload the bot",
    description_localizations={discord.Locale.brazil_portuguese: "Atualiza e reinicia o bot"}
)
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    is_pt = interaction.locale == discord.Locale.brazil_portuguese
    msg = "🔄 Atualizando..." if is_pt else "🔄 Updating..."
    
    await interaction.response.send_message(msg)
    subprocess.run(["git", "pull"])
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot.run(TOKEN)
