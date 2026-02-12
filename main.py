from flask import Flask
import os
import discord
from discord.ext import commands
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/ping')
def ping():
    return "Pong!"

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    await bot.tree.sync()

# Slash command: /ping - Responds with Pong
@bot.tree.command(name="ping", description="Ping the bot")
async def ping_slash(interaction: discord.Interaction):
    """Slash command version of ping"""
    await interaction.response.send_message("Pong! 🏓")

# Slash command: /panic - Delete all messages
@bot.tree.command(name="panic", description="Delete all messages in this channel (Admin only)")
@discord.app_commands.checks.has_permissions(administrator=True)
async def panic(interaction: discord.Interaction):
    """
    Delete all messages in the current channel.
    Only users with Administrator permissions can use this.
    """
    await interaction.response.defer()
    
    channel = interaction.channel
    deleted_count = 0
    
    try:
        # Fetch and delete messages in batches
        async for message in channel.history(limit=None):
            try:
                await message.delete()
                deleted_count += 1
            except discord.Forbidden:
                await interaction.followup.send(f"⚠️ Missing permissions to delete some messages.")
                break
            except discord.HTTPException:
                # Rate limit handling
                continue
        
        await interaction.followup.send(f"✅ Panic mode activated! Deleted {deleted_count} messages.")
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")

# Legacy prefix command version (optional)
@bot.command(name="panic_legacy")
@commands.has_permissions(administrator=True)
async def panic_legacy(ctx):
    """Legacy prefix command to delete all messages"""
    deleted_count = 0
    async for message in ctx.channel.history(limit=None):
        try:
            await message.delete()
            deleted_count += 1
        except:
            break
    
    await ctx.send(f"✅ Panic mode activated! Deleted {deleted_count} messages.")

@bot.command()
async def hello(ctx):
    await ctx.send('Hello, World!')

if __name__ == '__main__':
    # Start Discord bot
    bot.loop.create_task(app.run_async(host='0.0.0.0', port=os.getenv('PORT', 5000)))
    bot.run(os.getenv('TOKEN'))