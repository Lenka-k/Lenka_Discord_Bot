# Lenka's Discord Music Bot

## Just Skipalong :)

## We Will Not Grow Old :)

## Features

- Translations, get the bot in your preferred langauge!
- Round Robin style queue, you won't have to wait forever for your songs to play.
- Nice per server customization options & Toit embeds.
- DJ roles.

### Setup

1. Change or copy data/config.yaml.example to config.yaml
2. Create or find a [lavalink](https://github.com/freyacodes/Lavalink/releases) server you can use.
3. install requirements `python -m pip install -r requirements.txt`
4. Add your bot token in /data/config.yaml and lavalink server OR lavalink server package to the bot's root directory.
5. First start the lavalink server by opening a terminal or command prompt window in the Lavalink's package directory
   and run the command `java -jar Lavalink.jar` or whatever is the package name of lavalink package.
6. Edit any other settings you want.
7. open the terminal or command prompt in bot's directory and run the command `python3 bot.py` :)

### Docker

### Compose Example

````yaml
version: '3'
networks:
  internal:
    driver: bridge

services:
    backbone:
        hostname: lavalink
        image: fredboat/lavalink:dev
        ports:
        - 2333:2333
        networks:
            internal:
                aliases:
                  - lavalink
        volumes:
          - /compose/BottStack/lavalink/application.yml:/opt/Lavalink/application.yml
    bot:
        container_name: ProdMaster
        image: rnorge/music
        networks:
          - internal
        command: python3 bot.py
        volumes:
          - /compose/BottStack/ProdBetaMaster/script:/diks
          - /compose/BottStack/ProdBetaMaster/data:/app/data
````
