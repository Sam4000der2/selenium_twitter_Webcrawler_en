# Selenium Twitter Webcrawler – English Version

[**To the German Version**](https://github.com/Sam4000der2/selenium_twitter_Webcrawler_de)

---

## Important Notes

- **Snap Packages:**  
  Selenium does not seem to support Snap packages. Therefore, **do not** use the Ubuntu distribution in combination with this project – Mint and Debian have proven to work well.

- **Firefox via Flatpak:**  
  Using Firefox via Flatpak has not been tested with this project.

- **Google Chrome:**  
  Chrome generally works with Selenium, but its integration may be less stable.

- **Twitter Login:**  
  To use Twitter lists, you must be logged in. Lists are the only reliably chronological views. The best approach is to log in to Twitter with a new profile in Firefox and then copy this profile to the target server (including Raspberry Pi, etc.). Adjust the profile path accordingly in the script. You can find your Firefox profile by navigating to `about:profiles`. The bot can also work without login, but in that case, the page must be publicly accessible without authentication.

---

## Overview

This project enables Twitter data crawling **without** using the official Twitter API. All retrieved tweets are automatically forwarded through two modules:

- **Telegram Bot:**  
  With optional filtering (e.g., by specific keywords, lines, or locations).

- **Mastodon Bot:**  
  Simple forwarding of tweets to Mastodon.

Additionally, there is a **Control Bot** for Telegram, allowing you to manage chat IDs, filter terms, and control the bot.

---

## Installation & Configuration

### Requirements

- **Python** (including pip)
- The following Python modules (installable via pip):
  - See requirements.txt

### Step-by-Step Guide

#### 1. Install Python and Required Modules

Ensure Python and pip are installed. Then, install the required modules:
```bash
pip install -r requirements.txt
```

#### 2. Adjustments for Publicly Accessible Twitter Data (No Login)

If you want to crawl Twitter data without logging in, make the following changes in the `twitter_bot.py` file:

- **Comment out:**
  ```python
  # firefox_profile = webdriver.FirefoxProfile(firefox_profile_path)
  # firefox_options.profile = firefox_profile
  ```
- **In the `def main()` function:**
  - Uncomment:
    ```python
    driver = webdriver.Firefox(options=firefox_options)
    ```
  - Comment out:
    ```python
    # driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile_path)
    ```
- **Additionally:**  
  Comment out the `delete_temp_files()` function, as it is probably not needed in this mode.

#### 3. Access to Non-Public Twitter Pages (e.g., Chronologically Sorted Lists)

- Adjust the `firefox_profile_path` value in `twitter_bot.py` to access protected or personalized pages.
- You can find your profile name under `about:profiles` in Firefox.

#### 4. Target Pages and Module Selection

- **Add Twitter Pages:**  
  Enter the Twitter page you want to capture tweets from in `twitter_bot.py`.
- **Disable Unnecessary Modules:**  
  Comment out the calls to the Telegram or Mastodon bots in `def main()` if you do not need them:
  ```python
  # await telegram_bot.main(new_tweets)
  # mastodon_bot.main(new_tweets)
  ```

#### 5. Set Up API Keys

- **Telegram:**  
  Get your API keys via [BotFather](https://t.me/BotFather) and enter them into the respective files.

- **Mastodon:**  
  The API key can be found in your instance's settings (under **Development**). Make sure the required permissions are granted – if changes are made, the API key must be regenerated. Also, specify your instance in the script. The Gemini API is used to generate free alt texts for images.

- **Gemini API (For Testing Purposes):**  
  Add your Gemini API key to your `~/.bashrc`. Open the file with:
  ```bash
  nano ~/.bashrc
  ```
  and add the line:
  ```bash
  export GOOGLE_API_KEY="YOURAPIKEY"
  ```
  You can get a free Gemini API key here: [Gemini API Key](https://aistudio.google.com/apikey).

#### 6. Test Run of the Bot

Run the bot in the appropriate directory for testing:
```bash
python twitter_bot.py
```
- **Note:**  
  Selenium usually tries to install the correct Geckodriver for Firefox automatically. If this does not work, download the Geckodriver manually:
  - **x64 & ARM:** [Geckodriver Releases](https://github.com/mozilla/geckodriver/releases)
  
  Extract Geckodriver and copy it to the system directory:
  ```bash
  sudo cp geckodriver /usr/local/bin/geckodriver
  ```

#### 7. Configure the Telegram Control Bot

If using the Telegram bot, add your API key to `telegram_controll_bot.py`.  
It is recommended to use an absolute path instead of `DATA_FILE = 'data.json'` – do not forget to apply this change in `telegram_bot.py` as well.

#### 8. Set Up Bots as a Service

To run the bot continuously in the background, set it up as a system service:

1. Create a service file:
   ```bash
   sudo nano /etc/systemd/system/twitter_bot.service
   ```
2. Add the following content, adjusting `YOURUSER` and `YOURAPIKEY`:
   ```ini
   [Unit]
   Description=twitter_bot
   After=network.target

   [Service]
   Environment="GEMINI_API_KEY=YOURAPIKEY"
   WorkingDirectory=/home/YOURUSER/bots
   ExecStart=/home/YOURUSER/bots/venv/bin/python3 /home/YOURUSER/bots/twitter_bot.py
   Restart=always
   RestartSec=10
   User=YOURUSER
   Group=YOURUSER

   [Install]
   WantedBy=multi-user.target
   ```
3. Reload system services:
   ```bash
   sudo systemctl daemon-reload
   ```
4. Start and enable the service:
   ```bash
   sudo systemctl start twitter_bot.service
   sudo systemctl enable twitter_bot.service
   ```
5. Set up `telegram_controll_bot` similarly.

#### 9. Completion

Congratulations – the bot should now be running successfully!

---

## Acknowledgment

Special thanks to [shaikhsajid1111](https://github.com/shaikhsajid1111/twitter-scraper-selenium/blob/main/twitter_scraper_selenium/element_finder.py). This project helped me understand how to use CSS selectors to extract tweets. It is particularly useful for beginners who want to crawl profiles, even though chronological sorting is often no longer available. My approach using Twitter lists offers more flexibility.

---

Best of luck using the Selenium Twitter Webcrawler!

