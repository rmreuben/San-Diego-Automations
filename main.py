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

GUILD_ID = 1279067581743108197  # replace with your server ID
# -------------------
# Channels
# -------------------
PROMOTION_LOG_CHANNEL_ID = 1425894157213372471  # where promotions go
INFRACTION_LOG_CHANNEL_ID = 1425894301333721178  # where infractions go
SUPPORT_ROLE_ID = 1424992786830327842  # ⬅️ the Support Team role ID
ASSISTANCE_CHANNEL_ID = 1403556064603144392 # ⬅️ channel where the Assistance embed should be posted
TICKET_LOG_CHANNEL_ID = 1424992791003402303 # ⬅️ channel where transcripts/logs go
TICKET_CATEGORY_ID = 1426040093704978526


guild = discord.Object(id=GUILD_ID)

# -------------------
# Helper functions
# -------------------
def has_permission(user: discord.Member):
    """Check if a user has HR, SHR, or FT role"""
    allowed_roles = ["━━━━━━━━━━━━ High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Senior High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Foundation Team ━━━━━━━━━━━━"]
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
    embed.set_author(name="Washington State RP", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User:", value=member.mention, inline=False)
    embed.add_field(name="New Rank:", value=f"<@&{role.id}>", inline=False)
    embed.add_field(name="Reason:", value=reason, inline=False)
    embed.add_field(name="Issued By:", value=interaction.user.mention, inline=False)
    embed.set_footer(text="Washington State RP Promotions")
    embed.timestamp = discord.utils.utcnow()
    embed.set_image(url="https://cdn.discordapp.com/attachments/1403553589573713930/1425900567401730148/Add_a_heading_-_2.png?ex=68e944e3&is=68e7f363&hm=2c0526a622d27ca2ff6cd8460b9f163151613748d6599f5378ab57f6c64b5630&")  # replace with the image URL you want

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
    allowed_roles = ["━━━━━━━━━━━━ Internal Affairs Team ━━━━━━━━━━━━", "━━━━━━━━━━━━ High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Senior High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Foundation Team ━━━━━━━━━━━━"]
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
    embed.set_author(name="Washington State RP", icon_url=bot.user.display_avatar.url)
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="User:", value=member.mention, inline=False)
    embed.add_field(name="Infraction Type:", value=infraction_type.value, inline=False)
    embed.add_field(name="Reason:", value=reason, inline=False)
    embed.add_field(name="Issued By:", value=interaction.user.mention, inline=False)
    embed.set_footer(text="Washington State RP Infractions")
    embed.timestamp = discord.utils.utcnow()
    embed.set_image(url="https://cdn.discordapp.com/attachments/1403553589573713930/1425900567078764544/Add_a_heading_-_3.png?ex=68e944e3&is=68e7f363&hm=8cf356ea7aae0fc99cdc16076cc436caf5734415cf746fc267da2c2ca150c863&")  # optional: replace with your infraction banner

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



# -------------------
# TICKET BUTTONS
# -------------------
class TicketButtons(discord.ui.View):
    def __init__(self, user: discord.Member):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not any(role.id == SUPPORT_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message("❌ You are not allowed to claim tickets.", ephemeral=True)
            return
        await interaction.response.send_message(f"✅ Ticket claimed by {interaction.user.mention}", ephemeral=False)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
        messages = [msg async for msg in interaction.channel.history(limit=100)]
        transcript = "\n".join(f"{msg.author}: {msg.content}" for msg in messages)
        if log_channel:
            await log_channel.send(f"**Ticket Transcript - {interaction.channel.name}**\n```{transcript}```")
        await interaction.channel.delete()

# -------------------
# TICKET DROPDOWN
# -------------------
class TicketDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Open a Support Ticket", emoji="🙋"),
            discord.SelectOption(label="Report", description="Report a Staff Member", emoji="📋")
        ]
        super().__init__(
            placeholder="Select a Ticket Type",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_dropdown"
        )

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0].lower()
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.get(guild.categories, id=TICKET_CATEGORY_ID)

        if not category:
            await interaction.response.send_message("❌ Ticket Category Not Found.", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.get_role(SUPPORT_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel_name = f"{ticket_type}-{user.name}".lower()
        ticket_channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

        embed = discord.Embed(
            title=f"{ticket_type.capitalize()} Ticket",
            description=f"Hi {user.mention}! 👋 Thanks for reaching out to our support team. For our team to best help you, please fill out the below format:\n\n",
            
            
            color=0xffe573
        )
                
        embed.set_footer(text="Washington State RP"),        
        embed.set_author(name="Washington State RP", 
                         icon_url=bot.user.display_avatar.url)
        await ticket_channel.send(
            content=f"<@&{SUPPORT_ROLE_ID}> {user.mention}",  # This actually pings
            embed=embed,
            view=TicketButtons(user)
        )
        await interaction.response.send_message(f"✅ Your {ticket_type} ticket has been created: {ticket_channel.mention}", ephemeral=True)

# -------------------
# TICKET VIEW
# -------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketDropdown())

@bot.tree.command(name="ticket-setup", description="Set up the assistance embed", guild=guild)
async def ticket_setup(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)  # hides the command usage

    embed = discord.Embed(
        title="Washington State RP - Assistance",
        description=(
            "> Our Support Team is dedicated to addressing the various enquiries our community members may have. \n"
            "⤷ For our team to best address your enquiry, please select the appropriate ticket type from the dropdown below.\n\n"
            "Do you have a General Enquiry for our Support Team? Open a `Support Ticket`, where our Support Team will be able to assist you!\n"
            "Is there a CSRP Staff Member who has broken a rule? Open a Report Ticket, where our Internal Affairs team will assist you."
        ),
        color=0xffe573  # change color to your preference
    )
    embed.set_author(name="Washington State RP", icon_url=bot.user.display_avatar.url)
    embed.set_footer(text="Washington State RP Ticket System")
    embed.set_image(url="https://media.discordapp.net/attachments/1403553589573713930/1425744425073508402/Add_a_heading.png?ex=68e95c37&is=68e80ab7&hm=e577e53a5aac102759dc90af5ab7d4b2a4c2d8a2cf47b75e0a62cc86f4fe2d17&=&format=webp&quality=lossless&width=2244&height=1092")

    view = TicketView()  # the view with the dropdown

    assistance_channel = bot.get_channel(ASSISTANCE_CHANNEL_ID)
    await assistance_channel.send(embed=embed, view=view)


# Close Command

@bot.tree.command(name="close", description="Close a ticket", guild=guild)
async def close(interaction: discord.Interaction):
    # Check that we're in the ticket category
    if interaction.channel.category_id != TICKET_CATEGORY_ID:
        await interaction.response.send_message("❌ This command can only be used inside a ticket channel.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)  # acknowledge command

    # Fetch all messages from the channel
    transcript = ""
    async for msg in interaction.channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
        author = msg.author
        content = msg.content
        transcript += f"[{timestamp}] {author}: {content}\n"

    # Save transcript to a file
    transcript_file = f"{interaction.channel.name}_transcript.txt"
    with open(transcript_file, "w", encoding="utf-8") as f:
        f.write(transcript)

    # Send transcript to the log channel
    log_channel = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
    if log_channel:
        await log_channel.send(
            content=f"Transcript for {interaction.channel.mention} closed by {interaction.user.mention}:",
            file=discord.File(transcript_file)
        )

    # Delete the ticket channel
    await interaction.channel.delete(reason=f"Ticket closed by {interaction.user}")


# -------------------
# Inactive ticket command
# -------------------
@bot.tree.command(name="inactive", description="Mark a ticket as inactive", guild=guild)
async def inactive(interaction: discord.Interaction):
    # Ensure the command is run in a ticket category channel
    if interaction.channel.category_id != TICKET_CATEGORY_ID:
        await interaction.response.send_message("❌ This command can only be used in ticket channels.", ephemeral=True)
        return

    # Ping the ticket owner (assuming the first message sender is the ticket creator)
    messages = await interaction.channel.history(limit=10).flatten()
    ticket_owner = None
    for msg in messages:
        if msg.author != bot.user:
            ticket_owner = msg.author
            break

    if ticket_owner:
        await interaction.response.send_message(
            f"⚠️ {ticket_owner.mention}, this ticket has been marked as inactive. Please respond to continue or use `/close` to close it.",
            ephemeral=False
        )
    else:
        await interaction.response.send_message("❌ Could not find the ticket owner.", ephemeral=True)

# /say Command

from discord import app_commands
import discord

# --- SAY COMMAND ---
@app_commands.command(name="say", description="HR+ can send a message as the bot")
async def say(interaction: discord.Interaction, message: str):
    await interaction.channel.send(message)
    await interaction.response.send_message("✅ Message sent!", ephemeral=True)
    # check for HR+ role
    if not any(role.name in ["━━━━━━━━━━━━ High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Senior High Ranking ━━━━━━━━━━━━", "━━━━━━━━━━━━ Foundation Team ━━━━━━━━━━━━"] for role in interaction.user.roles):
        await interaction.response.send_message("❌ You don’t have permission to use this.", ephemeral=True)
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
    return "Washington State RP is currently online, without any issues. To continue monitoring the bot, please visit https://dashboard.uptimerobot.com/monitors/801552933"

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
