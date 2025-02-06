import telebot
from telebot.types import CallbackQuery, Message
from random import shuffle
from config import APItoken
from users import *
from keyboards import *
from users import UserCallbackData


bot = telebot.TeleBot(APItoken)

@bot.message_handler(commands=['start', 'menu'])
def start(message: Message):
    users = read_users()
    user_id = message.from_user.id

    if user_id not in users.user_id.unique():
        add_user(user_id)

    bot.send_message(message.chat.id,
                     'Это главное меню. Дальнейшая навигация производиться с помощью кнопок. Если вы захотите вызвать это меню сново, воспользуйтесь командой /menu.',
                     reply_markup=start_menu_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "train")
def train_handler(callback: CallbackQuery):
    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'Варианты тренировок:',
                          reply_markup=train_kb)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("read_"))
def reader(callback: CallbackQuery):

    name  = callback.data.split("_")[-1]

    with open(f"{name}.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()
        shuffle(lines)

    UserCallbackData.words = lines

    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'''Варианты количества слов''',
                          reply_markup=options_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "items")
def items_handler(callback: CallbackQuery):
    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'''Все возможные предметы которые могут помочь вам в этой игре.''',
                          reply_markup=items_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "buy_skip")
def buy_skip_handler(callback: CallbackQuery):

    user_id = callback.from_user.id
    users = read_users()

    if user_id not in users.user_id.unique():
        add_user(user_id)

    set_users = users.set_index("user_id")

    set_users.loc[user_id, "passes"] += 1
    set_users.loc[user_id, "points"] -= 150
    users = set_users.reset_index()

    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'''Вы приобрели ПРОПУСК.''',
                          reply_markup=buy_skip_kb)


@bot.callback_query_handler(func=lambda callback: callback.data in ("5", "25", "all"))
def recounter_words(callback: CallbackQuery):
    length = callback.data

    if length != "all":
        UserCallbackData.words = UserCallbackData.words[:int(length) + 1]

    UserCallbackData.word = UserCallbackData.words.pop()
    start, correct_answer, *incorrect, desc = UserCallbackData.word.split("; ")

    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'''Пояснение к слову: {desc}\n\nВыберите правильный вариант\n\n{start}''',
                          reply_markup=kb_quiz_maker(correct_answer, incorrect))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith("answer_cb_"))
def checker(callback: CallbackQuery):
    answer = callback.data.split("_")[-1]
    user_id = callback.from_user.id
    users = read_users()

    if user_id not in users.user_id.unique():
        add_user(user_id)

    set_df = users.set_index("user_id")

    if answer == "correct":

        start, correct_answer, *incorrect, desc = UserCallbackData.word.split("; ")
        if UserCallbackData.session_streak != int:
            UserCallbackData.session_streak += 1

        else:
            UserCallbackData.session_streak = 1

        if UserCallbackData.session_score != float and UserCallbackData.session_streak < 5:
            UserCallbackData.session_score += 10

        elif UserCallbackData.session_score != float and 5<= UserCallbackData.session_streak < 10:
            UserCallbackData.session_score += 12.5

        elif UserCallbackData.session_score != float and 10 <= UserCallbackData.session_streak < 20:
            UserCallbackData.session_score += 15

        elif UserCallbackData.session_score != float and UserCallbackData.session_streak >= 20:
            UserCallbackData.session_score += 20

        else:
            UserCallbackData.session_score = 10


        if UserCallbackData.session_correct != int:
            UserCallbackData.session_correct += 1

        else:
            UserCallbackData.session_correct = 1


        set_df.loc[user_id, "correct"] += 1


        if UserCallbackData.session_streak < 5:
            set_df.loc[user_id, "points"] += 10
        elif 5 <= UserCallbackData.session_streak < 10:
            set_df.loc[user_id, "points"] += 12.5
        elif 10 <= UserCallbackData.session_streak < 20:
            set_df.loc[user_id, "points"] += 15
        elif 20 <= UserCallbackData.session_streak:
            set_df.loc[user_id, "points"] += 20


        bot.edit_message_text(chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              text=f'Правильно\nПравильный вариант: {correct_answer}\nОписание: {desc}',
                              reply_markup=next_kb)

        UserCallbackData.word = UserCallbackData.words.pop()

    else:
        start, correct_answer, *incorrect, desc = UserCallbackData.word.split("; ")
        UserCallbackData.word = UserCallbackData.words.pop()
        UserCallbackData.session_streak = 0
        bot.edit_message_text(chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              text=f'''Увы, но это неправильный ответ(\n\nПравильный ответ: {correct_answer}\n\nОписание: {desc}''',
                              reply_markup=next_kb)

    if UserCallbackData.session_streak != int:
        if set_df.loc[user_id, "max_streak"] < UserCallbackData.session_streak:
            set_df.loc[user_id, "max_streak"] = UserCallbackData.session_streak

    if UserCallbackData.session_answers != int:
        UserCallbackData.session_answers += 1

    else:
        UserCallbackData.session_answers = 1

    users = set_df
    users.loc[user_id, "answers"] += 1
    users = users.reset_index()

    save_changes(users)


@bot.callback_query_handler(func=lambda callback: callback.data == "skip")
def skip_handler(callback: CallbackQuery):

    user_id = callback.from_user.id
    users = read_users()

    if user_id not in users.user_id.unique():
        add_user(user_id)

    set_users = users.set_index("user_id")
    if set_users.loc[user_id, "passes"]:
        pass

        # if UserCallbackData.words:
        #
        #     start, correct_answer, *incorrect, desc = UserCallbackData.word.split("; ")
        #
        #     bot.edit_message_text(chat_id=callback.message.chat.id,
        #                           message_id=callback.message.message_id,
        #                           text=f'''Выберите правильный вариант\n{start}''',
        #                           reply_markup=kb_quiz_maker(correct_answer, incorrect))
        #
        # else:
        #     bot.edit_message_text(chat_id=callback.message.chat.id,
        #                           message_id=callback.message.message_id,
        #                           text=f'''Тренировка закончена \n\nКоличество ответов: {UserCallbackData.session_answers}\nКоличество правильных ответов: {UserCallbackData.session_correct}\nНабрано очков: {UserCallbackData.session_score}\nИспользовано ПРОПУСКОВ: {UserCallbackData.session_passes}''',
        #                           reply_markup=return_kb)
        #
        #     UserCallbackData.session_passes = int
        #     UserCallbackData.session_correct = int
        #     UserCallbackData.session_answers = int
        #     UserCallbackData.session_score = float
        #
        # set_users.loc[user_id, "passes"] -= 1
        # users = set_users.reset_index()
        #
        # save_changes(users)

    else:
        bot.answer_callback_query(callback_query_id=callback.id, text="У вас нет пропусков") # show_alert=True,


@bot.callback_query_handler(func=lambda callback: callback.data == "inventory")
def next_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    users = read_users()

    if user_id not in users.user_id.unique():
        add_user(user_id)

    set_users = users.set_index("user_id")
    num = set_users.loc[user_id, "passes"]
    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'У вас {num} пропусков',
                          reply_markup=goto_store_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "next")
def next_handler(callback: CallbackQuery):
    if UserCallbackData.words:

        start, correct_answer, *incorrect, desc = UserCallbackData.word.split("; ")

        bot.edit_message_text(chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              text=f'''Пояснение к слову: {desc}\n\nВыберите правильный вариант\n{start}''',
                              reply_markup=kb_quiz_maker(correct_answer, incorrect))

    else:
        if UserCallbackData.session_passes == int:
            UserCallbackData.session_passes = 0

        bot.edit_message_text(chat_id=callback.message.chat.id,
                              message_id=callback.message.message_id,
                              text=f'''Тренировка закончена \n\nКоличество ответов: {UserCallbackData.session_answers}\nКоличество правильных ответов: {UserCallbackData.session_correct}\nНабрано очков: {UserCallbackData.session_score}\nИспользовано ПРОПУСКОВ: {UserCallbackData.session_passes}''',
                              reply_markup=return_kb)

        UserCallbackData.session_passes = int
        UserCallbackData.session_correct = int
        UserCallbackData.session_answers = int
        UserCallbackData.session_score = float


@bot.callback_query_handler(func=lambda callback: callback.data == "return")
def return_message(callback: CallbackQuery):
    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text='Это главное меню. Дальнейшая навигация производиться с помощью кнопок.',
                          reply_markup=start_menu_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "store")
def store_message(callback: CallbackQuery):

    user_id = callback.from_user.id
    users = read_users()

    if user_id not in users.user_id.unique():
        add_user(user_id)

    set_users = users.set_index("user_id")

    points = set_users.loc[user_id, "points"]

    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'Тут показаны все предметы которые есть у вас на данный момент. Они помогут вам в выполнении заданий. Предметы можно купить в магазине.\n\nОчки: {points}',
                          reply_markup=store_kb)


@bot.callback_query_handler(func=lambda callback: callback.data == "stats")
def stats_message(callback: CallbackQuery):

    user_id = callback.from_user.id
    users = read_users()

    set_users = users.set_index("user_id")

    correct_answers = set_users.loc[user_id, "correct"]
    all_answers = set_users.loc[user_id, "answers"]
    max_streak = set_users.loc[user_id, "max_streak"]
    proc = round(correct_answers/all_answers,2)

    bot.edit_message_text(chat_id=callback.message.chat.id,
                          message_id=callback.message.message_id,
                          text=f'Всего отвечено слов: {all_answers}\nПравильно отвеченных: {correct_answers}\nСоотношение: {proc}\nНаибольшее количество правильно отгаданных слов подряд: {max_streak}',
                          reply_markup=return_kb)

bot.polling(non_stop=True)