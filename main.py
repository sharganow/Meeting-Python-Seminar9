#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

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
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Stages
QUATION_QUEUE, QUATION_SIGHN_MOVE, PLAY_GAME, WIN_USER, WIN_BOT, DRAW = range(6)
# Callback data
ONIL, ONE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT = range(9)

gameBoard = []
viewkeyboard = []
maxScore = 10
players = []
player = int
whoMakeChoice = dict()
userSign = dict()


def fill_correct_view_keyboard() -> None:
    global gameBoard
    global viewkeyboard
    for i, d in enumerate(gameBoard):
        for j, k in enumerate(d):
            if k in range(9):
                viewkeyboard[i][j] = ' '
            else:
                viewkeyboard[i][j] = k


def search_for_a_winner(board: list) -> str:
    for i in range(3):
        string = board[i][0]
        column = board[0][i]
        for j in range(3):
            if string != board[i][j]:
                string = 'No'
            if column != board[j][i]:
                column = 'No'
        if string != 'No':
            return string
        if column != 'No':
            return column
    center = board[1][1]
    for i in range(3):
        if center != board[2 - i][i]:
            center = 'No'
    if center != 'No':
        return center
    center = board[1][1]
    for i in range(3):
        if center != board[i][i]:
            center = 'No'
    return center


def enter_sign(board: list, entr: int, sign: str):
    for i in range(3):
        for j in range(3):
            if board[i][j] == entr:
                board[i][j] = sign
                break
        else:
            continue
        break


def get_progress_score(board: list, depth: int, own_player: int, move_player: int) -> list:
    weightList = list()
    match_winner = search_for_a_winner(board)
    match match_winner:
        case 'No':
            virtualBoard = [[(board[string][column]) for column in range(3)] for string in range(3)]
            freeFields = [k for i, d in enumerate(board) for j, k in enumerate(d) if k in range(9)]
            if len(freeFields) == 0:
                weightList.append(0)
                weightList.append(0)
                return weightList
            else:
                next_move = 0 if move_player else 1
                weightValues = list()
                for i in freeFields:
                    enter_sign(virtualBoard, i, userSign[players[next_move]])
                    weightValues.append(get_progress_score(virtualBoard, depth + 1, own_player, next_move))
                    virtualBoard = [[(board[string][column]) for column in range(3)] for string in range(3)]
                maxWeight = weightValues[0][0]
                collectAllbranches = 0
                for i, d in enumerate(weightValues):
                    if abs(maxWeight) < abs(weightValues[i][0]):
                        maxWeight = weightValues[i][0]
                    collectAllbranches += weightValues[i][0] + weightValues[i][1]
                weightList.append(maxWeight)
                weightList.append(collectAllbranches)
                return weightList
        case _:
            if match_winner == userSign[players[move_player]]:
                if move_player == own_player:
                    weightList.append(maxScore - depth)
                else:
                    weightList.append(depth - maxScore)
            else:
                print('Произошел сбой маркеровки оппонента при выполнении виртуального хода')
                weightList.append(0)
            weightList.append(0)
            return weightList


def make_a_bot_move(board: list, move_player: int) -> None:
    freeFields = [k for i, d in enumerate(board) for j, k in enumerate(d) if k in range(9)]
    if len(freeFields) != 0:
        virtualBoard = [[(board[string][column]) for column in range(3)] for string in range(3)]
        weightValues = list()
        for i in freeFields:
            enter_sign(virtualBoard, i, userSign[players[move_player]])
            weightValues.append(get_progress_score(virtualBoard, 0, move_player, move_player))
            virtualBoard = [[(board[string][column]) for column in range(3)] for string in range(3)]
        maxWeight = weightValues[0][0]
        indexMaxWeight = 0
        for i, d in enumerate(weightValues):
            if maxWeight < weightValues[i][0]:
                maxWeight = weightValues[i][0]
                indexMaxWeight = i
            elif maxWeight == weightValues[i][0]:
                if weightValues[i][1] > weightValues[indexMaxWeight][1]:
                    indexMaxWeight = i
        enter_sign(board, freeFields[indexMaxWeight], userSign[players[move_player]])


#     ----------------------------------


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global players
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    players.append(user.name)
    players.append("Бот Ерёма")
    keyboard = [
        [
            InlineKeyboardButton(f"Вы - {players[0]}", callback_data=str(ONIL)),
            InlineKeyboardButton("Бот Ерёма", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Выберите - кто сделает первый ход?", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return QUATION_QUEUE


async def you_first(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    player = 0
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("X", callback_data=str(ONIL)),
            InlineKeyboardButton("O", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите знак отметки вашего хода: ", reply_markup=reply_markup)
    return QUATION_SIGHN_MOVE


async def bot_first(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    player = 1
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("X", callback_data=str(ONIL)),
            InlineKeyboardButton("O", callback_data=str(ONE)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text="Выберите знак отметки вашего хода: ", reply_markup=reply_markup)
    return QUATION_SIGHN_MOVE


async def x_sighn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    userSign[players[0]] = 'X'
    userSign[players[1]] = 'O'
    query = update.callback_query
    await query.answer()
    if player:
        # await query.edit_message_text(text=f"Сейчас ходит бот Ерёма: ",
        #                           reply_markup=reply_markup)

        make_a_bot_move(gameBoard, player)
        fill_correct_view_keyboard()
        player = 0
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                  reply_markup=reply_markup)
    return PLAY_GAME


async def o_sighn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    userSign[players[1]] = 'X'
    userSign[players[0]] = 'O'
    query = update.callback_query
    await query.answer()
    if player:
        make_a_bot_move(gameBoard, player)
        fill_correct_view_keyboard()
        player = 0
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                  reply_markup=reply_markup)
    return PLAY_GAME


async def onil(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if ONIL in freeFields:
        player = 0
        enter_sign(gameBoard, ONIL, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
                if len(freeFields):
                    player = 1
                    make_a_bot_move(gameBoard, player)
                    fill_correct_view_keyboard()
                    match_winner = search_for_a_winner(gameBoard)
                    match match_winner:
                        case 'No':
                            freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
                            if len(freeFields):
                                player = 0
                                keyboard = [
                                    [
                                        InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                        InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                        InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                        InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                        InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                                    ],
                                    [
                                        InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                        InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                        InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                                    ]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                await query.edit_message_text(
                                    text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                    reply_markup=reply_markup)
                                return PLAY_GAME
                            else:
                                keyboard = [
                                    [
                                        InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                        InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                                    ]
                                ]
                                reply_markup = InlineKeyboardMarkup(keyboard)
                                await query.edit_message_text(text=f"В игре никто не победил",
                                                              reply_markup=reply_markup)
                                return DRAW
                        case _:
                            keyboard = [
                                [
                                    InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                    InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                                ]
                            ]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                          reply_markup=reply_markup)
                            return WIN_BOT
                else:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре никто не победил",
                                                  reply_markup=reply_markup)
                    return DRAW
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def one(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if ONE in freeFields:
        player = 0
        enter_sign(gameBoard, ONE, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def two(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if TWO in freeFields:
        player = 0
        enter_sign(gameBoard, TWO, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def three(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if THREE in freeFields:
        player = 0
        enter_sign(gameBoard, THREE, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def four(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if FOUR in freeFields:
        player = 0
        enter_sign(gameBoard, FOUR, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def five(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if FIVE in freeFields:
        player = 0
        enter_sign(gameBoard, FIVE, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def six(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if SIX in freeFields:
        player = 0
        enter_sign(gameBoard, SIX, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def seven(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if SEVEN in freeFields:
        player = 0
        enter_sign(gameBoard, SEVEN, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def eight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global player
    global players
    global userSign
    global gameBoard
    global viewkeyboard
    """Show new choice of buttons"""
    freeFields = [k for i, d in enumerate(gameBoard) for j, k in enumerate(d) if k in range(9)]
    fill_correct_view_keyboard()
    query = update.callback_query
    await query.answer()
    if EIGHT in freeFields:
        player = 0
        enter_sign(gameBoard, EIGHT, userSign[players[player]])
        fill_correct_view_keyboard()
        match_winner = search_for_a_winner(gameBoard)
        match match_winner:
            case 'No':
                player = 1
                make_a_bot_move(gameBoard, player)
                fill_correct_view_keyboard()
                match_winner = search_for_a_winner(gameBoard)
                match match_winner:
                    case 'No':
                        player = 0
                        keyboard = [
                            [
                                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
                            ],
                            [
                                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(
                            text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                            reply_markup=reply_markup)
                        return PLAY_GAME

                    case _:
                        keyboard = [
                            [
                                InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                                InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                            ]
                        ]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        await query.edit_message_text(text=f"В игре победил {players[player]}",
                                                      reply_markup=reply_markup)
                        return WIN_BOT
            case _:
                if match_winner == userSign[players[player]]:
                    keyboard = [
                        [
                            InlineKeyboardButton("Начать новую игру?", callback_data=str(ONIL)),
                            InlineKeyboardButton("Отпустить бота", callback_data=str(ONE)),
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await query.edit_message_text(text=f"В игре победил {players[player]}", reply_markup=reply_markup)
                    return WIN_USER

    else:
        keyboard = [
            [
                InlineKeyboardButton(f'{viewkeyboard[0][0]}', callback_data=str(ONIL)),
                InlineKeyboardButton(f'{viewkeyboard[0][1]}', callback_data=str(ONE)),
                InlineKeyboardButton(f'{viewkeyboard[0][2]}', callback_data=str(TWO)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[1][0]}', callback_data=str(THREE)),
                InlineKeyboardButton(f'{viewkeyboard[1][1]}', callback_data=str(FOUR)),
                InlineKeyboardButton(f'{viewkeyboard[1][2]}', callback_data=str(FIVE)),
            ],
            [
                InlineKeyboardButton(f'{viewkeyboard[2][0]}', callback_data=str(SIX)),
                InlineKeyboardButton(f'{viewkeyboard[2][1]}', callback_data=str(SEVEN)),
                InlineKeyboardButton(f'{viewkeyboard[2][2]}', callback_data=str(EIGHT)),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=f"Ваша очередь хода, выберите свободное поле, {players[0]}: ",
                                      reply_markup=reply_markup)
    return PLAY_GAME


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data=str(ONE)),
            InlineKeyboardButton("2", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Start handler, Choose a route", reply_markup=reply_markup)
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    global gameBoard
    global viewkeyboard
    gameBoard = [[(string * 3 + column) for column in range(3)] for string in range(3)]
    viewkeyboard = [[' ' for column in range(3)] for string in range(3)]
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5957565943:AAEOJWjTQZc2TWUVq6unssLWcHjgueaub1Y").build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUATION_QUEUE: [
                CallbackQueryHandler(you_first, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(bot_first, pattern="^" + str(ONE) + "$"),
            ],
            QUATION_SIGHN_MOVE: [
                CallbackQueryHandler(x_sighn, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(o_sighn, pattern="^" + str(ONE) + "$"),
            ],
            PLAY_GAME: [
                CallbackQueryHandler(onil, pattern="^" + str(ONIL) + "$"),
                CallbackQueryHandler(one, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(two, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
                CallbackQueryHandler(five, pattern="^" + str(FIVE) + "$"),
                CallbackQueryHandler(six, pattern="^" + str(SIX) + "$"),
                CallbackQueryHandler(seven, pattern="^" + str(SEVEN) + "$"),
                CallbackQueryHandler(eight, pattern="^" + str(EIGHT) + "$"),
            ],
            WIN_USER: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
