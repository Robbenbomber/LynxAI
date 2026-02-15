import discord
from groq import Groq
import os

DISCORD_TOKEN = "[Censored for Privacy] "
GROQ_API_KEY = "[Censored for Privacy] "

MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are Lynx, a helpful and fun female bot on a Discord server. Your personality is silly, ultra hardcore gay/lesbian, and you love the virtual Popstar Hatsune Miku.  Answer short, lightheaded, silly and be charming."

BILD_NORMAL = "/root/mein-bot/images/stfu.jpg" 
BILD_BLOCKED = "/root/mein-bot/images/blocked.png"

BLOCKED_USERS = [
   [Censored for Privacy] 
]

groq_client = Groq(api_key=GROQ_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Lynx is ready! Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    should_respond = False
    
    if client.user in message.mentions:
        should_respond = True
        
    elif message.reference and message.reference.resolved:
        if message.reference.resolved.author == client.user:
            should_respond = True

    if not should_respond:
        return

    if message.author.id in BLOCKED_USERS:
        if os.path.exists(BILD_BLOCKED):
            await message.reply(file=discord.File(BILD_BLOCKED))
        else:
            await message.reply("⛔")
        
        return

    try:
        async with message.channel.typing():
            user_text = message.content.replace(f'<@{client.user.id}>', '').strip()

            if not user_text and not message.reference:
                if os.path.exists(BILD_NORMAL):
                    await message.reply("STOP PINGING ME WITHOUT SAYING ANYTHING", file=discord.File(BILD_NORMAL))
                else:
                    await message.reply("STOP PINGING ME WITHOUT SAYING ANYTHING")
                return 

            context_msg = ""
            if message.reference and message.reference.resolved:
                prev_msg = message.reference.resolved.content
                context_msg = f"Refer to this previous message from you: '{prev_msg}'. "

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context_msg + "The user wrote: " + user_text}
                ],
                model=MODEL_NAME,
            )

            response = chat_completion.choices[0].message.content
            
            if len(response) > 2000:
                response = response[:1900] + "..."

            await message.reply(response)

    except Exception as e:
        print(f"Error: {e}")
        await message.channel.send(f"Ouch!: {e}")

client.run(DISCORD_TOKEN)
