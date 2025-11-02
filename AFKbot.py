# ...existing code...
import os
import asyncio
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands, tasks

# Configuration: set these as environment variables or replace with literal values.
# - DISCORD_TOKEN: your bot token
# - AFK_CHANNEL_ID: ID of the voice channel to move idle members to
# Optional:
# - CHECK_INTERVAL (seconds): how often to scan (default 30)
# - THRESHOLD_SECONDS: how long muted/deaf before moving (default 7*60)
TOKEN = os.getenv("DISCORD_TOKEN")
|
AFK_CHANNEL_ID = int(os.getenv("AFK_CHANNEL_ID", "0"))  # replace 0 with your channel id if you prefer
|
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "30"))
THRESHOLD_SECONDS = int(os.getenv("THRESHOLD_SECONDS", str(7 * 60)))

if not TOKEN or AFK_CHANNEL_ID == 0:
    print("Missing configuration. Set DISCORD_TOKEN and AFK_CHANNEL_ID environment variables.")
    raise SystemExit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)
# tracked: member_id -> first detection datetime (UTC)
tracked = {}


def is_muted_or_deaf(vs: discord.VoiceState) -> bool:
    if vs is None:
        return False
    return bool(vs.self_mute or vs.self_deaf or vs.mute or vs.deaf)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    if not check_afk_task.is_running():
        check_afk_task.start()


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    # If member left voice channel or is in AFK channel, remove from tracking
    if after is None or (after.channel and after.channel.id == AFK_CHANNEL_ID):
        tracked.pop(member.id, None)
        return

    # If member is muted/deaf (self or server), start tracking timestamp
    if is_muted_or_deaf(after):
        if member.id not in tracked:
            tracked[member.id] = datetime.now(timezone.utc)
            # optional debug
            print(f"Started tracking {member} at {tracked[member.id].isoformat()}")
    else:
        # Unmuted/un-deafened -> stop tracking
        if member.id in tracked:
            tracked.pop(member.id, None)
            print(f"Stopped tracking {member} (became active)")

@tasks.loop(seconds=CHECK_INTERVAL)
async def check_afk_task():
    now = datetime.now(timezone.utc)
    to_move = []
    for member_id, ts in list(tracked.items()):
        elapsed = (now - ts).total_seconds()
        if elapsed >= THRESHOLD_SECONDS:
            to_move.append(member_id)

    if not to_move:
        return

    # For each member to move, attempt to move to AFK channel
    channel = bot.get_channel(AFK_CHANNEL_ID)
    if channel is None:
        print(f"AFK channel {AFK_CHANNEL_ID} not found. Check configuration.")
        return

    for member_id in to_move:
        tracked.pop(member_id, None)
        # Find member object across guilds
        member = None
        for guild in bot.guilds:
            m = guild.get_member(member_id)
            if m and m.voice and m.voice.channel and m.voice.channel.id != AFK_CHANNEL_ID:
                member = m
                break
        if member is None:
            continue
        try:
            await member.move_to(channel, reason="Automatic AFK move: muted/deaf > threshold")
            print(f"Moved {member} to AFK channel {channel}.")
        except discord.Forbidden:
            print(f"Missing permission to move {member}.")
        except discord.HTTPException as e:
            print(f"Failed to move {member}: {e}")


@check_afk_task.after_loop
async def after_check():
    print("AFK checker stopped.")


if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        print("Interrupted, shutting down.")
# ...existing code...
