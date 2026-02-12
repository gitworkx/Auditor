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
        # 1. Limpeza de Cache (.pyc e __pycache__)
        deleted_folders = 0
        for root, dirs, files in os.walk('.'):
            if '__pycache__' in dirs:
                shutil.rmtree(os.path.join(root, '__pycache__'))
                deleted_folders += 1
        
        # 2. Puxar código do GitHub/GitLab
        # O comando 'git pull' assume que você configurou o repositório no servidor
        git_output = subprocess.check_output(['git', 'pull']).decode("utf-8")
        
        embed = discord.Embed(
            title="✅ Atualização Concluída",
            description=f"**Cache:** {deleted_folders} pastas limpas.\n**Git:** `{git_output.strip()}`",
            color=discord.Color.green()
        )
        await interaction.followup.send(embed=embed)
        await interaction.followup.send("♻️ Reiniciando o Auditor...")

        # 3. Reinicia o script
        # Substitui o processo atual por um novo, mantendo os mesmos argumentos
        os.execv(sys.executable, ['python'] + sys.argv)

    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Erro na Atualização",
            description=f"Ocorreu um problema: ```{e}```",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=error_embed)

# --- COMANDOS EXISTENTES --- #
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
