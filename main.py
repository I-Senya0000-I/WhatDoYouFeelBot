from telebot import types, TeleBot
import database
import json



     


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
@bot.message_handler(commands=['start'])
def menu(message):
    msg = bot.send_message(message.chat.id, "Секунду!")
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
    #bot.send_message(message.chat.id, "Это очень крутой бот с мощными кнопками и промптами! вот кнопки а промптов нет", reply_markup=kb)
    bot.edit_message_text("Ботяра", message.chat.id, msg.id, reply_markup=kb)


def menu_edit(message, prev_bot_msg):
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
    #bot.send_message(message.chat.id, "Это очень крутой бот с мощными кнопками и промптами! вот кнопки а промптов нет", reply_markup=kb)
    bot.edit_message_text("Ботяра", message.chat.id, prev_bot_msg.id, reply_markup=kb)



"""
Выбор чата
"""
@bot.callback_query_handler(func=lambda call: call.data == "chat_menu")
def chat_menu(call):
    user = db.get_user(call.from_user.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Back", callback_data="menu"))
    print(db.get_user_chats(user["id"]))
    for chat in db.get_user_chats(user["id"]):
        print(db.get_user_by_id(chat["user1_id"] if chat["user1_id"] != user["id"] else chat["user2_id"]))
        kb.add(types.InlineKeyboardButton(
            db.get_user_by_id(
                chat["user1_id"] if chat["user1_id"] != user["id"] else chat["user2_id"])["nickname"], 
                callback_data=f"chat_{chat["id"]}"
            )
        )
    kb.add(types.InlineKeyboardButton("New chat", callback_data="new_chat"))
    #bot.send_message(call.message.chat.id, "Select action or chat:", reply_markup=kb)
    bot.edit_message_text("Select action or chat", call.message.chat.id, call.message.id, reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data == "menu")
def menu_from_button(call):
    menu_edit(call.message, call.message)


@bot.callback_query_handler(func=lambda call: call.data[:4] == "chat" and call.data != "chat_menu")
def enter_chat(call):
    print(call.data)
    user = db.get_user(call.from_user.id)
    db.update_user(user["chat_id"], user["nickname"], user["chat_id"], "", int(call.data[5:]), user["searching"])
    chat = db.get_chat(int(call.data[5:]))
    #bot.send_message(call.message.chat.id, "Entering chat...")
    user2 = db.get_user_by_id(chat["user2_id" if chat["user1_id"] == user["id"] else "user1_id"])
    bot.edit_message_text(f"Entering chat with user {user2["nickname"]}\nThere is yours message history:", call.message.chat.id, call.message.id)
    message_history_message_text = ""
    hist = json.loads(chat["history"])
    if not hist: hist = []
    for msg in hist:
        if msg["sender"] == user["id"]:
            message_history_message_text += f"*You*: \n{msg["text"]}\n\n"
        else:
            message_history_message_text += f"*{user2["nickname"]}*: \n{msg["text"]}\n\n"
    bot.send_message(call.message.chat.id, message_history_message_text, parse_mode="markdown")


@bot.message_handler(commands=["leave_chat"])
def leave_chat(message):
    user = db.get_user(message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "Please use /start")
        return
    
    db.update_user(user["chat_id"], user["nickname"], user["chat_id"], "", -1, user["searching"])
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Back in menu", callback_data="chat_menu"))
    bot.send_message(message.chat.id, "You leaved chat.", reply_markup=kb)




"""
Меню создания чата
"""
@bot.callback_query_handler(func=lambda call: call.data == "new_chat")
def create_chat(call):
    user = db.get_user(call.from_user.id)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Back", callback_data="chat_menu"))
    kb.add(types.InlineKeyboardButton("Anon", callback_data="create_chat_anon"), types.InlineKeyboardButton("Public", callback_data="create_chat_public"))
    #bot.send_message(call.message.chat.id, "Select chat type:", reply_markup=kb)
    bot.edit_message_text("Select chat type", call.message.chat.id, call.message.id, reply_markup=kb)



@bot.callback_query_handler(func=lambda call: call.data == "chat_menu")
def chat_menu_from_button(call):
    chat_menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == "create_chat_anon")
def create_chat_anon(call):
    pass


@bot.callback_query_handler(func=lambda call: call.data == "create_chat_public")
def create_chat_public(call):
    bot.edit_message_text("Enter username. User must use bot once.", call.message.chat.id, call.message.id)
    bot.register_next_step_handler(call.message, get_username_handler)


def get_username_handler(message):
    user1 = db.get_user(message.from_user.id)
    user2 = db.get_user_by_nickname(message.text)
    if not user2:
        bot.send_message(message.chat.id, "This user is not registered in our system. Tell this person to start chat with this bot.")
        return
    chat = db.get_chat(db.create_chat(user1["id"], user2["id"], 0))
    db.update_user(user1["user_id"], user1["nickname"], user1["chat_id"], "", chat["id"], 0)
    bot.send_message(message.chat.id, "Chat creaaated! Now every message will be sent to this chat.")


# main message handler
@bot.message_handler()
def default_message_handler(message):
    user = db.get_user(message.from_user.id)
    if not user:
        # user is not in db
        bot.send_message(message.chat.id, "Please use /start")
        return
    if user["current_chat"] == -1:
        # no chat selected, so message is unknown command
        bot.send_message(message.chat.id, "Unknown command")
        return
    
    # else user in chat
    chat = db.get_chat(user["current_chat"])
    user2 = db.get_user_by_id(chat["user2_id" if chat["user1_id"] == user["id"] else "user1_id"])

    # appending message to chat history
    history = json.loads(chat["history"])
    if not history:
        history = []
    history.append({
        "sender": user["id"],
        "text": message.text,
    })
    history = json.dumps(history)
    db.update_chat(chat["id"], chat["user1_id"], chat["user2_id"], chat["anonymous"], chat["active"], history)
    print(history)
    
    if user2["current_chat"] == user["current_chat"]:
        # if chat is active send message
        bot.send_message(user2["chat_id"], message.text)
        



bot.infinity_polling()