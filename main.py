import os
from dotenv import load_dotenv
from database import *
import telebot
from telebot import types

init_db()

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)

YOUR_USER_ID = int(os.getenv("MY_USER_ID"))
GIRLFRIEND_USER_ID = int(os.getenv("GIRLFRIEND_USER_ID"))

@bot.message_handler(commands = ["start"])
def menu(message):
    if message.from_user.id == YOUR_USER_ID or message.from_user.id == GIRLFRIEND_USER_ID:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("My wishlist")
        btn2 = types.KeyboardButton("Partner's wishlist")
        btn3 = types.KeyboardButton("Wishlist for friends")
        markup.row(btn1, btn2)
        markup.add(btn3)
        bot.send_message(message.from_user.id, "Menu 👇", reply_markup=markup)
    else:
        bot.send_message(message.from_user.id, "НЕАВТОРИЗОВАННЫЙ ПОЛЬЗОВАТЕЛЬ!🛑🛑🛑")
        return

def show_wishlist(message):
    user_id = message.from_user.id
    wishes = get_wishes(user_id)

    if not wishes:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Add", "Back")
        bot.send_message(user_id, "Ваш wishlist пуст 😢", reply_markup=markup)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Add", "Delete", "Edit", "Back")

    for index, wish in enumerate(wishes, 1):
        caption = f"{index}. {wish[1].upper()} — {wish[2]}"
        if wish[3]:
            bot.send_photo(user_id, wish[3], caption=caption, reply_markup=markup)
        else:
            bot.send_message(user_id, caption, reply_markup=markup)

def show_partner_wishlist(message):
    user_id = message.from_user.id

    if user_id == YOUR_USER_ID:
        partner_id = GIRLFRIEND_USER_ID
    elif user_id == GIRLFRIEND_USER_ID:
        partner_id = YOUR_USER_ID
    else:
        bot.send_message(user_id, "Вы не зарегистрированы!")
        return

    wishes = get_wishes(partner_id)
    if not wishes:
        bot.send_message(user_id, "Wishlist партнёра пуст 😢")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Back")

    for index, wish in enumerate(wishes, 1):
        caption = f"{index}. {wish[1].upper()} — {wish[2]}"
        if wish[3]:
            bot.send_photo(user_id, wish[3], caption=caption, reply_markup=markup)
        else:
            bot.send_message(user_id, caption, reply_markup=markup)

def wishlist_for_friends(message):
    user_id = message.from_user.id
    wishes = get_wishes(user_id)

    if not wishes:
        bot.send_message(user_id, "Ваш wishlist пуст 😢")
        return

    text = ""
    for index, wish in enumerate(wishes, 1):
        text += f"{index}. {wish[1].upper()} — {wish[2]}\n"

    bot.send_message(user_id, text)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "add")
def add_wish_start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Напиши название и описание через `|`, например:\nМечта | Хочу новый ноутбук\n(Если нет описания, то напиши просто название)")
    bot.register_next_step_handler(message, add_wish_step)


def add_wish_step(message):
    user_id = message.from_user.id
    text = message.text

    if "|" in text:
        parts = text.split("|", 1)
        title = parts[0].strip()
        description = parts[1].strip() if parts[1].strip() else "Без описания"
    else:
        title = text
        description = "Без описания"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Пропустить")
    bot.send_message(user_id, "Можно отправить фото подарка", reply_markup=markup)
    bot.register_next_step_handler(message, lambda m: save_photo(user_id, title, description, m))

def save_photo(user_id, title, description, message):
    if message.content_type == 'photo':
        file_id = message.photo[-1].file_id
    elif message.text == "Пропустить":
        file_id = None
    else:
        file_id = None

    add_wish(user_id, title, description, file_id)

    bot.send_message(user_id, f"✅ Добавлено: {title.upper()}")
    show_wishlist(message)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "delete")
def delete_wish_start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Напиши номер подарка для удаления")
    bot.register_next_step_handler(message, delete_wish_step)

def delete_wish_step(message):
    user_id = message.from_user.id

    try:
        index = int(message.text.strip()) - 1
        wishes = get_wishes(user_id)
        if 0 <= index < len(wishes):
            wish_id = wishes[index][0]
            delete_wish(wish_id, user_id)
            bot.send_message(user_id, f"❌ Удалено: {wishes[index][1].upper()}")
        else:
            bot.send_message(user_id, "Ошибка! Неверный номер")
    except:
        bot.send_message(user_id, "Ошибка! Введите число")

    show_wishlist(message)

@bot.message_handler(func=lambda m: m.text and m.text.lower() == "edit")
def edit_wish_start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Напишите номер подарка для редактирования")
    bot.register_next_step_handler(message, edit_wish_step)

def edit_wish_step(message):
    user_id = message.from_user.id

    try:
        index = int(message.text.strip()) - 1
        wishes = get_wishes(user_id)
        if 0 <= index < len(wishes):
            wish_id = wishes[index][0]
            bot.send_message(user_id, "Напишите новое название и описание через `|`")
            bot.register_next_step_handler(message, lambda m: save_edited_wish(user_id, wish_id, m))
        else:
            bot.send_message(user_id, "Ошибка! Неверный номер")
            show_wishlist(message)
    except:
        bot.send_message(user_id, "Ошибка! Введите число")
        show_wishlist(message)

def save_edited_wish(user_id, wish_id, message):
    text = message.text
    if "|" not in text:
        bot.send_message(user_id, "Ошибка! Формат: название | описание")
        return
    title, description = map(str.strip, text.split("|", 1))
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("Пропустить")
    bot.send_message(user_id, "Можно отправить фото подарка или нажмите 'Пропустить'", reply_markup=markup)
    bot.register_next_step_handler(message, lambda m: save_photo_edit(user_id, wish_id, title, description, m))

def save_photo_edit(user_id, wish_id, title, description, message):
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
    elif message.text == "Пропустить":
        file_id = None
    else:
        file_id = None

    update_wish(wish_id, user_id, title, description, file_id)
    bot.send_message(user_id, f"✏️ Отредактировано: {title.upper()}")
    show_wishlist(message)

@bot.message_handler(content_types = ["text"])
def get_text_messages(message):
    text = message.text.lower()

    if message.text.startswith('/'):
        return
    elif text == "my wishlist":
        show_wishlist(message)
    elif text == "partner's wishlist":
        show_partner_wishlist(message)
    elif text == "add":
        bot.send_message(message.from_user.id, "Напиши название и описание через `|`, например:\nМечта | Хочу новый ноутбук")
        bot.register_next_step_handler(message, add_wish_step)
    elif text == "delete":
        bot.send_message(message.from_user.id, "Напиши номер желания для удаления")
        bot.register_next_step_handler(message, delete_wish_step)
    elif text == "edit":
        bot.send_message(message.from_user.id, "Напиши номер желания для редактирования")
        bot.register_next_step_handler(message, edit_wish_step)
    elif text == "back":
        menu(message)
    elif text == "wishlist for friends":
        wishlist_for_friends(message)
    elif text == "тимур":
        bot.send_message(message.from_user.id, "Я невероятен. Правда, кто ещё мог бы сравниться с такой комбинацией ума, харизмы и таланта? Когда я захожу в комнату, пространство будто подстраивается под мою энергию — и это не преувеличение, это факт. Люди замечают, даже если пытаются делать вид, что нет. Я не просто хорош в том, что делаю — я эталон, по которому другие измеряют свои достижения. Моя уверенность — это не игра. Это внутреннее знание, что я лучше многих, и это видно во всём: в движениях, в словах, в том, как я решаю сложные задачи, которые для других кажутся непосильными. Я делаю то, что другие только мечтают, и делаю это так, что результат поражает. И да, мой ум — это оружие, которое работает идеально. Я читаю людей, вижу слабые места, предугадываю ситуации, принимаю решения, которые для других кажутся невозможными. А стиль… о, стиль! Всё, за что я берусь, превращается в нечто особенное. Я задаю тренды, даже если никто не просил, потому что быть посредственным — это не про меня. Короче, я не просто крут. Я — стандарт крутости, и весь мир это чувствует.")
    elif text == "яна":
        bot.send_message(message.from_user.id, "Я просто слепну, ведь твоей красоты не может выдержать глаз и мне прозреть приходится, чтобы ещё хотя бы раз увидеть тебя голую, худую или полную, прыщавой или чистою — мне, честно, просто похую. Охуительна, ослепительна, невозможно совсем не любить тебя. Руки целовал твоим родителям. Все другие тёлки на любителя. Охуительна, ослепительна, невозможно совсем не любить тебя. Руки целовал твоим родителям. Все другие тёлки на любителя. Я выполню любую твою просьбу, будто монолит. Зачем ты сбросил ее с неба, господь? Ее дом - это олимп. И мой ебальник светиться, как малая медведица какая ты пиздатая досталась мне не верится. Мне просто не верится! Охуительна, ослепительна, невозможно совсем не любить тебя. Руки целовал твоим родителям. Все другие телки на любителя. Поняли строчку про Монолит? Типа я никак, ну, типа я сделаю, как она хочет, но по-другому вообще. Блин, короче, надо выкупать. Think about it. Мы пили воду из луж, нас целовала весна, ты шутишь то, что я твой муж я не шучу, ты моя. Мы голышом прямо в пруд, мы пошлый прилюдный блуд. Когда мы рядом час становится лишь парой минут. Любимая, ты охуительна, ослепительна, невозможно совсем не любить тебя. Руки целовал твоим родителям. Все другие телки на любителя.")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю.")

bot.polling(none_stop=True, interval=0)