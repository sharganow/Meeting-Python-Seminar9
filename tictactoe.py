# Создайте программу для игры в 'Крестики-нолики'
# НЕОБЯЗАТЕЛЬНО Добавить игру против бота с интеллектом

import Randomizer as rnd
import time


maxScore = 10


def fill_correct_view_keyboard(gameboard: list, viewkeyboard: list) -> list:
    for i, d in enumerate(gameboard):
        for j, k in enumerate(d):
            if k in range(9):
                viewkeyboard[i][j] = ' '
            else:
                viewkeyboard[i][j] = k
    return viewkeyboard


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


def enter_sign(board: list, entr: int, sign: str) -> None:
    for i in range(3):
        for j in range(3):
            if board[i][j] == entr:
                board[i][j] = sign
                break
        else:
            continue
        break


def get_progress_score(board: list, depth: int, own_player: int, move_player: int, usersign: dict, players: list) -> list:
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
                    enter_sign(virtualBoard, i, usersign[players[next_move]])
                    weightValues.append(get_progress_score(virtualBoard, depth + 1, own_player, next_move, usersign, players))
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
            if match_winner == usersign[players[move_player]]:
                if move_player == own_player:
                    weightList.append(maxScore - depth)
                else:
                    weightList.append(depth - maxScore)
            else:
                print('Произошел сбой маркеровки оппонента при выполнении виртуального хода')
                weightList.append(0)
            weightList.append(0)
            return weightList


def make_a_bot_move(board: list, move_player: int, usersign: dict, players: list) -> None:
    freeFields = [k for i, d in enumerate(board) for j, k in enumerate(d) if k in range(9)]
    if len(freeFields) != 0:
        virtualBoard = [[(board[string][column]) for column in range(3)] for string in range(3)]
        weightValues = list()
        for i in freeFields:
            enter_sign(virtualBoard, i, usersign[players[move_player]])
            weightValues.append(get_progress_score(virtualBoard, 0, move_player, move_player, usersign, players))
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
        enter_sign(board, freeFields[indexMaxWeight], usersign[players[move_player]])
