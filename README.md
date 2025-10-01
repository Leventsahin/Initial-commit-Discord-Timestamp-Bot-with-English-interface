# Discord Timestamp Bot

A Discord bot that creates dynamic timestamps for Discord messages. Convert dates, times, and durations into Discord's native timestamp format with interactive buttons and multiple display options.

## Features

- **📅 `/at` Command**: Convert specific dates and times to Discord timestamps
- **⏱️ `/in` Command**: Create timestamps for future times based on duration
- **🕐 `/now` Command**: Show current time with optional offset and timezone
- **❓ `/help` Command**: Comprehensive usage guide with examples
- **🔄 Interactive Buttons**: Switch between different timestamp formats
- **🔓 Public/Private Toggle**: Share timestamps publicly or keep them private
- **🌍 Timezone Support**: Supports various timezones and abbreviations
- **📋 Copy-Paste Ready**: Get formatted timestamp codes for use anywhere

## Supported Timestamp Formats

- **Short Time** (`t`): 16:20
- **Long Time** (`T`): 16:20:30
- **Short Date** (`d`): 20/04/2021
- **Long Date** (`D`): 20 April 2021
- **Short Date/Time** (`f`): 20 April 2021 16:20
- **Long Date/Time** (`F`): Tuesday, 20 April 2021 16:20
- **Relative Time** (`R`): 2 months ago

## Installation

### Prerequisites

- Python 3.8 or higher
- Discord.py library
- A Discord Bot Token

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/discord-timestamp-bot.git
   cd discord-timestamp-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Discord Bot Token**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Go to the "Bot" section
   - Copy the bot token

4. **Configure the bot**
   - Open `bot.py`
   - Replace `YOUR_BOT_TOKEN_HERE` with your actual bot token:
     ```python
     TOKEN = "your_bot_token_here"
     ```

5. **Run the bot**
   ```bash
   python bot.py
   ```

6. **Invite the bot to your server**
   - Go to OAuth2 > URL Generator in Discord Developer Portal
   - Select scopes: `bot`, `applications.commands`
   - Select permissions: `Send Messages`, `Use Slash Commands`
   - Use the generated URL to invite the bot

## Usage Examples

### `/at` Command
Convert specific dates and times:
```
/at date: 2025-12-31 time: 23:59 tz: UTC
/at date: 01.10.2025 time: 15:30 tz: GMT+3
/at date: 25/12/2024 time: 12:00 tz: Europe/Istanbul
```

### `/in` Command
Create timestamps for future times:
```
/in duration: 2h30m
/in duration: 1d12h
/in duration: 90m
/in duration: 1w3d
```

### `/now` Command
Show current time with options:
```
/now
/now tz: Europe/London
/now offset: +2h tz: UTC
/now offset: -30m
```

## Supported Date Formats

- **ISO Format**: YYYY-MM-DD (2025-12-31)
- **European Format**: DD.MM.YYYY (31.12.2025)
- **Alternative Format**: DD/MM/YYYY (31/12/2025)

## Supported Time Formats

- **24-hour format**: HH:mm (15:30)
- **With seconds**: HH:mm:ss (15:30:45)

## Supported Duration Formats

- **Minutes**: `30m`, `90m`
- **Hours**: `2h`, `24h`
- **Days**: `1d`, `7d`
- **Weeks**: `1w`, `2w`
- **Combined**: `1d12h30m`, `2w3d4h`

## Timezone Support

The bot supports various timezone formats:
- **UTC/GMT**: `UTC`, `GMT`, `GMT+0`
- **GMT Offsets**: `GMT+1` to `GMT+12`, `GMT-1` to `GMT-12`
- **Common Abbreviations**: `EST`, `PST`, `CST`, `MST`, `CET`, `EET`, `JST`, `IST`
- **Full Timezone Names**: `Europe/Istanbul`, `America/New_York`, `Asia/Tokyo`

## Interactive Features

- **Format Buttons**: Click to switch between different timestamp formats
- **Public Toggle**: Share timestamps publicly in the channel
- **Copy Hint**: Get instructions on how to copy and use timestamp codes

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
1. Check the `/help` command in Discord
2. Open an issue on GitHub
3. Make sure your bot token is correctly configured

## Changelog

### v1.0.0
- Initial release
- Basic timestamp conversion functionality
- Interactive buttons and public/private toggle
- Comprehensive timezone support
- Multi-language support (English)