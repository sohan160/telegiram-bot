# post_content.py

import os
import shutil
import asyncio

async def send_post_from_folder(client, folder_path, destination):
    message_file_path = os.path.join(folder_path, 'message.txt')
    if not os.path.exists(message_file_path): return False
    with open(message_file_path, 'r', encoding='utf-8') as f: caption = f.read()

    media_file = None
    for file in os.listdir(folder_path):
        if file != 'message.txt':
            media_file = os.path.join(folder_path, file)
            break
    try:
        if media_file:
            await client.send_file(destination, media_file, caption=caption, link_preview=False)
        elif caption:
            await client.send_message(destination, caption, link_preview=False)
        else:
            return False
        print(f"[✅] Successfully posted to '{destination}'.")
        return True
    except Exception as e:
        print(f"[❌] Error while posting: {e}")
        return False

# --- Main function for this module ---

async def check_and_post_from_queue(client, config):
    print("\n--- [🚀 POST MODE] Checking content for posting... ---")
    source_folder_path = os.path.join(config.BASE_FOLDER, config.TARGET_CHANNEL_FOR_POSTING)
    
    if not os.path.exists(source_folder_path):
        print(f"[⚠️] Source folder '{source_folder_path}' not found.")
        return 'empty'  # Folder is empty or does not exist

    post_folders = sorted([f for f in os.listdir(source_folder_path) if os.path.isdir(os.path.join(source_folder_path, f))])

    if not post_folders:
        print(f"[📂] Folder '{source_folder_path}' is empty. Nothing to post.")
        return 'empty'  # Folder is empty
        
    oldest_post_folder_name = post_folders[0]
    full_folder_path = os.path.join(source_folder_path, oldest_post_folder_name)
    
    print(f"[📦] Found {len(post_folders)} items to post. Processing the first one...")

    posted_successfully = await send_post_from_folder(client, full_folder_path, config.POST_DESTINATION)
    
    if posted_successfully:
        shutil.rmtree(full_folder_path)
        print(f"[🧹] Folder of the successful post ({oldest_post_folder_name}) has been deleted.")
        return 'posted'  # Posted successfully
    else:
        print("[🔄] Post failed. Will retry after some time.")
        return 'failed'  # Post failed
