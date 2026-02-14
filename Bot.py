import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# --- Cấu hình logging ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- THAY TOKEN CỦA BẠN VÀO ĐÂY ---
TOKEN = "6556057870:AAFPx3CJpAcGt-MfKRoAo00SlAEQ26XSS-s"   # <--- Thay token mới vào đây

# --- Hàm format số (1.200.000 -> 1.2M) ---
def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

# --- Lấy dữ liệu từ TikTok bằng TikTokApi ---
def get_tiktok_stats(username):
    try:
        from TikTokApi import TikTokApi
    except ImportError:
        logger.error("Chưa cài TikTokApi. Chạy: pip install TikTokApi")
        return None

    try:
        with TikTokApi() as api:
            user = api.user(username)
            user_data = user.info()
            stats = user_data['stats']
            return {
                'followers': stats['followerCount'],
                'likes': stats['heartCount'],
                'videos': stats['videoCount']
            }
    except Exception as e:
        logger.error(f"Lỗi khi lấy dữ liệu TikTok: {e}")
        return None

# --- Lệnh /start ---
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Chào bạn! Tôi là bot kiểm tra tương tác TikTok.\n"
        "Dùng lệnh /check <tên_tài_khoản> để xem thông tin.\n"
        "Ví dụ: /check therock"
    )

# --- Lệnh /check ---
def check(update: Update, context: CallbackContext):
    if len(context.args) == 0:
        update.message.reply_text("⚠️ Vui lòng nhập tên tài khoản TikTok.\nVí dụ: /check therock")
        return

    username = context.args[0].strip()
    update.message.reply_text(f"🔍 Đang kiểm tra tài khoản @{username}...")

    stats = get_tiktok_stats(username)

    if stats is None:
        update.message.reply_text("❌ Không thể lấy dữ liệu. Tài khoản không tồn tại hoặc có lỗi xảy ra.")
        return

    followers = format_number(stats['followers'])
    likes = format_number(stats['likes'])
    videos = stats['videos']

    if videos > 0:
        avg_likes = stats['likes'] / videos
        engagement = format_number(avg_likes)
    else:
        engagement = "0"

    message = (
        f"📊 **Kết quả cho @{username}**\n"
        f"👥 **Người theo dõi:** {followers}\n"
        f"❤️ **Tổng lượt thích:** {likes}\n"
        f"🎬 **Số video:** {videos}\n"
        f"📈 **Trung bình likes/video:** {engagement}"
    )
    update.message.reply_text(message, parse_mode='Markdown')

# --- Hàm main chạy bot ---
def main():
    # Khởi tạo Updater với token mới
    updater = Updater(token=TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("check", check))

    updater.start_polling()
    logger.info("Bot đã khởi động. Nhấn Ctrl+C để dừng.")
    updater.idle()

if __name__ == '__main__':
    main()
