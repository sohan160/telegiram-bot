# main.py

import asyncio
from telethon import TelegramClient
from datetime import datetime

# Import modules and configuration
import config
from save_posts import fetch_and_save_new_posts
from post_content import check_and_post_from_queue as post_to_telegram
from post_to_facebook import check_and_post_to_facebook

# Initialize the Telegram client
client = TelegramClient('main_session3', config.API_ID, config.API_HASH)

async def main_loop():
    await client.start(phone=lambda: input('Please enter your phone number: '))
    print("[✅] Logged into Telegram successfully. Automation is starting...")

    while True:
        print("\n" + "="*80)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting new cycle...")

        # Step 1: Fetch and save new posts from all channels
        await fetch_and_save_new_posts(client, config)

        # Step 2: Post to Telegram (from modyolo_official)
        telegram_status = await post_to_telegram(client, config)
        
        # Step 3: Post to Facebook (from iPapkorn)
        # If content is available in the iPapkorn file, this function will try to post
        facebook_status = await check_and_post_to_facebook(config)

        # Step 4: Wait based on post status
        wait_times = []
        if telegram_status == 'posted': wait_times.append(config.POST_INTERVAL_SUCCESS)
        elif telegram_status == 'failed': wait_times.append(config.POST_INTERVAL_FAIL)
        
        if facebook_status == 'posted': wait_times.append(config.FACEBOOK_POST_INTERVAL_SUCCESS)
        elif facebook_status == 'failed': wait_times.append(config.FACEBOOK_POST_INTERVAL_FAIL)

        if not wait_times:
            wait_time = config.FETCH_INTERVAL
            print(f"\n[⏰] No items to post. New content will be fetched again after {wait_time // 60} minutes...")
        else:
            wait_time = min(wait_times)
            print(f"\n[⏰] Waiting {wait_time // 60} minutes for the next cycle...")

        for i in range(wait_time, 0, -1):
            minutes, seconds = divmod(i, 60)
            print(f"\r[⏳] Next cycle will start in: {minutes:02d}:{seconds:02d}", end='', flush=True)
            await asyncio.sleep(1)
        print()

if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main_loop())
