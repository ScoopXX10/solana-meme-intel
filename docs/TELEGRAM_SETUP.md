# Telegram Bot Setup Guide

This guide will help you create a Telegram bot for receiving alerts from Solana Meme Intel.

## Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a conversation and send `/newbot`
3. Follow the prompts:
   - Choose a **name** for your bot (e.g., "Solana Meme Intel Alerts")
   - Choose a **username** (must end in `bot`, e.g., `solana_meme_intel_bot`)
4. BotFather will give you a **Bot Token** - save this!
   - Format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

## Step 2: Get Your Chat ID

You need your chat ID to receive messages from the bot.

### Option A: Personal Chat (1-on-1 with bot)

1. Start a conversation with your new bot (search for its username in Telegram)
2. Send any message to the bot (e.g., "Hello")
3. Open this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Find your chat ID in the response:
   ```json
   {
     "result": [{
       "message": {
         "chat": {
           "id": 123456789  <-- This is your Chat ID
         }
       }
     }]
   }
   ```

### Option B: Group Chat

1. Create a new Telegram group or use an existing one
2. Add your bot to the group (search for the bot's username and add it)
3. Send a message in the group mentioning the bot
4. Visit the `getUpdates` URL above
5. Group chat IDs are **negative numbers** (e.g., `-123456789`)

### Option C: Channel

1. Create a Telegram channel
2. Add your bot as an **Administrator** to the channel
3. Post something in the channel
4. Visit the `getUpdates` URL
5. Channel IDs start with `-100` (e.g., `-1001234567890`)

## Step 3: Configure Environment Variables

Add these to your `.env` file:

```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

Replace with your actual values.

## Step 4: Test the Bot

Run this command from your project directory:

```bash
python -c "
import asyncio
from src.alerts.telegram_bot import telegram_service

async def test():
    result = await telegram_service.send_message('Test alert from Solana Meme Intel!')
    print('Success!' if result else 'Failed - check your config')

asyncio.run(test())
"
```

You should receive a test message in Telegram.

## Alert Types

Once configured, you'll receive these alerts:

1. **New Token Discovery** - When high-potential new tokens are found
2. **Score Changes** - When a token's composite score changes by 5+ points
3. **Price Alerts** - When price moves 10%+ in either direction
4. **Liquidity Alerts** - When liquidity changes by 20%+

## Customizing Alert Thresholds

Edit `src/alerts/alert_manager.py` to adjust thresholds:

```python
SCORE_CHANGE_THRESHOLD = 5.0    # Points
PRICE_CHANGE_THRESHOLD = 10.0   # Percentage
LIQUIDITY_CHANGE_THRESHOLD = 20.0  # Percentage
```

## Troubleshooting

### "Telegram not configured" warning
- Verify both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are set in `.env`
- Make sure there are no extra spaces or quotes

### Bot doesn't respond
- Make sure you started a conversation with the bot first
- Check the bot token is correct (try the getUpdates URL)

### No messages received
- Verify the chat ID is correct
- For groups/channels, ensure the bot has permission to send messages
- Check that the bot is actually a member of the group/channel

### Rate limiting
- Telegram limits bots to ~30 messages per second
- If you're tracking many tokens, consider batching alerts
