# Requirements: discord.py>=2.3.2, python-dateutil, tzdata
# Installation: pip install -U discord.py python-dateutil tzdata
# Usage: python bot.py

import discord
from discord.ext import commands
from discord import app_commands
import re
import logging
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import asyncio

# ==================== CONFIG ====================
TOKEN = "YOUR_BOT_TOKEN_HERE"
DEFAULT_TZ = "UTC"
# ================================================

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Discord timestamp formats
TIMESTAMP_FORMATS = {
    't': 'Short Time',
    'T': 'Long Time', 
    'd': 'Short Date',
    'D': 'Long Date',
    'f': 'Short Date/Time',
    'F': 'Long Date/Time',
    'R': 'Relative Time'
}

# Timezone abbreviations mapping
TIMEZONE_ABBREVIATIONS = {
    'UTC': 'UTC',
    'GMT': 'GMT',
    'GMT+0': 'GMT',
    'GMT+1': 'Etc/GMT-1',
    'GMT+2': 'Etc/GMT-2',
    'GMT+3': 'Etc/GMT-3',
    'GMT+4': 'Etc/GMT-4',
    'GMT+5': 'Etc/GMT-5',
    'GMT+6': 'Etc/GMT-6',
    'GMT+7': 'Etc/GMT-7',
    'GMT+8': 'Etc/GMT-8',
    'GMT+9': 'Etc/GMT-9',
    'GMT+10': 'Etc/GMT-10',
    'GMT+11': 'Etc/GMT-11',
    'GMT+12': 'Etc/GMT-12',
    'GMT-1': 'Etc/GMT+1',
    'GMT-2': 'Etc/GMT+2',
    'GMT-3': 'Etc/GMT+3',
    'GMT-4': 'Etc/GMT+4',
    'GMT-5': 'Etc/GMT+5',
    'GMT-6': 'Etc/GMT+6',
    'GMT-7': 'Etc/GMT+7',
    'GMT-8': 'Etc/GMT+8',
    'GMT-9': 'Etc/GMT+9',
    'GMT-10': 'Etc/GMT+10',
    'GMT-11': 'Etc/GMT+11',
    'GMT-12': 'Etc/GMT+12',
    'EST': 'US/Eastern',
    'PST': 'US/Pacific',
    'CST': 'US/Central',
    'MST': 'US/Mountain',
    'CET': 'Europe/Berlin',
    'EET': 'Europe/Athens',
    'JST': 'Asia/Tokyo',
    'IST': 'Asia/Kolkata',
    'TRT': 'Europe/Istanbul'
}

class TimestampBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(command_prefix='!', intents=intents)
        
    async def setup_hook(self):
        await self.tree.sync()
        logger.info("Slash commands synchronized")
        
    async def on_ready(self):
        logger.info(f'{self.user} is ready!')

bot = TimestampBot()

def parse_timezone(tz_str):
    """Parse timezone string, supporting both IANA names and common abbreviations"""
    if not tz_str:
        return DEFAULT_TZ
    
    tz_str = tz_str.strip().upper()
    
    # Check if it's a known abbreviation
    if tz_str in TIMEZONE_ABBREVIATIONS:
        return TIMEZONE_ABBREVIATIONS[tz_str]
    
    # If not an abbreviation, return as-is (assume it's a valid IANA name)
    return tz_str.strip()

def parse_date(date_str):
    """Parse date string in various formats"""
    date_str = date_str.strip()
    
    # YYYY-MM-DD format (priority)
    match = re.match(r'^(\d{4})-(\d{1,2})-(\d{1,2})$', date_str)
    if match:
        year, month, day = map(int, match.groups())
        return year, month, day
    
    # DD.MM.YYYY format
    match = re.match(r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', date_str)
    if match:
        day, month, year = map(int, match.groups())
        return year, month, day
        
    # DD/MM/YYYY format
    match = re.match(r'^(\d{1,2})/(\d{1,2})/(\d{4})$', date_str)
    if match:
        day, month, year = map(int, match.groups())
        return year, month, day
    
    raise ValueError("Invalid duration format")

def parse_time(time_str):
    """Parse time string in HH:mm or HH:mm:ss format"""
    if not time_str:
        return 0, 0, 0
        
    time_str = time_str.strip()
    
    # HH:mm:ss format
    match = re.match(r'^(\d{1,2}):(\d{1,2}):(\d{1,2})$', time_str)
    if match:
        hour, minute, second = map(int, match.groups())
        return hour, minute, second
    
    # HH:mm format
    match = re.match(r'^(\d{1,2}):(\d{1,2})$', time_str)
    if match:
        hour, minute = map(int, match.groups())
        return hour, minute, 0
    
    raise ValueError("Invalid duration format")

def parse_duration(duration_str):
    """Parse duration string like 90m, 2h, 1d12h, 1w, 3d4h30m"""
    duration_str = duration_str.strip().lower()
    
    # Find all duration components
    pattern = r'(\d+)([wdhms])'
    matches = re.findall(pattern, duration_str)
    
    if not matches:
        raise ValueError("Invalid duration format")
    
    total_seconds = 0
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
    
    for value, unit in matches:
        total_seconds += int(value) * multipliers[unit]
    
    if total_seconds <= 0:
        raise ValueError("Duration must be positive")
        
    return total_seconds

def create_timestamp_embed(epoch, format_type, title, details, user_id):
    """Create embed with timestamp preview and buttons"""
    embed = discord.Embed(color=0x5865F2)
    embed.add_field(name=f"⏱️ {title}", value=f"<t:{epoch}:{format_type}>", inline=False)
    embed.add_field(name="📋 Code", value=f"`<t:{epoch}:{format_type}>`", inline=False)
    embed.add_field(name="ℹ️ Details", value=details, inline=False)
    
    return embed

def create_timestamp_view(epoch, current_format, user_id, is_public=False):
    """Create view with timestamp format buttons"""
    view = TimestampView(epoch, current_format, user_id, is_public)
    return view

class TimestampView(discord.ui.View):
    def __init__(self, epoch, current_format, user_id, is_public=False):
        super().__init__(timeout=300)
        self.epoch = epoch
        self.current_format = current_format
        self.user_id = user_id
        self.is_public = is_public
        
        # Add format buttons
        for fmt, label in TIMESTAMP_FORMATS.items():
            button = TimestampButton(fmt, label, fmt == current_format)
            self.add_item(button)
        
        # Add utility buttons
        self.add_item(PublicToggleButton(is_public))
        self.add_item(CopyHintButton())

class TimestampButton(discord.ui.Button):
    def __init__(self, format_type, label, is_current=False):
        style = discord.ButtonStyle.primary if is_current else discord.ButtonStyle.secondary
        super().__init__(style=style, label=format_type, custom_id=f"format_{format_type}")
        self.format_type = format_type
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This interaction doesn't belong to you!", ephemeral=True)
            return
            
        # Update view
        self.view.current_format = self.format_type
        
        # Update button styles
        for item in self.view.children:
            if isinstance(item, TimestampButton):
                item.style = discord.ButtonStyle.primary if item.format_type == self.format_type else discord.ButtonStyle.secondary
        
        # Create new embed
        embed = discord.Embed(color=0x5865F2)
        embed.add_field(name="⏱️ Dynamic Timestamp Ready", 
                       value=f"<t:{self.view.epoch}:{self.format_type}>", inline=False)
        embed.add_field(name="📋 Code", 
                       value=f"`<t:{self.view.epoch}:{self.format_type}>`", inline=False)
        embed.add_field(name="ℹ️ Format", 
                       value=f"{TIMESTAMP_FORMATS[self.format_type]} ({self.format_type})", inline=False)
        
        await interaction.response.edit_message(embed=embed, view=self.view)
        logger.info(f"User {interaction.user.id} changed format to {self.format_type} for epoch {self.view.epoch}")

class PublicToggleButton(discord.ui.Button):
    def __init__(self, is_public):
        label = "🔓 Make Public" if not is_public else "🔒 Make Ephemeral"
        super().__init__(style=discord.ButtonStyle.secondary, label=label, custom_id="toggle_public")
        self.is_public = is_public
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This interaction doesn't belong to you!", ephemeral=True)
            return
            
        if not self.is_public:
            # Send public message
            embed = discord.Embed(color=0x5865F2)
            embed.add_field(name="⏱️ Dynamic Timestamp", 
                           value=f"<t:{self.view.epoch}:{self.view.current_format}>", inline=False)
            embed.add_field(name="📋 Code", 
                           value=f"`<t:{self.view.epoch}:{self.view.current_format}>`", inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Update ephemeral message to show success
            embed_ephemeral = discord.Embed(color=0x57F287)
            embed_ephemeral.add_field(name="✅ Message Shared", 
                                    value="Timestamp sent to channel!", inline=False)
            await interaction.edit_original_response(embed=embed_ephemeral, view=None)
        else:
            # Toggle back to ephemeral - recreate the view with updated timestamp
            new_view = create_timestamp_view(self.view.epoch, self.view.current_format, self.view.user_id, is_public=False)
            embed = create_timestamp_embed(self.view.epoch, self.view.current_format, 
                                         "⏱️ Dynamic Timestamp Ready", "Select format and share options:", self.view.user_id)
            await interaction.response.edit_message(embed=embed, view=new_view)

class CopyHintButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.secondary, label="📋 Copy Hint", custom_id="copy_hint")
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.view.user_id:
            await interaction.response.send_message("❌ This interaction doesn't belong to you!", ephemeral=True)
            return
            
        await interaction.response.send_message(
            "💡 **Tip:** You can copy the code above and paste it in any channel!", 
            ephemeral=True
        )

@bot.tree.command(name="at", description="Convert a specific date and time to Discord timestamp")
@app_commands.describe(
    date="Date (YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY)",
    time="Time (HH:mm or HH:mm:ss, optional)",
    tz="Timezone (UTC, GMT, GMT+3, Europe/Istanbul etc.)"
)
async def at_command(interaction: discord.Interaction, date: str, time: str = None, tz: str = None):
    try:
        # Parse date
        year, month, day = parse_date(date)
        
        # Parse time
        hour, minute, second = parse_time(time)
        
        # Get timezone
        timezone = parse_timezone(tz)
        zone = ZoneInfo(timezone)
        
        # Create datetime
        dt = datetime(year, month, day, hour, minute, second, tzinfo=zone)
        epoch = int(dt.timestamp())
        
        # Create response
        embed = discord.Embed(color=0x5865F2)
        embed.add_field(name="⏱️ Dynamic Timestamp Ready", 
                       value=f"<t:{epoch}:F>", inline=False)
        embed.add_field(name="📋 Code", 
                       value=f"`<t:{epoch}:F>`", inline=False)
        embed.add_field(name="ℹ️ Details", 
                       value=f"Timezone: {timezone} · Input: {date} {time or '00:00'} · Epoch: {epoch}", 
                       inline=False)
        
        view = create_timestamp_view(epoch, 'F', interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        logger.info(f"User {interaction.user.id} used /at: {date} {time} {timezone} -> {epoch}")
        
    except ValueError as e:
        embed = discord.Embed(color=0xED4245)
        embed.add_field(name="❌ Error", 
                       value=str(e), inline=False)
        embed.add_field(name="📝 Example", 
                       value="Correct usage: `/at date: 2025-10-01 time: 15:30 tz: GMT+3`", 
                       inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(color=0xED4245)
        embed.add_field(name="❌ Unexpected Error", 
                       value="Invalid timezone or date value.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="in", description="Create Discord timestamp for a specific duration from now")
@app_commands.describe(duration="Duration (e.g: 90m, 2h, 1d12h, 1w, 3d4h30m)")
async def in_command(interaction: discord.Interaction, duration: str):
    try:
        # Parse duration
        seconds = parse_duration(duration)
        
        # Calculate future time
        now = datetime.now(ZoneInfo('UTC'))
        future_time = now + timedelta(seconds=seconds)
        epoch = int(future_time.timestamp())
        
        # Create response
        embed = discord.Embed(color=0x5865F2)
        embed.add_field(name="⏱️ Dynamic Timestamp Ready", 
                       value=f"<t:{epoch}:R>", inline=False)
        embed.add_field(name="📋 Code", 
                       value=f"`<t:{epoch}:R>`", inline=False)
        embed.add_field(name="ℹ️ Details", 
                       value=f"Duration: {duration} · Epoch: {epoch}", inline=False)
        
        view = create_timestamp_view(epoch, 'R', interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        logger.info(f"User {interaction.user.id} used /in: {duration} -> {epoch}")
        
    except ValueError as e:
        embed = discord.Embed(color=0xED4245)
        embed.add_field(name="❌ Error", 
                       value=str(e), inline=False)
        embed.add_field(name="📝 Example", 
                       value="Correct usage: `/in duration: 2h30m` or `/in duration: 1d`", 
                       inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="now", description="Show current time in different formats")
@app_commands.describe(
    offset="Time offset (e.g: +2h, -30m, +1d, optional)",
    tz="Timezone (UTC, GMT, GMT+3, Europe/Istanbul etc.)"
)
async def now_command(interaction: discord.Interaction, offset: str = None, tz: str = None):
    try:
        # Get current time
        timezone = parse_timezone(tz)
        zone = ZoneInfo(timezone)
        now = datetime.now(zone)
        
        # Apply offset if provided
        if offset:
            offset = offset.strip()
            sign = 1 if offset.startswith('+') else -1
            offset_str = offset[1:] if offset.startswith(('+', '-')) else offset
            offset_seconds = parse_duration(offset_str) * sign
            now += timedelta(seconds=offset_seconds)
        
        epoch = int(now.timestamp())
        
        # Create response
        embed = discord.Embed(color=0x5865F2)
        embed.add_field(name="⏱️ Dynamic Timestamp Ready", 
                       value=f"<t:{epoch}:F>", inline=False)
        embed.add_field(name="📋 Code", 
                       value=f"`<t:{epoch}:F>`", inline=False)
        embed.add_field(name="ℹ️ Details", 
                       value=f"Timezone: {timezone} · Offset: {offset or 'None'} · Epoch: {epoch}", 
                       inline=False)
        
        view = create_timestamp_view(epoch, 'F', interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        logger.info(f"User {interaction.user.id} used /now: offset={offset} tz={timezone} -> {epoch}")
        
    except ValueError as e:
        embed = discord.Embed(color=0xED4245)
        embed.add_field(name="❌ Error", 
                       value=str(e), inline=False)
        embed.add_field(name="📝 Example", 
                       value="Correct usage: `/now offset: +1d tz: GMT+3`", 
                       inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    except Exception as e:
        embed = discord.Embed(color=0xED4245)
        embed.add_field(name="❌ Unexpected Error", 
                       value="Invalid timezone or offset value.", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="help", description="Bot usage guide and examples")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Discord Timestamp Bot", color=0x5865F2)
    
    embed.add_field(
        name="📅 /at - Specific Date/Time",
        value="**Usage:** `/at date: 01.10.2025 time: 15:30 tz: GMT+3`\n"
              "**Date formats:** YYYY-MM-DD, DD.MM.YYYY, DD/MM/YYYY\n"
              "**Time formats:** HH:mm, HH:mm:ss (optional)",
        inline=False
    )
    
    embed.add_field(
        name="⏰ /in - Relative Duration",
        value="**Usage:** `/in duration: 2h30m`\n"
              "**Duration formats:** 90m, 2h, 1d12h, 1w, 3d4h30m\n"
              "**Units:** s(seconds), m(minutes), h(hours), d(days), w(weeks)",
        inline=False
    )
    
    embed.add_field(
        name="🕐 /now - Current Time",
        value="**Usage:** `/now offset: +1d tz: GMT+3`\n"
              "**Offset examples:** +2h, -30m, +1d\n"
              "**Timezones:** UTC, GMT, GMT+3, Europe/Istanbul",
        inline=False
    )
    
    embed.add_field(
        name="🎛️ Interactive Buttons",
        value="• **Format buttons:** t, T, d, D, f, F, R\n"
              "• **🔒/🔓 Toggle:** Ephemeral/Public switch\n"
              "• **📋 Hint:** Copy assistance",
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips",
        value="• All responses are initially visible only to you\n"
              "• Use buttons to change format and share to channel\n"
              "• Copy the code and use it in other channels",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

if __name__ == "__main__":
    if TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please update the TOKEN value in bot.py file!")
        print("🔗 To create a bot: https://discord.com/developers/applications")
    else:
        bot.run(TOKEN)

# ==================== README ====================
# Discord Timestamp Bot - Setup and Usage
# 
# 1. Requirements:
#    pip install -U discord.py python-dateutil tzdata
# 
# 2. Getting Bot Token:
#    - Go to https://discord.com/developers/applications
#    - Create new application with "New Application"
#    - Copy token from "Bot" tab
#    - Update TOKEN value in bot.py file
# 
# 3. Running the Bot:
#    python bot.py
# 
# 4. Adding to Server:
#    - OAuth2 > URL Generator > Scopes: bot, applications.commands
#    - Bot Permissions: Send Messages, Use Slash Commands
#    - Add to server with generated URL
# 
# 5. Usage:
#    /at date: 2025-12-31 time: 23:59 tz: Europe/Istanbul
#    /in duration: 2h30m
#    /now offset: +1d tz: UTC
#    /help
# ================================================