# This program keeps searching for existing user-created tera raids and notifies the user if a raid is found via telegram.
# The tera raid live data is taken from https://asia-northeast1-boshu-prod.cloudfunctions.net/boshu/boards/pokemonTeraraid/items_bundle

# Library to fetch the webpage data
import requests

# Libraries to send the telegram and discord messages
import telegram_send
import discord

# Library to wait for a certain amount of time
import time
import datetime

# Library to read the metadata json files
import json

# Library for regular expressions
import re

# The URL to fetch the webpage data
URL="https://asia-northeast1-boshu-prod.cloudfunctions.net/boshu/boards/pokemonTeraraid/items_bundle"

# The URL for the discord server to notify. It is read from the fil ".discord-url"
with open(".discord-url", "r") as discord_url_file:
    DISCORD_URL = discord_url_file.read()
    webhook = discord.SyncWebhook.from_url(DISCORD_URL)

# The list of subscriptions. Each subscription is a dictionary with the following keys (case-sensitive):
#   - Pokemon name: The desired pokemon tera raid to subscribe to. For regional forms, include the region demonym (e.g. Alolan Raichu, Paldean Wooper, Galarian Meowth, etc.)
#   - Tera type: The desired tera type to subscribe to. Can be either "Any" or any of the 18 elemental types.
#   - No. of ★: The desired tera raid star level to subscribe to. Can be either "Any" or "{number}★", where {number} is any number from 1 to 7.
#   - Join conditions: The join conditions to meet the raid. Can be: "Any", "Lvl. 100 Only", "Legends Only", "Type Focused" or "{specific pokemon} Only".
subscriptions = [
    {
        "Pokemon name": "Ditto",
        "Tera type": "Any",
        "No. of ★": "6★",
        "Join conditions": "Any"
    },

    {
        "Pokemon name": "Dragonite",
        "Tera type": "Any",
        "No. of ★": "6★",
        "Join conditions": "Any"
    },

    {
        "Pokemon name": "Cinderace",
        "Tera type": "Any",
        "No. of ★": "7★",
        "Join conditions": "Any"
    },

    {
        "Pokemon name": "Breloom",
        "Tera type": "Any",
        "No. of ★": "6★",
        "Join conditions": "Any"
    },
]

# Constant that defines the number of items to fetch each time.
FETCH_LIMIT = 30
# Constant that defines the time to wait between each fetch.
FETCH_INTERVAL = 5

# Read the metadata json files: pokemon-names.json and meta-names.json
with open("pokemon-names.json", "r") as pokemon_names_file:
    pokemon_names = json.load(pokemon_names_file)
with open("meta-names.json", "r") as meta_names_file:
    meta_names = json.load(meta_names_file)

# Create english to japanese and japanes to english dictionaries for pokemon names and metadata.
pokemon_names_eng_to_jpn = {}
pokemon_names_jpn_to_eng = {}

type_names_eng_to_jpn = {}
type_names_jpn_to_eng = {}

label_names_eng_to_jpn = {}
label_names_jpn_to_eng = {}

for pokemon in pokemon_names:
    pokemon_names_eng_to_jpn[pokemon["englishName"]] = pokemon["japaneseName"]
    pokemon_names_jpn_to_eng[pokemon["japaneseName"]] = pokemon["englishName"]

for meta in meta_names:
    if meta["type"] == "type":
        type_names_eng_to_jpn[meta["englishName"]] = meta["japaneseName"]
        type_names_jpn_to_eng[meta["japaneseName"]] = meta["englishName"]
    elif meta["type"] == "label":
        label_names_eng_to_jpn[meta["englishName"]] = meta["japaneseName"]
        label_names_jpn_to_eng[meta["japaneseName"]] = meta["englishName"]

# Regular expression to find integer numbers
int_regex = re.compile(b"\d+")

last_list = [[] for i in range(len(subscriptions))]
last_list_codes = [[] for i in range(len(subscriptions))]

# Start the loop
while True:
    # For each subscription item we convert it in a query string to be used in the URL
    for sid, subscription in enumerate(subscriptions):
        query = {}
        if subscription["Pokemon name"] != "Any":
            query["pokemonName"] = pokemon_names_eng_to_jpn[subscription["Pokemon name"]]
        if subscription["Tera type"] != "Any":
            query["terasType"] = type_names_eng_to_jpn[subscription["Tera type"]]
        if subscription["No. of ★"] != "Any":
            # Remove the last character from the string (the "★" character)
            query["difficultyLevel"] = subscription["No. of ★"][:-1]
        if subscription["Join conditions"] != "Any":
            query["requestTag"] = label_names_eng_to_jpn[subscription["Join conditions"]]
        
        query["limit"] = FETCH_LIMIT

        # Fetch the webpage data
        response = requests.get(URL, params=query)

        # Check if the response is valid
        if response.status_code == 200:
            # The response is valid. 
            dict_list = []
            # Convert response into a byte array.
            response_text = response.content
            
            # While response text is not empty
            while response_text:
                # First bytes in the array are an integer number.
                dict_length = int_regex.search(response_text).group(0)
                # Pop that number from the response text.
                response_text = response_text.replace(dict_length, b"", 1)
                dict_length = int(dict_length)
                # Pop dict_length characters from the response text.
                a_dict = response_text[:dict_length]
                response_text = response_text[dict_length:]
                # Convert the dictionary to a python dictionary.
                a_dict = json.loads(a_dict)
                # Append the dictionary to the list of dictionaries.
                dict_list.append(a_dict)

            # Filter the dictionary and get the relevant items.
            # We want only dictionaries that have the "document" key.
            filtered_dict_list = []
            for a_dict in dict_list:
                if "document" in a_dict and "isDeleted" in a_dict["document"]["fields"] and not a_dict["document"]["fields"]["isDeleted"]["booleanValue"]:
                    try:
                        new_dict = {}
                        # print(a_dict["document"]["fields"])
                        # We add only the needed keys and values to the new dictionary.
                        new_dict["pokemonName"] = pokemon_names_jpn_to_eng[a_dict["document"]["fields"]["pokemonName"]["stringValue"]]
                        if "terasType" in a_dict["document"]["fields"]:
                            new_dict["terasType"] = type_names_jpn_to_eng[a_dict["document"]["fields"]["terasType"]["stringValue"]]
                        else:
                            new_dict["terasType"] = "???"
                        new_dict["difficultyLevel"] = a_dict["document"]["fields"]["difficultyLevel"]["integerValue"] + "★"
                        if "values" in a_dict["document"]["fields"]["requestTags"]['arrayValue']:
                            new_dict["requestTags"] = [label_names_jpn_to_eng[a_dict["document"]["fields"]["requestTags"]["arrayValue"]["values"][i]["stringValue"]] for i in range(len(a_dict["document"]["fields"]["requestTags"]["arrayValue"]["values"]))]
                        else:
                            new_dict["requestTags"] = []
                        new_dict["passcode"] = a_dict["document"]["fields"]["passcode"]["stringValue"]

                        new_dict["remainingTime"] = 180 - (int(time.time()) - int(a_dict["document"]["fields"]["createdAt"]["timestampValue"]["seconds"]))
                        new_dict["remainingTimeStr"] = str(datetime.timedelta(seconds=new_dict["remainingTime"]))
                        new_dict["currentTimeStr"] = datetime.datetime.now().strftime("%H:%M:%S")
                        # Append the new dictionary to the list of new dictionaries.
                        if new_dict["remainingTime"] > 0:
                            filtered_dict_list.append(new_dict)

                    except KeyError as e:
                        print("KeyError: missing key " + str(e))
            print(json.dumps(filtered_dict_list, indent=2))

            # Send to telegram and discord only the new items (use passcode as unique identifier)
            for a_dict in filtered_dict_list:
                if a_dict["passcode"] not in last_list_codes[sid]:
                    message = f"Pokemon: <b>{a_dict['pokemonName']}</b>\nTera type: <b>{a_dict['terasType']}</b>\nDifficulty: <b>{a_dict['difficultyLevel']}</b>\nJoin conditions: <b>{', '.join(a_dict['requestTags'])}</b>\nCode: <code>{a_dict['passcode']}</code>\nTime left: <b>{a_dict['remainingTimeStr']}</b> <i>(at {a_dict['currentTimeStr']})</i>"
                    disc_message = f"--------------------------\nPokemon: **{a_dict['pokemonName']}**\nTera type: **{a_dict['terasType']}**\nDifficulty: **{a_dict['difficultyLevel']}**\nJoin conditions: **{', '.join(a_dict['requestTags'])} **\nCode: `{a_dict['passcode']}`\nTime left: **{a_dict['remainingTimeStr']}** *(at {a_dict['currentTimeStr']})*"
                    # For telegram
                    # telegram_send.send(messages=[message], parse_mode="HTML")
                    # For discord
                    webhook.send(disc_message)


            # Save list as last list.
            last_list[sid] = filtered_dict_list
            last_list_codes[sid] = [a_dict["passcode"] for a_dict in last_list[sid]] 

        else:
            # The response is not valid. Print the error code.
            print("Error: " + str(response.status_code))

            
    # Wait for FETCH_INTERVAL seconds before checking again.
    time.sleep(FETCH_INTERVAL)

    # Item example:
    """
    x = {'document': 
            {'name': '{url_name}}', 
            'fields': {'comment': {'stringValue': ''}, 
                       'ipAddress': {'stringValue': 'XXX.YYY.ZZZ.WWW'},'}, 
                       'numberOfRepopped': {'integerValue': '0'}, 
                       'passcode': {'stringValue': 'H877DB'}, 
                       'firebaseUserId': {'stringValue': 'XXXXXXXXXXXXXXXXXXXXXXXXXXXX'}, 
                       'id': {'stringValue': 'XXXXXXXXXXXXXXXXXXXX'}, 
                       'terasType': {'stringValue': 'ほのお'}, 
                       'pokemonName': {'stringValue': 'メタモン'}, 
                       'updatedAt': {'timestampValue': {'seconds': '1672274624', 
                                                        'nanos': 784000000}}, 
                       'createdAt': {'timestampValue': {'seconds': '1672274624', 
                                                        'nanos': 784000000}}, 
                       'requestTags': {'arrayValue': {'values': [{'stringValue': 'LV100のみ'}]}}, 
                       'raidType': {'stringValue': '通常'}, 
                       'numberOfParticipants': {'integerValue': '0'}, 
                       'isDeleted': {'booleanValue': False}, 
                       'difficultyLevel': {'integerValue': '6'}}, 
                       'createTime': {'seconds': '1672274624', 'nanos': 795920000}, 
                       'updateTime': {'seconds': '1672274624', 'nanos': 795920000}}}
    """
            
    # (Yes, everything is so over-commented just to get most of the job done by Copilot. Thanks!)
