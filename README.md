# Tera Raid Bot

[![](https://img.shields.io/badge/language-Python-green.svg)](https://www.python.org/)
[![Python 3.8](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/downloads/release/python-380/)

A Python bot to notify via Telegram or Discord about user created tera raids in real time for Pokemon Scarlet/Violet.

## Instructions

Just install the dependencies and run `tera_bot.py`. The `telegram-send` and `discord` tokens and urls have to be specified in the corresponding files, which can be checked in their corresponding docs. To subscribe to an specific raid you have to modify the `subscriptions` list inside `tera_bot.py` as described there. There is not an interactive way to do it yet, but feel free to take the code and modify it to your needs.

The raid data is fetched from a database where the users manually inscribe their raids to ask for help.

## Requirements

- `Python=3.8`
- `telegram-send`
- `discord.py`
- `requests`
