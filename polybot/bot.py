import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img

class Bot:
    def __init__(self, token, telegram_chat_url):
        self.telegram_bot_client = telebot.TeleBot(token)
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)
        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')

class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])

class ImageProcessingBot(Bot):

    def greet_user(self, chat_id):
        self.send_text(chat_id, "Hello! I am your image processing bot. Send me a photo with one of the following captions to apply a filter: ['Blur', 'Contour', 'Segment'].")

    def handle_message(self, msg):
        try:
            logger.info(f'Incoming message: {msg}')

            if 'text' in msg and msg['text'] == '/start':
                self.greet_user(msg['chat']['id'])
                return

            if self.is_current_msg_photo(msg):
                img_path = self.download_user_photo(msg)
                caption = msg.get('caption', '')

                if not caption:
                    self.send_text(msg['chat']['id'], "Please provide a caption with the photo for processing. Possible captions are: ['Blur', 'Contour', 'Segment'].")
                    return

                img_processor = Img(img_path)

                if caption == 'Blur':
                    logger.info(f'Applying blur filter to {img_path}')
                    processed_img_path = img_processor.apply_blur()

                elif caption == 'Contour':
                    logger.info(f'Applying contour filter to {img_path}')
                    processed_img_path = img_processor.find_contours()

                elif caption == 'Rotate':
                    logger.info(f'Applying rotate filter to {img_path}')
                    processed_img_path = img_processor.rotate()

                elif caption == 'Segment':
                    logger.info(f'Applying segment filter to {img_path}')
                    processed_img_path = img_processor.segment()

                elif caption == 'Salt and pepper':
                    logger.info(f'Applying salt and pepper filter to {img_path}')
                    processed_img_path = img_processor.add_salt_and_pepper_noise()

                elif caption == 'Concat':
                    other_img_path = self.download_user_photo(msg)  # Assuming you handle the second image appropriately
                    logger.info(f'Applying concat filter to {img_path} and {other_img_path}')
                    processed_img_path = img_processor.concatenate(other_img_path)

                else:
                    self.send_text(msg['chat']['id'], "Invalid caption. Please provide one of the following: ['Blur', 'Contour', 'Segment']")
                    return

                self.send_photo(msg['chat']['id'], processed_img_path)
                logger.info(f'Successfully processed image: {processed_img_path}')

            else:
                self.send_text(msg['chat']['id'], "Please send a photo with a caption for processing.")

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(msg['chat']['id'], "Something went wrong... please try again.")
