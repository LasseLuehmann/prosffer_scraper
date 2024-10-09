# Prosffer scrapy repo
1. create a virtual environment in your repo with `python3 -m venv .venv`
2. activate your virtual environment with `source .venv/bin/activate`
3. install all requirements with `pip install -r requirements.txt`
4. open a seperate terminal and install cronjob with `sudo apt install cron`
5. open your cronjb with `crontab -e` and add the following command at the end
   `* * * * * /path/to/your/sh/file/run_spider.sh >> /path/to/your/working/directory/log_file.log 2>&1`
   -> keep in mind that the * * * * * means that the code will be executed every minute so adjust it acordingly
7. save it and get back to your woring directory
8. in here you have to create a file called `run_spider.sh`
9. add the following code to that file
   `#!/bin/bash
    cd /path/to/your/repo/prosffer_scraper
    source .venv/bin/activate
    scrapy crawl kaufland &&
    scrapy crawl netto &&
    scrapy crawl aldi_sued &&
    scrapy crawl edeka
    wait
    deactivate`
11. additionaly add a .env file wich contains your Database information like
    `DB_NAME=prosffer_db
     DB_USER=prosffer_user
     DB_PWD=password123
     DB_PORT=5432
     DB_HOST=localhost`
