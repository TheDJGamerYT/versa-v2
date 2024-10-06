import os
import discord
import openai
from discord.ext import commands

# Load variables from variables.txt
def load_variables(filename):
    variables = {}
    with open(filename, 'r') as file:
        for line in file:
            # Ignore empty lines and comments
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                variables[key.strip()] = value.strip()
    return variables

# Load the variables
config = load_variables('variables.txt')

# Set the required variables
TOKEN = config.get('TOKEN')
OPENAI_API_KEY = config.get('OPENAI_API_KEY')

# Check if the variables are set
if not TOKEN or not OPENAI_API_KEY:
    raise Exception("TOKEN and OPENAI_API_KEY must be set in variables.txt")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

# Sample command for testing
@bot.command(name='setstatus')
async def setstatus(ctx, status: str):
    """Sets the bot's online presence status."""
    status_types = {
        "online": discord.Status.online,
        "dnd": discord.Status.do_not_disturb,
        "idle": discord.Status.idle,
        "invisible": discord.Status.invisible
    }

    if status.lower() not in status_types:
        await ctx.send("Invalid status. Choose from: online, dnd, idle, invisible.")
        return

    await bot.change_presence(status=status_types[status.lower()])
    await ctx.send(f"Status set to {status}")

@bot.command(name='broadcast')
@commands.has_permissions(administrator=True)
async def broadcast(ctx, *, message: str):
    """Broadcasts a message to all text channels in the server."""
    guild = ctx.guild
    failed_channels = []

    for channel in guild.text_channels:
        try:
            await channel.send(message)
        except Exception as e:
            print(f"Could not send message to {channel.name}: {e}")
            failed_channels.append(channel.name)

    if failed_channels:
        await ctx.send(f"Broadcast completed, but failed to send to: {', '.join(failed_channels)}.")
    else:
        await ctx.send("Broadcast completed successfully.")

try:
    if not TOKEN:
        raise Exception("Please add your TOKEN to variables.txt")
    bot.run(TOKEN)
except discord.HTTPException as e:
    if e.status == 429:
        print("The Discord servers denied the connection for making too many requests")
        print("Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests")
    else:
        raise e
