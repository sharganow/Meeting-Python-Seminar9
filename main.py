#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.
# pip install python-telegram-bot[all]

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)
from tictactoe import fill_correct_view_keyboard, search_for_a_winner, enter_sign, make_a_bot_move, bold_winner
from confection import max_candy, is_int_number, get_int_value, make_choce_bot
from ceaderbot import TOKEN

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
SELECT_GAME, QUATION_QUEUE, QUATION_SIGHN_MOVE, PLAY_CONFECTION, PLAY_TICTACTOE, TICTACTOE_OVER = range(6)
# Callback data
ONIL, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, CONFECTION, TICTACTOE = range(13)
# Состояния игры в конфеты
confection_states = [
                        'Задайте начальное количество конфет на столе',
                        'Возьмите со стола условное количество конфет'
]

guests = dict()


def cleanbattlefields(user: str) -> None:
    if user in list(guests.keys()):
        guests[user]['gameBoard'] = [[(string * 3 + column) for column in range(3)] for string in range(3)]
        guests[user]['viewkeyboard'] = [[' ' for column in range(3)] for string in range(3)]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    guester = update.message.from_user
    user = guester.name
    freedom = dict()
    if user in list(guests.keys()):
        freedom = guests.pop(user)
    guests[user] = dict()
    guests[user]['players'] = list()
    guests[user]['players'].append(user)
    guests[user]['players'].append("Бот Ерёма")
    guests[user]['SelectedGame'] = 'NotSelected'

    guests[user]['gameBoard'] = [[(string * 3 + column) for column in range(3)] for string in range(3)]
    guests[user]['viewkeyboard'] = [[' ' for column in range(3)] for string in range(3)]
    guests[user]['userSign'] = dict()
    """Send message on `/start`."""
    # Get user that sent /start and log his name

    logger.info("User %s started the conversation.", guester.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    print(logger)

    keyboard = [
        [
            InlineKeyboardButton(f"Конфеты", callback_data=str(CONFECTION)),
            InlineKeyboardButton(f"Крестики-нолики", callback_data=str(TICTACTOE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Выберите игру в которую хотите сыграть?", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return SELECT_GAME


async def select_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    guests[user]['SelectedGame'] = int(update.callback_query.data)
    match guests[user]['SelectedGame']:
        case 11:
            guests[user]['SelectedGame'] = 'confection'
        case 12:
            guests[user]['SelectedGame'] = 'tic-tac-toe'
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(f"Вы - {guests[user]['players'][0]}", callback_data=str(ONIL)),
            InlineKeyboardButton(f"Соперник - {guests[user]['players'][1]}", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await query.edit_message_text("Выберите - кто сделает первый ход?", reply_markup=reply_markup)
    return QUATION_QUEUE


async def you_bot_first(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    guests[user]['player'] = int(update.callback_query.data)
    query = update.callback_query
    await query.answer()
    match guests[user]['SelectedGame']:
        case 'confection':
            guests[user]['confection_states'] = 'Задайте начальное количество конфет на столе'
            guests[user]['action_field'] = "Подсказка"
            keyboard = [
                [
                    InlineKeyboardButton(f"{guests[user]['action_field']}", callback_data=str(CONFECTION)),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f"{guests[user]['confection_states']}: ", reply_markup=reply_markup)
            return PLAY_CONFECTION
        case 'tic-tac-toe':
            keyboard = [
                [
                    InlineKeyboardButton("X", callback_data=str(ONIL)),
                    InlineKeyboardButton("O", callback_data=str(ONE)),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text="Выберите знак отметки вашего хода: ", reply_markup=reply_markup)
            return QUATION_SIGHN_MOVE


async def x_o_sighn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    sighn = int(update.callback_query.data)
    match sighn:
        case 0:
            guests[user]['userSign'][guests[user]['players'][0]] = 'X'
            guests[user]['userSign'][guests[user]['players'][1]] = 'O'
        case _:
            guests[user]['userSign'][guests[user]['players'][1]] = 'X'
            guests[user]['userSign'][guests[user]['players'][0]] = 'O'
    # print(f'{update.callback_query.data}')
    # print(f'{update.callback_query.from_user.name}')

    query = update.callback_query
    await query.answer()
    if guests[user]['player']:
        make_a_bot_move(guests[user]['gameBoard'],
                        guests[user]['player'],
                        guests[user]['userSign'],
                        guests[user]['players'])
        vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
        guests[user]['player'] = 0
        keyboard = [
            [
                InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    else:
        vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
        keyboard = [
            [
                InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, "
                                       f"{guests[user]['players'][guests[user]['player']]}: ",
                                  reply_markup=reply_markup)
    return PLAY_TICTACTOE


async def tictactoe_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    key = int(update.callback_query.data)
    print(f'{update.callback_query.data}')
    print(f'{update.callback_query.from_user.name}')
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(guests[user]['gameBoard']) for j, k in enumerate(d) if k in range(9)]
    vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
    query = update.callback_query
    await query.answer()
    if key in freeFields:
        guests[user]['player'] = 0
        enter_sign(guests[user]['gameBoard'],
                   key,
                   guests[user]['userSign'][guests[user]['players'][guests[user]['player']]])
        vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
        match_winner = search_for_a_winner(guests[user]['gameBoard'])
        match match_winner:
            case 'No':
                freeFields = [k for i, d in enumerate(guests[user]['gameBoard']) for j, k in enumerate(d) if
                              k in range(9)]
                if len(freeFields):
                    guests[user]['player'] = 1
                    make_a_bot_move(guests[user]['gameBoard'],
                                    guests[user]['player'],
                                    guests[user]['userSign'],
                                    guests[user]['players'])
                    vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
                    match_winner = search_for_a_winner(guests[user]['gameBoard'])
                    match match_winner:
                        case 'No':
                            freeFields = [k for i, d in enumerate(guests[user]['gameBoard'])
                                          for j, k in enumerate(d) if k in range(9)]
                            if len(freeFields):
                                guests[user]['player'] = 0
                                keyboard = [
                                    [
                                        InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                                        InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                                        InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                                        InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                                        InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                                        InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                                        InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
                                    ]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                await query.edit_message_text(
                                    text=f"Ваша очередь хода, выберите свободное поле, "
                                         f"{guests[user]['players'][guests[user]['player']]}: ",
                                    reply_markup=reply_markup)
                                return PLAY_TICTACTOE
                            else:
                                keyboard = [
                                    [
                                        InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                                        InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                                        InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                                        InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                                        InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                                        InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                                        InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
                                    ],
                                    [
                                        InlineKeyboardButton("Начать новую игру?", callback_data=str(NINE)),
                                        InlineKeyboardButton("Отпустить бота", callback_data=str(TEN)),
                                    ]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                await query.edit_message_text(text=f"В игре никто не победил",
                                                              reply_markup=reply_markup)
                                cleanbattlefields(user)
                                return TICTACTOE_OVER
                        case _:
                            vkb = fill_correct_view_keyboard(bold_winner(guests[user]['gameBoard']),
                                                             guests[user]['viewkeyboard'])
                            keyboard = [
                                [
                                    InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                                    InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                                    InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
                                ],
                                [
                                    InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                                    InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                                    InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
                                ],
                                [
                                    InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                                    InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                                    InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
                                ],
                                [
                                    InlineKeyboardButton("Начать новую игру?", callback_data=str(NINE)),
                                    InlineKeyboardButton("Отпустить бота", callback_data=str(TEN)),
                                ]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await query.edit_message_text(text=f"В игре победил "
                                                               f"{guests[user]['players'][guests[user]['player']]}",
                                                          reply_markup=reply_markup)
                            cleanbattlefields(user)
                            return TICTACTOE_OVER
                else:
                    keyboard = [
                        [
                            InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                            InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                            InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
                        ],
                        [
                            InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                            InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                            InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
                        ],
                        [
                            InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                            InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                            InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
                        ],
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(NINE)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(TEN)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре никто не победил",
                                                  reply_markup=reply_markup)
                    cleanbattlefields(user)
                    return TICTACTOE_OVER
            case _:
                if match_winner == guests[user]['userSign'][guests[user]['players'][guests[user]['player']]]:
                    vkb = fill_correct_view_keyboard(bold_winner(guests[user]['gameBoard']),
                                                     guests[user]['viewkeyboard'])
                    keyboard = [
                        [
                            InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                            InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                            InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
                        ],
                        [
                            InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                            InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                            InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
                        ],
                        [
                            InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                            InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                            InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
                        ],
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(NINE)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(TEN)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил "
                                                       f"{guests[user]['players'][guests[user]['player']]}",
                                                  reply_markup=reply_markup)
                    cleanbattlefields(user)
                    return TICTACTOE_OVER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, "
                                           f"{guests[user]['players'][guests[user]['player']]}: ",
                                      reply_markup=reply_markup)
    return PLAY_TICTACTOE


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    cleanbattlefields(user)
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton(f"Вы - {guests[user]['players'][0]}", callback_data=str(ONIL)),
            InlineKeyboardButton(f"Соперник - {guests[user]['players'][1]}", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await query.edit_message_text("Игра начинается заново. Выберите - кто сделает первый ход?",
                                  reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return QUATION_QUEUE


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    freedom = dict()
    if user in list(guests.keys()):
        freedom = guests.pop(user)
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text=f"До встречи! {freedom['players'][0]}")
    return ConversationHandler.END


async def joke(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    key = int(update.callback_query.data)
    query = update.callback_query
    await query.answer()
    vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
    enter_sign(guests[user]['gameBoard'],
               key,
               search_for_a_winner(guests[user]['gameBoard']).lower())
    vkb = fill_correct_view_keyboard(guests[user]['gameBoard'], guests[user]['viewkeyboard'])
    keyboard = [
        [
            InlineKeyboardButton(f'{vkb[0][0]}', callback_data=str(ONIL)),
            InlineKeyboardButton(f'{vkb[0][1]}', callback_data=str(ONE)),
            InlineKeyboardButton(f'{vkb[0][2]}', callback_data=str(TWO)),
        ],
        [
            InlineKeyboardButton(f'{vkb[1][0]}', callback_data=str(THREE)),
            InlineKeyboardButton(f'{vkb[1][1]}', callback_data=str(FOUR)),
            InlineKeyboardButton(f'{vkb[1][2]}', callback_data=str(FIVE)),
        ],
        [
            InlineKeyboardButton(f'{vkb[2][0]}', callback_data=str(SIX)),
            InlineKeyboardButton(f'{vkb[2][1]}', callback_data=str(SEVEN)),
            InlineKeyboardButton(f'{vkb[2][2]}', callback_data=str(EIGHT)),
        ],
        [
            InlineKeyboardButton("Начать новую игру?", callback_data=str(NINE)),
            InlineKeyboardButton("Отпустить бота", callback_data=str(TEN)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Последним в игре ходил "
                                       f"{guests[user]['players'][guests[user]['player']]}",
                                  reply_markup=reply_markup)
    cleanbattlefields(user)
    return TICTACTOE_OVER


async def confection_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.callback_query.from_user.name
    query = update.callback_query
    await query.answer()
    match guests[user]['confection_states']:
        case 'Задайте начальное количество конфет на столе':
            match guests[user]['action_field']:
                case 'Подсказка':
                    guests[user]['action_field'] = 'Введите через текстовое поле целое\n значение количества конфет'
                    keyboard = [
                        [
                            InlineKeyboardButton(f"{guests[user]['action_field']}", callback_data=str(CONFECTION)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"{guests[user]['confection_states']}: ",
                                                  reply_markup=reply_markup)
                    return PLAY_CONFECTION
                case _:
                    if is_int_number(guests[user]['action_field']):
                        if guests[user]['action_field'] > max_candy:
                            guests[user]['confection_on_table'] = guests[user]['action_field']
                            guests[user]['confection_states'] = 'Возьмите со стола условное количество конфет'
                            if guests[user]['player']:
                                bot_took = make_choce_bot(guests[user]['confection_on_table'])
                                name_bot = guests[user]['players'][guests[user]['player']]
                                text = f'{name_bot} взял со стола {bot_took}'
                                guests[user]['player'] = 0
                                guests[user]['confection_on_table'] -= bot_took
                            number = guests[user]['confection_on_table']
                            guests[user]['action_field'] = f'На столе {number} конфет {text}'
                            keyboard = [
                                [
                                    InlineKeyboardButton(f"{guests[user]['action_field']}",
                                                         callback_data=str(CONFECTION)),
                                ]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await query.edit_message_text(text=f"{guests[user]['confection_states']}: ",
                                                          reply_markup=reply_markup)
                            return PLAY_CONFECTION

                    else:
                        guests[user]['action_field'] = 'Подсказка'
                        keyboard = [
                            [
                                InlineKeyboardButton(f"{guests[user]['action_field']}", callback_data=str(CONFECTION)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"{guests[user]['confection_states']}: ",
                                                      reply_markup=reply_markup)
                        return PLAY_CONFECTION
        case 'Возьмите со стола условное количество конфет':
            pass

async def key_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user.name
    match guests[user]['SelectedGame']:
        case 'confection':
            match guests[user]['confection_states']:
                case 'Задайте начальное количество конфет на столе':
                    value = get_int_value(update.message.text)
                    if is_int_number(value):
                        if max_candy < value:
                            guests[user]['action_field'] = value
                        else:
                            guests[user]['action_field'] = f'Значение должно быть более {max_candy}'
                    else:
                        guests[user]['action_field'] = 'Значение должно быть целым положительным числом'
                    keyboard = [
                        [
                            InlineKeyboardButton(f"{guests[user]['action_field']}", callback_data=str(CONFECTION)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.message.reply_text(text=f"{guests[user]['confection_states']}: ",
                                                    reply_markup=reply_markup)
                    return PLAY_CONFECTION


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_GAME: [
                CallbackQueryHandler(select_game, pattern="^" + str(CONFECTION) + "$"),
                CallbackQueryHandler(select_game, pattern="^" + str(TICTACTOE) + "$"),
            ],
            QUATION_QUEUE: [
                CallbackQueryHandler(you_bot_first, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(you_bot_first, pattern="^" + str(ONE) + "$"),
            ],
            QUATION_SIGHN_MOVE: [
                CallbackQueryHandler(x_o_sighn, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(x_o_sighn, pattern="^" + str(ONE) + "$"),
            ],
            PLAY_CONFECTION: [
                CallbackQueryHandler(confection_game, pattern="^" + str(CONFECTION) + "$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, key_message)
            ],
            PLAY_TICTACTOE: [
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(tictactoe_game, pattern="^" + str(EIGHT) + "$"),
            ],
            TICTACTOE_OVER: [
                CallbackQueryHandler(joke, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(joke, pattern="^" + str(EIGHT) + "$"),
                CallbackQueryHandler(start_over, pattern="^" + str(NINE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TEN) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # per_message = [MessageHandler(filters.TEXT & ~filters.COMMAND, echo)],
    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
