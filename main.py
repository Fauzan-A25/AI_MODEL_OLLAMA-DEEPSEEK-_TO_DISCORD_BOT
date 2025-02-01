import os
import discord
import re
from discord.ext import commands
from dotenv import load_dotenv
from ollama import chat
from ollama import ChatResponse

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready as {bot.user.name}")

@bot.command(name="hello")
async def hello(ctx):
    await ctx.send("Hello, I'm a bot")

import asyncio

@bot.command(name="tanya")
async def tanya(ctx, *, message):
    print(message)
    print("=========================")
    
    # Jalankan fungsi chat di thread terpisah untuk menghindari pemblokiran event loop
    response: ChatResponse = await asyncio.to_thread(chat, model='deepseek-r1:1.5b', messages=[
        {
            'role': 'user',
            'content': message,
        },
    ])
    
    # Filter konten dalam <think>
    cleaned_content = re.sub(r'<think>.*?</think>', '', response['message']['content'], flags=re.DOTALL).strip()
    
    # Cek apakah respons melebihi 1000 kata
    if len(cleaned_content) > 4000:
        # Split menjadi chunk 1000 kata
        words = cleaned_content.split()
        chunks = [' '.join(words[i:i+1000]) for i in range(0, len(words), 1000)]
        
        # Kirim per bagian, pastikan tidak melebihi 4000 karakter
        for chunk in chunks:
            if len(chunk) > 4000:
                # Jika chunk lebih dari 4000 karakter, bagi lagi
                for i in range(0, len(chunk), 4000):
                    await ctx.send(chunk[i:i+4000])
            else:
                await ctx.send(chunk)
    else:
        await ctx.send(cleaned_content)

bot.run(os.getenv("DISCORD_TOKEN"))