from bson import ObjectId
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, CallbackQueryHandler, ConversationHandler

import text_config
from config import TOKEN
from database import *

# pip install python-telegram-bot

db = DB("Test")
db.add_collection(Appeal)
db.add_collection(Basket)
db.add_collection(Doctor)
db.add_collection(Service)
db.add_collection(Specialisation)
db.add_collection(Tablets)
db.add_collection(User)


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
    # TODO: add  validation
    context.user_data["full_name"] = update.message.text
    update.message.reply_text(text='Введите вашу электронную почту.')
    return 2


def registration_step_email(update, context):
    # TODO: add  validation
    context.user_data["email"] = update.message.text
    update.message.reply_text(text='Введите ваш возраст.')
    return 3


def registration_step_age(update, context):
    # TODO: add  validation

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
            elif button_data == "admission":
                show_admission(update, context)
            elif button_data == "initial_examination":
                choose_doctor(update, context, "Первичная консультация")
            elif button_data == "certain_service":
                certain_service(update, context)

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

    elif button_data.startswith("service_using"):
        _, service_id, doctor_id = button_data.split(":")
        buy_service(update, context, service_id, doctor_id)
        query.answer()
        return 4

    elif button_data.startswith("choose_doctor"):
        choose_doctor(update, context, button_data.split(":")[1])

    elif button_data == "ask_appeal_reject":
        context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                              message_id=update["callback_query"]["message"]["message_id"])
        context.bot.send_message(chat_id=query.message.chat_id, text="Заявка отменена")
    elif button_data == "ask_appeal_accept":
        appeal_accept(update, context)

    elif button_data == "get_appeals":
        res = [appeal for appeal in db.Appeal if appeal.user_id == user_id]
        for appeal in res:
            msg = f"Услуга: {db.Service.find(_id=ObjectId(appeal.service_id)).name}\n" \
                  f"Врач: {str(db.Doctor.find(_id=ObjectId(appeal.doctor_id)))}\n" \
                  f"Время: {appeal.time}\n" \
                  f"Дополнительная информация:\n{appeal.description}"

            buttons = [[InlineKeyboardButton("Отменить запись", callback_data=f"cancel_appeal:{appeal.id()}")]]
            markup = InlineKeyboardMarkup(buttons)

            context.bot.send_message(chat_id=query.message.chat_id,
                                     text=msg, reply_markup=markup)

    elif button_data.startswith("cancel_appeal"):
        appeal_id = ObjectId(button_data.split(":")[1])
        db.Appeal.remove(_id=appeal_id)
        context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                              message_id=update["callback_query"]["message"]["message_id"])
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=update["callback_query"]["message"]["message_id"],
                                      text="Запись отменена")

    elif button_data == "buy_basket":
        basket = db.Basket.find(user_id=user_id)
        basket.items = []
        db.Basket.commit()

        msg = query.message.text.split("Корзина")[0] + "Корзина пуста"

        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=msg,
                                      reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                          text="Посмотреть записи к врачам", callback_data="get_appeals")]]))

    elif button_data == "change_busket":
        tablets = dict()
        for tablet in db.Basket.find(user_id=user_id).items:
            if tablet in tablets:
                tablets[tablet] += 1
            else:
                tablets[tablet] = 1

        for tablet in tablets:
            buttons = [[InlineKeyboardButton("➕", callback_data=f"increment_tablet:{tablet}:{tablets[tablet]}"),
                        InlineKeyboardButton("➖", callback_data=f"decrement_tablet:{tablet}:{tablets[tablet]}")]]
            markup = InlineKeyboardMarkup(buttons)

            context.bot.send_message(chat_id=query.message.chat_id,
                                     text=f"{db.Tablets.find(_id=ObjectId(tablet)).name}: {tablets[tablet]}шт.",
                                     reply_markup=markup)
    elif button_data.startswith("increment_tablet"):
        num = int(button_data.split(":")[2])
        tablet_id = button_data.split(":")[1]
        basket = db.Basket.find(user_id=user_id)
        basket.items = basket.items + [ObjectId(tablet_id)]

        buttons = [[InlineKeyboardButton("➕", callback_data=f"increment_tablet:{tablet_id}:{num + 1}"),
                    InlineKeyboardButton("➖", callback_data=f"decrement_tablet:{tablet_id}:{num + 1}")]]
        markup = InlineKeyboardMarkup(buttons)

        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text=f"{db.Tablets.find(_id=ObjectId(tablet_id)).name}: {num + 1}шт.",
                                      reply_markup=markup)
        db.Basket.commit()

    elif button_data.startswith("decrement_tablet"):
        num = int(button_data.split(":")[2])
        tablet_id = button_data.split(":")[1]
        basket = db.Basket.find(user_id=user_id)

        if num > 0:
            ind = basket.items.index(ObjectId(tablet_id))
            basket.items = basket.items[:ind] + basket.items[ind + 1:]

            buttons = [[InlineKeyboardButton("➕", callback_data=f"increment_tablet:{tablet_id}:{num - 1}"),
                        InlineKeyboardButton("➖", callback_data=f"decrement_tablet:{tablet_id}:{num - 1}")]]
            markup = InlineKeyboardMarkup(buttons)

            context.bot.edit_message_text(chat_id=query.message.chat_id,
                                          message_id=query.message.message_id,
                                          text=f"{db.Tablets.find(_id=ObjectId(tablet_id)).name}: {num - 1}шт.",
                                          reply_markup=markup)
            db.Basket.commit()
    query.answer()


def show_doctors(update, context):
    query = update.callback_query

    for doctor in db.Doctor:
        msg = str(doctor) + "\n" + f"Специализация: {db.Specialisation.find(_id=doctor.specialisation).name}"
        context.bot.send_message(chat_id=query.message.chat_id, text=msg)
    query.answer()


def show_admission(update, context):
    query = update.callback_query

    context.bot.send_message(chat_id=query.message.chat_id, text=text_config.admission_message)
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


def choose_doctor(update, context, service):
    query = update.callback_query
    service_id = db.Service.find(name=service).id()
    specialisations = [spec.id() for spec in db.Specialisation if service_id in spec.services]
    doctors = [doctor for doctor in db.Doctor if doctor.specialisation in specialisations]

    for doctor in doctors:
        buttons = [
            [InlineKeyboardButton(text="Записаться", callback_data=f"service_using:{service_id}:{doctor.id()}")]]
        markup = InlineKeyboardMarkup(buttons)

        msg = f"Врач: {str(doctor)}\nСпециализация: {db.Specialisation.find(_id=doctor.specialisation).name}\nУслуга: {service}"

        context.bot.send_message(chat_id=query.message.chat_id, text=msg, reply_markup=markup)


def certain_service(update, context):
    query = update.callback_query
    buttons = []
    for service in db.Service:
        buttons.append([InlineKeyboardButton(text=service.name, callback_data=f"choose_doctor:{service.name}")])

    markup = InlineKeyboardMarkup(buttons)
    context.bot.send_message(chat_id=query.message.chat_id, text="Выберите интересующую вас услугу",
                             reply_markup=markup)


def buy_service(update, context, service_id, doctor_id):
    query = update.callback_query

    msg = f"Вы выбрали запись к специалисту: {str(db.Doctor.find(_id=ObjectId(doctor_id)))}\nУслуга: {db.Service.find(_id=ObjectId(service_id)).name}"

    context.user_data["service_id"] = service_id
    context.user_data["doctor_id"] = doctor_id

    context.user_data["doctor"] = str(db.Doctor.find(_id=ObjectId(doctor_id)))
    context.user_data["service"] = db.Service.find(_id=ObjectId(service_id)).name

    context.bot.send_message(chat_id=query.message.chat_id, text=msg)
    context.bot.send_message(chat_id=query.message.chat_id,
                             text="Для записи, пожалуйста, уточните дату и время, в которое вам было бы удобно посетить врача в формате dd.mm.yyyy hh:mm")


def get_date(update, context):
    # TODO: validation

    update.message.reply_text(f"Выбрана дата: {update.message.text}")
    context.user_data["date_of_appeal"] = update.message.text

    update.message.reply_text(f"Пожалуйста, уточните детали перед записью")
    return 5


def get_description(update, context):
    # TODO: add validation

    msg = f"Текущая анкета к специалисту: {context.user_data['doctor']}.\n" \
          f"Услуга: {context.user_data['service']}\n" \
          f"Дата и время: {context.user_data['date_of_appeal']}\n" \
          f"Дополнительная информация:\n{update.message.text}"

    context.user_data["description"] = update.message.text

    buttons = [[InlineKeyboardButton("Всё верно", callback_data="ask_appeal_accept"),
                InlineKeyboardButton("Отмена", callback_data="ask_appeal_reject")]]
    markup = InlineKeyboardMarkup(buttons)
    update.message.reply_text(msg, reply_markup=markup)
    return ConversationHandler.END


def appeal_accept(update, context):
    query = update.callback_query

    user_id = update["callback_query"]["message"]["chat"]["id"]
    doctor_id = context.user_data["doctor_id"]
    service_id = context.user_data["service_id"]
    time = context.user_data["date_of_appeal"]
    description = context.user_data["description"]
    context.bot.edit_message_reply_markup(chat_id=query.message.chat_id,
                                          message_id=query.message.message_id)
    db.Appeal.add(user_id=user_id, doctor_id=doctor_id, service_id=service_id, time=time, description=description)
    context.bot.send_message(chat_id=query.message.chat_id, text="Заявка создана.")


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

    buttons = [
        [InlineKeyboardButton(text="Посмотреть записи к врачам", callback_data="get_appeals")],
        [InlineKeyboardButton(text="Оплатить корзину", callback_data="buy_basket")],
        [InlineKeyboardButton(text="Редактировать корзину", callback_data="change_busket")]
    ]
    markup = InlineKeyboardMarkup(buttons)

    update.message.reply_text(user_info_message + "\n" + basket_info_message, reply_markup=markup)


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
            3: [MessageHandler(Filters.text, registration_step_age)],
            4: [MessageHandler(Filters.text, get_date)],
            5: [MessageHandler(Filters.text, get_description)],
        },
        fallbacks=[]
    ))

    dispatcher.add_handler(menu_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(buttons_handler)

    updater.start_polling()
