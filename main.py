import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from pymongo import MongoClient
import os
import random
import requests
from datetime import datetime, timedelta

load_dotenv()

TOKEN = os.getenv("TOKEN")
MONGO_URI = os.getenv("MONGO_URI")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GUILD_ID = int(os.getenv("GUILD_ID", "0"))

# ==================================================
# MONGODB
# ==================================================

mongo = MongoClient(MONGO_URI)
db = mongo["senjurealm"]

col = db["users"]
characters_col = db["characters"]
market_col = db["market"]

# ==================================================
# ANIME CHARACTERS DATABASE
# ==================================================

ANIME_CHARACTERS = [
    {
        "name": "Gojo Satoru",
        "anime": "Jujutsu Kaisen",
        "rarity": "Mythic",
        "value": 500000,
        "image": "https://i.imgur.com/VaX0pfM.jpeg",
    },
    {
        "name": "Naruto Uzumaki",
        "anime": "Naruto",
        "rarity": "Legendary",
        "value": 350000,
        "image": "https://i.imgur.com/qh0Jk4A.jpeg",
    },
    {
        "name": "Monkey D. Luffy",
        "anime": "One Piece",
        "rarity": "Legendary",
        "value": 450000,
        "image": "https://i.imgur.com/t8KQZQp.jpeg",
    },
    {
        "name": "Tanjiro Kamado",
        "anime": "Demon Slayer",
        "rarity": "Epic",
        "value": 150000,
        "image": "https://i.imgur.com/yVY6X9P.jpeg",
    },
    {
        "name": "Sung Jin-Woo",
        "anime": "Solo Leveling",
        "rarity": "Mythic",
        "value": 600000,
        "image": "https://i.imgur.com/e9h6B4A.jpeg",
    },
    {
        "name": "Levi Ackerman",
        "anime": "Attack on Titan",
        "rarity": "Epic",
        "value": 180000,
        "image": "https://i.imgur.com/6N2VY6v.jpeg",
    },
    {
        "name": "Yoriichi",
        "anime": "Demon Slayer",
        "rarity": "Divine",
        "value": 850000,
        "image": "https://i.imgur.com/V5kQn4M.jpeg",
    },
]

# ==================================================
# USER DATA
# ==================================================


def get_user(user_id: int) -> dict:
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
            # NEW SYSTEMS
            "inventory": [],
            "loan": 0,
            "wins": 0,
            "losses": 0,
            "summons": 0,
        }

        col.insert_one(user)

    return user


# ==================================================
# UPDATE FUNCTION
# ==================================================


def upd(user_id: int, data: dict):
    col.update_one({"user_id": user_id}, data)


# ==================================================
# RANK SYSTEM
# ==================================================


def get_rank(aura: int) -> str:
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


RANK_ORDER = [
    ("🥀 Weakling", 0),
    ("⚔️ Fighter", 500),
    ("🔥 Elite", 2000),
    ("💠 Ascended", 5000),
    ("🌌 Mythic", 10000),
    ("👑 Divine", 25000),
    ("☄️ Cosmic Monarch", 50000),
]

# ==================================================
# ANIME API SYSTEM
# ==================================================

def fetch_character(name):

    url = f"https://api.jikan.moe/v4/characters?q={name}&limit=1"

    response = requests.get(url)

    data = response.json()

    if not data["data"]:
        return None

    char = data["data"][0]

    return {

        "name": char["name"],

        "image": char["images"]["jpg"]["image_url"],

        "favorites": char["favorites"]

    }

# ==================================================
# CHARACTER POOL
# ==================================================

character_names = [

    "Gojo",
    "Naruto",
    "Luffy",
    "Levi",
    "Yoriichi",
    "Sung Jin-Woo",
    "Itachi",
    "Madara",
    "Aizen",
    "Goku",
    "Vegeta",
    "Eren",
    "Mikasa",
    "Rimuru",
    "Anos",
    "Saitama",
    "Killua",
    "Kurapika",
    "Zoro",
    "Law"
]

# ==================================================
# BOT SETUP
# ==================================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents, help_command=None)
guild_obj = discord.Object(id=GUILD_ID)

# ==================================================
# READY
# ==================================================


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=guild_obj)
        print("━━━━━━━━━━━━━━━━━━━━━━")
        print(f"🌌 Logged in as {bot.user}")
        print(f"⚡ Synced {len(synced)} slash commands")
        print("🌌 MongoDB Connected")
        print("━━━━━━━━━━━━━━━━━━━━━━")
    except Exception as e:
        print(f"❌ Sync error: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return


# ==================================================
# BOT MENTION → welcome embed
# ==================================================


@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user in message.mentions:
        embed = discord.Embed(
            title="🌌 𝐒𝐄𝐍𝐉𝐔 𝐑𝐄𝐀𝐋𝐌",
            description=(
                ">>> ⚡ THE NEXT GENERATION ANIME ECONOMY SYSTEM\n\n"
                "💰 Economy\n⚔️ Combat\n🎴 Summons\n🏪 Market\n👑 Aura Progression\n\n"
                "📚 Use `/help` to begin your journey."
            ),
            color=0x7E22CE,
        )
        await message.channel.send(embed=embed)
    await bot.process_commands(message)


# ==================================================
# HELP  — dropdown UI
# ==================================================

HELP_PAGES = {
    "economy": discord.Embed(
        title="💰 Economy Commands",
        description=(
            "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃ 💰 `/balance`\n"
            "┃ 🏦 `/deposit <amount>`\n"
            "┃ 🏦 `/withdraw <amount>`\n"
            "┃ 🎁 `/daily`\n"
            "┃ 💼 `/work`\n"
            "┃ 🎰 `/slots <amount>`\n"
            "┃ 🪙 `/coinflip <amount>`\n"
            "┃ 📊 `/leaderboard`\n"
            "╰━━━━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0xFACC15,
    ),
    "training": discord.Embed(
        title="⚔️ Training Commands",
        description=(
            "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃ ⚔️ `/train`\n"
            "┃ 🧘 `/meditate`\n"
            "┃ 👤 `/profile`\n"
            "┃ 🏆 `/rank`\n"
            "╰━━━━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0xA855F7,
    ),
    "owner": discord.Embed(
        title="👑 Owner Commands",
        description=(
            "╭━━━━━━━━━━━━━━━━━━━━━╮\n"
            "┃ 💵 `/addmoney @user amount`\n"
            "┃ 🌐 `/addmoneyall amount`\n"
            "┃ ⚡ `/addaura @user amount`\n"
            "┃ 🏅 `/setrank @user rank`\n"
            "╰━━━━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0xEF4444,
    ),
}


class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Economy",
                description="Yen, bank, gambling",
                emoji="💰",
                value="economy",
            ),
            discord.SelectOption(
                label="Training",
                description="Aura, XP, rank",
                emoji="⚔️",
                value="training",
            ),
            discord.SelectOption(
                label="Owner",
                description="Admin-only commands",
                emoji="👑",
                value="owner",
            ),
        ]
        super().__init__(placeholder="✨ Select a category", options=options)

    async def callback(self, interaction: discord.Interaction):
        page = HELP_PAGES[self.values[0]]
        await interaction.response.edit_message(embed=page)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)
        self.add_item(HelpDropdown())


@bot.tree.command(name="help", description="Browse all commands", guild=guild_obj)
async def slash_help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="👑 SENJU REALM — Command Hub",
        description=(
            "╭━━━ ✦ SELECT A CATEGORY BELOW ✦ ━━━╮\n\n"
            "💰 Economy  •  ⚔️ Training  •  👑 Owner\n\n"
            "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0x2B2D31,
    )
    embed.set_footer(text="⚡ SENJU Realm • Anime Economy System")
    embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
    await interaction.response.send_message(
        embed=embed, view=HelpView(), ephemeral=True
    )


# ==================================================
# BALANCE
# ==================================================


@bot.tree.command(name="balance", description="Check your balance", guild=guild_obj)
@app_commands.describe(member="User to check (default: yourself)")
async def slash_balance(
    interaction: discord.Interaction, member: discord.Member = None
):
    target = member or interaction.user
    user = get_user(target.id)
    embed = discord.Embed(
        title=f"💰 {target.display_name}'s Balance",
        description=(
            f"╭━━━ 👑 STATUS ━━━╮\n"
            f"┃ ⛩ Wallet: **{user['yen']} Yen**\n"
            f"┃ 🏦 Bank:   **{user['bank']} Yen**\n"
            f"┃ ⚡ Aura:   **{user['aura']}**\n"
            f"┃ 👑 Influence: **{user['influence']}**\n"
            f"┃ 🏆 Rank:   **{user['rank']}**\n"
            f"╰━━━━━━━━━━━━━━╯"
        ),
        color=0xFACC15,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# PROFILE
# ==================================================


@bot.tree.command(name="profile", description="View your full profile", guild=guild_obj)
@app_commands.describe(member="User to check (default: yourself)")
async def slash_profile(
    interaction: discord.Interaction, member: discord.Member = None
):
    target = member or interaction.user
    user = get_user(target.id)
    embed = discord.Embed(
        title=f"👤 {target.display_name}'s Profile",
        description=(
            f"╭━━━ 🌌 PROFILE ━━━╮\n"
            f"┃ 🏆 Rank:      **{user['rank']}**\n"
            f"┃ ⚡ Aura:      **{user['aura']}**\n"
            f"┃ 🧠 XP:        **{user['xp']}**\n"
            f"┃ 👑 Influence: **{user['influence']}**\n"
            f"┃ ⛩ Wallet:    **{user['yen']} Yen**\n"
            f"┃ 🏦 Bank:      **{user['bank']} Yen**\n"
            f"╰━━━━━━━━━━━━━━━━╯"
        ),
        color=0xA855F7,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# DAILY
# ==================================================


@bot.tree.command(
    name="daily", description="Claim your daily Yen reward", guild=guild_obj
)
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
            embed = discord.Embed(
                title="⏳ Already Claimed",
                description=f"Come back in **{hours}h {mins}m**.",
                color=0xEF4444,
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)
    amount = random.randint(500, 1500)
    upd(
        interaction.user.id,
        {"$inc": {"yen": amount}, "$set": {"daily": now.isoformat()}},
    )
    embed = discord.Embed(
        title="🎁 DAILY REWARD",
        description=f"⚡ You claimed **{amount} Yen**!",
        color=0x22C55E,
    )
    await interaction.response.send_message(embed=embed)


# ==================================================
# WORK
# ==================================================


@bot.tree.command(name="work", description="Work to earn Yen", guild=guild_obj)
async def slash_work(interaction: discord.Interaction):
    amount = random.randint(200, 800)
    job = random.choice(
        [
            "⚔️ Defeated shadow beasts",
            "🏪 Worked at the black market",
            "🌌 Explored a cosmic dungeon",
            "⚡ Trained rookie hunters",
            "🎴 Sold rare relics",
        ]
    )
    upd(interaction.user.id, {"$inc": {"yen": amount}})
    embed = discord.Embed(
        title="💼 WORK COMPLETE",
        description=f"{job}\n\n💰 Earned: **{amount} Yen**",
        color=0x3B82F6,
    )
    await interaction.response.send_message(embed=embed)


# ==================================================
# TRAIN — with buttons
# ==================================================


class TrainView(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=60)
        self.user_id = user_id

    @discord.ui.button(label="⚔️ Train Again", style=discord.ButtonStyle.danger)
    async def train_again(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This isn't yours!", ephemeral=True
            )
        gain = random.randint(50, 300)
        user = get_user(interaction.user.id)
        new_aura = user["aura"] + gain
        new_rank = get_rank(new_aura)
        upd(
            interaction.user.id,
            {"$inc": {"aura": gain, "xp": 20}, "$set": {"rank": new_rank}},
        )
        event = random.choice(
            [
                "⚡ Aura Surge Activated!",
                "🔥 Critical Awakening!",
                "👹 Shadow Beast Appeared!",
                "🌌 Cosmic Energy Resonated!",
            ]
        )
        embed = discord.Embed(
            title="⚔️ TRAINING COMPLETE",
            description=(
                f"⚡ Aura Gained: **+{gain}**\n"
                f"🧠 XP Gained:  **+20**\n"
                f"🌌 Event: {event}\n"
                f"🏆 Rank: **{new_rank}**"
            ),
            color=0xEF4444,
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="👤 Profile", style=discord.ButtonStyle.secondary)
    async def view_profile(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                "This isn't yours!", ephemeral=True
            )
        user = get_user(interaction.user.id)
        embed = discord.Embed(
            title=f"👤 {interaction.user.display_name}'s Profile",
            description=(
                f"┃ 🏆 Rank: **{user['rank']}**\n"
                f"┃ ⚡ Aura: **{user['aura']}**\n"
                f"┃ 🧠 XP:   **{user['xp']}**\n"
                f"┃ ⛩ Yen:  **{user['yen']}**"
            ),
            color=0xA855F7,
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.edit_message(embed=embed, view=self)


@bot.tree.command(name="train", description="Train your aura", guild=guild_obj)
async def slash_train(interaction: discord.Interaction):
    gain = random.randint(50, 300)
    user = get_user(interaction.user.id)
    new_aura = user["aura"] + gain
    new_rank = get_rank(new_aura)
    upd(
        interaction.user.id,
        {"$inc": {"aura": gain, "xp": 20}, "$set": {"rank": new_rank}},
    )
    event = random.choice(
        [
            "⚡ Aura Surge Activated!",
            "🔥 Critical Awakening!",
            "👹 Shadow Beast Appeared!",
            "🌌 Cosmic Energy Resonated!",
        ]
    )
    embed = discord.Embed(
        title="⚔️ TRAINING COMPLETE",
        description=(
            f"⚡ Aura Gained: **+{gain}**\n"
            f"🧠 XP Gained:  **+20**\n"
            f"🌌 Event: {event}\n"
            f"🏆 Rank: **{new_rank}**"
        ),
        color=0xEF4444,
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(
        embed=embed, view=TrainView(interaction.user.id)
    )


# ==================================================
# MEDITATE
# ==================================================


@bot.tree.command(
    name="meditate", description="Meditate to gain aura and influence", guild=guild_obj
)
async def slash_meditate(interaction: discord.Interaction):
    gain = random.randint(10, 80)
    user = get_user(interaction.user.id)
    new_aura = user["aura"] + gain
    new_rank = get_rank(new_aura)
    upd(
        interaction.user.id,
        {"$inc": {"aura": gain, "xp": 10, "influence": 1}, "$set": {"rank": new_rank}},
    )
    embed = discord.Embed(
        title="🧘 MEDITATION COMPLETE",
        description=(
            f"╭━━━ 🌌 RESULTS ━━━╮\n"
            f"┃ ⚡ Aura Gained: **+{gain}**\n"
            f"┃ 🧠 XP Gained:  **+10**\n"
            f"┃ 👑 Influence:  **+1**\n"
            f"┃ 🏆 Rank: **{new_rank}**\n"
            f"╰━━━━━━━━━━━━━━╯"
        ),
        color=0x6366F1,
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# RANK
# ==================================================


@bot.tree.command(name="rank", description="Check rank progress", guild=guild_obj)
@app_commands.describe(member="User to check (default: yourself)")
async def slash_rank(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    user = get_user(target.id)
    cur = user["rank"]
    idx = next((i for i, (r, _) in enumerate(RANK_ORDER) if r == cur), 0)
    if idx + 1 < len(RANK_ORDER):
        next_name, next_thresh = RANK_ORDER[idx + 1]
        needed = next_thresh - user["aura"]
        progress = f"**{needed} Aura** until **{next_name}**"
    else:
        progress = "🏆 **MAX RANK ACHIEVED**"
    embed = discord.Embed(
        title=f"🏆 {target.display_name}'s Rank",
        description=(
            f"╭━━━ 🌌 RANK INFO ━━━╮\n"
            f"┃ 🏆 Current: **{cur}**\n"
            f"┃ ⚡ Aura:    **{user['aura']}**\n"
            f"┃ 📈 Next:    {progress}\n"
            f"╰━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0xF59E0B,
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# COINFLIP
# ==================================================


@bot.tree.command(
    name="coinflip", description="Flip a coin to double or lose Yen", guild=guild_obj
)
@app_commands.describe(amount="Amount of Yen to bet")
async def slash_coinflip(interaction: discord.Interaction, amount: int):
    user = get_user(interaction.user.id)
    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Amount must be positive.", ephemeral=True
        )
    if user["yen"] < amount:
        return await interaction.response.send_message(
            "❌ Not enough Yen.", ephemeral=True
        )
    win = random.choice([True, False])
    if win:
        upd(interaction.user.id, {"$inc": {"yen": amount}})
        embed = discord.Embed(
            title="🪙 YOU WON!", description=f"**+{amount} Yen**", color=0x22C55E
        )
    else:
        upd(interaction.user.id, {"$inc": {"yen": -amount}})
        embed = discord.Embed(
            title="💀 YOU LOST!", description=f"**-{amount} Yen**", color=0xEF4444
        )
    await interaction.response.send_message(embed=embed)


# ==================================================
# SLOTS
# ==================================================


@bot.tree.command(name="slots", description="Spin the slot machine", guild=guild_obj)
@app_commands.describe(amount="Amount of Yen to bet")
async def slash_slots(interaction: discord.Interaction, amount: int):
    user = get_user(interaction.user.id)
    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Amount must be positive.", ephemeral=True
        )
    if user["yen"] < amount:
        return await interaction.response.send_message(
            "❌ Not enough Yen.", ephemeral=True
        )
    emojis = ["🍒", "💎", "🔥", "⚡", "👑"]
    s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
    result = f"**{s1} | {s2} | {s3}**"
    if s1 == s2 == s3:
        win = amount * 3
        upd(interaction.user.id, {"$inc": {"yen": win}})
        embed = discord.Embed(
            title="🎰 JACKPOT!",
            description=f"{result}\n\n💰 Won **{win} Yen**!",
            color=0x22C55E,
        )
    else:
        upd(interaction.user.id, {"$inc": {"yen": -amount}})
        embed = discord.Embed(
            title="🎰 No Match",
            description=f"{result}\n\n💀 Lost **{amount} Yen**",
            color=0xEF4444,
        )
    await interaction.response.send_message(embed=embed)


# ==================================================
# LEADERBOARD
# ==================================================


@bot.tree.command(
    name="leaderboard", description="Top 10 richest players", guild=guild_obj
)
async def slash_leaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    top = list(col.find().sort("yen", -1).limit(10))
    lines = []
    medals = ["🥇", "🥈", "🥉"]
    for i, u in enumerate(top):
        try:
            member = await bot.fetch_user(u["user_id"])
            icon = medals[i] if i < 3 else f"`{i + 1}.`"
            lines.append(f"{icon} **{member.name}** — {u['yen']} Yen")
        except Exception:
            pass
    embed = discord.Embed(
        title="🏆 RICHEST PLAYERS",
        description="\n".join(lines) or "No data yet.",
        color=0xEAB308,
    )
    await interaction.followup.send(embed=embed)


# ==================================================
# DEPOSIT / WITHDRAW
# ==================================================


@bot.tree.command(
    name="deposit", description="Deposit Yen into your bank", guild=guild_obj
)
@app_commands.describe(amount="Amount to deposit")
async def slash_deposit(interaction: discord.Interaction, amount: int):
    user = get_user(interaction.user.id)
    if amount <= 0 or amount > user["yen"]:
        return await interaction.response.send_message(
            "❌ Invalid amount.", ephemeral=True
        )
    upd(interaction.user.id, {"$inc": {"yen": -amount, "bank": amount}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🏦 Deposited",
            description=f"**{amount} Yen** moved to bank.",
            color=0x3B82F6,
        )
    )


@bot.tree.command(
    name="withdraw", description="Withdraw Yen from your bank", guild=guild_obj
)
@app_commands.describe(amount="Amount to withdraw")
async def slash_withdraw(interaction: discord.Interaction, amount: int):
    user = get_user(interaction.user.id)
    if amount <= 0 or amount > user["bank"]:
        return await interaction.response.send_message(
            "❌ Invalid amount.", ephemeral=True
        )
    upd(interaction.user.id, {"$inc": {"yen": amount, "bank": -amount}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🏦 Withdrawn",
            description=f"**{amount} Yen** moved to wallet.",
            color=0x3B82F6,
        )
    )


# ==================================================
# OWNER COMMANDS
# ==================================================


def owner_only(interaction: discord.Interaction) -> bool:
    return interaction.user.id == OWNER_ID


@bot.tree.command(
    name="addmoney", description="[Owner] Add Yen to a user", guild=guild_obj
)
@app_commands.describe(member="Target user", amount="Yen to add")
async def slash_addmoney(
    interaction: discord.Interaction, member: discord.Member, amount: int
):
    if not owner_only(interaction):
        return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
    get_user(member.id)
    upd(member.id, {"$inc": {"yen": amount}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="👑 Done",
            description=f"Added **{amount} Yen** to {member.mention}",
            color=0xFACC15,
        )
    )


@bot.tree.command(
    name="addmoneyall", description="[Owner] Add Yen to all users", guild=guild_obj
)
@app_commands.describe(amount="Yen to add to everyone")
async def slash_addmoneyall(interaction: discord.Interaction, amount: int):
    if not owner_only(interaction):
        return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
    col.update_many({}, {"$inc": {"yen": amount}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🌐 Done",
            description=f"Added **{amount} Yen** to ALL users.",
            color=0xFACC15,
        )
    )


@bot.tree.command(
    name="addaura", description="[Owner] Add Aura to a user", guild=guild_obj
)
@app_commands.describe(member="Target user", amount="Aura to add")
async def slash_addaura(
    interaction: discord.Interaction, member: discord.Member, amount: int
):
    if not owner_only(interaction):
        return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
    get_user(member.id)
    upd(member.id, {"$inc": {"aura": amount}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="⚡ Done",
            description=f"Added **{amount} Aura** to {member.mention}",
            color=0xFACC15,
        )
    )


@bot.tree.command(
    name="setrank", description="[Owner] Set a user's rank", guild=guild_obj
)
@app_commands.describe(member="Target user", rank_name="New rank name")
async def slash_setrank(
    interaction: discord.Interaction, member: discord.Member, rank_name: str
):
    if not owner_only(interaction):
        return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
    get_user(member.id)
    upd(member.id, {"$set": {"rank": rank_name}})
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🏅 Done",
            description=f"{member.mention} rank set to **{rank_name}**",
            color=0xFACC15,
        )
    )


# ==================================================
# AURA LEADERBOARD
# ==================================================


@bot.tree.command(
    name="auraleaderboard", description="Top 10 players by aura", guild=guild_obj
)
async def slash_auraleaderboard(interaction: discord.Interaction):
    await interaction.response.defer()
    top = list(col.find().sort("aura", -1).limit(10))
    medals = ["🥇", "🥈", "🥉"]
    lines = []
    for i, u in enumerate(top):
        try:
            member = await bot.fetch_user(u["user_id"])
            icon = medals[i] if i < 3 else f"`{i + 1}.`"
            lines.append(
                f"{icon} **{member.name}**\n⚡ Aura: **{u['aura']}** • 🏆 {u['rank']}\n"
            )
        except Exception:
            pass
    embed = discord.Embed(
        title="👑 SENJU REALM • AURA LEADERBOARD",
        description="\n".join(lines) if lines else "No data found.",
        color=0xA855F7,
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text="⚡ Only the strongest survive")
    await interaction.followup.send(embed=embed)


# ==================================================
# CRIME
# ==================================================


@bot.tree.command(
    name="crime", description="Commit a crime for rewards", guild=guild_obj
)
async def slash_crime(interaction: discord.Interaction):
    good_events = [
        "🏦 Robbed a corrupt bank",
        "💎 Stole legendary relics",
        "🌌 Looted a shadow dungeon",
        "⚔️ Defeated bounty hunters",
        "👑 Hacked a royal vault",
    ]
    bad_events = [
        "🚔 Aura police caught you",
        "💀 Your mission failed",
        "👹 A shadow beast attacked you",
        "⚡ Security systems detected you",
    ]
    if random.randint(1, 100) >= 40:
        amount = random.randint(500, 2500)
        upd(interaction.user.id, {"$inc": {"yen": amount, "aura": 25}})
        embed = discord.Embed(
            title="💀 CRIME SUCCESSFUL",
            description=(
                f"{random.choice(good_events)}\n\n"
                f"💰 Earned: **{amount} Yen**\n"
                f"⚡ Aura: **+25**"
            ),
            color=0x22C55E,
        )
    else:
        loss = random.randint(200, 1000)
        upd(interaction.user.id, {"$inc": {"yen": -loss}})
        embed = discord.Embed(
            title="🚔 CRIME FAILED",
            description=(f"{random.choice(bad_events)}\n\n💸 Lost: **{loss} Yen**"),
            color=0xEF4444,
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# ROB
# ==================================================


@bot.tree.command(name="rob", description="Rob another player", guild=guild_obj)
@app_commands.describe(member="User to rob")
async def slash_rob(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        return await interaction.response.send_message(
            "❌ You can't rob bots.", ephemeral=True
        )
    if member.id == interaction.user.id:
        return await interaction.response.send_message(
            "❌ You can't rob yourself.", ephemeral=True
        )
    target = get_user(member.id)
    if target["yen"] < 500:
        return await interaction.response.send_message(
            "💀 Target is too broke to rob.", ephemeral=True
        )
    if random.randint(1, 100) >= 45:
        steal = random.randint(300, min(2500, target["yen"]))
        upd(interaction.user.id, {"$inc": {"yen": steal, "aura": 15}})
        upd(member.id, {"$inc": {"yen": -steal}})
        embed = discord.Embed(
            title="🦹 ROB SUCCESSFUL",
            description=(
                f"💰 Stole **{steal} Yen** from {member.mention}\n⚡ Aura: **+15**"
            ),
            color=0x22C55E,
        )
    else:
        loss = random.randint(200, 1000)
        upd(interaction.user.id, {"$inc": {"yen": -loss}})
        embed = discord.Embed(
            title="🚔 ROB FAILED",
            description=(
                f"💀 You got caught trying to rob {member.mention}\n"
                f"💸 Lost **{loss} Yen**"
            ),
            color=0xEF4444,
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# FIGHT
# ==================================================


@bot.tree.command(name="fight", description="Fight another player", guild=guild_obj)
@app_commands.describe(member="Player to fight")
async def slash_fight(interaction: discord.Interaction, member: discord.Member):
    if member.bot:
        return await interaction.response.send_message(
            "❌ You can't fight bots.", ephemeral=True
        )
    if member.id == interaction.user.id:
        return await interaction.response.send_message(
            "❌ You can't fight yourself.", ephemeral=True
        )
    user1 = get_user(interaction.user.id)
    user2 = get_user(member.id)
    power1 = user1["aura"] + random.randint(1, 500)
    power2 = user2["aura"] + random.randint(1, 500)
    attacks = [
        "🔥 Crimson Slash",
        "⚡ Thunder Impact",
        "🌌 Void Burst",
        "👹 Shadow Strike",
        "☄️ Cosmic Punch",
    ]
    if power1 > power2:
        reward = random.randint(500, 2000)
        upd(interaction.user.id, {"$inc": {"yen": reward, "aura": 50}})
        embed = discord.Embed(
            title="⚔️ BATTLE RESULTS",
            description=(
                f"{interaction.user.mention} used **{random.choice(attacks)}**\n\n"
                f"🏆 Winner: {interaction.user.mention}\n"
                f"💰 Reward: **{reward} Yen**\n"
                f"⚡ Aura: **+50**"
            ),
            color=0x22C55E,
        )
    else:
        loss = random.randint(300, 1200)
        upd(interaction.user.id, {"$inc": {"yen": -loss}})
        embed = discord.Embed(
            title="💀 BATTLE LOST",
            description=(
                f"{member.mention} used **{random.choice(attacks)}**\n\n"
                f"💸 Lost: **{loss} Yen**"
            ),
            color=0xEF4444,
        )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)


# ==================================================
# LOAN
# ==================================================


@bot.tree.command(
    name="loan", description="Take a loan (20% interest)", guild=guild_obj
)
@app_commands.describe(amount="Amount to borrow")
async def slash_loan(interaction: discord.Interaction, amount: int):
    if amount <= 0:
        return await interaction.response.send_message(
            "❌ Invalid amount.", ephemeral=True
        )
    user = get_user(interaction.user.id)
    if user.get("debt", 0) > 0:
        return await interaction.response.send_message(
            "💀 You already have an unpaid loan.", ephemeral=True
        )
    total = amount + int(amount * 0.20)
    upd(interaction.user.id, {"$inc": {"yen": amount}, "$set": {"debt": total}})
    embed = discord.Embed(
        title="🏦 LOAN APPROVED",
        description=(
            f"💰 Received: **{amount} Yen**\n"
            f"📈 Interest: **20%**\n"
            f"💸 Repayment: **{total} Yen**"
        ),
        color=0x3B82F6,
    )
    await interaction.response.send_message(embed=embed)


# ==================================================
# PAY LOAN
# ==================================================


@bot.tree.command(
    name="payloan", description="Repay your outstanding loan", guild=guild_obj
)
async def slash_payloan(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    debt = user.get("debt", 0)
    if debt <= 0:
        return await interaction.response.send_message(
            "❌ You have no outstanding loan.", ephemeral=True
        )
    if user["yen"] < debt:
        return await interaction.response.send_message(
            f"💀 You need **{debt} Yen** to repay. You only have **{user['yen']}**.",
            ephemeral=True,
        )
    upd(interaction.user.id, {"$inc": {"yen": -debt}, "$set": {"debt": 0}})
    embed = discord.Embed(
        title="✅ LOAN REPAID",
        description=f"💸 You repaid **{debt} Yen**. You're debt-free!",
        color=0x22C55E,
    )
    await interaction.response.send_message(embed=embed)

# ==================================================
# SUMMON
# ==================================================

@bot.tree.command(name="summon", description="Summon an anime character (costs 5000 Yen)", guild=guild_obj)
async def slash_summon(interaction: discord.Interaction):
    user = get_user(interaction.user.id)
    if user["yen"] < 5000:
        return await interaction.response.send_message("💀 You need **5000 Yen** to summon.", ephemeral=True)
    await interaction.response.defer()
    picked    = random.choice(character_names)
    character = fetch_character(picked)
    if not character:
        return await interaction.followup.send("❌ Failed to summon a character. Try again.")
    roll = random.randint(1, 100)
    if roll <= 50:
        rarity = "🟢 Rare"
    elif roll <= 80:
        rarity = "🟣 Epic"
    elif roll <= 95:
        rarity = "🟡 Legendary"
    else:
        rarity = "🔴 Mythic"
    value = character["favorites"] * random.randint(8, 15)
    character_data = {"name": character["name"], "rarity": rarity, "value": value, "image": character["image"]}
    upd(interaction.user.id, {"$inc": {"yen": -5000, "summons": 1}, "$push": {"inventory": character_data}})
    embed = discord.Embed(
        title="🎴 CHARACTER SUMMONED",
        description=(
            f"╭━━━ 🌌 SUMMON RESULT ━━━╮\n"
            f"┃ 👤 Name: **{character['name']}**\n"
            f"┃ 💎 Rarity: **{rarity}**\n"
            f"┃ 💰 Value: **{value:,} Yen**\n"
            f"┃ 🔥 Popularity: **{character['favorites']:,}**\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━╯"
        ),
        color=0xa855f7,
    )
    embed.set_image(url=character["image"])
    embed.set_footer(text="⚡ SENJU REALM • Anime Summon")
    await interaction.followup.send(embed=embed)

# ==================================================
# INVENTORY
# ==================================================

@bot.tree.command(name="inventory", description="View your anime character collection", guild=guild_obj)
async def slash_inventory(interaction: discord.Interaction):
    user      = get_user(interaction.user.id)
    inventory = user.get("inventory", [])
    if not inventory:
        return await interaction.response.send_message("💀 Your inventory is empty.", ephemeral=True)
    lines       = []
    total_value = 0
    for i, char in enumerate(inventory[:15]):
        total_value += char["value"]
        lines.append(f"`{i+1}.` {char['rarity']} **{char['name']}** — 💰 {char['value']:,}")
    embed = discord.Embed(
        title=f"🎴 {interaction.user.display_name}'s Collection",
        description="\n".join(lines),
        color=0x7e22ce,
    )
    embed.add_field(
        name="🌌 Collection Stats",
        value=f"👑 Characters: **{len(inventory)}**\n💰 Total Value: **{total_value:,} Yen**",
        inline=False,
    )
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="⚡ SENJU REALM • Anime Inventory")
    await interaction.response.send_message(embed=embed)

# ==================================================
# SELL CHARACTER
# ==================================================

@bot.tree.command(name="sell", description="Sell a character from your inventory (75% value)", guild=guild_obj)
@app_commands.describe(number="Character number from /inventory")
async def slash_sell(interaction: discord.Interaction, number: int):
    user      = get_user(interaction.user.id)
    inventory = user.get("inventory", [])
    if not inventory:
        return await interaction.response.send_message("💀 Your inventory is empty.", ephemeral=True)
    if number < 1 or number > len(inventory):
        return await interaction.response.send_message("❌ Invalid character number.", ephemeral=True)
    character  = inventory[number - 1]
    sell_price = int(character["value"] * 0.75)
    inventory.pop(number - 1)
    upd(interaction.user.id, {"$set": {"inventory": inventory}, "$inc": {"yen": sell_price}})
    embed = discord.Embed(
        title="💰 CHARACTER SOLD",
        description=(
            f"🌌 Sold: **{character['name']}**\n\n"
            f"💎 Rarity: {character['rarity']}\n"
            f"💰 Received: **{sell_price:,} Yen**"
        ),
        color=0x22c55e,
    )
    embed.set_thumbnail(url=character["image"])
    await interaction.response.send_message(embed=embed)

# ==================================================
# SELL TO MARKET
# ==================================================

@bot.tree.command(name="sellmarket", description="List a character on the global market", guild=guild_obj)
@app_commands.describe(number="Character number from /inventory", price="Your asking price in Yen")
async def slash_sellmarket(interaction: discord.Interaction, number: int, price: int):
    user      = get_user(interaction.user.id)
    inventory = user.get("inventory", [])
    if not inventory:
        return await interaction.response.send_message("💀 Your inventory is empty.", ephemeral=True)
    if number < 1 or number > len(inventory):
        return await interaction.response.send_message("❌ Invalid character number.", ephemeral=True)
    if price <= 0:
        return await interaction.response.send_message("❌ Invalid price.", ephemeral=True)
    character = inventory[number - 1]
    inventory.pop(number - 1)
    upd(interaction.user.id, {"$set": {"inventory": inventory}})
    market_col.insert_one({
        "seller_id":   interaction.user.id,
        "seller_name": interaction.user.name,
        "price":       price,
        "character":   character,
    })
    embed = discord.Embed(
        title="🏪 CHARACTER LISTED",
        description=(
            f"🌌 **{character['name']}** listed on market\n\n"
            f"💰 Price: **{price:,} Yen**\n"
            f"👤 Seller: {interaction.user.mention}"
        ),
        color=0xf59e0b,
    )
    embed.set_thumbnail(url=character["image"])
    await interaction.response.send_message(embed=embed)

# ==================================================
# MARKET VIEW
# ==================================================

@bot.tree.command(name="market", description="Browse the global anime character market", guild=guild_obj)
async def slash_market(interaction: discord.Interaction):
    listings = list(market_col.find().limit(10))
    if not listings:
        return await interaction.response.send_message("💀 The market is empty right now.")
    lines = []
    for i, item in enumerate(listings):
        char = item["character"]
        lines.append(
            f"`{i+1}.` {char['rarity']} **{char['name']}**\n"
            f"💰 {item['price']:,} Yen • 👤 {item['seller_name']}\n"
        )
    embed = discord.Embed(
        title="🏪 GLOBAL ANIME MARKET",
        description="\n".join(lines),
        color=0x7e22ce,
    )
    embed.set_footer(text="⚡ Buy with /buycharacter <number>")
    await interaction.response.send_message(embed=embed)

# ==================================================
# BUY CHARACTER
# ==================================================

@bot.tree.command(name="buycharacter", description="Buy a character from the market", guild=guild_obj)
@app_commands.describe(number="Listing number from /market")
async def slash_buycharacter(interaction: discord.Interaction, number: int):
    listings = list(market_col.find().limit(10))
    if not listings:
        return await interaction.response.send_message("💀 The market is empty.")
    if number < 1 or number > len(listings):
        return await interaction.response.send_message("❌ Invalid listing number.", ephemeral=True)
    listing   = listings[number - 1]
    buyer     = get_user(interaction.user.id)
    if buyer["yen"] < listing["price"]:
        return await interaction.response.send_message("💀 Not enough Yen.", ephemeral=True)
    character = listing["character"]
    upd(interaction.user.id, {"$inc": {"yen": -listing["price"]}, "$push": {"inventory": character}})
    upd(listing["seller_id"], {"$inc": {"yen": listing["price"]}})
    market_col.delete_one({"_id": listing["_id"]})
    embed = discord.Embed(
        title="🛒 PURCHASE COMPLETE",
        description=(
            f"🌌 Bought **{character['name']}**\n\n"
            f"💰 Paid: **{listing['price']:,} Yen**\n"
            f"👤 Seller: **{listing['seller_name']}**"
        ),
        color=0x22c55e,
    )
    embed.set_image(url=character["image"])
    await interaction.response.send_message(embed=embed)

from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

keep_alive()
# ==================================================
# RUN
# ==================================================

bot.run(TOKEN)
