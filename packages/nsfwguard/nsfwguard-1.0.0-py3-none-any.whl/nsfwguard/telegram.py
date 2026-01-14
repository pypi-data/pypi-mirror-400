from pyrogram import Client, filters
from nsfwguard.image import scan_image

@Client.on_message(filters.photo | filters.video)
async def nsfw_guard(client, message):
    file = await message.download()
    result = scan_image(file)

    if result["nsfw"]:
        await message.delete()
        await message.reply("🚫 NSFW content blocked.")
