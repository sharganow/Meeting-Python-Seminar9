max_candy = 28
min_candy = 1
confection = 2023


def is_int_number(value) -> bool:
    try:
        if value > 0 and value%1 == 0:
            return True
        else:
            return False
    except:
        return False


def get_int_value(value):
    try:
        value =  int(value)
        return value
    except:
        value = 'Должно быть введено положитеньное натуральное число'
        return value


def make_choce_bot(con: int) -> int:
    bot_choice = con % (max_candy + min_candy)
    if bot_choice == 0:
        bot_choice = min_candy  # тянем время - ожидаем ошибку оппонента
    return bot_choice
