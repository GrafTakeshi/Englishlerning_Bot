import random

from sqlalchemy.orm import sessionmaker

from config import bot, DSN
from telebot.types import Message
from sqlalchemy import create_engine

from models import create_tables, Dicrionary, Users, Usersdict

engine = create_engine(DSN)
Session = sessionmaker(bind=engine)
dictionary = Dicrionary()
users = Users()
usersdict = Usersdict


def welcome(message: Message, cid):
    session = Session()
    create_tables(engine)
    userslist = session.query(Users.tg_user_id).all()
    if any(cid in usertyp for usertyp in userslist):
        bot.send_message(cid, f"С возвращением {message.from_user.first_name}, продолжим?")
    else:
        bot.send_message(cid, f"Привет {message.from_user.first_name}, я вижу ты у нас впервые давай "
                              f"начнем учить английский?")
        insert_id = Users(tg_user_id=cid)
        session.add(insert_id)
        session.flush()
        session.commit()
        first_words = []
        for i in range(1, 11):
            first_words.append(Usersdict(tg_user_id=insert_id.id, userdictunit=i))
        session.bulk_save_objects(first_words)
    session.commit()
    session.close()


def add_new_word(message: Message):
    num_of_word = 0
    cid = message.chat.id
    if ' ' not in message.text:
        bot.send_message(chat_id=cid, text=f'Некоректный ввод повторите операцию')
        return
    if message.text.split()[0].isalpha() and message.text.split()[1].isalpha():
        enword = message.text.split()[0].capitalize()
        ruword = message.text.split()[1].capitalize()
        session = Session()
        for u in session.query(Users).filter(Users.tg_user_id == cid).all():
            u_id = u.id
        dict_res = []
        for d in session.query(Dicrionary).all():
            dict_res.append(d.enword)
        if enword not in dict_res:
            words = Dicrionary(enword=enword, ruword=ruword)
            session.add(words)
            session.flush()
            add_words = Usersdict(userdictunit=words.id, tg_user_id=u_id)
            session.add(add_words)
            query = session.query(Usersdict, Users) \
                .join(Users, Users.id == Usersdict.tg_user_id).filter(Users.tg_user_id == cid).all()
            for i in query:
                num_of_word += 1
            log_message = f'Пара {enword} - {ruword} добавлена в словарь. Теперь вы учите ' \
                          f'{num_of_word} слов нажмите  кнопку "Дальше ⏭"'
        else:
            dict_res = []
            query = session.query(Usersdict, Dicrionary, Users).join(Dicrionary,
                                                                     Dicrionary.id == Usersdict.userdictunit).join(
                Users, Users.id == Usersdict.tg_user_id).filter(Users.tg_user_id == cid).all()
            for a, b, c in query:
                dict_res.append(b.enword)
            if enword not in dict_res:
                query = session.query(Dicrionary).filter(Dicrionary.enword == enword).all()
                for c in query:
                    dict_id = c.id
                words = Usersdict(userdictunit=dict_id, tg_user_id=u_id)
                session.add(words)
                query = session.query(Usersdict, Users) \
                    .join(Users, Users.id == Usersdict.tg_user_id).filter(Users.tg_user_id == cid).all()
                for i in query:
                    num_of_word += 1

                log_message = f'Пара {enword} - {ruword} добавлена в словарь. Теперь вы учите ' \
                              f'{num_of_word} слов'
            else:
                log_message = f' Пара {enword} - {ruword} уже присутствует в Базе! нажмите  кнопку "Дальше ⏭"'
        session.commit()
        session.close()
        bot.send_message(chat_id=cid, text=log_message)
    else:
        bot.send_message(chat_id=cid, text=f'Некоректный ввод повторите операцию')


def delite_from_userdict(cid, targetword):
    session = Session()
    word_dict = []
    ids = 0
    query = session.query(Usersdict, Dicrionary, Users).join(Dicrionary, Dicrionary.id == Usersdict.userdictunit).join(
        Users, Users.id == Usersdict.tg_user_id).filter(Users.tg_user_id == cid, Dicrionary.enword == targetword).all()
    for a, b, c in query:
        ids = a.userdictunit
        d_enword = b.enword
        d_ruword = b.ruword
    temp = session.query(Usersdict).all()
    for tt in temp:
        word_dict.append(tt.userdictunit)
    if ids not in word_dict:
        log_message = f'Пара уже удалена из вашего словаря ' \
                      f'нажмите  кнопку "Дальше ⏭"'
        bot.send_message(chat_id=cid, text=log_message)
        return
    else:
        session.query(Usersdict).filter(Usersdict.userdictunit == ids).delete()
        log_message = f'Пара {d_enword} - {d_ruword} успешно удалена из' \
                      f' вашего словаря нажмите  кнопку "Дальше ⏭"'
        bot.send_message(chat_id=cid, text=log_message)
        session.commit()
        session.close()


def get_user_words(cid):
    session = Session()
    userwords_list = []
    ower_list = []
    count = 0
    query = session.query(Usersdict, Dicrionary, Users).join(Dicrionary, Dicrionary.id == Usersdict.userdictunit).join(
        Users, Users.id == Usersdict.tg_user_id).filter(Users.tg_user_id == cid).all()
    for a, b, c in query:
        userwords_list.append((b.enword, b.ruword))
    target_list = random.choice(userwords_list)
    userwords_list.remove(target_list)
    while count <= 4:
        for pair in userwords_list:
            ower_list.append(pair)
            userwords_list.remove(pair)
            count += 1
    ower_word_list = [ower_list[0][0], ower_list[1][0], ower_list[2][0], ower_list[3][0]]
    return target_list, ower_word_list
