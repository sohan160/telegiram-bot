# save_posts.py

import os
import asyncio
from datetime import datetime

# --- Helper Functions ---

def get_last_processed_id(channel_name):
    last_id_file = f'last_id_{channel_name}.txt'
    if not os.path.exists(last_id_file): return 0
    with open(last_id_file, 'r') as f:
        try: return int(f.read().strip())
        except: return 0

def save_last_processed_id(channel_name, message_id):
    last_id_file = f'last_id_{channel_name}.txt'
    with open(last_id_file, 'w') as f: f.write(str(message_id))
    print(f"[🧠] New last ID for {channel_name}: {message_id}")

async def save_message(message, channel_name, base_folder):
    channel_folder = os.path.join(base_folder, channel_name)
    os.makedirs(channel_folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    post_folder = os.path.join(channel_folder, f'post_{timestamp}_{message.id}')
    os.makedirs(post_folder, exist_ok=True)
    
    text = message.text or ""
    with open(os.path.join(post_folder, 'message.txt'), 'w', encoding='utf-8') as f: f.write(text)
        
    if message.media:
        await message.download_media(file=post_folder)
        print(f"[💾] Message (ID: {message.id}) and media saved: {post_folder}")
    else:
        print(f"[💾] Only text message (ID: {message.id}) saved: {post_folder}")

# --- Main function for this module ---

async def fetch_and_save_new_posts(client, config):
    print("\n--- [🚀 FETCH MODE] Searching for new posts... ---")
    for channel in config.SOURCE_CHANNELS:
        print(f"\n[🔎] Checking channel '{channel}'...")
        try:
            last_id = get_last_processed_id(channel)
            new_messages = []
            
            if last_id == 0:
                print(f"[!] Running for the first time for '{channel}'. Saving last 5 posts...")
                async for message in client.iter_messages(channel, limit=5):
                    new_messages.append(message)
            else:
                async for message in client.iter_messages(channel, min_id=last_id):
                    new_messages.append(message)
            
            if new_messages:
                print(f"[✨] Found {len(new_messages)} new posts in '{channel}'!")
                for msg in reversed(new_messages):
                    await save_message(msg, channel, config.BASE_FOLDER)
                save_last_processed_id(channel, new_messages[0].id)
            else:
                print(f"[👍] No new posts found in '{channel}'.")

        except Exception as e:
            print(f"[❌] Error while processing channel '{channel}': {e}")
    print("\n--- [✅ FETCH MODE] Post fetching completed. ---")
