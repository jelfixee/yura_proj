from random import shuffle

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def kb_quiz_maker(correct_answer, incorrect):
    keyboard = InlineKeyboardMarkup()

    lst_incorrect = [element for element in incorrect if element!= "-"]
    lst_incorrect.append(correct_answer)
    shuffle(lst_incorrect)

    while lst_incorrect:
        var = lst_incorrect.pop()
        keyboard.add(InlineKeyboardButton(text=var, callback_data="answer_cb_incorrect")) if var != correct_answer else keyboard.add(InlineKeyboardButton(text=var, callback_data="answer_cb_correct"))

    keyboard.add(InlineKeyboardButton(text="Назад", callback_data="train"), InlineKeyboardButton(text="Пропустить", callback_data="skip"))

    return keyboard


items_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Пропуск\n150 очков", callback_data="buy_skip")],
    [InlineKeyboardButton(text="Назад", callback_data="store")]
])

buy_skip_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Назад", callback_data="store")]
])

store_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Предметы", callback_data="items"),
     InlineKeyboardButton(text="Инвентарь", callback_data="inventory")],
    [InlineKeyboardButton(text="Назад", callback_data="return")]
])

options_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="5", callback_data="5"),
     InlineKeyboardButton(text="25", callback_data="25")],
    [InlineKeyboardButton(text="Все", callback_data="all")],
    [InlineKeyboardButton(text="Назад", callback_data="train")]
])

train_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Орфоэпия", callback_data="read_data-orf-words")],
    [InlineKeyboardButton(text="Словарные слова", callback_data="read_data-voc-words")],
    [InlineKeyboardButton(text="Назад", callback_data="return")]
])

start_menu_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Статистика", callback_data="stats")],
    # InlineKeyboardButton(text="Магазин", callback_data="store")],
    [InlineKeyboardButton(text="Тренировка", callback_data="train")]
])

return_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Меню", callback_data="return")]
])

next_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Далее", callback_data="next")]
])

goto_store_kb = InlineKeyboardMarkup([
    [InlineKeyboardButton(text="Назад", callback_data="store")]
])