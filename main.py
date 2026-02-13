import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sys
import subprocess
import shutil
import requests  # Certifique-se de que 'requests' está no requirements.txt

# --- CONFIGURAÇÕES --- #
TOKEN = os.getenv('DISCORD_TOKEN')
# Adicionada a barra "/" ao final para evitar erro de URL grudada
RAW_BASE_URL = "https://raw.githubusercontent.com" 
CATALOG_URL = f"{RAW_BASE_URL}catalog.json"

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
        
        # Tenta baixar o arquivo do repositório
        res = requests.get(f"{RAW_BASE_URL}{self.filename}")
        if res.status_code == 200:
            with open(self.filename, "wb") as f:
                f.write(res.content)
            
            await interaction.followup.send(
                content=f"✅ Download concluído: `{self.filename}`", 
                file=discord.File(self.filename), 
                ephemeral=True
            )
            os.remove(self.filename)
        else:
            await interaction.followup.send("❌ Erro: Arquivo não encontrado no repositório.", ephemeral=True)

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
        self.add_item(discord.ui.Button(label="Perfil do Dev", url="https://github.com", style=discord.ButtonStyle.link))

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
            return await interaction.response.send_message(f"❌ Erro ao carregar catálogo (Status: {response.status_code})", ephemeral=True)
        
        data = response.json()
        scripts = data.get("scripts", [])

        embed = discord.Embed(
            title="🌐 Central WebScripts",
            description="Escolha um script abaixo. O download será enviado de forma privada.",
            color=discord.Color.purple()
        )
        embed.set_footer(text="gitworkx/WebScripts • 2026")
        await interaction.response.send_message(embed=embed, view=WebScriptsView(scripts))
    except Exception as e:
        await interaction.response.send_message(f"⚠️ Erro no sistema: {e}", ephemeral=True)

@auditor.tree.command(name="update", description="Limpa cache, atualiza via Git e reinicia o bot")
@app_commands.checks.has_permissions(administrator=True)
async def update(interaction: discord.Interaction):
    await interaction.response.send_message("🛠️ Iniciando manutenção e busca de atualizações...")
    try:
        deleted_folders = 0
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                shutil.rmtree(os.path.join(root, '__pycache__'))
                deleted_folders += 1
        
        git_output = subprocess.check_output(['git', 'pull']).decode("utf-8")
        
        embed = discord.Embed(
            title="✅ Atualização Concluída",
            description=f"**Cache:** {deleted_folders} pastas limpas.\n**Git:** `{git_output.strip()}`",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        await interaction.followup.send("♻️ Reiniciando o Auditor...")
        
        # Reinicia o processo
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erro na Atualização: ```{e}```")

@auditor.tree.command(name="creditos", description="Exibe informações sobre o criador")
async def creditos_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🕵️‍♂️ Auditor - Central de Informações",
        description="Sistema avançado de auditoria e distribuição de scripts.",
        color=discord.Color.blue()
    )
    embed.add_field(name="🚀 Desenvolvedor", value="[gitworkx](https://github.com)", inline=True)
    if auditor.user.avatar:
        embed.set_thumbnail(url=auditor.user.display_avatar.url)
    embed.set_footer(text="Desenvolvido por gitworkx • 2026")
    await interaction.response.send_message(embed=embed, view=CreditButtons())

@auditor.tree.command(name="ping", description="Verifica a latência do Auditor")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(auditor.latency * 1000)
    await interaction.response.send_message(f"📡 Latência: **{latencia}ms**")

# --- EVENTO DE MENSAGEM (PREFIXO) --- #

@auditor.event
async def on_message(message):
    if message.author.bot: return
    await auditor.process_commands(message)

# --- INICIALIZAÇÃO --- #
if __name__ == "__main__":
    if TOKEN:
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: Variável de ambiente 'DISCORD_TOKEN' não encontrada.")
