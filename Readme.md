# How to run the Discord AFK-move bot

This repository contains a small Discord bot that automatically moves voice members to an AFK voice channel if they have been muted/deafened for a configured amount of time.

Quick checklist
- Python 3.8+ installed (3.10+ recommended)
- A Discord bot token (Developer Portal)
- The bot invited to your guild with appropriate permissions
- The target AFK voice channel ID

1) Create a bot in the Discord Developer Portal
- Go to https://discord.com/developers/applications and create an Application.
- In the app, go to "Bot" → "Add Bot".
- Copy the Bot Token and store it somewhere safe (you will use it as DISCORD_TOKEN).
- Under "Privileged Gateway Intents" enable "SERVER MEMBERS INTENT" (this corresponds to intents.members in code).
- Save changes.

2) Invite the bot to your server
- In the Developer Portal -> OAuth2 -> URL Generator:
  - Scopes: select "bot"
  - Bot Permissions: give it at least:
    - View Channels
    - Connect
    - Move Members
  - Generate the invite URL and open it to invite the bot into your server.

3) Get the AFK voice channel ID
- In Discord, enable Developer Mode (User Settings → Advanced → Developer Mode).
- Right-click the voice channel you want to use as AFK → "Copy ID".
- Use that numeric ID for AFK_CHANNEL_ID.

4) Environment variables
The script reads configuration from environment variables:
- DISCORD_TOKEN (required) — the bot token
- AFK_CHANNEL_ID (required) — numeric voice channel ID
- CHECK_INTERVAL (optional, seconds) — default 30
- THRESHOLD_SECONDS (optional, seconds) — default 7 * 60 = 420

Examples:

Unix / macOS (bash/zsh):
export DISCORD_TOKEN="your_token_here"
export AFK_CHANNEL_ID="123456789012345678"
export CHECK_INTERVAL=30
export THRESHOLD_SECONDS=420
python bot.py

PowerShell:
$env:DISCORD_TOKEN="your_token_here"
$env:AFK_CHANNEL_ID="123456789012345678"
python bot.py

Windows CMD:
set DISCORD_TOKEN=your_token_here
set AFK_CHANNEL_ID=123456789012345678
python bot.py

(If you prefer a .env file, you can use python-dotenv and load it at the top of the script — the provided code uses os.getenv directly.)

5) Install dependencies
Create a virtual environment (recommended) and install the required package:

python -m venv .venv
source .venv/bin/activate    # macOS/Linux
.venv\Scripts\Activate.ps1   # Windows PowerShell

pip install -r requirements.txt

6) Run the bot
Once environment variables are set and dependencies installed:

python bot.py

You should see a console message like:
Logged in as <bot-name> (id: ...)

The background task will start and print debug messages when it starts/stops tracking members and when it moves members.

7) Permissions & common issues
- If the bot prints "AFK channel ... not found", verify AFK_CHANNEL_ID is correct and the bot is in the same guild.
- If the bot cannot move members, ensure it has the "Move Members" permission and its role is high enough in the role hierarchy if necessary.
- If the bot cannot see members or voice states, make sure "Server Members Intent" is enabled in the Developer Portal and that `intents.members = True` is set (the script already sets this).
- Restart the bot after changing intents in the Developer Portal.

8) Optional improvements
- Add logging (logging module) instead of print() for better runtime logs.
- Add a small CLI or .env loader (python-dotenv) to make local development easier.
- Run the bot as a systemd service, Docker container, or on a cloud host for continuous uptime.

If you want, I can:
- Provide an example .env loader change.
- Create a systemd unit file or Dockerfile to run this service.
- Add logging and a requirements file (already included below).
