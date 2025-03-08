# TwitchChatPy

A Python application for Twitch channel point rewards and TTS integration.

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env`:
   ```
   cp .env.example .env
   ```
4. Edit the `.env` file and add your API keys:
   - TWITCH_CLIENT_ID: Your Twitch API client ID
   - TWITCH_CHANNEL_ID: Your Twitch channel ID
   - TWITCH_ACCESS_TOKEN: Your Twitch access token
   - OPENAI_API_KEY: Your OpenAI API key

5. Run the application:
   ```
   python ChannelPointRewards/ChannelPoints.py
   ```

## Important Security Notes

- Never commit your `.env` file containing API keys
- The `.env` file is in `.gitignore` to prevent accidental commits
- Use `.env.example` as a template without actual sensitive values
