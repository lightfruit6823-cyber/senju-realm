import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask
from threading import Thread
import os
import random
import requests
from datetime import datetime, timedelta

# ==================================================
# LOAD ENV
# ==================================================

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# ==================================================
# KEEP ALIVE FOR RENDER
# ==================================================

app = Flask('')

@app.route('/')
def home():
    return "SENJU REALM ONLINE ⚡"


def run_web():
    app.run(host='0.0.0.0', port=10000)


def keep_alive():
    t = Thread(target=run_web)
    t.start()


keep_alive()

# ==================================================
# MONGODB
# ==================================================

mongo = MongoClient(MONGO_URI)
db = mongo["senjurealm"]

col = db["users"]
market_col = db["market"]
prefix_col = db["prefixes"]

# ==================================================
# PREFIX SYSTEM
# ==================================================

DEFAULT_PREFIX = "s!"


async def get_prefix(bot, message):
    if not message.guild:
        return DEFAULT_PREFIX

    data = prefix_col.find_one({"guild_id": message.guild.id})

    return data["prefix"] if data else DEFAULT_PREFIX

# ==================================================
# BOT SETUP
# ==================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    help_command=None
)

guild_obj = discord.Object(id=GUILD_ID)

# ==================================================
# USER SYSTEM
# ==================================================


def get_user(user_id: int):
    user = col.find_one({"user_id": user_id})

    if not user:
        user = {
            "user_id": user_id,
            "yen": 500,
            "bank": 0,
            "aura": 0,
            "influence": 0,
            "rank": "🥀 Weakling",
            "xp": 0,
            "daily": None,
            "inventory": [],
            "wins": 0,
            "losses": 0,
            "summons": 0,
            "debt": 0
        }

        col.insert_one(user)

    return user


def upd(user_id: int, data: dict):
    col.update_one({"user_id": user_id}, data)

# ==================================================
# RANK SYSTEM
# ==================================================


def get_rank(aura: int):
    if aura >= 50000:
        return "☄️ Cosmic Monarch"

    if aura >= 25000:
        return "👑 Divine"

    if aura >= 10000:
        return "🌌 Mythic"

    if aura >= 5000:
        return "💠 Ascended"

    if aura >= 2000:
        return "🔥 Elite"

    if aura >= 500:
        return "⚔️ Fighter"

    return "🥀 Weakling"

# ==================================================
# READY EVENT
# ==================================================


@bot.event
async def on_ready():

    try:
        synced = await bot.tree.sync(guild=guild_obj)
        print(f"✅ Synced {len(synced)} command(s)")

    except Exception as e:
        print(e)

    print(f"🔥 Logged in as {bot.user}")

# ==================================================
# ERRORS
# ==================================================


@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.CommandNotFound):
        return

    print(error)

# ==================================================
# MENTION RESPONSE
# ==================================================


@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if bot.user in message.mentions:

        prefix = DEFAULT_PREFIX

        if message.guild:
            data = prefix_col.find_one({"guild_id": message.guild.id})
            prefix = data["prefix"] if data else DEFAULT_PREFIX

        embed = discord.Embed(
            title="🌌 SENJU REALM",
            description=(
                f">>> ⚡ Anime Economy System\n\n"
                f"💰 Economy\n"
                f"⚔️ Combat\n"
                f"🎴 Summons\n"
                f"🏪 Market\n\n"
                f"📚 Prefix: `{prefix}`\n"
                f"📚 Slash Commands: `/help`"
            ),
            color=0x7e22ce
        )

        await message.channel.send(embed=embed)

    await bot.process_commands(message)

# ==================================================
# PREFIX COMMAND
# ==================================================


@bot.tree.command(name="setprefix", description="Change the server prefix", guild=guild_obj)
@app_commands.describe(prefix="New prefix")
async def setprefix(interaction: discord.Interaction, prefix: str):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Administrator only.",
            ephemeral=True
        )

    prefix_col.update_one(
        {"guild_id": interaction.guild.id},
        {"$set": {"prefix": prefix}},
        upsert=True
    )

    embed = discord.Embed(
        title="⚙️ PREFIX UPDATED",
        description=f"🌌 New Prefix: `{prefix}`",
        color=0x22c55e
    )

    await interaction.response.send_message(embed=embed)

# ==================================================
# PREFIX HELP
# ==================================================


@bot.command()
async def help(ctx):

    prefix = await get_prefix(bot, ctx.message)

    embed = discord.Embed(
        title="🌌 SENJU REALM COMMANDS",
        description=(
            f"⚡ Current Prefix: `{prefix}`\n\n"
            f"💰 Economy:\n"
            f"`{prefix}balance`\n"
            f"`{prefix}daily`\n"
            f"`{prefix}work`\n"
            f"`{prefix}train`\n"
            f"`{prefix}profile`\n"
            f"`{prefix}crime`\n"
            f"`{prefix}coinflip <amount>`\n"
        ),
        color=0xa855f7
    )

    await ctx.send(embed=embed)

# ==================================================
# BALANCE
# ==================================================


@bot.command()
async def balance(ctx):

    user = get_user(ctx.author.id)

    embed = discord.Embed(
        title=f"💰 {ctx.author.display_name}'s Balance",
        description=(
            f"⛩ Wallet: **{user['yen']} Yen**\n"
            f"🏦 Bank: **{user['bank']} Yen**\n"
            f"⚡ Aura: **{user['aura']}**\n"
            f"🏆 Rank: **{user['rank']}**"
        ),
        color=0xfacc15
    )

    await ctx.send(embed=embed)

# ==================================================
# DAILY
# ==================================================


@bot.command()
async def daily(ctx):

    user = get_user(ctx.author.id)

    now = datetime.utcnow()

    if user["daily"]:

        last = datetime.fromisoformat(user["daily"])
        diff = now - last

        if diff < timedelta(hours=24):

            rem = timedelta(hours=24) - diff
            hours = int(rem.total_seconds() // 3600)
            mins = int((rem.total_seconds() % 3600) // 60)

            return await ctx.send(
                f"⏳ Come back in {hours}h {mins}m"
            )

    amount = random.randint(500, 1500)

    upd(
        ctx.author.id,
        {
            "$inc": {"yen": amount},
            "$set": {"daily": now.isoformat()}
        }
    )

    embed = discord.Embed(
        title="🎁 DAILY REWARD",
        description=f"💰 You received **{amount} Yen**",
        color=0x22c55e
    )

    await ctx.send(embed=embed)

# ==================================================
# WORK
# ==================================================


@bot.command()
async def work(ctx):

    jobs = [
        "⚔️ Defeated shadow beasts",
        "🌌 Explored a cosmic dungeon",
        "🏪 Worked at the black market",
        "🎴 Sold rare relics"
    ]

    amount = random.randint(200, 800)

    upd(ctx.author.id, {"$inc": {"yen": amount}})

    embed = discord.Embed(
        title="💼 WORK COMPLETE",
        description=(
            f"{random.choice(jobs)}\n\n"
            f"💰 Earned: **{amount} Yen**"
        ),
        color=0x3b82f6
    )

    await ctx.send(embed=embed)

# ==================================================
# TRAIN
# ==================================================


@bot.command()
async def train(ctx):

    gain = random.randint(50, 300)

    user = get_user(ctx.author.id)

    new_aura = user["aura"] + gain
    new_rank = get_rank(new_aura)

    upd(
        ctx.author.id,
        {
            "$inc": {
                "aura": gain,
                "xp": 20
            },
            "$set": {
                "rank": new_rank
            }
        }
    )

    embed = discord.Embed(
        title="⚔️ TRAINING COMPLETE",
        description=(
            f"⚡ Aura Gained: **+{gain}**\n"
            f"🧠 XP Gained: **+20**\n"
            f"🏆 Rank: **{new_rank}**"
        ),
        color=0xef4444
    )

    await ctx.send(embed=embed)

# ==================================================
# PROFILE
# ==================================================


@bot.command()
async def profile(ctx):

    user = get_user(ctx.author.id)

    embed = discord.Embed(
        title=f"👤 {ctx.author.display_name}'s Profile",
        description=(
            f"🏆 Rank: **{user['rank']}**\n"
            f"⚡ Aura: **{user['aura']}**\n"
            f"🧠 XP: **{user['xp']}**\n"
            f"👑 Influence: **{user['influence']}**\n"
            f"💰 Yen: **{user['yen']}**"
        ),
        color=0xa855f7
    )

    await ctx.send(embed=embed)

# ==================================================
# CRIME
# ==================================================


@bot.command()
async def crime(ctx):

    if random.randint(1, 100) >= 40:

        amount = random.randint(500, 2500)

        upd(ctx.author.id, {
            "$inc": {
                "yen": amount,
                "aura": 25
            }
        })

        embed = discord.Embed(
            title="💀 CRIME SUCCESSFUL",
            description=(
                f"💰 Earned: **{amount} Yen**\n"
                f"⚡ Aura: **+25**"
            ),
            color=0x22c55e
        )

    else:

        loss = random.randint(200, 1000)

        upd(ctx.author.id, {
            "$inc": {
                "yen": -loss
            }
        })

        embed = discord.Embed(
            title="🚔 CRIME FAILED",
            description=f"💸 Lost: **{loss} Yen**",
            color=0xef4444
        )

    await ctx.send(embed=embed)

# ==================================================
# COINFLIP
# ==================================================


@bot.command()
async def coinflip(ctx, amount: int):

    user = get_user(ctx.author.id)

    if amount <= 0:
        return await ctx.send("❌ Invalid amount")

    if user["yen"] < amount:
        return await ctx.send("💀 Not enough Yen")

    if random.choice([True, False]):

        upd(ctx.author.id, {"$inc": {"yen": amount}})

        embed = discord.Embed(
            title="🪙 YOU WON",
            description=f"💰 +{amount} Yen",
            color=0x22c55e
        )

    else:

        upd(ctx.author.id, {"$inc": {"yen": -amount}})

        embed = discord.Embed(
            title="💀 YOU LOST",
            description=f"💸 -{amount} Yen",
            color=0xef4444
        )

    await ctx.send(embed=embed)

# ==================================================
# SLASH BALANCE
# ==================================================


@bot.tree.command(name="balance", description="Check your balance", guild=guild_obj)
async def slash_balance(interaction: discord.Interaction):

    user = get_user(interaction.user.id)

    embed = discord.Embed(
        title=f"💰 {interaction.user.display_name}'s Balance",
        description=(
            f"⛩ Wallet: **{user['yen']} Yen**\n"
            f"🏦 Bank: **{user['bank']} Yen**\n"
            f"⚡ Aura: **{user['aura']}**\n"
            f"🏆 Rank: **{user['rank']}**"
        ),
        color=0xfacc15
    )

    await interaction.response.send_message(embed=embed)

# ==================================================
# SLASH DAILY
# ==================================================


@bot.tree.command(name="daily", description="Claim daily reward", guild=guild_obj)
async def slash_daily(interaction: discord.Interaction):

    user = get_user(interaction.user.id)

    now = datetime.utcnow()

    if user["daily"]:

        last = datetime.fromisoformat(user["daily"])
        diff = now - last

        if diff < timedelta(hours=24):

            rem = timedelta(hours=24) - diff
            hours = int(rem.total_seconds() // 3600)
            mins = int((rem.total_seconds() % 3600) // 60)

            return await interaction.response.send_message(
                f"⏳ Come back in {hours}h {mins}m",
                ephemeral=True
            )

    amount = random.randint(500, 1500)

    upd(
        interaction.user.id,
        {
            "$inc": {"yen": amount},
            "$set": {"daily": now.isoformat()}
        }
    )

    embed = discord.Embed(
        title="🎁 DAILY REWARD",
        description=f"💰 You received **{amount} Yen**",
        color=0x22c55e
    )

    await interaction.response.send_message(embed=embed)

# ==================================================
# RUN BOT
# ==================================================

bot.run(TOKEN)
