import json
from copy import deepcopy
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Message
from database_1.database import user_dict_template
from filters.filters import IsDelBookmarkCallbackData, IsDigitCallbackData
from keyboards.bookmarks_kb import create_bookmarks_keyboard, create_edit_keyboard
from keyboards.pagination_kb import create_pagination_keyboard
from lexicon.lexicon import LEXICON
from services.file_handling import book

router = Router()

USERS_DB_FILE = 'users_db.json'

def load_users_db():
    try:
        with open(USERS_DB_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users_db():
    with open(USERS_DB_FILE, 'w') as file:
        json.dump(users_db, file)

users_db = load_users_db()

@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(LEXICON[message.text])
    user_id = str(message.from_user.id)
    if user_id not in users_db:
        users_db[user_id] = deepcopy(user_dict_template)
        users_db[user_id]["bookmarks"] = []
        save_users_db()

@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(LEXICON[message.text])

@router.message(Command(commands='beginning'))
async def process_beginning_command(message: Message):
    user_id = str(message.from_user.id)
    users_db[user_id]['page'] = 1
    save_users_db()
    text = book[users_db[user_id]['page']]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{users_db[user_id]["page"]}/{len(book)}',
            'forward'
        )
    )

@router.message(Command(commands='continue'))
async def process_continue_command(message: Message):
    user_id = str(message.from_user.id)
    text = book[users_db[user_id]['page']]
    await message.answer(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{users_db[user_id]["page"]}/{len(book)}',
            'forward'
        )
    )

@router.message(Command(commands='bookmarks'))
async def process_bookmarks_command(message: Message):
    user_id = str(message.from_user.id)
    if users_db[user_id]["bookmarks"]:
        await message.answer(
            text=LEXICON[message.text],
            reply_markup=create_bookmarks_keyboard(
                *users_db[user_id]["bookmarks"]
            )
        )
    else:
        await message.answer(text=LEXICON['no_bookmarks'])

@router.callback_query(F.data == 'forward')
async def process_forward_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    if users_db[user_id]['page'] < len(book):
        users_db[user_id]['page'] += 1
        save_users_db()
        text = book[users_db[user_id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[user_id]["page"]}/{len(book)}',
                'forward'
            )
        )
    await callback.answer()

@router.callback_query(F.data == 'backward')
async def process_backward_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    if users_db[user_id]['page'] > 1:
        users_db[user_id]['page'] -= 1
        save_users_db()
        text = book[users_db[user_id]['page']]
        await callback.message.edit_text(
            text=text,
            reply_markup=create_pagination_keyboard(
                'backward',
                f'{users_db[user_id]["page"]}/{len(book)}',
                'forward'
            )
        )
    await callback.answer()

@router.callback_query(lambda x: '/' in x.data and x.data.replace('/', '').isdigit())
async def process_page_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    users_db[user_id]['bookmarks'].append(users_db[user_id]['page'])
    save_users_db()
    await callback.answer('Страница добавлена в закладки!')

@router.callback_query(IsDigitCallbackData())
async def process_bookmark_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    text = book[int(callback.data)]
    users_db[user_id]['page'] = int(callback.data)
    save_users_db()
    await callback.message.edit_text(
        text=text,
        reply_markup=create_pagination_keyboard(
            'backward',
            f'{users_db[user_id]["page"]}/{len(book)}',
            'forward'
        )
    )

@router.callback_query(F.data == 'edit_bookmarks')
async def process_edit_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    await callback.message.edit_text(
        text=LEXICON[callback.data],
        reply_markup=create_edit_keyboard(
            *users_db[user_id]["bookmarks"]
        )
    )

@router.callback_query(F.data == 'cancel')
async def process_cancel_press(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON['cancel_text'])

@router.callback_query(IsDelBookmarkCallbackData())
async def process_del_bookmark_press(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    users_db[user_id]['bookmarks'].remove(int(callback.data[:-3]))
    save_users_db()
    if users_db[user_id]['bookmarks']:
        await callback.message.edit_text(
            text=LEXICON['/bookmarks'],
            reply_markup=create_edit_keyboard(
                *users_db[user_id]["bookmarks"]
            )
        )
    else:
        await callback.message.edit_text(text=LEXICON['no_bookmarks'])
