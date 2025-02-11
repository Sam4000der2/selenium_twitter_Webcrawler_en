import asyncio
import os
import logging
import requests
from tempfile import NamedTemporaryFile  # import only once
from PIL import Image
import io  # new import (if not already present)
import cairosvg  # new import for SVG conversion

import aiohttp
import aiofiles

from mastodon import Mastodon
from google import genai

# Initialize the Google Gemini client with the API key
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# Updated logging configuration for general use.
logging.basicConfig(
    filename='mastodon_bot.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s'
)
print("Logging configured")

# Renamed and simplified instance configuration for customization.
mastodon_instances = {
    'example_instance': {'access_token': 'your_access_token', 'api_base_url': 'https://your.instance.url'}
}
print("Instances configured")

# Use a generic post_status function. Customize visibility here if needed.
def post_status(mastodon, status_message, username, instance_name):
    try:
        mastodon.status_post(status_message, visibility='unlisted')  # change to 'public' if preferred
    except Exception as e:
        logging.error(f"Error posting to {instance_name}: {e}")

def shorten_text(text):
    # Replace all '@' with '#' and remove duplicate '#'
    text = text.replace('@', '#').replace('##', '#')
    text = text.replace('https://x.com', 'x')
    return text[:500] if len(text) > 500 else text

def extract_hashtags(content, username):
    # Remove a possible leading "@" from the username.
    if username.startswith("@"):
        username = username[1:]
    hashtags = ""
    for word in content.split():
        if word.startswith("#") and len(word) > 1:
            word = word.replace('.', '').replace(',', '').replace(':', '').replace(';', '')
            hashtags += f" {word}_{username}"
    return hashtags

async def download_image(session, url):
    try:
        async with session.get(url) as response:
            if response.status == 200:
                # Create a temporary path for the downloaded image
                temp_file_path = os.path.join('/tmp', os.path.basename(url))
                async with aiofiles.open(temp_file_path, 'wb') as f:
                    await f.write(await response.read())
                return temp_file_path
            else:
                logging.error(f"Error downloading image: {url}")
                return None
    except Exception as e:
        logging.error(f"Error downloading image: {e}")
        return None

async def generate_alt_text(client, image_path):
    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                'Generate an extensive alternative text (also called alt-text or image description) for the image, maximum 1500 characters. Reply with only the alternative text.',
                Image.open(image_path)
            ]
        )
        return response.text[:1500]
    except Exception as e:
        logging.error(f"Error generating alt-text: {e}")
        return ""

def prepare_image_for_upload(orig_image_bytes, ext):
    """
    Convert and process the image to JPG/PNG format,
    resize to max 1280px and compress below 8MB.
    """
    if ext == '.svg':
        orig_image_bytes = cairosvg.svg2png(bytestring=orig_image_bytes)
    elif ext not in ['.jpg', '.jpeg', '.png']:
        with Image.open(io.BytesIO(orig_image_bytes)) as img:
            output_io = io.BytesIO()
            img.convert('RGB').save(output_io, format='JPEG')
            orig_image_bytes = output_io.getvalue()
    processed_bytes = process_image_for_mastodon(orig_image_bytes)
    return processed_bytes

async def upload_media(mastodon, images, username):
    media_ids = []
    async with aiohttp.ClientSession() as session:
        for image_link in images:
            # Download image if not local
            if os.path.isfile(image_link):
                image_path = image_link
            else:
                image_path = await download_image(session, image_link)
            if image_path:
                try:
                    async with aiofiles.open(image_path, 'rb') as image_file:
                        orig_image_bytes = await image_file.read()
                    ext = os.path.splitext(image_path)[1].lower()
                    processed_bytes = prepare_image_for_upload(orig_image_bytes, ext)
                    temp_file = NamedTemporaryFile(delete=False, suffix=".jpg")
                    temp_file.write(processed_bytes)
                    temp_file.close()
                    image_description = await generate_alt_text(client, temp_file.name)
                    media_info = await asyncio.to_thread(
                        mastodon.media_post,
                        io.BytesIO(processed_bytes),
                        description=image_description,
                        mime_type='image/jpeg'
                    )
                    media_ids.append(media_info['id'])
                except Exception as e:
                    logging.error(f"Error in media post: {e}")
                finally:
                    if 'temp_file' in locals() and os.path.isfile(temp_file.name):
                        os.remove(temp_file.name)
                    if (not os.path.isfile(image_link)) and os.path.isfile(image_path):
                        os.remove(image_path)
            else:
                logging.error("No image path retrieved; skipping image.")
    return media_ids

# A unified asynchronous function for posting with images.
async def post_status_with_images(mastodon, status_message, images, username, instance_name):
    try:
        media_ids = await upload_media(mastodon, images, username)
        status_message = shorten_text(status_message)
        mastodon.status_post(status_message, media_ids=media_ids, visibility='unlisted')
    except Exception as e:
        logging.error(f"Error posting with images to {instance_name}: {e}")

async def main(new_tweets):
    print("Entering main function")
    # Iterate over all configured instances
    for instance_name, instance in mastodon_instances.items():
        try:
            access_token = instance['access_token']
            api_base_url = instance['api_base_url']
            print(f"Processing instance: {instance_name}")
        except KeyError as e:
            logging.error(f"Error accessing parameters for {instance_name}: {e}")
            continue

        try:
            mastodon = Mastodon(
                access_token=access_token,
                api_base_url=api_base_url
            )
            print(f"Created Mastodon object for {instance_name}")
        except Exception as e:
            logging.error(f"Error creating Mastodon object for {instance_name}: {e}")
            continue

        for tweet in new_tweets:
            user = tweet['user']
            username = tweet['username']
            content = tweet['content']
            posted_time = tweet['posted_time']
            source_url = tweet['var_href']  # renamed for clarity
            images = tweet['images']
            extern_urls = tweet['extern_urls']
            hashtags = extract_hashtags(content, username)
            status_message = (
                f"@{username}:\n\n{content}\n\n#bot\n\n"
                f"source: {source_url}\n{extern_urls}\n{posted_time}"
            )

            if not images:
                print(f"Posting status without images for {username}")
                post_status(mastodon, status_message, username, instance_name)
            else:
                print(f"Posting status with images for {username}")
                await post_status_with_images(mastodon, status_message, images, username, instance_name)

    print("Main function completed")

print("Script loaded")
