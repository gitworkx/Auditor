# Setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Bot is ready!')

@client.event
async def on_message(message):
    # Automatic message deletion feature
    if message.author == client.user:
        return
    await asyncio.sleep(86400)  # Wait for 24 hours
    await message.delete()

@client.command()
async def ping(ctx):
    await ctx.send('Pong!')

@client.command()
async def panic(ctx):
    await ctx.send('Panic!')

@client.command()
async def hello(ctx):
    await ctx.send('Hello there!')

# Start both the Flask app and the Discord bot
if __name__ == '__main__':
    app.run(debug=True)
    client.run('YOUR_TOKEN')
