import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
import sys
import subprocess
import shutil

# Token do ambiente
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

auditor = commands.Bot(command_prefix='!', intents=intents)

# --- CLASSE PARA O BOTÃO DE LINKS --- #
class CreditButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        # Adiciona o botão que redireciona para o GitHub
        self.add_item(discord.ui.Button(label="Ver Repositório", url="https://github.com", style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="Perfil do Dev", url="https://github.com", style=discord.ButtonStyle.link))

@auditor.event
async def on_ready():
    print(f'🕵️‍♂️ Auditor pronto para serviço!')
    await auditor.change_presence(activity=discord.Game(name="Monitorando protocolos"))
    try:
        synced = await auditor.tree.sync()
        print(f"📡 {len(synced)} comandos de barra sincronizados!")
    except Exception as e:
        print(f"❌ Erro ao sincronizar: {e}")

# --- COMANDO DE UPDATE E RESTART --- #
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

        os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erro na Atualização",
            description=f"Ocorreu um problema: ```{e}```",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed)

# --- COMANDO DE CRÉDITOS COM BOTÃO --- #
@auditor.tree.command(name="creditos", description="Exibe informações sobre o criador e o projeto")
async def creditos_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🕵️‍♂️ Auditor - Central de Informações",
        description="Sistema avançado de auditoria e monitoramento de protocolos.",
        color=discord.Color.blue()
    )
    embed.add_field(name="🚀 Desenvolvedor", value="[gitworkx](https://github.com/gitworkx)", inline=True)
    embed.add_field(name="📂 Projeto", value="Auditor", inline=True)
    
    if auditor.user.avatar:
        embed.set_thumbnail(url=auditor.user.display_avatar.url)
        
    embed.set_footer(text="Desenvolvido por gitworkx • 2026")
    
    # Enviando a mensagem com a View que contém os botões
    await interaction.response.send_message(embed=embed, view=CreditButtons())

@auditor.command(name="creditos")
async def creditos_prefix(ctx):
    embed = discord.Embed(
        title="🕵️‍♂️ Auditor - Créditos", 
        description="Desenvolvido por **Matteo**.",
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=CreditButtons())

# --- COMANDOS DE PING --- #
@auditor.command(name="ping")
async def ping_prefix(ctx):
    latencia = round(auditor.latency * 1000)
    await ctx.send(f"📡 Latência: **{latencia}ms**")

@auditor.tree.command(name="ping", description="Verifica a latência do Auditor")
async def ping_slash(interaction: discord.Interaction):
    latencia = round(auditor.latency * 1000)
    await interaction.response.send_message(f"📡 Latência: **{latencia}ms**")

@auditor.event
async def on_message(message):
    if message.author.bot:
        return
    await auditor.process_commands(message)

# --- INICIALIZAÇÃO --- #
if __name__ == "__main__":
    if TOKEN:
        auditor.run(TOKEN)
    else:
        print("❌ ERRO: TOKEN não encontrado. Verifique suas variáveis de ambiente.")
        sys.exit(1)
        
