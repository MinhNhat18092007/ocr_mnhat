import re
import requests
import base64
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
    'Connection': 'keep-alive',
    # Already added when you pass json=
    # 'Content-Type': 'application/json',
    'Origin': 'https://xcan.vercel.app',
    'Referer': 'https://xcan.vercel.app/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

params = {
    'apiKey': 'AIzaSyC0QRhATYcE5NMZHZIS0FNQm_09eCpNOnM',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gửi cho tôi một bức ảnh để thực hiện OCR.")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lấy bức ảnh từ tin nhắn
    photo = update.message.photo[-1]
    
    # Lấy file từ ảnh
    file = await photo.get_file()
    file_path = 'photo.jpg'
    
    # Tải xuống file
    await file.download_to_drive(file_path)

    # Đọc file ảnh và chuyển đổi thành chuỗi Base64
    with open('photo.jpg', 'rb') as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    # Tạo JSON data
    json_data = f"data:image/jpeg;base64,{base64_image}"
    response = requests.post(
        'https://xcan-server.azurewebsites.net/Main/ExtractTextFromImage',
        params=params,
        headers=headers,
        json=json_data,
    )

    print(response.text)

    # Sử dụng BeautifulSoup để loại bỏ các thẻ HTML
    soup = BeautifulSoup(response.text, "html.parser")
    clean_text = soup.get_text(separator="\n", strip=True)

    # Chuẩn hóa văn bản
    standardized_text = clean_text.replace("*", "").replace("#", "").strip()

    # Trả về kết quả OCR
    await update.message.reply_text(standardized_text)

if __name__ == '__main__':
    app = ApplicationBuilder().token('7840925461:AAHdg7QLo8qEE8V0f-smar2eNAKXfiXMRVA').build()
    
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    app.run_polling()
