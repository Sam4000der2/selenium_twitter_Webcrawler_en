**Selenium Twitter Webcrawler - English Version**

***[ZUR DEUTSCHEN VERSION](https://github.com/Sam4000der2/selenium_twitter_Webcrawler_de)***

---

**Overview:**

This bot enables crawling Twitter data without using the Twitter API. It redirects all toots through the Telegram_Bot and Mastodon_Bot modules. In Telegram, there's the option to filter by keywords like specific lines or locations. Additionally, there's a Control-Bot to control the Telegram bot, allowing for the creation of chat IDs and filter terms, and to be operated by the user.

**Instructions:**

**Step 1:** Install Python with pip.

**Step 2:** Install the following modules with pip: selenium, mastodon.py, and python-telegram-bot.

**Step 3A:** If you want to crawl Twitter data without logging in, make the following changes in the file `twitter_bot.py`:

- Comment out `firefox_profile = webdriver.FirefoxProfile(firefox_profile_path)`.
- Comment out `firefox_options.profile = firefox_profile`.
- In the `def main()` function: Uncomment `driver = webdriver.Firefox(options=firefox_options)`.
- Comment out `driver = webdriver.Firefox(options=firefox_options, firefox_profile=firefox_profile_path)`.
- Also, comment out `delete_temp_files()`, as it's likely no longer needed.

**Step 3B:** If you want to access non-public Twitter pages, such as chronologically sorted lists, adjust the `firefox_profile_path` in the `twitter_bot.py` file. You can find your profile name from your current profile under `about:profiles`.

**Step 4:** Add the desired Twitter page whose tweets you want to crawl in `twitter_bot.py` and comment out unnecessary modules:

- If you don't need the Telegram bot, comment out `await telegram_bot.main(new_tweets)` in the `def main()`.
- If you don't need the Telegram bot, comment out `mastodon_bot.main(new_tweets)` in the `def main()`.

**Step 5:** Add API keys to the Telegram bots and the Mastodon bot:

- For Telegram, get the API keys from the account https://t.me/BotFather, where you can also set up your bots.
- For Mastodon, get the API key under `your_instance.example_social/settings/applications` (in the settings menu under Development). Don't forget to assign appropriate permissions; otherwise, you'll quickly get a 403 error. You'll need to regenerate the API key for any changes to the assigned permissions. Also, don't forget to enter your instance into the script.

**Step 6:** Test run the bot in the bot's folder: `python twitter_bot.py`.

- Ideally, the selenium module will automatically install the appropriate Geckodriver for Firefox.
- If not: Download the appropriate Geckodriver version (x64: [https://github.com/mozilla/geckodriver/releases](https://github.com/mozilla/geckodriver/releases) or arm: [https://github.com/jamesmortensen/geckodriver-arm-binaries/releases](https://github.com/jamesmortensen/geckodriver-arm-binaries/releases)). Unpack the Geckodriver and copy it from the open folder using the command `sudo cp geckodriver /usr/local/bin/geckodriver` to the appropriate folder.

**Step 7:** If you're using the Telegram bot, also add the API key in `telegram_controll_bot.py`. It's best to use an absolute path instead of `DATA_FILE = 'data.json'` for your bot folder, and don't forget to change this in `telegram_bot.py` as well.

**Step 8:** Set up the bots as services, so they can run permanently in the background.

- `sudo nano /etc/systemd/system/twitter_bot.service`

```plaintext
[Unit]
Description=twitter_bot
After=network.target

[Service]
WorkingDirectory=/[Path to your bot folder]
ExecStart=python twitter_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

- `sudo systemctl daemon-reload`
- `sudo systemctl start twitter_bot.service`
- `sudo systemctl enable twitter_bot.service`
- Do the same with the `telegram_controll_bot`.

**Step 9:** Congratulations, the bot should now be running.

Many thanks to [https://github.com/shaikhsajid1111/twitter-scraper-selenium/blob/main/twitter_scraper_selenium/element_finder.py](https://github.com/shaikhsajid1111/twitter-scraper-selenium/blob/main/twitter_scraper_selenium/element_finder.py), thanks to this project I got the CSS sectors to get the tweets. The project is suitable as a complete solution for beginners who only want to crawl profiles. However, these are often no longer sorted chronologically. That's why my approach with the Twitter lists and more freedom for the Twitter pages.
