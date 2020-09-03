import random
import sqlite3

db = sqlite3.connect('card.s3db')
cur = db.cursor()
cur.execute(
    'CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
db.commit()


def get_luhn_number(number_string):
    number_list = [int(n) for n in number_string]
    for n in range(0, len(number_list), 2):
        a = number_list[n] * 2
        number_list[n] = a if a < 10 else a - 9
    rest = 10 - sum(number_list) % 10
    luhn_number = rest if rest != 10 else 0
    return str(luhn_number)


def generate_card_number():
    number_string = '400000' + str(random.randint(100000000, 999999999))
    return number_string + get_luhn_number(number_string)


def get_current_balance(card_number, checked=True):
    if not checked:
        checked = check_card_existence(card_number)
    if checked:
        cur.execute('SELECT balance FROM card WHERE number=:number',
                    {'number': card_number})
        query_result = cur.fetchall()
        if len(query_result) != 0:
            return query_result[0][0]
    return False


def charge_card(card_number, income, checked=True):
    if not checked:
        checked = check_card_existence(card_number)
    if checked:
        current_balance = get_current_balance(card_number)
        if current_balance is not False:
            new_user_card_balance = current_balance + income
            cur.execute('UPDATE card SET balance=:balance WHERE number=:number', {
                'balance': new_user_card_balance, 'number': card_number})
            db.commit()
            return True
    return False


def transfer_money(from_card, to_card, amount, from_card_checked=True, to_card_checked=True):
    if from_card_checked is not True:
        from_card_checked = check_card_existence(from_card)
    if to_card_checked is not True:
        to_card_checked = check_card_existence(to_card)
    if from_card_checked and to_card_checked:
        from_card_balance = get_current_balance(from_card)
        to_card_balance = get_current_balance(to_card)
        print(from_card_balance)
        print(to_card_balance)
        if from_card_balance >= 0 and to_card_balance >= 0:
            if amount > from_card_balance:
                return 'Not enough money!'
            else:
                new_from_card_balance = from_card_balance - amount
                new_to_card_balance = to_card_balance + amount
                cur.execute('UPDATE card SET balance=:balance WHERE number=:number', {
                    'balance': new_from_card_balance, 'number': from_card})
                cur.execute('UPDATE card SET balance=:balance WHERE number=:number', {
                    'balance': new_to_card_balance, 'number': to_card})
                db.commit()
                return 'Success!'
    return False


def check_card_number_is_correct(card_number):
    if len(card_number) == 16 and get_luhn_number(card_number[:-1:]) == card_number[-1::]:
        return True
    return False


def check_card_existence(card_number, number_is_correct=True):
    if not number_is_correct:
        number_is_correct = check_card_number_is_correct(card_number)
    if number_is_correct:
        cur.execute('SELECT number FROM card')
        cards_numbers = [i[0] for i in cur.fetchall()]
        if card_number in cards_numbers:
            return True
    return False


while True:
    # cur.execute('SELECT * FROM card')
    # for i in cur.fetchall():
    #     print(i)
    # print()
    # print()

    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    answer_1 = input()
    print()

    if answer_1 == '1':
        cur.execute('SELECT number FROM card')
        cards_numbers = [i[0] for i in cur.fetchall()]
        print('Your card has been created')
        print('Your card number:')

        while True:
            number = generate_card_number()
            if number not in cards_numbers:
                pin = str(random.randint(1000, 9999))
                cur.execute('INSERT INTO card VALUES (?, ?, ?, ?)',
                            (0, number, pin, 0))
                db.commit()
                break

        print(number)
        print('Your card PIN:')

        print(pin)
        print()

    elif answer_1 == '2':
        print('Enter your card number:')
        current_user_card_number = input()
        print('Enter your PIN:')
        current_user_card_pin = input()
        print()
        cur.execute('SELECT * FROM card WHERE number=:cn',
                    {'cn': current_user_card_number})
        query_result = cur.fetchall()

        if len(query_result) == 0 or query_result[0][2] != current_user_card_pin:
            print('Wrong card number or PIN!')

        else:
            print('You have successfully logged in!')

            while True:
                print()
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfer')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                answer_2 = input()
                print()

                if answer_2 == '1':
                    print(
                        f"Balance: {get_current_balance(current_user_card_number)}")

                elif answer_2 == '2':
                    print('Enter income:')
                    income = int(input())
                    if charge_card(current_user_card_number, income):
                        print('Income was added!')

                elif answer_2 == '3':
                    print('Transfer')
                    print('Enter card number:')
                    transfer_card_number = input()
                    if not check_card_number_is_correct(transfer_card_number):
                        print(
                            'Probably you made a mistake in the card number. Please try again!')
                    elif not check_card_existence(transfer_card_number):
                        print('Such a card does not exist.')
                    else:
                        print('Enter how much money you want to transfer:')
                        money_to_transfer = int(input())
                        print(transfer_money(current_user_card_number,
                                             transfer_card_number, money_to_transfer))

                elif answer_2 == '4':
                    cur.execute('DELETE FROM card WHERE number=:number',
                                {'number': current_user_card_number})
                    db.commit()
                    print('The account has been closed!')
                    break

                elif answer_2 == '5':
                    print('You have successfully logged out!')
                    break

                elif answer_2 == '0':
                    print('Bye!')
                    exit()

    elif answer_1 == '0':
        print('Bye!')
        exit()
