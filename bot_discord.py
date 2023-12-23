import discord
from discord.ext import commands
import logging
from pytube import YouTube
import random
from collections import deque

swear_words = ['Это была ошибка уровня "перепутать левую и правую руку", да?',
'В следующий раз можно попробовать не нажимать на кнопку "Выдать ошибку".',
'Неплохо для человека. Следующий раз проверь, не кот ты случайно.',
'Кто-то здесь решил добавить немного интриги в процесс, понимаю.',
'Даже компьютер воспринял это как вызов сложности. Поставлю галочку "Эпичный фейл".',
'Твоя ошибка была так неожиданна, что даже браузер задумался.',
'Думаю, это было секретное испытание на уровень терпимости к ошибкам.',
'Чтобы сделать ошибку, нужно много ума. Ты явно тут не разочаровал.',
'Эй, даже великие художники начинали с палитры из пятен.',
'В мире ошибок ты - настоящий путешественник.']

support_words = ['Ты на верном пути, продолжай!',
'Твой труд идет на пользу, не останавливайся.',
'Маленькая ошибка, большой опыт.',
'Ты делаешь отличную работу, верь в себя.',
'Каждая попытка приближает к успеху.',
'Не переживай, ошибки - это часть обучения.',
'Ты умеешь извлекать уроки из своих ошибок.',
'Твоя настойчивость всегда приводит к результатам.',
'Помни, что твой потенциал бесконечен.',
'С тобой все в порядке, просто продолжай двигаться вперед.']

# Конфигурация логирования
logging.basicConfig(level=logging.INFO)  # Уровень логирования: INFO

# Конфигурация
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

queues = {}

bot = commands.Bot(command_prefix='?', intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')

@bot.command()
async def play(ctx, *, query):
    try:
        video = YouTube(query)
        audio_stream = video.streams.filter(only_audio=True).first()
        try:
            voice_client = ctx.author.voice.channel
            await voice_client.connect()
        except Exception as e:
            print('Бот уже подключен.')

        if audio_stream:
            vc = discord.utils.get(bot.voice_clients, guild=ctx.guild)
            
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = deque()

            def after(error):
                coro = vc.disconnect()
                fut = asyncio.run_coroutine_threadsafe(coro, bot.loop)
                try:
                    fut.result()
                except:
                    pass

            if not vc.is_playing() and not queues[ctx.guild.id]:
                vc.play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable="./lib/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe", source=audio_stream.url), volume=0.5), after=after)
            else:
                queues[ctx.guild.id].append(audio_stream.url)
                await ctx.send("Трек добавлен в очередь.")
        else:
            await ctx.send(f"Не удалось получить URL аудио. \n {random.choice(support_words)}")
    except Exception as e:
        await ctx.send(f"Произошла ошибка: {e}. \n {random.choice(swear_words)}")

@bot.command()
async def stop(ctx):
    logging.info('Command received: !stop')
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()

@bot.command()
async def leave(ctx):
    logging.info('Command received: !leave')
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client:
        await voice_client.disconnect()

@bot.command()
async def skip(ctx):
    logging.info('Command received: !skip')
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client.is_playing():
        voice_client.stop()

@bot.command()
async def queue(ctx):
    if ctx.guild.id in queues and queues[ctx.guild.id]:
        queue_list = '\n'.join([f'{i + 1}. {queues[ctx.guild.id][i]}' for i in range(len(queues[ctx.guild.id]))])
        await ctx.send(f"Очередь треков:\n{queue_list}")
    else:
        await ctx.send("Очередь пуста.")

bot.run('MTEzNjMzMzM3ODE1NzgwNTcyOQ.GQilYh.ruansreu3DRbx5hYGqHqsmqlIJfKaBoST5hTH0')

