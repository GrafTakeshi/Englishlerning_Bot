import psycopg2 as psycopg2
import random

from config import bot, db_connection
from telebot.types import Message


def welcome(message: Message, cid):
    with psycopg2.connect(db_connection) as conn:
        with conn.cursor() as cur:
            cur.execute("""SELECT tg_user_id FROM users;""")
            users_list = cur.fetchall()
            if any(cid in usertyp for usertyp in users_list):
                bot.send_message(cid, f"С возвращением {message.from_user.first_name}, продолжим?")
            else:
                bot.send_message(cid, f"Привет {message.from_user.first_name}, я вижу ты у нас впервые давай "
                                      f"начнем учить английский?")
                cur.execute("""insert into users (tg_user_id) values (%s) returning id""", [cid])

                insert_id = cur.fetchone()[0]
                cur.executemany("""insert into usersdict(tg_user_id, userdictunit) values (%s, %s)""", [
                    (insert_id, 1), (insert_id, 2), (insert_id, 3),
                    (insert_id, 4), (insert_id, 5), (insert_id, 6),
                    (insert_id, 7), (insert_id, 8), (insert_id, 9),
                    (insert_id, 10)

                ])
                conn.commit()
                conn.close()


def add_new_word(message: Message):
    cid = message.chat.id
    if ' ' not in message.text:
        bot.send_message(chat_id=cid, text=f'Некоректный ввод повторите операцию')
        return
    if message.text.split()[0].isalpha() and message.text.split()[1].isalpha():
        enword = message.text.split()[0].capitalize()
        ruword = message.text.split()[1].capitalize()
        with psycopg2.connect(db_connection) as conn:
            with conn.cursor() as cur:
                cur.execute("""select id from users where tg_user_id = %s;""", [cid])
                u_id = cur.fetchone()
                cur.execute("""SELECT enword FROM dictionary;""")
                dictionary = cur.fetchall()
                dict_res = []
                for word in dictionary:
                    dict_res.append(word[0])
                if enword not in dict_res:
                    cur.execute("""insert into dictionary (enword, ruword) values (%s, %s) returning id;""",
                                (enword, ruword))
                    insert_id = cur.fetchone()[0]
                    cur.execute("""insert into usersdict (userdictunit, tg_user_id) values (%s, %s);""",
                                (insert_id, u_id[0]))
                    cur.execute("""select count(*) from usersdict u join users u2 on u.tg_user_id = u2.id 
                    where u2.tg_user_id = %s;""", [cid])
                    num_of_word = cur.fetchone()[0]
                    log_message = f'Пара {enword} - {ruword} добавлена в словарь. Теперь вы учите {num_of_word} слов'
                else:
                    cur.execute("""select enword, ruword from usersdict u join users u2 on u.tg_user_id = u2.id
                    join "dictionary" d on u.userdictunit = d.id
                    where u2.tg_user_id = '%s'""", [cid])
                    userwords_list = cur.fetchall()
                    dict_res = []
                    for word in userwords_list:
                        dict_res.append(word[0])
                    if enword not in dict_res:
                        cur.execute("""select id from dictionary where enword = %s;""", [enword])
                        dict_id = cur.fetchone()[0]
                        cur.execute("""insert into usersdict (userdictunit, tg_user_id) values (%s, %s);""",
                                    (dict_id, u_id[0]))
                        cur.execute("""select count(*) from usersdict u join users u2 on u.tg_user_id = u2.id 
                        where u2.tg_user_id = %s;""", [cid])
                        num_of_word = cur.fetchone()[0]
                        log_message = f'Пара {enword} - {ruword} добавлена в словарь. Теперь вы учите ' \
                                      f'{num_of_word} слов'
                    else:
                        log_message = f' Пара {enword} - {ruword} уже присутствует в Базе'
                conn.commit()
                conn.close()
            bot.send_message(chat_id=cid, text=log_message)
    else:
        bot.send_message(chat_id=cid, text=f'Некоректный ввод повторите операцию')


def delite_from_userdict(cid, targetword):
    with psycopg2.connect(db_connection) as conn:
        with conn.cursor() as cur:
            cur.execute("""select u.id, enword, ruword from usersdict u join users u2 on u.tg_user_id = u2.id
            join "dictionary" d on u.userdictunit = d.id
            where u2.tg_user_id = %s AND enword = %s;""", (cid, targetword))
            userwords_list = cur.fetchall()
            cur.execute("""DELETE FROM usersdict Where id = %s; """, [userwords_list[0][0]])
            log_message = f'Пара {userwords_list[0][1]} - {userwords_list[0][2]} успешно удалена из вашего словаря'
            bot.send_message(chat_id=cid, text=log_message)
        conn.commit()
        conn.close()


def get_user_words(cid):
    with psycopg2.connect(db_connection) as conn:
        with conn.cursor() as cur:
            cur.execute("""select enword, ruword from usersdict u
            join users u2 on u.tg_user_id = u2.id 
            join "dictionary" d on u.userdictunit = d.id 
            where u2.tg_user_id = '%s'""", [cid])
            userwords_list = cur.fetchall()
            target_list = random.choice(userwords_list)
            userwords_list.remove(target_list)
            ower_list = random.choices(userwords_list, k=4)
            ower_word_list = [ower_list[0][0], ower_list[1][0], ower_list[2][0], ower_list[3][0]]
    conn.commit()
    conn.close()
    return target_list, ower_word_list
