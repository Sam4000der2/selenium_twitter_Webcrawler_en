import asyncio
from mastodon import Mastodon

# Customisable variables
api_base_url = 'https://EXEMPEL.social'  # The base URL of your Mastodon instance
access_token = 'YOUR_TOKEN'  # Your access token


def post_tweet(mastodon, message):
    # Publish the tweet on Mastodon
    message_cut = truncate_text(message)
    mastodon.status_post(message_cut, visibility='unlisted')
    
    
def truncate_text(text):
    # Replace all '@' characters with '#'
    text = text.replace('@', '#')
    # Remove duplicate '#'
    text = text.replace('##', '#')
    # replace the beginning of the Twitter link with #shitter.
    text = text.replace('https://twitter.com', '#shitter ')
    # Check whether the text is longer than 500 characters. If so, only send the first 500 characters.
    if len(text) > 500:
        return text[:500]
    else:
        return text


    
def extract_hashtags(content, username):
    # Remove "@" symbol from the user name, if present
    if username.startswith("@"):
        username = username[1:]
    
    # Search for hashtags in the content
    hashtags = ""
    words = content.split()
    for word in words:
        if word.startswith("#") and len(word) > 1:
            word = word.replace('.', '')
            word = word.replace(',', '')
            word = word.replace(':', '')
            word = word.replace(';', '')
            hashtag_with_username = f"{word}_{username}"
            hashtags += " " + hashtag_with_username
            
    return hashtags

#Sending images currently only works as a link, so the function is currently not used.
def post_tweet_with_images(mastodon, message, images):
  # Publish the post with one or more pictures on Mastodon    
    message_cut = truncate_text(message)
    
    # Upload the images and receive the media IDs
    media = []
    for image_link in images:
        media = mastodon.media_post(image_link)
    
    # Publish the post with the attached images
    mastodon.status_post(message_cut, media_ids=[media['id']], visibility='unlisted')




def main(new_tweets):
    mastodon = Mastodon(
        access_token=access_token,
        api_base_url=api_base_url
    )
    
    for n, tweet in enumerate(new_tweets, start=1):
        user = tweet['user']
        username = tweet['username']
        content = tweet['content']
        posted_time = tweet['posted_time']
        var_href = tweet['var_href']

        images = tweet['images']
        hashtags = extract_hashtags(content, username)
        message = f"#{username}:\n\n{content}\n\n#öpnv_berlin_bot\n\nscr: {var_href}\n\nposted time (utc): {posted_time}"

        post_tweet(mastodon, message)
        
        #if not images:
            #print("")
            #post_tweet(mastodon, message)
        #else:
            #post_tweet_with_images(mastodon, message, images)

# The script should not run independently
if __name__ == "__main__":
    print("This script should be imported and not run directly.")
