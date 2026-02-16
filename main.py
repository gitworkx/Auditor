import discord
from discord.ext import commands
from discord import app_commands
import os

# --- CONFIGURAÇÃO --- #
TOKEN = os.getenv('DISCORD_TOKEN')

# Tratamento das quebras de linha nas variáveis de ambiente logo na carga
REGRAS_PT = os.getenv('REGRAS_PT', 'Regras em português não configuradas.').replace('\\n', '\n')
REGRAS_EN = os.getenv('REGRAS_EN', 'English rules not configured.').replace('\\n', '\n')

class AuditorBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)

    async def setup_hook(self):
        # Sincroniza os comandos globais (Slash Commands)
        await self.tree.sync()
        print(f"✅ Logado como {self.user} | Comandos sincronizados.")

bot = AuditorBot()

# --- TRATAMENTO DE ERROS GLOBAL --- #
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "🚫 **Erro:** Você precisa da permissão `Gerenciar Canais` para usar isso.", 
            ephemeral=True
        )
    else:
        # Log de erro no console para debug
        print(f"Erro no comando: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("⚠️ Ocorreu um erro inesperado.", ephemeral=True)

# --- COMANDOS --- #

@bot.tree.command(name="nuke", description="Reseta o canal atual (apaga tudo e recria)")
@app_commands.checks.has_permissions(manage_channels=True)
async def nuke(interaction: discord.Interaction):
    # Precisamos responder antes de deletar o canal
    await interaction.response.send_message("☢️ Executando limpeza total...", ephemeral=True)
    
    channel = interaction.channel
    pos = channel.position
    
    # Clona o canal com as mesmas permissões e configurações
    new_channel = await channel.clone(reason=f"Nuke solicitado por {interaction.user}")
    
    # Deleta o canal antigo
    await channel.delete()
    
    # Ajusta a posição para não ficar no fim da lista
    await new_channel.edit(position=pos)
    
    embed = discord.Embed(
        title="☣️ Canal Resetado",
        description=f"Este canal foi purificado por **{interaction.user.mention}**.",
        color=0xff4747,
        timestamp=discord.utils.utcnow()
    )
    await new_channel.send(embed=embed)

@bot.tree.command(name="regras", description="Exibe as regras no seu idioma local")
async def regras(interaction: discord.Interaction):
    # Detecta o idioma do usuário no Discord
    # Exemplos: 'pt-BR' ou 'pt-PT' começam com 'pt'
    lang = str(interaction.locale)
    
    if lang.startswith("pt"):
        titulo = "📜 Regras do Servidor"
        conteudo = REGRAS_PT
        footer = f"Solicitado por {interaction.user.display_name}"
    else:
        # Padrão Internacional (Inglês)
        titulo = "📜 Server Rules"
        conteudo = REGRAS_EN
        footer = f"Requested by {interaction.user.display_name}"
    
    embed = discord.Embed(
        title=titulo,
        description=conteudo,
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=footer)
    
    # Enviamos como efêmero para não poluir o chat geral com as regras toda hora
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Verifica a saúde da conexão")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latência: **{latency}ms**")

# --- INICIALIZAÇÃO --- #
if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("❌ ERRO: A variável de ambiente DISCORD_TOKEN não foi encontrada.")
