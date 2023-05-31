from telegram.ext import MessageHandler, Filters, Updater, CommandHandler

from config import TOKEN


def echo(update, context):
    text = update.message.text
    if text in ["привет", "Привет", "привет!", "Привет!"]:
        update.message.reply_text("Привет!")
    else:
        update.message.reply_text(update.message.text)


def start(update, context):
    update.message.reply_text("Добро пожаловать! Это бот стоматологической клиники.\nМы предлагаем следующие услуги:\n")


def help_func(update, context):
    update.message.reply_text("Для начала введите /start")


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_func))
    dispatcher.add_handler(MessageHandler(Filters.text, echo))
    updater.start_polling()
