import telegram_bot
import mastodon_bot
import time
import os
import asyncio
import logging
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from dateutil.parser import parse

#To call up non-publicly visible Twitter pages, the saved cookies from the Twitter login are required. Optional, of course
firefox_profile_path = "C:\\Users\\YOUR_USER\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\YOUR_PROFILE.default-release"
#firefox_profile_path = "/home/YOUR_USER/.mozilla/firefox/YOUR_PROFILE.default-release"

twitter_link = "https://twitter.com/i/lists/1741534129215172901"

#filename = "existing_tweets.txt"

firefox_options = Options()
firefox_options.headless = True   # Opens the browser invisibly for the user

#If you want to crawl Twitter without logging in, please exclude it:
firefox_profile = webdriver.FirefoxProfile(firefox_profile_path)
firefox_options.profile = firefox_profile


# Configure the logging
logging.basicConfig(filename='twitter_bot.log', level=logging.ERROR)

#selenium constantly creates a working copy of the Firefox profile, the function deletes this again. Otherwise the storage space will quickly run out.
#If you want to work on Twitter without logging in, this function and the profile option can be disabled.
def delete_temp_files():
    try:
        # Check temporary files in /tmp and /var/tmp
        for temp_dir in ['/tmp', '/var/tmp']:
            for root, dirs, files in os.walk(temp_dir):
                for name in files:
                    if name.startswith("rust_mozprofile") or name.startswith("tmp"):
                        os.remove(os.path.join(root, name))
    except Exception as ex:
         logging.error(f"Error deleting temp files: {ex}")

def find_all_tweets(driver):
    """Finds all tweets from the page"""
    try:
        tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        time.sleep(15)
        tweets = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweet"]')
        tweet_data = []
        for i, tweet in enumerate(tweets):
            tweet_parts = tweet.text.split("\n")
            
            user = tweet_parts[0]  # The user name is the first part of the first line content
            username = tweet_parts[1]  # The user is the first part of the user name

            content_element = tweet.find_element(By.CSS_SELECTOR, 'div[lang]')
            content = content_element.text
            
            replies_element = tweet.find_element(By.CSS_SELECTOR, '[data-testid="reply"]')
            replies = replies_element.text
            
            anchor = tweet.find_element(By.CSS_SELECTOR, "a[aria-label][dir]")
            var_href = anchor.get_attribute("href")
            
            timestamp = tweet.find_element(By.TAG_NAME, "time").get_attribute("datetime")
            
            # Parse timestamp
            posted_time_utc = parse(timestamp)

            # Check whether daylight saving time is currently in effect
            is_dst = bool(datetime.datetime.now().astimezone().dst())

            # Set local time zone (here as an example Berlin)
            local_timezone = datetime.timezone(datetime.timedelta(hours=2 if is_dst else 1))  # MESZ (UTC+2) oder MEZ (UTC+1)

            # Convert timestamp to local time zone
            posted_time_local = posted_time_utc.astimezone(local_timezone)

            # Define desired format for date and time
            desired_format = "%d.%m.%Y %H:%M"

            # Output timestamp in the desired format
            posted_time = posted_time_local.strftime(desired_format)
                       
            image_element = tweet.find_elements(By.CSS_SELECTOR,'div[data-testid="tweetPhoto"]')
            images = []
            
            for image_div in image_element:
                href = image_div.find_element(By.TAG_NAME,
                                              "img").get_attribute("src")
                images.append(href)
                href = href.replace("&name=small", "")
        
            extern_url_elements = tweet.find_elements(By.CSS_SELECTOR, '[data-testid="card.wrapper"]')
            extern_urls = []
            for extern_url_element in extern_url_elements:
                href_0 = extern_url_element.find_element(By.TAG_NAME, 'a')
                href = href_0.get_attribute("href")
                extern_urls.append(href)
            
            # Regular expression to recognise URLs
            url_pattern = re.compile(r"https?://\S+")
            content = url_pattern.sub('', content)
            
            url_pattern = re.compile(r"http?://\S+")
            content = url_pattern.sub('', content)
            
            if not images:
                images_as_string = ""
            else:
                images_as_string = str(images).replace("[]", "").replace("'", "")
                
            if not extern_urls:
                extern_urls_as_string = ""
            else:
                extern_urls_as_string = str(extern_urls).replace("[]", "").replace("'", "")

            
            tweet_data.append({
                "user": user,
                "username": username,
                "content": content,
                "posted_time": posted_time,
                "var_href": var_href,
                "images": images,
                "extern_urls": extern_urls,
                "images_as_string": images_as_string,
                "extern_urls_as_string": extern_urls_as_string
            })
           
 
        return tweet_data
    except Exception as ex:
        logging.error(f"Error finding tweets: {ex}")
        return []

def check_and_write_tweets(tweet_data):
    try:
        #Überprüfe, ob die Datei existiert und lese vorhandene Tweets
        if not os.path.exists(filename):
            # Wenn die Datei nicht existiert, erstelle sie
            open(filename, "a").close()  # Erstelle die Datei, falls sie nicht existiert

       # Öffne die Datei im Lese-Modus, um vorhandene Links zu überprüfen
        with open(filename, "r") as file:
            existing_tweets = file.read().splitlines()

        new_tweets = []
        # Überprüfe jeden Tweet in den Daten
        for n, tweet in enumerate(tweet_data, start=1):
            user = tweet['user']
            username = tweet['username']
            content = tweet['content']
            posted_time = tweet['posted_time']
            var_href = tweet['var_href']
            images = tweet['images']


            # Überprüfe, ob der Link bereits in den vorhandenen Tweets enthalten ist
            if var_href not in existing_tweets:
                new_tweets.append({
                    "user": user,
                    "username": username,
                    "content": content,
                    "posted_time": posted_time,
                    "var_href": var_href,
                    "images": images
                })

                # Wenn nicht, schreibe den Link in die Datei
                with open(filename, "a") as file:
                    file.write(var_href + "\n")

        return new_tweets
    except Exception as ex:
        logging.error(f"Error checking and writing tweets: {ex}")
        return []


def trim_existing_tweets_file():
    try:
        # Öffne die Datei im Lese-Modus, um die Anzahl der Zeilen zu überprüfen
        with open(filename, "r") as file:
            lines = file.readlines()
        
        # Überprüfe die Anzahl der Zeilen
        num_lines = len(lines)
        
        if num_lines > 100:
            # Wenn mehr als 100 Zeilen vorhanden sind, lösche die ältesten 50 Zeilen
            with open(filename, "w") as file:
                file.writelines(lines[50:])
            
            #print("Trimmed existing_tweets.txt file.")
        #else:
            #print("No trimming needed for existing_tweets.txt file.")
    except Exception as ex:
        logging.error(f"Error trimming existing_tweets.txt file: {ex}")


async def main():
    while True:
        try:
            #Falls du ohne einloggen Twitter crawlen willst:
            #driver = webdriver.Firefox(options=firefox_options)
            
            driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile_path)
            driver.get(twitter_link)
            tweet_data = find_all_tweets(driver)
            new_tweets = check_and_write_tweets(tweet_data)

            #print(new_tweets)

            # Aufruf der Funktion in telegram_bot.py
            await telegram_bot.main(new_tweets)

            # Aufruf der Funktion in mastodon_bot.py
            mastodon_bot.main(new_tweets)

            # Browser schließen
            driver.quit()

            trim_existing_tweets_file()

            #Falls du ohne einloggen Twitter crawlen willst, brauchst du die nicht mehr
            delete_temp_files()

            # Wartezeit, bevor die nächste Iteration beginnt
            await asyncio.sleep(60)   # Wartezeit in Sekunden (hier: 1 Minuten)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            # Fehlerbehandlung, z.B. Neustart des Browsers oder Wartezeit vor erneutem Versuch
            time.sleep(60)  # Wartezeit vor erneutem Versuch in Sekunden (hier: 1 Minute)
        
        
if __name__ == '__main__':
    #main()
    asyncio.run(main())



#Weitere css Selektoren findet ihr hier: https://github.com/shaikhsajid1111/twitter-scraper-selenium/blob/main/twitter_scraper_selenium/element_finder.py
