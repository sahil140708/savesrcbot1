import yt_dlp
import os
import tempfile
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from devgagan import app
from devgagan.core.func import fast_upload

# Simple /yt command to download and send video
@app.on_message(filters.command("yt"))
async def yt_download(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Please provide a YouTube link.
Usage: /yt <link>")

    url = message.command[1]
    msg = await message.reply("🔄 **Downloading video...**")

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "video.%(ext)s")

    ydl_opts = {
        "format": "best",
        "outtmpl": output_path,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_file = ydl.prepare_filename(info)

        await msg.edit("📤 **Uploading to Telegram...**")
        await client.send_video(
            chat_id=message.chat.id,
            video=video_file,
            caption=f"**{info.get('title', 'YouTube Video')}**"
        )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")

    finally:
        try:
            if os.path.exists(video_file):
                os.remove(video_file)
            os.rmdir(temp_dir)
        except:
            pass


# Simple /yta command to download and send audio
@app.on_message(filters.command("yta"))
async def yta_download(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Please provide a YouTube link.
Usage: /yta <link>")

    url = message.command[1]
    msg = await message.reply("🔄 **Extracting audio...**")

    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            audio_file = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")

        await msg.edit("📤 **Uploading audio...**")
        await client.send_audio(
            chat_id=message.chat.id,
            audio=audio_file,
            caption=f"**{info.get('title', 'YouTube Audio')}**"
        )
        await msg.delete()

    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")

    finally:
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            os.rmdir(temp_dir)
        except:
            pass

@app.on_message(filters.command("ytbatch"))
async def yt_batch_download(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Please provide multiple YouTube links.
Usage: /ytbatch <link1> <link2> ...")

    urls = message.text.split()[1:]
    if len(urls) > 10:
        return await message.reply("⚠️ You can only download up to 10 videos at once.")

    msg = await message.reply(f"🔄 **Processing {len(urls)} videos...**")
    temp_dir = tempfile.mkdtemp()
    results = []

    for index, url in enumerate(urls):
        await msg.edit(f"📥 Downloading video {index+1}/{len(urls)}...")
        output_path = os.path.join(temp_dir, f"video{index}.%(ext)s")

        ydl_opts = {
            "format": "best",
            "outtmpl": output_path,
            "quiet": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_file = ydl.prepare_filename(info)
                results.append((video_file, info.get("title", "Video")))

        except Exception as e:
            await client.send_message(message.chat.id, f"❌ Failed to download `{url}`: `{e}`")

    await msg.edit("📤 **Uploading videos...**")

    for video_path, title in results:
        try:
            await client.send_video(
                chat_id=message.chat.id,
                video=video_path,
                caption=f"**{title}**"
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"❌ Failed to upload `{title}`: `{e}`")
        finally:
            if os.path.exists(video_path):
                os.remove(video_path)

    await msg.delete()
    try:
        os.rmdir(temp_dir)
    except:
        pass