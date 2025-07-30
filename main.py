from telegram.ext import Updater, MessageHandler, Filters
from telegram import MessageEntity

TOKEN = "8246326883:AAEQ-Mg2vuqYK0S5BYwD9_fm9dPdKbZAqPI"

IDS_TO_REMOVE = ['@khabar_gh', '@example_id', '@test_channel']

def remove_hyperlinks_and_ids(text, entities):
    result = text
    offset_correction = 0

    for entity in sorted(entities, key=lambda e: e.offset):
        start = entity.offset + offset_correction
        end = start + entity.length

        if entity.type == "text_link":
            visible_text = result[start:end]
            result = result[:start] + visible_text + result[end:]
        elif entity.type == "url":
            url_text = result[start:end]
            disabled_url = url_text.replace(".", "[dot]")
            result = result[:start] + disabled_url + result[end:]
            offset_correction += len(disabled_url) - len(url_text)

    for id_ in IDS_TO_REMOVE:
        result = result.replace(id_, "")

    return result.strip()

def handle_message(update, context):
    message = update.message
    if not message or not message.text:
        return

    text = message.text
    entities = message.entities if message.entities else []

    cleaned_text = remove_hyperlinks_and_ids(text, entities)

    if cleaned_text != text:
        try:
            context.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            context.bot.send_message(chat_id=message.chat.id, text=cleaned_text)

            warning = context.bot.send_message(
                chat_id=message.chat.id,
                text="❗ لطفاً از ارسال لینک یا آی‌دی خودداری کنید."
            )

            context.job_queue.run_once(
                lambda ctx: ctx.bot.delete_message(chat_id=warning.chat.id, message_id=warning.message_id),
                10
            )
        except Exception as e:
            print("خطا:", e)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
