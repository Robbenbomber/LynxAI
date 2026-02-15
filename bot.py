import discord
from groq import Groq
import os

DISCORD_TOKEN = "discord_key"
GROQ_API_KEY = "groq_key"

MODEL_NAME = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = "You are Lynx, a helpful and fun female bot on a Discord server. Anwser short, cutely and be charming."

BILD_PFAD = "/root/mein-bot/stfu.jpg"

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

    try:
        async with message.channel.typing():
            user_text = message.content.replace(f'<@{client.user.id}>', '').strip()

            if not user_text and not message.reference:
                if os.path.exists(BILD_PFAD):
                    await message.reply("STOP PINGING ME WITHOUT SAYING ANYTHING", file=discord.File(BILD_PFAD))
                else:
                    await message.reply(f"STOP PINGING ME WITHOUT SAYING ANYTHING (Image not found at: {BILD_PFAD})")
                
                return

            context_msg = ""
            if message.reference and message.reference.resolved:
                prev_msg = message.reference.resolved.content
                context_msg = f"Refer to this previous message by you: '{prev_msg}'. "

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": context_msg + "The User wrote: " + user_text}
                ],
                model=MODEL_NAME,
            )

            response = chat_completion.choices[0].message.content
            
            if len(response) > 2000:
                response = response[:1900] + "..."

            await message.reply(response)

    except Exception as e:
        print(f"Critical Error: {e}")
        await message.channel.send(f"Ouch! Fehler: {e}")

client.run(DISCORD_TOKEN)
