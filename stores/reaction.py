import discord
import re
import os
import requests
import asyncio

from utils.validators import EmojiValidator

from dotenv import load_dotenv
load_dotenv()


class ReactionStore():
    def __init__(self, jb):
        self.jb = jb
        self.local_storage = {}
    
    def increment_emoji(self, payload):
        reaction = payload.emoji.name if payload.emoji.id is None else payload.emoji.id
        user = self.jb.get_user(payload.user_id).name
        
        try:
            u = self.local_storage[user]
            try:
                r = u[reaction]
                u[reaction] = r + 1
            except:
                self.local_storage[user][reaction] = 1
        except:
            self.local_storage[user] = {
                reaction: 1
            }
            print(f"Created self.local_storage object for {user}.")
        print(self.local_storage)
    
    def decrement_emoji(self, payload):
        reaction = payload.emoji.name if payload.emoji.id is None else payload.emoji.id
        user = self.jb.get_user(payload.user_id).name
        
        # Since these are temporary values, they will be summed
        # with total values in the myJson file. It's okay to have
        # negative values since they are measuring differentials.
        try:
            u = self.local_storage[user]
            try:
                r = u[reaction]
                u[reaction] = r - 1
            except:
                self.local_storage[user][reaction] = -1
        except:
            self.local_storage[user] = {
                reaction: -1
            }
            print(f"Created self.local_storage object for {user}.")
        print(self.local_storage)
    
    def push_to_cloud_store(self, storage_system=None):
        storage_system = storage_system if storage_system is not None else self.local_storage
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
            r = requests.put(os.environ['CLOUD_STORE_URL'], json=cloud_store)
            if r.ok:
                print("Updated cloud store.")
            if storage_system is not None:
                return
            else:
                self.local_storage = {}
        else:
            print("Failed to pull cloud store, will try again.")
    
    def clear_cloud_store(self):
        url = os.environ['CLOUD_STORE_URL']
        resp = requests.put(url, json={})
        if resp.ok:
            print("Cloud store cleared")
    
    def get_cloud_store(self):
        url = os.environ['CLOUD_STORE_URL']
        resp = requests.get(url)
        return resp.ok, resp.json()
    
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
                                print("Skipping JokeyBot")
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
