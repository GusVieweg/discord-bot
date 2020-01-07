import discord
import re
import os
import requests
import asyncio
from collections import defaultdict

from utils.validators import EmojiValidator

from dotenv import load_dotenv
load_dotenv()


class ReactionStore():
    def __init__(self, jb):
        self.jb = jb
        self.cloud_store_url = os.environ['CLOUD_STORE_URL']
    
    def get_cloud_store(self):
        resp = requests.get(self.cloud_store_url)
        return resp.ok, resp.json()

    def clear_cloud_store(self):
        resp = requests.put(self.cloud_store_url, json={})
        if resp.ok:
            print("Cloud store cleared")

    def push_to_cloud_store(self, storage_system):
        ok, cloud_store = self.get_cloud_store()
        if (ok):
            print("Pulled cloud store.")
            emoji_count = 0
            for user in storage_system:
                try:
                    cloud_store[f"{user}"]
                except Exception as e:
                    print(e)
                    cloud_store[f"{user}"] = {}
                for reaction in storage_system[user]:
                    emoji_count += 1
                    try:
                        cloud_store[f"{user}"][f"{reaction}"] += storage_system[user][reaction]
                    except Exception as e:
                        cloud_store[f"{user}"][f"{reaction}"] = storage_system[user][reaction]
            print(f"Updating {emoji_count} records...")
            r = requests.put(self.cloud_store_url, json=cloud_store)
            if r.ok:
                print("Updated cloud store.")
            if storage_system is not None:
                return
            else:
                self.local_storage = {}
        else:
            print("Failed to pull cloud store, will try again.")
    
    async def get_all_reactions(self):
        function_storage = {
            "Total": {}
        }
        for guild in self.jb.guilds:
            for channel in guild.text_channels:
                if (channel.name == 'bot-test'):
                    break
                print(f"Computing totals for {channel.name}")
                async for msg in channel.history(limit=None):
                    for reaction in msg.reactions:
                        users = await reaction.users().flatten()
                        for user in users:
                            if (user.name == 'JokeyBot'):
                                break
                            name = user.name
                            emoji_id = reaction.emoji.id if reaction.custom_emoji else reaction.emoji
                            try:
                                u = function_storage[f"{name}"]
                                try:
                                    r = u[f"{emoji_id}"]
                                    function_storage[f"{name}"][f"{emoji_id}"] = r + 1
                                except:
                                    function_storage[f"{name}"][f"{emoji_id}"] = 1
                            except:
                                function_storage[f"{name}"] = {emoji_id: 1}
        
        for user in function_storage:
            for emoji in function_storage[user]:
                try:
                    function_storage["Total"][emoji] += function_storage[user][emoji]
                except:
                    function_storage["Total"][emoji] = function_storage[user][emoji]
                                
        print("Function storage completed! Pushing to cloud.")
        self.push_to_cloud_store(function_storage)

    def get_reaction_list(self, name, amount=-1):
        ok, cloud_store = self.get_cloud_store()
        names = cloud_store.keys()
        if name not in names:
            return f"User {name} not found. Use one of the following: {', '.join(list(names))}."
        else:
            emoji_validator = EmojiValidator()
            name_store = {k: v for k, v in sorted(cloud_store[name].items(), key=lambda item: item[1], reverse=True)}
            message = f"Reaction counts for {name}:\n"
            for idx, emoji_name in enumerate(name_store):
                if (amount == idx):
                    break
                emoji_count = name_store[emoji_name]
                if (emoji_validator.text_has_emoji(emoji_name)):
                    message += f"{idx+1}: {emoji_name} ({emoji_count})\n"
                else:
                    try:
                        custom_emoji = self.jb.get_emoji(int(emoji_name))
                        if custom_emoji is None:
                            custom_emoji = "Deleted"
                        message += f"{idx+1}: {custom_emoji} ({emoji_count})\n"
                    except:
                        message += f"{idx+1}: {emoji_name} ({emoji_count})\n"
            return message

    def get_emoji_stats(self, emoji_id):
        ok, cloud_store = self.get_cloud_store()
        flipped = defaultdict(dict)
        for key, val in cloud_store.items():
            for subkey, subval in val.items():
                flipped[subkey][key] = subval
        
        data = flipped[str(emoji_id)]
        print(data)
        data = {k: v for k, v in sorted(data.items(), key=lambda item: item[1], reverse=True)}
        message = f'Emoji Stats for {self.jb.get_emoji(emoji_id) or emoji_id}:\n'
        
        for idx, user in enumerate(data):
            user_stat = data[user]
            message += f'{idx+1}: {user} ({user_stat})\n'

        return message
