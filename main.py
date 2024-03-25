import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router, F
from helpers import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from aiogram.types.input_file import FSInputFile

logging.basicConfig(level=logging.INFO)
bot = Bot(token=config['bot']['token'], parse_mode='HTML')
dp = Dispatcher()
router = Router()
dp.include_router(router)
scheduler = AsyncIOScheduler({'apscheduler.timezone': 'UTC'})


async def send_accepted(chat_id):
    kb = [[types.KeyboardButton(text="/start")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Начать заново'
    )
    agree_text = '''Привет, это снова Алгус!

Спасибо за ожидание, мне только пришел ответ от коллег, я возвращаюсь к тебе с обратной связью. 

Коллеги хотят познакомиться с тобой лично, для этого запишись на интервью по ссылке https://calendly.com/alexey-nazarow/30min.

Спасибо тебе за уделённое время, было очень приятно познакомиться. Желаю только удачи в дальнейшем отборе на вакансию!'''
    await update_user('result_sent', 1, str(chat_id))
    await bot.send_message(chat_id=chat_id, text=agree_text, reply_markup=keyboard)


async def send_declined(chat_id):
    kb = [[types.KeyboardButton(text="/start")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Начать заново'
    )
    decline_text = '''Привет, это снова Алгус!
Спасибо за ожидание, мне только пришел ответ от коллег, я возвращаюсь к тебе с обратной связью.

К сожалению, на данный момент мы не можем предложить тебе стать частью компании Алгоритмика.

Спасибо за уделённое время, было очень приятно познакомиться. Желаю только удачи в дальнейших поисках и успехов в работе!'''
    await update_user('result_sent', 1, str(chat_id))
    await bot.send_message(chat_id=chat_id, text=decline_text, reply_markup=keyboard)


class HandleClient(StatesGroup):
    waiting_for_step1 = State()
    waiting_for_step2 = State()
    waiting_for_step3 = State()
    waiting_for_step4 = State()
    waiting_for_step5 = State()
    waiting_for_step6 = State()
    waiting_for_step7 = State()
    waiting_for_step8 = State()
    waiting_for_step9 = State()
    waiting_for_step10 = State()
    waiting_for_feedback = State()
    waiting_for_admin_action = State()



@router.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    kb = [[types.KeyboardButton(text="Дальше"), ]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Нажмите "Дальше", чтобы продолжить'
    )
    await message.answer('''Привет, меня зовут Алгус! 

Я карьерный помощник компании Алгоритмика. Меня сделали, чтобы помочь тебе трудоустроиться в компанию.

Чтобы продолжить отбор по вакансии, нам нужно с тобой обсудить несколько вопросов, которые помогут тебе и твоему будущему руководителю.''', reply_markup=keyboard)
    user = User((0, str(message.chat.id), message.chat.first_name if not None else 'Undefined', message.chat.last_name if not None else 'Undefined', message.chat.username if not None else 'Undefined', str(datetime.utcnow()), 'Undefined', -1, -1, '0', '0', '0', '0', '0'))
    await add_user(user)
    await state.update_data({'user': user})
    
    await state.set_state(HandleClient.waiting_for_step1)


@router.message(HandleClient.waiting_for_step1, F.text.in_(['Дальше']))
async def about_company(message: types.Message, state: FSMContext):
    kb = [[types.KeyboardButton(text="Мне подходит"), types.KeyboardButton(text="Мне не подходит")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов'
    )
    await message.answer('''Мы - Алгоритмика, уже более 7 лет обучаем детей программированию и являемся одной из крупнейших онлайн-школ.

Мы продолжаем быстро расти, поэтому находимся в активном поиске менеджеров по продажам мини-курсов. 

Что значит “мини-курсы”: родитель оставляет заявку на обучение, менеджер по продажам связывается с родителем и записывает ребенка на мини-курс. Сами занятия у нас проводят преподаватели. После прохождения мини-курса, менеджер по продажам связывается снова и продает пакет уроков.''', reply_markup=keyboard)
    
    await state.set_state(HandleClient.waiting_for_step2)


@router.message(HandleClient.waiting_for_step2, F.text.in_(['Мне подходит', 'Мне не подходит']))
async def choice1(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Мне не подходит':
        await message.answer('''Очень жаль это слышать :(

Пожалуйста, оставь обратную связь, что именно тебя не устроило, а я передам ее нашим коллегам.''', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(HandleClient.waiting_for_feedback)
    elif text == 'Мне подходит':
        kb = [[types.KeyboardButton(text="Мне подходит"), types.KeyboardButton(text="Мне не подходит")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder='Выберите один из вариантов'
        )
        await message.answer('''Отлично! Рад начать наше знакомство.

Первым делом напомню условия по текущей вакансии:

• <b>Оклад 30.000, два бонуса по 3500 и % от продаж (от 4 до 12) Среднемесячный доход от 80.000, после испытательного от 100.000 рублей;</b>
• Оплачиваемое обучение и наставник;
• <b>Удаленка, ПН, ЧТ, ВС сегда рабочие, с 10 до 19 или с 11 до 20;</b>
• Полностью белая зарплата и оформление;
• Корпоративные скидки и клубы для сотрудников.
''', reply_markup=keyboard)
        
        await state.set_state(HandleClient.waiting_for_step3)

    
@router.message(HandleClient.waiting_for_step3, F.text.in_(['Мне подходит', 'Мне не подходит']))
async def choice1(message: types.Message, state: FSMContext):
    text = message.text
    if text == 'Мне не подходит':
        await message.answer('''Очень жаль это слышать :(

К сожалению, я не могу предложить тебе другие условия, но я бы хотел услышать, что повлияло на твой выбор.

Пожалуйста, оставь обратную связь, что именно тебя не устроило, а я передам ее нашим коллегам.''', reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(HandleClient.waiting_for_feedback)
    elif text == 'Мне подходит':
        kb = [[types.KeyboardButton(text="До 6 месяцев"), types.KeyboardButton(text="От 1 до 3 лет"), types.KeyboardButton(text="Больше 3 лет")]]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder='Выберите один из вариантов'
        )
        await message.answer('''Это радует :)
                             
Предлагаю обсудить твой опыт работы.
                             
Подскажи, какой у тебя опыт работы в продажах?
''', reply_markup=keyboard)
        
        await state.set_state(HandleClient.waiting_for_step4)


@router.message(HandleClient.waiting_for_step4, F.text.in_(['До 6 месяцев', 'От 1 до 3 лет', 'Больше 3 лет']))
async def choice2(message: types.Message, state: FSMContext):
    text = message.text # Текст с опытом работы
    await state.update_data({'exp': text})
    kb = [[types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов'
    )
    await message.answer('Есть ли опыт работы в CRM-системах? Например Bitrix или AMO CRM.', reply_markup=keyboard)
    await update_user('experience', text, str(message.chat.id))
    await state.set_state(HandleClient.waiting_for_step5)


@router.message(HandleClient.waiting_for_step5, F.text.in_(['Да', 'Нет']))
async def choice3(message: types.Message, state: FSMContext):
    text = message.text # Текст про CRM
    await state.update_data({'exp_crm': text})
    kb = [[types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов'
    )
    await message.answer('''Мне осталось задать тебе всего пару вопросов. Все они связаны с оформлением, чтобы я заранее мог передать информацию в отдел кадров и они смогли подготовиться к этому процессу.

Подскажи, есть ли у тебя гражданство России?''', reply_markup=keyboard)
    await update_user('crm', text, str(message.chat.id))
    await state.set_state(HandleClient.waiting_for_step6)


@router.message(HandleClient.waiting_for_step6, F.text.in_(['Да', 'Нет']))
async def choice4(message: types.Message, state: FSMContext):
    text = message.text # Текст про ргажданство
    await state.update_data({'citizenship': text})
    kb = [[types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов'
    )
    await message.answer('Находишься ли ты сейчас на территории России?', reply_markup=keyboard)
    await update_user('citizenship', text, str(message.chat.id))
    await state.set_state(HandleClient.waiting_for_step7)


@router.message(HandleClient.waiting_for_step7, F.text.in_(['Да', 'Нет']))
async def choice5(message: types.Message, state: FSMContext):
    text = message.text # Текст про метоснахождение
    await state.update_data({'location': text})
    kb = [[types.KeyboardButton(text="Да"), types.KeyboardButton(text="Нет")]]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder='Выберите один из вариантов'
    )
    await message.answer('Есть ли у тебя рублевый счет?', reply_markup=keyboard)
    await update_user('location', text, str(message.chat.id))
    await state.set_state(HandleClient.waiting_for_step8)


@router.message(HandleClient.waiting_for_step8, F.text.in_(['Да', 'Нет']))
async def choice6(message: types.Message, state: FSMContext):
    text = message.text # Текст про банковскую карту
    await state.update_data({'has_card': text})
    user_data = await state.get_data()
    check = user_data['exp'] != 'До 6 месяцев'
    check = check and user_data['exp_crm'] != 'Нет'
    check = check and user_data['has_card'] != 'Нет'
    check = check and not (user_data['citizenship'] == 'Нет' and user_data['location'] == 'Да')
    today = datetime.utcnow()
    tomorrow = today + timedelta(days=1)
    if check:
        scheduler.add_job(send_accepted, 'date', run_date=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0), args=[message.chat.id])
        await add_reply((1, str(message.chat.id), tomorrow.year, tomorrow.month, tomorrow.day))
    else:
        scheduler.add_job(send_declined, 'date', run_date=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0), args=[message.chat.id])
        await add_reply((0, str(message.chat.id), tomorrow.year, tomorrow.month, tomorrow.day))
    
    await update_user_final_touch(text, str(datetime.utcnow()), 1 if check else 0, 0, str(message.chat.id))
    await message.answer('''Отлично! Спасибо за ответы на все мои вопросы.
                         
Я передам всю информацию о тебе коллегам и вернусь с обратной связью в течение 2-х дней.
                         
Спасибо за знакомство и до скорой встречи!''', reply_markup=types.ReplyKeyboardRemove())

    await state.clear()



@router.message(HandleClient.waiting_for_feedback, F.text)
async def feedback(message: types.Message, state: FSMContext):
    feedback_given = message.text # Куда-то сохранить
    await message.answer('''Спасибо, что оставил комментарий, он помогает нам стать лучше.

Мне было приятно познакомиться, всегда буду рад видеть тебя снова, если что-то поменяется.

Просто напиши мне, и я начну диалог с самого начала :)

Хорошего дня и удачи!''', reply_markup=types.ReplyKeyboardRemove())
    
    await add_feedback(str(message.chat.id), feedback_given)

    await state.clear()


@router.message(Command(commands=["credits"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer('Разработал @kekartem')


@router.message(Command(commands=["admin"]))
async def admin(message: types.Message, state: FSMContext):
    password = message.text.split(' ')[1]
    if password == 'TH$JCmAn':
        if await get_admin_by_id(str(message.chat.id)) is not None:
            kb = [[types.KeyboardButton(text="Статистика юзеров"), types.KeyboardButton(text="Обратная связь")]]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder='Опция'
            )
            await message.answer('Ты уже админ', reply_markup=keyboard)
            await state.set_state(HandleClient.waiting_for_admin_action)
        else:
            await add_admin(str(message.chat.id))
            kb = [[types.KeyboardButton(text="Статистика юзеров"), types.KeyboardButton(text="Обратная связь")]]
            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder='Опция'
            )
            await message.answer('Теперь здесь можно получать статистику. Привет, Лёша!', reply_markup=keyboard)
            await state.set_state(HandleClient.waiting_for_admin_action)
    else:
        await message.answer('Пароль неправильный')
    
    await message.delete()


@router.message(HandleClient.waiting_for_admin_action, F.text)
async def getstats(message: types.Message, state: FSMContext):
    if message.text == 'Статистика юзеров':
        await get_csv_users()
        await bot.send_document(message.chat.id, FSInputFile('users.csv'))
    elif message.text == 'Обратная связь':
        await get_csv_feedback()
        await bot.send_document(message.chat.id, FSInputFile('feedback.csv'))



async def main():
    scheduler.start()
    await init_db()
    replies = await get_all_replies()
    for reply in replies:
        if reply.is_past():
            print('removed')
            await remove_reply(reply.id)
        else:
            if reply.status == 1:
                scheduler.add_job(send_accepted, 'date', run_date=datetime(reply.year, reply.month, reply.day, 9, 0, 0), args=[reply.chat_id])
            else:
                scheduler.add_job(send_declined, 'date', run_date=datetime(reply.year, reply.month, reply.day, 9, 0, 0), args=[reply.chat_id])

    await dp.start_polling(bot, skip_updates=True)



if __name__ == "__main__":
    asyncio.run(main())