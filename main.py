import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

import os




# Включаем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получаем токен из переменной окружения
TOKEN = "BOT_TOKEN"


# Инициализируем бот и диспетчер

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Вопросы теста
QUESTIONS = [
    {
        "question": "1. Как ты отреагируешь на критику?",
        "answers": ["Буду доказывать свою правоту", "Спокойно выслушаю и подумаю", "Обижусь и замолчу"]
    },
    {
        "question": "2. Твой идеальный вечер - это:",
        "answers": ["Пиво с друзьями", "Время с семьей", "Развлечение с девушкой"]
    },
    {
        "question": "3. Что для тебя самое важное?",
        "answers": ["Баня с мужиками", "Девушка", "Другое.."]
    },
    {
        "question": "4. Как часто ты занимаешься спортом?",
        "answers": ["Каждый день", "2-3 раза в неделю", "Редко или не занимаюсь"]
    },
    {
        "question": "5. Твое отношение к домашним делам:",
        "answers": ["Помогаю всегда", "Иногда помогаю", "Это не мое"]
    },
    {
        "question": "6. Тебе нравятся мужики?",
        "answers": ["Конечно", "Да", "Мне нравятся мужики"]
    },
    {
        "question": "7. Твое отношение к рискам:",
        "answers": ["Люблю адреналин", "Предпочитаю стабильность", "Зависит от ситуации"]
    },
    {
        "question": "8. Как часто ты смеешься?",
        "answers": ["Часто, люблю юмор", "Иногда", "Редко"]
    },
    {
        "question": "9. Твое отношение к обязательствам:",
        "answers": ["Выполняю всегда", "Стараюсь выполнять", "Не люблю давать обещания"]
    },
    {
        "question": "10. Роналдо или Месси?",
        "answers": ["Роналдо", "Месси", "Не смотрю футбол"]
    }
]

# Коэффициенты маскулинности для каждого ответа (от 0 до 3)
MASCULINITY_SCORES = [
    [3, 1, 0],  # Вопрос 1
    [3, 2, 1],  # Вопрос 2
    [3, 2, 2],  # Вопрос 3
    [0, 2, 3],  # Вопрос 4
    [2, 1, 0],  # Вопрос 5
    [2, 2, 2],  # Вопрос 6
    [3, 1, 2],  # Вопрос 7
    [2, 1, 0],  # Вопрос 8
    [3, 2, 1],  # Вопрос 9
    [3, 1, 0],  # Вопрос 10
]

# Состояния FSM
class TestState(StatesGroup):
    question_index = State()
    score = State()

# Результаты теста
RESULTS = {
    "very_low": {
        "title": "🌸 Ты вумен",
        "description": "Ты чувствительный, добрый и ценишь эмоциональную связь",
        "emoji": "🧸",
        "picture": "https://avatars.mds.yandex.net/i?id=ac3ea1db94a3ddbeee03e5632baef264_l-9145401-images-thumbs&n=13"
    },
    "low": {
        "title": "💙 Фембой",
        "description": "У тебя развита эмоциональная сфера, ты крутой фембой",
        "emoji": "🐰",
        "picture": "https://avatars.mds.yandex.net/i?id=f696a8d1102bf88ab63fb0bb3ae5ec4c_l-5876132-images-thumbs&n=13"
    },
    "medium": {
        "title": "👨 Обычный парень",
        "description": "Ты сбалансирован - не слишком мягкий, но и не агрессивный",
        "emoji": "👨‍💼",
        "picture":"https://avatars.mds.yandex.net/i?id=622fd67ec3b9d84d9f752cf9a140c9dc493bc53c-4948104-images-thumbs&n=13"

    },
    "high": {
        "title": "💪 Тасманский дьявол",
        "description": "Ты решительный и смелый, полон уверенности в себе",
        "emoji": "🐯",
        "picture": "https://i.pinimg.com/736x/fc/03/29/fc0329634b9d20604846ffb226b6c1b5.jpg"
    },
    "very_high": {
        "title": "🔥 Абсолютный альфа-самец(возможно гей)",
        "description": "Ты максимально маскулинен - настоящий мужик по жизни!",
        "emoji": "🦁",
        "picture": "https://avatars.mds.yandex.net/i?id=37255753d3bb12843ccc7f6dfc876aca9f429988-10397524-images-thumbs&n=13"

    }
}

def get_result_category(percentage):
    """Определяет категорию результата по проценту"""
    if percentage < 20:
        return "very_low"
    elif percentage < 40:
        return "low"
    elif percentage < 60:
        return "medium"
    elif percentage < 80:
        return "high"
    else:
        return "very_high"

def create_test_keyboard(question_index):
    """Создает инлайн-клавиатуру с ответами"""
    builder = InlineKeyboardBuilder()
    
    for i, answer in enumerate(QUESTIONS[question_index]["answers"]):
        builder.add(InlineKeyboardButton(
            text=answer,
            callback_data=f"answer_{i}"
        ))
    
    builder.adjust(1)
    return builder.as_markup()

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.set_state(TestState.question_index)
    await state.update_data(question_index=0, score=0)
    
    await message.answer(
        "🎯 <b>Добро пожаловать в тест маскулинности!</b>\n\n"
        "Я помогу определить, насколько ты мужик по жизни 😎\n\n"
        "Ответь на 10 вопросов честно, и ты получишь свой результат!\n\n"
        "Давай начнем? 💪",
        parse_mode="HTML"
    )
    
    await asyncio.sleep(1)
    await send_question(message.chat.id, state)

async def send_question(chat_id, state: FSMContext):
    """Отправляет текущий вопрос"""
    data = await state.get_data()
    question_index = data["question_index"]
    
    if question_index >= len(QUESTIONS):
        # Тест завершен, показываем результат
        await show_result(chat_id, state)
        return
    
    question = QUESTIONS[question_index]["question"]
    keyboard = create_test_keyboard(question_index)
    
    progress = f"\n\n📊 Вопрос {question_index + 1}/{len(QUESTIONS)}"
    
    await bot.send_message(
        chat_id,
        f"<b>{question}</b>{progress}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

async def show_result(chat_id, state: FSMContext):
    """Показывает результат теста"""
    data = await state.get_data()
    score = data["score"]
    
    # Максимально возможный результат: 10 вопросов * 3 балла = 30
    percentage = (score / 30) * 100
    category = get_result_category(percentage)
    result = RESULTS[category]
    
    result_text = (
        f"{result['emoji']} <b>{result['title']}</b>\n\n"
        f"<i>{result['description']}</i>\n\n"
        f"📈 <b>Твой результат: {percentage:.0f}%</b>\n"
        f"<b>Баллы: {score}/30</b>"
    )
    
    # Создаем инлайн-клавиатуру для повтора теста
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🔄 Пройти тест заново", callback_data="restart_test")
    ]])
    
    await bot.send_photo(
        chat_id,
        photo=result["picture"],
        caption= result_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    await state.clear()

@dp.callback_query(F.data.startswith("answer_"))
async def answer_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик ответа на вопрос"""
    answer_index = int(callback.data.split("_")[1])
    data = await state.get_data()
    question_index = data["question_index"]
    
    # Добавляем баллы
    score = data["score"] + MASCULINITY_SCORES[question_index][answer_index]
    
    # Переходим к следующему вопросу
    await state.update_data(question_index=question_index + 1, score=score)
    
    # Удаляем предыдущее сообщение
    await callback.message.delete()
    
    # Отправляем следующий вопрос или результат
    await send_question(callback.message.chat.id, state)
    
    await callback.answer()

@dp.callback_query(F.data == "restart_test")
async def restart_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик перезапуска теста"""
    await state.set_state(TestState.question_index)
    await state.update_data(question_index=0, score=0)
    
    await callback.message.delete()
    
    await callback.message.answer(
        "🎯 <b>Тест запущен заново!</b>\n\n"
        "Давай еще раз проверим твою маскулинность 💪",
        parse_mode="HTML"
    )
    
    await asyncio.sleep(1)
    await send_question(callback.message.chat.id, state)
    await callback.answer()

async def main():
    """Главная функция"""
    logger.info("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
