import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sys
import subprocess
import shutil
import requests

# --- CONFIGURAÇÕES --- #
TOKEN = os.getenv('DISCORD_TOKEN')
# URL base para downloads (aponta para a raiz do seu repositório no GitHub)
RAW_BASE_URL = "https://raw.githubusercontent.com"
# URL direta do catálogo que você forneceu
CATALOG_URL = "https://raw.githubusercontent.com"

intents = discord.Intents.default()
intents.message_content = True
auditor = commands.Bot(command_prefix='!', intents=intents)

# --- SISTEMA WEBSCRIPTS (DINÂMICO VIA JSON) --- #

class DownloadView(discord.ui.View):
    def __init__(self, filename):
        super().__init__(timeout=None)
        self.filename = filename

    @discord.ui.button(label="Baixar Script", style=discord.ButtonStyle.success, emoji="📥")
    async def download(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        
        # Constrói a URL final: Base + Nome do arquivo vindo do JSON
        file_url = f"{RAW_BASE_URL}{self.filename}"
        res = requests.get(file_url)
        
        if res.status_code == 200:
            # Salva temporariamente para enviar no Discord
            with open(self.filename, "wb") as f:
                f.write(res.content)
            
            await interaction.followup.send(
                content=f"✅ Download concluído: `{self.filename}`", 
                file=discord.File(self.filename), 
                ephemeral=True
            )
            os.remove(self.filename) # Limpa o arquivo após o envio
        else:
            await interaction.followup.send(f"❌ Erro: Arquivo não encontrado no repositório.\nURL tentada: `{file_url}`", ephemeral=True)

class WebScriptsSelect(discord.ui.Select):
    def __init__(self, scripts_data):
        self.scripts_data = scripts_data
        options = [
            discord.SelectOption(
                label=s['nome'], 
                description=s['descricao'][:100], 
                value=s['arquivo']
            ) for s in scripts_data
        ]
        super().__init__(placeholder="Selecione um script do catálogo...", options=options)

    async def callback(self, interaction: discord.Interaction):
        script = next(s for s in self.scripts_data if s['arquivo'] == self.values)
        
        embed = discord.Embed(
            title=f"📦 {script['nome']}",
            description=f"**Descrição:** {script['descricao']}\n**Arquivo:** `{script['arquivo']}`",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, view=DownloadView(script['arquivo']), ephemeral=True)

class WebScriptsView(discord.ui.View):
    def __init__(self, scripts_data):
        super().__init__()
        self.add_item(WebScriptsSelect(scripts_data))

# --- CLASSES DE INTERFACE --- #

class CreditButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="Ver Repositório", url="https://github.com", style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="Suporte", url="https://discord.com", style=discord.ButtonStyle.link))

# --- EVENTOS PRINCIPAIS --- #

@auditor.event
async def on_ready():
    print(f'🕵️‍♂️ Auditor pronto para serviço!')
    await auditor.change_presence(activity=discord.Game(name="WebScripts Cloud 2026"))
    try:
        synced = await auditor.tree.sync()
        print(f"📡 {len(synced)} comandos sincronizados!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

# --- COMANDOS DE BARRA (SLASH COMMANDS) --- #

@auditor.tree.command(name="webscripts", description="Acesse o catálogo dinâmico de scripts")
async def webscripts(interaction: discord.Interaction):
    try:
        response = requests.get(CATALOG_URL)
        if response.status_code != 200:
            return await interaction.response.send_message(f"❌ Erro ao carregar `catalog.json`. Status: {response.status_code}", ephemeral=True)
        
        data = response.json()
        scripts = data.get("scripts", [])

        if not scripts:
            return await interaction.response.send_message("📭 O catálogo está vazio no momento.", ephemeral=True)

        embed = discord.Embed(
            title="🌐 Central WebScripts",
            description="Escolha um script abaixo. O download será enviado no seu privado.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="gitworkx/WebScripts • 2026")
        await interaction.response.send_message(embed=embed, view=WebScriptsView(scripts))
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erro no sistema: {e}", ephemeral=True)

@auditor.tree.command(name="ping", description="Verifica a latência do Auditor")
async def ping_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f"📡 Latência: **{round(auditor.latency * 1000)}ms**")

@auditor.tree.command(name="update", description="Atualiza via Git e reinicia o bot")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🛠️ Atualizando código via Git...")
    try:
        # Limpa cache do Python
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                shutil.rmtree(os.path.join(root, '__pycache__'))
        
        # Puxa atualizações do GitHub
        subprocess.check_call(['git', 'pull'])
        
        await interaction.followup.send("♻️ Reiniciando...")
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro: {e}")

# --- INICIALIZAÇÃO --- #
if __name__ == "__main__":
    if TOKEN:
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: Variável DISCORD_TOKEN não configurada.")
