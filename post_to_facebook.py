# post_to_facebook.py (Direct API Call using requests)

import os
import shutil
import requests  # Using the requests library

# Base URL for Facebook API
FACEBOOK_GRAPH_URL = "https://graph.facebook.com/"

async def post_to_facebook_page(config, folder_path):
    print(f"\n[👍] Trying to post to Facebook page: {folder_path}")
    print("--- [DEBUG] Using DIRECT requests method. ---")  # Debug line

    message_file_path = os.path.join(folder_path, 'message.txt')
    if not os.path.exists(message_file_path):
        print(f"[⚠️] message.txt file not found!")
        return False
    
    with open(message_file_path, 'r', encoding='utf-8') as f:
        message_text = f.read()

    video_file_path = None
    photo_file_path = None
    
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    photo_extensions = ['.jpg', '.jpeg', '.png', '.gif']

    for file in os.listdir(folder_path):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_file_path = os.path.join(folder_path, file)
            break
    
    if not video_file_path:
        for file in os.listdir(folder_path):
            if any(file.lower().endswith(ext) for ext in photo_extensions):
                photo_file_path = os.path.join(folder_path, file)
                break
    
    try:
        if video_file_path:
            # === Code to post video directly ===
            print(f"[▶️] Posting video: {os.path.basename(video_file_path)}")
            video_upload_url = f"https://graph-video.facebook.com/v19.0/{config.FACEBOOK_PAGE_ID}/videos"
            files = {'source': open(video_file_path, 'rb')}
            params = {
                'access_token': config.FACEBOOK_PAGE_ACCESS_TOKEN,
                'description': message_text
            }
            response = requests.post(video_upload_url, files=files, params=params)

        elif photo_file_path:
            # === Code to post photo directly ===
            print(f"[▶️] Posting photo: {os.path.basename(photo_file_path)}")
            photo_upload_url = f"{FACEBOOK_GRAPH_URL}v19.0/{config.FACEBOOK_PAGE_ID}/photos"
            files = {'source': open(photo_file_path, 'rb')}
            params = {
                'access_token': config.FACEBOOK_PAGE_ACCESS_TOKEN,
                'message': message_text
            }
            response = requests.post(photo_upload_url, files=files, params=params)

        elif message_text:
            # === Code to post text directly ===
            print("[✍️] Posting text only...")
            text_post_url = f"{FACEBOOK_GRAPH_URL}v19.0/{config.FACEBOOK_PAGE_ID}/feed"
            params = {
                'access_token': config.FACEBOOK_PAGE_ACCESS_TOKEN,
                'message': message_text
            }
            response = requests.post(text_post_url, params=params)
        
        else:
            print("[⚠️] No content available for posting.")
            return False

        # Check response
        response.raise_for_status()  # Will raise an exception if HTTP error occurs
        response_data = response.json()

        if 'id' in response_data or 'post_id' in response_data:
            print("[✅] Successfully posted to Facebook page.")
            return True
        else:
            print(f"[❌] Unknown response from Facebook API: {response_data}")
            return False

    except requests.exceptions.HTTPError as e:
        print(f"[❌] HTTP error while posting to Facebook API: {e.response.json()}")
        return False
    except Exception as e:
        print(f"[❌] An unexpected error occurred: {e}")
        return False

# check_and_post_to_facebook function remains unchanged
async def check_and_post_to_facebook(config):
    print("\n--- [🚀 FACEBOOK POST MODE] Checking content for Facebook... ---")
    source_folder_path = os.path.join(config.BASE_FOLDER, config.FACEBOOK_SOURCE_CHANNEL)

    if not os.path.exists(source_folder_path):
        print(f"[⚠️] Facebook source folder '{source_folder_path}' not found.")
        return 'empty'

    post_folders = sorted([f for f in os.listdir(source_folder_path) if os.path.isdir(os.path.join(source_folder_path, f))])

    if not post_folders:
        print(f"[📂] Folder '{source_folder_path}' is empty. Nothing to post.")
        return 'empty'
    
    oldest_post_folder_name = post_folders[0]
    full_folder_path = os.path.join(source_folder_path, oldest_post_folder_name)

    print(f"[📦] Found {len(post_folders)} items for Facebook. Processing the first one...")

    posted_successfully = await post_to_facebook_page(config, full_folder_path)

    if posted_successfully:
        shutil.rmtree(full_folder_path)
        print(f"[🧹] Folder of the successful Facebook post ({oldest_post_folder_name}) has been deleted.")
        return 'posted'
    else:
        print("[🔄] Facebook post failed. Will try again later.")
        return 'failed'
