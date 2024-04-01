import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
from polybot.img_proc import Img


class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
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
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')


class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        if msg["text"] != 'Please don\'t quote me':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])


class ImageProcessingBot(Bot):
    def handle_message(self, msg):
        try:
            logger.info(f'Incoming message: {msg}')

            if self.is_current_msg_photo(msg):
                img_path = self.download_user_photo(msg)
                caption = msg.get('caption', '')

                if caption == 'Blur':
                    # Process the image to apply blur effect
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.apply_blur()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                elif caption == 'Contour':
                    # Process the image to find contours
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.find_contours()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                elif caption == 'Rotate':
                    # Process the image to rotate
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.rotate()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                elif caption == 'Segment':
                    # Process the image to segment
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.segment()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                elif caption == 'Salt and pepper':
                    # Process the image to add salt and pepper noise
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.add_salt_and_pepper_noise()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                elif caption == 'Concat':
                    # Process the image to concatenate
                    img_processor = Img(img_path)
                    processed_img_path = img_processor.concatenate()

                    # Send the processed image to the user
                    self.send_photo(msg['chat']['id'], processed_img_path)

                else:
                    # Caption value not recognized
                    self.send_text(msg['chat']['id'], "Invalid caption. Please provide one of the following: ['Blur', 'Contour', 'Rotate', 'Segment', 'Salt and pepper', 'Concat']")

            else:
                # Message does not contain a photo
                self.send_text(msg['chat']['id'], "Please send a photo with a caption for processing.")

        except Exception as e:
            logger.error(f"Error processing image: {e}")
            self.send_text(msg['chat']['id'], "Something went wrong... please try again.")

