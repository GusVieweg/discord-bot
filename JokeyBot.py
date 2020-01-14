import discord
import re
import os
import requests
import time
from datetime import datetime

from stores.reaction import ReactionStore
from utils.validators import EmojiValidator
from utils.EdgarFacts import EdgarFacts

from dotenv import load_dotenv
load_dotenv()

class JokeyBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super(JokeyBot, self).__init__(*args, **kwargs)
        self.reaction_store = ReactionStore(self)
    
    async def nightly_cloud_reset(self):
        print("Running nightly cloud reset.")
        self.reaction_store.clear_cloud_store()
        await self.reaction_store.get_all_reactions()
        print("Nightly cloud reset complete.")
    
    async def on_help_filter(self, message):
        if (re.search(r'help', message.content, re.IGNORECASE)):
            await message.channel.send("""
                Hello! I'm JokeyBot. Feel free to refer to me as 'JokeyBot' or 'JB'.

Here are some commands I respond to:
- "get top `<amount (limit 50)>` reaction list for `<user>`"
- "get emoji stats for `<emoji>`"
- "scoreboard"
- "edgar fact"
- "help"

Some example commands:
- "jb hit me with an edgar fact"
- "Jokeybot scoreboard"
- "jb get top 50 reaction list for PatPov"

Thanks, Edgars!
            """)
    
    async def on_edgar_fact_filter(self, message):
        if (re.search(r'edgar fact', message.content, re.IGNORECASE)):
            ef = EdgarFacts()
            await message.channel.send(ef.get_edgar_fact())

    async def on_jokeybot_status_filter(self, message):
        if (re.search(r"^JokeyBot, status!$", message.content, re.IGNORECASE)):
            if (os.environ['MAINTENANCE_MODE']):
                await message.channel.send(f"Sorry Edgars, but I'm down for maintenance right now.\n\nI'll come back even stronger and jokier before you know it though!")

    async def on_actually_filter(self, message):
        if (re.search('actually', message.content, re.IGNORECASE)):
            emoji = '<:WellActually:656886620859006976>'
            await message.add_reaction(emoji)
    
    async def on_together_filter(self, message):
        content = message.content
        if (re.search('together', content, re.IGNORECASE)):
            pattern = re.sub('together', "_TOG-EDGAR_", content, flags=re.IGNORECASE)
            await message.channel.send(f'Or should you say, "{pattern}"?')

    async def on_dad_filter(self, message):
        if (re.search(r"[\s]dad[\W]|^dad$|[\s]dad$", message.content, re.IGNORECASE)):
            await message.channel.send(f"I'm not your _fucking_ dad.")

    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
    
    async def on_update_cloud_store_filter(self, message):
        if (re.search('update_cloud_store', message.content, re.IGNORECASE)):
            self.reaction_store.push_to_cloud_store()
    
    async def on_cloud_store_clear_filter(self, message):
        if (re.search('clear_cloud_store', message.content, re.IGNORECASE)):
            self.reaction_store.clear_cloud_store()
    
    async def on_scoreboard_filter(self, message):
        if (re.search('scoreboard', message.content, re.IGNORECASE)):
            ok, json = self.reaction_store.get_cloud_store()
            lols = json["Total"]["453333328347791401"]
            darns = json["Total"]["453333295086960660"]
            lf = round((lols / (lols + darns))*100, 2)
            df = round((darns / (lols + darns))*100, 2)
            net = round(lf - df, 2)
            await message.channel.send(f"""```Lol Factor:   {lf}%\nDarn Factor:  {df}%\nNet Jokiness: {net}%```""")
    
    async def on_hug_filter(self, message):
        if (re.search(r"\shug($|\s)", message.content, re.IGNORECASE)):
            await message.channel.send(f"Hey there, {message.author.display_name}. **(hugs)**")
            time.sleep(2)
            await message.channel.send(f"It's okay, {message.author.display_name}, it's okay.")
            time.sleep(4)
            await message.channel.send(f"Daddy's got you.")

    async def on_cloud_store_reset_filter(self, message):
        if (re.search('reset_cloud_store', message.content, re.IGNORECASE)):
            self.reaction_store.clear_cloud_store()
            await self.reaction_store.get_all_reactions(message)
    
    async def on_get_emoji_list_filter(self, message):
        if (re.search(r'get\s?(\w+)?\s?(\d+)?\s?reaction list \w+ \w+.?$', message.content, re.IGNORECASE)):
            name = message.content.split()[-1]
            try:
                amount = int(re.search(r'\d+', message.content).group())
            except:
                amount = -1
            response = self.reaction_store.get_reaction_list(name, amount=amount)
            await message.channel.send(response)
    
    async def on_get_emoji_stats_filter(self, message):
        if (re.search(r'get emoji stats for', message.content, re.IGNORECASE)):
            ev = EmojiValidator()
            emoji = message.content.split()[-1]
            if (re.search(r'<:(\w+):(\d+)>', emoji, re.IGNORECASE)):
                emoji_id = int(re.search(r'\d+', message.content).group())
            if (ev.char_is_emoji(emoji)):
                emoji_id = emoji
            response = self.reaction_store.get_emoji_stats(emoji_id)
            await message.channel.send(response)
        

    async def on_message(self, message):
        # if (IS_TEST and message.channel.name != 'bot-test'):
        #     print(f'Skipping {message.author.name}\'s message "{message.content}" from unwanted channel {message.channel.name}.')
        #     return
        if (message.author.id == self.user.id):
            print("JokeyBot shouldn't react to himself. Skipping message.")
            return

        requested = True if message.content.lower().startswith(("jb", "jokeybot")) else False

        await self.on_jokeybot_status_filter(message)
        if (int(os.environ['MAINTENANCE_MODE'])):
            return

        await self.on_actually_filter(message)
        await self.on_together_filter(message)
        await self.on_dad_filter(message)
        
        if (requested):
            await self.on_get_emoji_list_filter(message)
            await self.on_scoreboard_filter(message)
            await self.on_get_emoji_stats_filter(message)
            await self.on_edgar_fact_filter(message)
            await self.on_help_filter(message)
            await self.on_hug_filter(message)

        if (message.channel.name == 'bot-test'):
            await self.on_update_cloud_store_filter(message)
            await self.on_cloud_store_clear_filter(message)
            await self.on_cloud_store_reset_filter(message)
            