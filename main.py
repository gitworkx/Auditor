import discord
import asyncio

class MyClient(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('!delete_after_24h'):
            await message.channel.send('This message will delete in 24 hours.')
            await asyncio.sleep(86400)  # Sleep for 24 hours (86400 seconds)
            await message.delete()

client = MyClient()
client.run('YOUR_TOKEN')