import discord
from discord.ext import tasks, commands
from mcstatus import JavaServer
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
SERVER_IP = os.getenv("MINECRAFT_SERVER_IP")
PORT = int(os.getenv("MINECRAFT_SERVER_PORT", 25565))

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user}")
    update_status.start()

@tasks.loop(seconds=60)
async def update_status():
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{PORT}")
        status = server.status()
        joueurs = [p.name for p in status.players.sample] if status.players.sample else []
        nb = status.players.online

        await bot.change_presence(activity=discord.Game(name=f"{nb} joueur(s) en ligne"))

        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            message = "**Joueurs connectés :**\n"
            message += "\n".join(joueurs) if joueurs else "Aucun joueur connecté."
            await channel.edit(topic=f"{nb} joueur(s) connecté(s)")
            async for msg in channel.history(limit=10):
                await msg.delete()
            await channel.send(message)

    except Exception as e:
        print("Erreur :", e)

bot.run(TOKEN)
