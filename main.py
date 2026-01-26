import discord
from discord.ext import commands
from discord import app_commands
import os

from keep_alive import keep_alive


# -------------------
# Bot setup
# -------------------
intents = discord.Intents.default()
intents.members = True  # required for pinging users
bot = commands.Bot(command_prefix="!", intents=intents)

GUILD_ID = 1462567895702831212  # replace with your server ID
# -------------------
# Channels
# -------------------
PROMOTION_LOG_CHANNEL_ID = 1463561484817797170  # where promotions go
INFRACTION_LOG_CHANNEL_ID = 1463561775269281792  # where infractions go


guild = discord.Object(id=GUILD_ID)

# -------------------
# Helper functions
# -------------------
def has_permission(user: discord.Member):
    """Check if a user has HR, SHR, or FT role"""
    allowed_roles = ["▬▬▬▬▬▬▬ High Ranking ▬▬▬▬▬▬▬", "▬▬▬▬▬▬▬ Senior High Ranking ▬▬▬▬▬▬▬", "▬▬▬▬▬▬▬ Foundation Team ▬▬▬▬▬▬▬"]
    return any(discord.utils.get(user.roles, name=role) for role in allowed_roles)

# -------------------
# PROMOTE command
# -------------------
@bot.tree.command(name="promote", description="Promote a Staff Member (HR+)", guild=guild)
@app_commands.describe(
    member="Staff Member to Promote", 
    role="New Rank", 
    reason="Reason for Promotion"
)
async def promote(interaction: discord.Interaction, member: discord.Member, role: discord.Role, reason: str):
    # Permission check
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    # Make sure the bot can assign the role
    if role >= interaction.guild.me.top_role:
        await interaction.response.send_message(f"❌ I cannot assign the role `{role.name}` because it is higher than my top role.", ephemeral=True)
        return

    # Assign role
    await member.add_roles(role)

    # Create customized embed
    embed = discord.Embed(
        title="🎉 Staff Promotion!",
        description=(
            "Congratulations! You have received a promotion. "
            "Please review the below details regarding your position. "
            "Our HR team will be in contact with you to help you transition into this role."
        ),
        color=discord.Color.from_rgb(255, 229, 115)  # ffe573
    )
    embed.set_author(name="San Diego City RP", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User:", value=member.mention, inline=False)
    embed.add_field(name="New Rank:", value=f"<@&{role.id}>", inline=False)
    embed.add_field(name="Reason:", value=reason, inline=False)
    embed.add_field(name="Issued By:", value=interaction.user.mention, inline=False)
    embed.set_footer(text="San Diego City RP Promotions")
    embed.timestamp = discord.utils.utcnow()
    embed.set_image(url="https://media.discordapp.net/attachments/1377761597858250943/1465261785375440896/image.jpg?ex=697876e0&is=69772560&hm=86fad7edf79068cb371450a07a2d8dc583df16cb47a4a0b9a320be05cfe4dc89&=&format=webp&width=2636&height=928")  # replace with the image URL you want

    # Send embed to log channel
    log_channel = interaction.guild.get_channel(PROMOTION_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

    # Send DM to member
    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ Could not DM {member.mention}", ephemeral=True)


    # Confirm to the command user
    await interaction.response.send_message(f"✅ {member.mention} has been promoted to {role.name}!", ephemeral=True)

# -------------------
# INFRACT command with dropdown
# -------------------
@bot.tree.command(name="infract", description="Infract a Staff Member (IA+)", guild=guild)
@app_commands.describe(
    member="Staff Member to Infract", 
    infraction_type="Select the Type of Infraction",
    reason="Reason for the Infraction"
)
@app_commands.choices(infraction_type=[
    app_commands.Choice(name="Warning", value="Warning"),
    app_commands.Choice(name="Strike", value="Strike"),
    app_commands.Choice(name="Demotion", value="Demotion"),
    app_commands.Choice(name="Termination", value="Termination"),
    app_commands.Choice(name="Suspension", value="Suspension"),
    app_commands.Choice(name="Under Investigation", value="Under Investigation"),
])
async def infract(interaction: discord.Interaction, member: discord.Member, infraction_type: app_commands.Choice[str], reason: str):
    # Permission check
    allowed_roles = ["Internal Affairs", "▬▬▬▬▬▬▬ High Ranking ▬▬▬▬▬▬▬", "▬▬▬▬▬▬▬ Senior High Ranking ▬▬▬▬▬▬▬", "▬▬▬▬▬▬▬ Foundation Team ▬▬▬▬▬▬▬"]
    if not any(discord.utils.get(interaction.user.roles, name=role) for role in allowed_roles):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    # Create embed
    embed = discord.Embed(
        title="❌ Staff Infraction",
        description=(
            f"You have received an infraction. Please review the details below regarding this action. If you have any questions, please contact the IA Team."
          
        ),
        color=discord.Color.red()
    )
    embed.set_author(name="San Diego City RP", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User:", value=member.mention, inline=False)
    embed.add_field(name="Infraction Type:", value=infraction_type.value, inline=False)
    embed.add_field(name="Reason:", value=reason, inline=False)
    embed.add_field(name="Issued By:", value=interaction.user.mention, inline=False)
    embed.set_footer(text="San Diego City RP Infractions")
    embed.timestamp = discord.utils.utcnow()
    embed.set_image(url="https://media.discordapp.net/attachments/1377761597858250943/1465261785090097273/image.jpg?ex=697876e0&is=69772560&hm=84e9f04c12b0d8223e5e6d538ee81fb390e63cf71ad01c6e5823546b80df92d5&=&format=webp&width=2636&height=928")  # optional: replace with your infraction banner

    # Send embed to log channel
    log_channel = interaction.guild.get_channel(INFRACTION_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(embed=embed)

    # Send DM to member
    try:
        await member.send(embed=embed)
    except discord.Forbidden:
        await interaction.followup.send(f"⚠️ Could not DM {member.mention}", ephemeral=True)


    # Confirm to the command user
    await interaction.response.send_message(f"✅ {member.mention} has received a **{infraction_type.value}**.", ephemeral=True)




# /say Command

from discord import app_commands
import discord

# --- SAY COMMAND ---
@app_commands.command(name="say", description="HR+ can send a message as the bot")
async def say(interaction: discord.Interaction, message: str):
    await interaction.channel.send(message)
    await interaction.response.send_message("✅ Message sent!", ephemeral=True)
   # Permission check
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return


    # bot sends the message
    await interaction.response.send_message(message)

# --- REGISTER THE COMMAND ---
# make sure this line is **after** you define 'say'
bot.tree.add_command(say, guild=guild)

# DM Command
@bot.tree.command(name="dm", description="Send a DM to a user", guild=guild)
@app_commands.describe(
    member="User to DM",
    message="Message to send"
)
async def dm(interaction: discord.Interaction, member: discord.Member, message: str):
    # Permission check (HR+)
    if not has_permission(interaction.user):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    try:
        await member.send(f"{message}")
        await interaction.response.send_message(f"✅ DM sent to {member.mention}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(f"❌ Could not send a DM to {member.mention}", ephemeral=True)

    
# ------------------ ON READY ------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await bot.tree.sync(guild=guild)
    print("Slash commands synced!")
    bot.add_view(TicketView())  # persistent view for dropdowns

# ------------------- Keep Alive Function -------------------

from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def home():
    return "San Diego City RP is currently online, without any issues. To continue monitoring the bot, please visit https://dashboard.uptimerobot.com/monitors/801552933"

def run():
    app.run(host="0.0.0.0", port=5500)

# Start Flask in a separate thread
Thread(target=run).start()

# -------------------
# Run bot
# -------------------
keep_alive()
print("Starting bot...")
bot.run(os.getenv("TOKEN"))
# Add persistent views so dropdowns/buttons work after bot restart
