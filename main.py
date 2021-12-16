from itertools import product
import xlsxwriter


def get_num_value(rev_pol_not_list: list, _operators: list) -> dict:
    """
    Функция, которая возвращает количество переменных и действий.
    :param rev_pol_not_list: Принимает строку в виде ОПЗ
    :param _operators: И приоритет операторов
    :return: Словарь 'variable' : ... , 'actions'
    """

    number_of_variable = 0
    number_of_actions = 0

    for ch in rev_pol_not_list:
        if ch not in _operators:
            number_of_variable += 1
        else:
            number_of_actions += 1

    return {'variable': number_of_variable, 'action': number_of_actions}


def is_in(symbol: str, _list) -> bool:
    """
    Данная функция смотрит, есть ли символ в списке
    :param symbol: Исходный символ
    :param _list: Список
    :return: Да/Нет
    """

    if len(_list) == 0:
        return False

    for _l in _list:
        for _ in _l:
            if _ == symbol:
                return True
    return False


def create_priorities(_priorities: str) -> dict:
    """
    Данная функция нужна для создания приоритетов
    Сначала идут самые высокие операции, потом ниже.
    :param _priorities: строка с знаками операций.
    Если они разделены запятой, то операция ниже по рангу
    :return: Словарь приоритета операций
    """

    pr = {}
    _prior = _priorities.split(',')
    count = len(_prior) + 1

    for ch in _prior:  # Проход по всей строке
        if len(ch) == 1:  # Если в текущем приоритете 1 символ
            if not is_in(ch, pr.values()):
                pr.update({count: list(ch)})
                count -= 1
        elif len(ch) > 1:  # Если в текущем приоритете больше 1 символа
            a = []
            for c in ch:  # То пробегаемся по всем им
                if not is_in(c, pr.values()):
                    if c not in a:
                        a.append(c)
            pr.update({count: a})
            count -= 1
    pr.update({count: ['(', ')']})
    return pr


def get_priorities(_operator: str, _priorities: dict) -> int:
    """
    Получаем номер приоритета операции
    :param _operator: Нужный символ
    :param _priorities: Словарь приоритетов
    :return: Номер приоритета
    """

    for num, ch in _priorities.items():
        if _operator in ch:
            return num
    # print("Incorrect operator [", _operator, "]! Returned -1.")
    return -1


def remake_to_rev_pol_not(_string: str, _priorities: dict) -> list:
    """
    Фукнция для перевода выражения в обратную польскую запись.
    Возвращает строку.
    :param _string: Исходное выражение
    :param _priorities: Приоритеты операций
    :return: Выражение в ОПЗ
    """

    stack = []
    result_str = ''
    temp_str = ''
    result_list = []

    for c in _string:
        if is_in(c, _priorities.values()):
            if len(temp_str) != 0:
                result_list.append(temp_str)  # Заполняем выходной список
                temp_str = ''

        if not is_in(c, _priorities.values()):  # Если это не символ операции
            temp_str += c
            result_str += c  # То пишем его в исходную строку
        elif c == '(':  # Если это открывающая скобка
            stack.append(c)  # То добавляем ее в стек
        elif len(stack) == 0 and c != ')':  # Иначе, это символ операции. Смотрим, пуст ли стек
            stack.append(c)  # Если да, то добавляем символ без проверки
        elif len(stack) != 0 and c != ')':  # Если нет, то проверяем Тек > Верх на стеке
            last_in_stack = None if not stack else stack[-1]  # Если нет, то выводим все
            while get_priorities(c, _priorities) <= get_priorities(last_in_stack, _priorities) \
                    or (c == '/' and last_in_stack == '/') or (c == '~' and last_in_stack == '~'):
                if last_in_stack == '(':
                    break

                # result_str += stack.pop()                     # Если нужена строка, то раскомментить это
                result_list.append(stack.pop())  # Закомментить это
                last_in_stack = None if not stack else stack[-1]
            stack.append(c)
        elif c == ')':  # Если закрывающая скобка, то
            last_in_stack = None if not stack else stack[-1]  # выводим все до открывающей скобки
            while last_in_stack != '(' and last_in_stack is not None:
                # result_str += stack.pop()                     # Если нужена строка, то раскомментить это
                result_list.append(stack.pop())  # Закомментить это
                last_in_stack = None if not stack else stack[-1]
            stack.pop()

    if len(temp_str) != 0:  # Если в конце не было никаких операторов, то проверяем, есть ли операнды в Temp
        result_list.append(temp_str)  # Заполняем выходной список

    while len(stack) != 0:  # Если после прохода по строке стек
        last_in_stack = None if not stack else stack[-1]  # еще не пуст, то выводим всё, что осталось
        if last_in_stack != '(':
            # result_str += stack.pop()                     # Если нужена строка, то раскомментить это
            result_list.append(stack.pop())  # Закомментить это
        else:
            stack.pop()

    return result_list


def create_truth_table(rev_pol_not_list: list, _operators: list) -> dict:
    """
    Функция, которая создает таблицу истинности для выражения в ОПЗ
    :param rev_pol_not_list: выражение в ОПЗ
    :param _operators: операторы в этом выражении
    :return: Таблица истинности (словарь)
    """

    table = {}
    stack = []
    number_of_variable = 0
    name_of_variable = []

    for ch in rev_pol_not_list:  # Считаем количество переменных
        if ch not in _operators:  # А также запоминаем их имена
            number_of_variable += 1
            name_of_variable.append(ch)

    var_truth_list = list(product([False, True], repeat=number_of_variable))  # Создастся список кортежей
    for i in range(number_of_variable):  # Считываем по одному столбу
        temp_list = []  # Записываем в темплист
        for j in range(pow(2, number_of_variable)):
            temp_list.append(var_truth_list[j][i])
        table.update({name_of_variable[i]: temp_list})  # Добавляем в таблицу с переменной

    for ch in rev_pol_not_list:
        if ch not in _operators:
            stack.append(ch)
        else:
            if ch == '/' or ch == '~':  # Если отрицание
                if len(stack) != 0:  # Достаем из стека 1 элемент
                    var1 = stack.pop()
                    _l = table[var1]  # Получаем столбец истинности этого элемента

                    for i in range(pow(2, number_of_variable)):  # Меняем значения в этом столбце на противоположные
                        _l[i] = not _l[i]
                    stack.append(f'{ch}{var1}')
                    name_of_variable.append(f'{ch}{var1}')
                    table.update({f'{ch}{var1}': _l})  # Добавляем в таблицу истинности
            else:
                if len(stack) > 1:
                    var1 = stack.pop()
                    var2 = stack.pop()
                    _l1 = table[var1]
                    _l2 = table[var2]
                    _l = []

                    if ch == '*' or ch == '&':
                        for i in range(pow(2, number_of_variable)):  # Меняем значения в этом столбце на AND
                            _l.append(_l1[i] and _l2[i])
                    elif ch == 'v' or ch == '|':
                        for i in range(pow(2, number_of_variable)):  # Меняем значения в этом столбце на OR
                            _l.append(_l1[i] or _l2[i])
                    elif ch == '+' or '^':
                        for i in range(pow(2, number_of_variable)):  # Меняем значения в этом столбце на XOR
                            _l.append(_l1[i] ^ _l2[i])
                    stack.append(f'({var2} {ch} {var1})')
                    name_of_variable.append(f'({var2} {ch} {var1})')
                    table.update({f'({var2} {ch} {var1})': _l})  # Добавляем в таблицу истинности

    # for c in name_of_variable:
    #     print(c, ': ', table[c])
    return table


def create_excel_file(table: dict, TRUE_FALSE: bool):
    # Create a workbook and add a worksheet.
    workbook = xlsxwriter.Workbook('output/TruthTable.xlsx')
    worksheet = workbook.add_worksheet('TruthTable')
    cell_format = workbook.add_format({'italic': True, 'bold': True, 'align': 'center'})

    row = col = 0
    k = 0
    for variable, data in table.items():
        worksheet.write(row, col, variable, cell_format)
        worksheet.set_column(k, k, len(variable) + 2)
        for i in range(len(data)):
            row += 1
            if TRUE_FALSE:
                worksheet.write(row, col, data[i])
            else:
                worksheet.write(row, col, 1 if data[i] is True else 0)
        row = 0
        col += 1
        k += 1

    workbook.close()

# def main():
#     source_str = input('Enter boolean expression: ').replace(' ', '')
#     priority_str = input('Enter priorities: ')
#     choose = input('Show:\n1]True/False\n2]1/2\n->> ')
#     p = create_priorities(priority_str)
#     r = remake_to_rev_pol_not(source_str, p)
#     print("Priorities: ", p)
#     print("Reverse Pol Notation: ", r)
#     t = create_truth_table(r, list(priority_str.replace(',', '')))
#     create_excel_file(t, int(choose) - 1)
#
#
# if __name__ == '__main__':
#     main()