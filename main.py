from bson import ObjectId
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler, ConversationHandler

import text_config
from config import TOKEN
from database import *

# pip install python-telegram-bot

db = DB("Test")
db.add_collection(User)
db.add_collection(Basket)
db.add_collection(Tablets)
db.add_collection(Doctor)


def start(update, context):
    services = text_config.services
    buttons = [
        [InlineKeyboardButton(services["initial_examination"], callback_data="initial_examination"),
         InlineKeyboardButton(services["repeat_examination"], callback_data="repeat_examination")],
        [InlineKeyboardButton(services["admission"], callback_data="admission")],
        [InlineKeyboardButton(services["certain_service"], callback_data="certain_service")],
        [InlineKeyboardButton(services["doctors"], callback_data="doctors"),
         InlineKeyboardButton(services["purchase"], callback_data="purchase")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    message = "Добро пожаловать! Это бот стоматологической клиники.\nМы предлагаем следующие услуги:\n"
    update.message.reply_text(text=message, reply_markup=markup)
    if db.User.find(_id=update.message.chat.id) is None:
        update.message.reply_text("Вы ещё не прошли регистрацию\nВведите ваше ФИО через пробел.")
        return 1
    return ConversationHandler.END


def help(update, context):
    update.message.reply_text(text_config.help_message)


def registration_step_name(update, context):
    context.user_data["full_name"] = update.message.text
    update.message.reply_text(text='Введите вашу электронную почту.')
    return 2


def registration_step_email(update, context):
    context.user_data["email"] = update.message.text
    update.message.reply_text(text='Введите ваш возраст.')
    return 3


def registration_step_age(update, context):
    buttons = [[InlineKeyboardButton("Да", callback_data="registration_accept"),
                InlineKeyboardButton("Нет", callback_data="registration_reject")]]
    markup = InlineKeyboardMarkup(buttons)

    context.user_data["age"] = update.message.text

    update.message.reply_text(
        f"Ваши данные: \n"
        f"\tФИО: {context.user_data['full_name']}\n"
        f"\tПочта: {context.user_data['email']}\n"
        f"\tВозраст: {context.user_data['age']}",
        reply_markup=markup)

    return ConversationHandler.END


def handle_button(update, context):
    query = update.callback_query
    button_data: str = query.data
    user_id = update["callback_query"]["message"]["chat"]["id"]

    if button_data in text_config.services:
        if db.User.find(_id=user_id):
            context.bot.send_message(chat_id=query.message.chat_id,
                                     text=f"Выбрана опция: {text_config.services[button_data]}")
            if button_data == "doctors":
                show_doctors(update, context)
            elif button_data == "purchase":
                medicaments_purchase(update, context)
        else:
            context.bot.send_message(chat_id=query.message.chat_id,
                                     text="Перед пользованием услуг требуется регистрация")
            query.answer()
            return 1

    elif button_data == "registration_accept":
        db.Basket.add(user_id=user_id, items=[])
        basket = db.Basket.find(user_id=user_id)
        name, surname, lastname = context.user_data["full_name"].split()
        age = context.user_data["age"]
        email = context.user_data["email"]

        db.User.add(_id=user_id, name=name, surname=surname, lastname=lastname, age=age, email=email,
                    busket_id=str(basket.id()))

        context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                              message_id=update["callback_query"]["message"]["message_id"])
        context.bot.send_message(chat_id=query.message.chat_id, text="Регистрация прошла успешно")

    elif button_data == "registration_reject":
        context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                              message_id=update["callback_query"]["message"]["message_id"])
        context.bot.send_message(chat_id=query.message.chat_id, text="Введите ваше ФИО.")
        query.answer()
        return 1

    elif button_data.startswith("buy_medicaments"):
        tablet_id = button_data.split(":")[1].strip()
        tablet = db.Tablets.find(_id=ObjectId(tablet_id))
        basket = db.Basket.find(user_id=user_id)
        basket.items = basket.items + [tablet.id()]
        db.Basket.commit()

        message = f"Товар: {tablet.name} добавлен в корзину"
        context.bot.send_message(chat_id=query.message.chat_id, text=message)
    query.answer()


def show_doctors(update, context):
    query = update.callback_query

    for doctor in db.Doctor:
        context.bot.send_message(chat_id=query.message.chat_id, text=str(doctor))
    query.answer()


def medicaments_purchase(update, context):
    query = update.callback_query

    for medicament in db.Tablets:
        buttons = [
            [InlineKeyboardButton(text="Добавить в корзину", callback_data=f"buy_medicaments:{medicament.id()}")]
        ]

        markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(chat_id=query.message.chat_id, text=str(medicament), reply_markup=markup)
    query.answer()


def menu(update, context):
    user_id = update.message.chat.id
    if db.User.find(_id=user_id) is None:
        update.message.reply_text("Для пользования ботом, пожалуйста, пройдите регистрацию.")
        update.message.reply_text("Введите ваше ФИО")
        return 1

    user: User = db.User.find(_id=user_id)
    user_info_message = f"Личная информация:\n" \
                        f"  ФИО: {user.surname} {user.name} {user.lastname}\n" \
                        f"  Возраст: {user.age}\n" \
                        f"  Контактные данные: {user.email}"

    basket = dict()
    for item in db.Basket.find(user_id=user_id).items:
        if item in basket:
            basket[item] += 1
        else:
            basket[item] = 1

    basket_info_message = "\nКорзина:\n"
    whole_cost = 0
    for item in basket:
        tablet = db.Tablets.find(_id=ObjectId(item))
        cost = basket[item] * tablet.price
        basket_info_message += "  " + tablet.name + f" x{basket[item]} | {cost}P.\n"
        whole_cost += cost
    basket_info_message += "-" * 20 + f"\nОбщая стоимость: {whole_cost}"

    update.message.reply_text(user_info_message + "\n" + basket_info_message)


if __name__ == '__main__':
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    menu_handler = CommandHandler('menu', menu)
    buttons_handler = CallbackQueryHandler(handle_button)

    dispatcher.add_handler(ConversationHandler(
        entry_points=[start_handler, buttons_handler],
        states={
            1: [MessageHandler(Filters.text, registration_step_name)],
            2: [MessageHandler(Filters.text, registration_step_email)],
            3: [MessageHandler(Filters.text, registration_step_age)]
        },
        fallbacks=[]
    ))
    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(buttons_handler)

    updater.start_polling()
