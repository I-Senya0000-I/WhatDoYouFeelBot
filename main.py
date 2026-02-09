from telebot import types, TeleBot
import database



def get_token(filename):
    with open(filename, 'r') as file:
        token = file.read().strip()
        return token

bot = TeleBot(get_token("token.txt"), parse_mode=None)
db = database.Database()
db.create_tables()


"""
Главное меню
"""
@bot.message_handler(commands=['start', 'home'])
def menu(message):
    bot.send_message(message.chat.id, "Секунду!")
    user = message.from_user
    db_user = db.get_user(user.id)
    if db_user:
        print("User in db")
    else:
        db.create_user(user.id, user.username, message.chat.id, "")
        db_user = db.get_user(user.id)
        print("created")
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Stats", callback_data="stats"))
    #kb.add(types.InlineKeyboardButton("", callback_data=""))
    kb.add(types.InlineKeyboardButton("Enter chat!", callback_data="chat_menu"))
    bot.send_message(message.chat.id, "Это очень крутой бот с мощными кнопками и промптами! вот кнопки а промптов нет", reply_markup=kb)


"""
Выбор чата
"""
@bot.callback_query_handler(func=lambda call: call.data == "chat_menu")
def chat_menu(call):
    user = db.get_user(call.from_user.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Back", callback_data="menu"))
    for chat in db.get_user_chats(user["id"]):
        kb.add(types.InlineKeyboardButton(chat.name, callback_data=f"chat_{chat.id}"))
    kb.add(types.InlineKeyboardButton("New chat", callback_data="new_chat"))
    bot.send_message(call.message.chat.id, "Select action or chat:", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu_from_button(call):
    menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data[:4] == "chat" and call.data != "chat_menu")
def enter_chat(call):
    print(call.data)
    bot.send_message(call.message.chat.id, "Entering chat...")


"""
Меню создания чата
"""
@bot.callback_query_handler(func=lambda call: call.data == "new_chat")
def create_chat(call):
    user = db.get_user(call.from_user.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Back", callback_data="chat_menu"))
    kb.add(types.InlineKeyboardButton("Anon", callback_data="create_chat_anon"), types.InlineKeyboardButton("Public", callback_data="create_chat_public"))
    bot.send_message(call.message.chat.id, "Select chat type:", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "chat_menu")
def chat_menu_from_button(call):
    chat_menu(call.message)


#@bot.message_handler(commands=['chat'])
#def start_chat(message):
    


bot.infinity_polling()