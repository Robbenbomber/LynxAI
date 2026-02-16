import discord
from groq import Groq
import os
import json

DISCORD_TOKEN = "Censored for Privacy"
GROQ_API_KEY = "Censored for Privacy"

MODEL_NAME = "llama-3.3-70b-versatile"
PFAD_RELATIONSHIPS = "/root/mein-bot/relationships.json"
PFAD_BILD_STFU = "/root/mein-bot/stfu.jpg"
PFAD_BILD_BLOCKED = "/root/mein-bot/blocked.jpg"

BLOCKED_USERS = [Censored for Privacy]

groq_client = Groq(api_key=GROQ_API_KEY)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

def lade_beziehungen():
    if not os.path.exists(PFAD_RELATIONSHIPS):
        return {}
    try:
        with open(PFAD_RELATIONSHIPS, "r") as f:
            return json.load(f)
    except:
        return {}

def speichere_beziehungen(daten):
    with open(PFAD_RELATIONSHIPS, "w") as f:
        json.dump(daten, f)

@client.event
async def on_ready():
    print(f'Lynx is ready!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.author.id in BLOCKED_USERS:
        if client.user in message.mentions or (message.reference and message.reference.resolved.author == client.user):
            if os.path.exists(PFAD_BILD_BLOCKED):
                await message.reply(file=discord.File(PFAD_BILD_BLOCKED))
            else:
                await message.reply("⛔ You have been blocked from LynxAI.")
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
            user_id = str(message.author.id)

            beziehungen = lade_beziehungen()
            score = beziehungen.get(user_id, 0)

            stimmung = "silly, happy, cute, chaotic "
            if score >= 5:
                stimmung = "Your best friend, very loving, use emojis"
            elif score <= -5:
                stimmung = (
                    "You completely despise this user. You are arrogant, toxic, and superior. "
                    "Your goal is to verbally destroy them with sarcasm and creative insults. "
                    "Don't just use swear words; attack their intelligence, their logic, and their existence. "
                    "Act like a disgusted queen looking down on a peasant. "
                    "Be savage, ruthless, and have absolutely NO respect. "
                    "Mock them for even trying to talk to you."
                )
            base_prompt = (
                f"You are Lynx. You are a lesbian AI assistant on a Discord server. You're a fan of Hatsune Miku. You are disorganized and therefore a bit chaotic when writing. You have a relationship to this user. "
                f"Your current relationship-score with them is: {score}. "
                f"Act accordingly: {stimmung}. "
                "IMPORTANT: Analyse the new message by the user. "
                "If they are nice/commendatory, write at the end of your message: [UP]"
                "If he is insulting/rude, write at the very end: [DOWN]"
                "Otherwise, don't write anything at the end."
            )

            if not user_text and not message.reference:
                if os.path.exists(PFAD_BILD_STFU):
                    await message.reply("STOP PINGING ME WITHOUT SAYING ANYTHING!!!", file=discord.File(PFAD_BILD_STFU))
                else:
                    await message.reply("STOP PINGING ME WITHOUT SAYING ANYTHING!!!")
                return

            context_msg = ""
            if message.reference and message.reference.resolved:
                prev_msg = message.reference.resolved.content
                context_msg = f"Previous Message: '{prev_msg}'. "

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": base_prompt},
                    {"role": "user", "content": context_msg + "User says: " + user_text}
                ],
                model=MODEL_NAME,
            )

            raw_response = chat_completion.choices[0].message.content

            new_score = score
            final_response = raw_response

            if "[UP]" in raw_response:
                new_score += 1
                final_response = raw_response.replace("[UP]", "").strip()
            elif "[DOWN]" in raw_response:
                new_score -= 1
                final_response = raw_response.replace("[DOWN]", "").strip()
            
            new_score = max(-20, min(20, new_score))

            if new_score != score:
                beziehungen[user_id] = new_score
                speichere_beziehungen(beziehungen)
                # Optional: Debug-Ausgabe in der Konsole
                print(f"Relationship with {message.author.name} changed: {score} -> {new_score}")

            if len(final_response) > 2000:
                final_response = final_response[:1900] + "..."

            await message.reply(final_response)

    except Exception as e:
        print(f"Error: {e}")
        await message.channel.send(f"Error: {e}")

client.run(DISCORD_TOKEN)
