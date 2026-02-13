import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import os
import sys
import subprocess
import shutil

# --- CONFIGURAÇÕES --- #
TOKEN = os.getenv('DISCORD_TOKEN')
RAW_BASE = "https://raw.githubusercontent.com"
CATALOG_URL = f"{RAW_BASE}catalog.json"

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        self.session = None # Sessão global para performance

    async def setup_hook(self):
        # Cria a sessão de rede uma única vez
        self.session = aiohttp.ClientSession()
        print(f"📡 Sincronizando comandos...")
        await self.tree.sync()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

bot = AuditorBot()

# --- SISTEMA DE DOWNLOADS --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename):
        super().__init__(timeout=180)
        self.filename = filename

    @discord.ui.button(label="Baixar Script", style=discord.ButtonStyle.success, emoji="📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        try:
            async with bot.session.get(f"{RAW_BASE}{self.filename}") as resp:
                if resp.status == 200:
                    data = await resp.read()
                    # Uso de BytesIO para não precisar salvar arquivo no disco do servidor
                    import io
                    file_data = io.BytesIO(data)
                    await interaction.followup.send(
                        content=f"✅ **{self.filename}** pronto!",
                        file=discord.File(file_data, filename=self.filename),
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(f"❌ Erro no GitHub (Status: {resp.status})", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Falha na conexão: {e}", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts):
        options = [
            discord.SelectOption(label=s['nome'], description=s.get('descricao', '')[:100], value=s['arquivo']) 
            for s in scripts
        ]
        super().__init__(placeholder="Selecione um script...", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"📥 Você selecionou: `{self.values[0]}`. Clique abaixo para baixar.",
            view=DownloadView(self.values[0]),
            ephemeral=True
        )

# --- COMANDOS --- #

@bot.tree.command(name="webscripts", description="Catálogo de scripts otimizado")
async def webscripts(interaction: discord.Interaction):
    try:
        async with bot.session.get(CATALOG_URL) as resp:
            if resp.status != 200:
                return await interaction.response.send_message("❌ Erro ao acessar catálogo.", ephemeral=True)
            
            data = await resp.json(content_type=None)
            scripts = data.get("scripts", [])

            view = discord.ui.View()
            view.add_item(WebScriptsSelect(scripts))
            
            embed = discord.Embed(title="🌐 WebScripts Cloud", color=0x2b2d31)
            embed.set_footer(text="Performance Mode Ativado 🚀")
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erro: {e}", ephemeral=True)

@bot.tree.command(name="ping", description="Latência real")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"⚡ `{round(bot.latency * 1000)}ms`", ephemeral=True)

@bot.tree.command(name="update", description="Git Pull & Reload")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🔄 Atualizando...")
    subprocess.run(["git", "pull"])
    os.execv(sys.executable, ['python'] + sys.argv)

if __name__ == "__main__":
    bot.run(TOKEN)
