import random
import sys
import sqlite3


class Bank:
    def __init__(self):
        self.users = {}
        self.num = []
        self.card_number = ''
        self.pin = ''
        self.balance = 0

    def menu(self):
        try:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")

            n = int(input())
            print("\n")
            if n == 1:
                print("Your card has been created")
                self.card_number = Bank.create_card_num(self)
                self.pin = Bank.create_pin(self)
                print(f'Your card number:\n{self.card_number}')
                print(f'Your card PIN:\n{self.pin}')
                print("\n")
                cur.execute(f"INSERT INTO card (number, pin) VALUES ('{self.card_number}', '{self.pin}')")
                conn.commit()
                Bank.menu(self)
            elif n == 2:
                self.card_number = int(input("Enter your card number:\n"))
                self.pin = int(input("Enter your PIN:\n"))
                if Bank.check_user(self, self.card_number, self.pin):
                    print("You have successfully logged in!")
                    print("\n")
                    Bank.account_menu(self)
                Bank.menu(self)
            elif n == 0:
                print("Bye!")
                sys.exit()
        except ValueError:
            sys.exit()

    def account_menu(self):
        try:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            n = int(input())
            print("\n")
            if n == 1:
                with conn:
                    cur.execute(f"SELECT balance FROM card WHERE number = '{self.card_number}';")
                    self.balance = cur.fetchone()
                    self.balance = int(''.join(map(str, self.balance)))
                print(f'Balance: {self.balance}')
                Bank.account_menu(self)
            elif n == 2:
                Bank.add_income(self)
                Bank.account_menu(self)
            elif n == 3:
                Bank.transfer(self)
                Bank.account_menu(self)
            elif n == 4:
                cur.execute(f"DELETE FROM card WHERE number= '{self.card_number}';")
                conn.commit()
                Bank.menu(self)
            elif n == 5:
                print("You have successfully logged out!")
                Bank.menu(self)
            elif n == 0:
                print("Bye!")
                sys.exit()
        except ValueError:
            sys.exit()

    def transfer(self):
        cur.execute(f"SELECT balance FROM card WHERE number = '{self.card_number}';")
        self.balance = cur.fetchone()
        self.balance = int(''.join(map(str, self.balance)))
        print("Transfer")
        num_to_trans = int(input("Enter your card number:\n"))
        if num_to_trans == self.card_number:
            print("You can't transfer money to the same account!")
        elif Bank.pass_luth(self, list(map(int, str(num_to_trans)))):
            if num_to_trans in self.users:
                price_to_transfer = int(input("Enter how much money you want to transfer:\n"))
                if price_to_transfer >= self.balance:
                    print("Not enough money!")
                else:
                    cur.execute(f"UPDATE card SET balance = balance + {price_to_transfer} WHERE number= '{num_to_trans}';")
                    cur.execute(f"UPDATE card SET balance = balance - {price_to_transfer} WHERE number= '{self.card_number}';")
                    conn.commit()
            else:
                print("Such a card does not exist.")
        else:
            print("Probably you made a mistake in the card number.")

    def add_income(self):
        income = int(input("Enter income:\n"))
        if income >= 0:
            cur.execute(f"UPDATE card SET balance = balance + {income} WHERE number= '{self.card_number}';")
            conn.commit()
            print("Income was added!")
        else:
            Bank.add_income(self)

    def create_card_num(self):
        self.num = []
        for i in range(9):
            self.num.append(random.randint(0, 9))
        num = [4, 0, 0, 0, 0, 0]
        new_card_number = num + self.num
        control_num = Bank.create_control_num(self, new_card_number)
        new_card_number.append(control_num)
        if Bank.pass_luth(self, new_card_number):
            new_card_number = "".join(map(str, new_card_number))
            self.card_number = int(new_card_number)
        return self.card_number

    def create_control_num(self, new_card_number):
        num_copy = new_card_number.copy()
        for i in range(len(num_copy)):
            if (i + 1) % 2 == 1:
                num_copy[i] = num_copy[i] * 2
            if num_copy[i] > 9:
                num_copy[i] = num_copy[i] - 9
        sum_card = sum(num_copy)
        control_num = 10 - (sum_card % 10)
        if control_num == 10:
            control_num = 0
        return control_num

    def pass_luth(self, card_num):
        first_15_digits = card_num[:-1]
        last_digit = Bank.create_control_num(self, first_15_digits)
        if last_digit == card_num[-1]:
            return True
        return False

    def create_pin(self):
        self.num = ''
        for i in range(4):
            self.num += str(random.randint(1, 9))
        self.pin = int(self.num)
        self.users[self.card_number] = self.pin
        return self.pin

    def check_user(self, user_card_num, user_pin):
        if user_card_num not in self.users:
            print("Wrong card number or PIN!")
        elif user_pin != self.users[user_card_num]:
            print("Wrong card number or PIN!")
        else:
            return True


if __name__ == "__main__":
    new_user = Bank()
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    cur.execute("CREATE TABLE if not exists card (id INTEGER PRIMARY KEY AUTOINCREMENT, number INT, pin INT, balance INTEGER DEFAULT 0)")
    new_user.menu()