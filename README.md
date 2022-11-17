
# Python discord bot that helps with events and clan management


There are five main areas where this bot can help you run your server
1. CR tracker. Members can use !cr/!res/!name commands to update their info. Bot also keeps track of active members with "home role" assigned
  
2. Role sync. There is an ability to sync member roles between multiple servers in a mesh form and update them on join or leave events.
When member from server1:role1 joins server2 member autoreceives role2 and name prefix

3. Kions tracker. Users with manage_roles permissions can create events for other officers to sign up

4. ROE groups manager. Assign people to groups. People can use commands like !mygroup or !whogroup to find their teammates

5. DI events tracker. AutoPosts Daily Diablo Immortal Events digest and 15 minutes update prior the event

If you have any questions reach out to hobz#8445 on discord
         



## Installation and pre-requisites

pip3 install -r requirements.txt


local .env file with the following information
```bash

env="PROD"
DISCORD_TOKEN_PROD=""
OWNER_DISCORD_ID=""
MYSQL_HOST=""
MYSQL_USER=""
MYSQL_PASSWORD=""
MYSQL_DB=""
```

SQL Schema and Events is  included in the resourcers/ folder

Run with 
```bash
  python3 main.py
```
    


## Bot Configuration Reference
ALLOW_CLAN_DATA: Allow viewing clan data on specified server ID

EVENT_ANNOUNCE_CHANNEL: Channel ID to announce game events

GUILD_HOME_ROLE: Role ID that will be used to check if user is in clan during the cross server sync

GUILD_NAME: Guild name that will be displayed on !top/!whois commands  

ROLE_SYNC: Value field is a column separated string with source_guild_id:source_guild_role:target_guild_role:prefix

TIME_CHANNEL: Voice channel that will be used to set current game time

KION_CHANNEL: Channel ID to announce kion events
## Demo


![cr_tools](https://i.imgur.com/Gh47gRE.png)

![kions](https://i.imgur.com/xK9ngvj.png)

![di_events](https://i.imgur.com/hXO8DjI.png)

![role_sync_in_action](https://i.imgur.com/Apv5Jlb.png)

