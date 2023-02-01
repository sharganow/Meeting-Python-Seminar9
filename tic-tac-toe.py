# Создайте программу для игры в 'Крестики-нолики'
# НЕОБЯЗАТЕЛЬНО Добавить игру против бота с интеллектом

import Randomizer as rnd
import time

gameBoard = []
maxScore = 10
players = []
whoMakeChoice = dict()
userSign = dict()


def get_user_name(plr: int) -> str:
    name = input(f'Введите имя игрока №{plr}: ')
    return name


def choice_sign_to_play(plrs: list, hmch: dict):
    for plr in plrs:
        while True:
            ch = input(f'Выберите персональный символ отметки хода для игрока - {plr}: ')
            if len(ch) == 1:
                if ch not in hmch.values():
                    hmch[plr] = ch
                    break
                else:
                    print('Этот символ уже занят')
            else:
                print('Символ должен состоять из одного знака')


def showBoard(board: list):
    for i in range(len(board)):
        print(f'  {board[i][0]} | {board[i][1]} | {board[i][2]}')
        if i < len(board) - 1:
            print(f' ---|---|--- ')


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
    else:
        print('Выбранная ячейка занята')


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


def make_a_custom_move(board: list, move_player: int) -> int:
    freeFields = [k for i, d in enumerate(board) for j, k in enumerate(d) if k in range(9)]
    if len(freeFields) != 0:
        move = None
        while True:
            move = int(input(f'Ход производит {players[move_player]}, выберите поле: '))
            if move in freeFields:
                break
            else:
                print('Выбор должен быть сделан из следующих значений: ', end='')
                print(*freeFields)
        enter_sign(board, move, userSign[players[move_player]])
        showBoard(board)
        match_winner = search_for_a_winner(board)
        match match_winner:
            case 'No':
                return 1
            case _:
                if match_winner == userSign[players[move_player]]:
                    print(f'Игра окончена, победил {players[move_player]}!')
                else:
                    print('Произошел сбой маркеровки победителя, Игра окончена неожиданностью')
                return 0
    else:
        print(f'Игра закончена - ничья')
        return 0


def make_a_bot_move(board: list, move_player: int) -> int:
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
        print(f'Ход производит {players[move_player]}: ')
        enter_sign(board, freeFields[indexMaxWeight], userSign[players[move_player]])
        showBoard(board)
        match_winner = search_for_a_winner(board)
        match match_winner:
            case 'No':
                return 1
            case _:
                if match_winner == userSign[players[move_player]]:
                    print(f'Игра окончена, победил {players[move_player]}!')
                else:
                    print('Произошел сбой маркеровки победителя, Игра окончена неожиданностью')
                return 0
    else:
        print(f'Игра закончена - ничья')
        return 0


def make_move(f, board: list, move_player: int) -> int:
    return f(board, move_player)


def choice_of_decision_algorithm(plrs: list, hmch: dict):
    for plr in plrs:
        while True:
            ch = input(f'Выберите метод принятия решения для игрока - {plr}\n'
                       f'\t - если игрок играет сам, то введите текст \'сам\',\n'
                       f'\t - если машина играет за него, то введите\'бот\': ')
            match ch.lower():
                case 'сам':
                    hmch[plr] = make_a_custom_move
                    break
                case 'бот':
                    hmch[plr] = make_a_bot_move
                    break
                case _:
                    print('Повторите попытку внимательнее')


gameBoard = [[(string * 3 + column) for column in range(3)] for string in range(3)]
players = [get_user_name(i) for i in range(1, 3)]
choice_of_decision_algorithm(players, whoMakeChoice)
choice_sign_to_play(players, userSign)
showBoard(gameBoard)

time.sleep(rnd.RandInt(0, 10) / 10)
player = rnd.RandInt(0, 1)
print(f'По результату жеребьёвки первым ходит {players[player]}')

while True:
    if make_move(whoMakeChoice[players[player]], gameBoard, player):
        player = 0 if player else 1
    else:
        break
