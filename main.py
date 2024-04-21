import re
class Invoice:
    def __init__(self, file):
        self.file = file
        self.create_invoice()

    def create_invoice(self):
        with open(self.file, "w") as f:
            pass


class InvoiceHandler:
    def __init__(self, invoice):
        self.file = invoice
        self.counter = 0
        self.amount = 0
        self.lines = []
        self.invoice = []
        self.header = ""
        self.transactions = []
        self.footer = ""

    def read_invoice_data(self):
        self.lines = self.read_invoice()
        self.amount = self.calculate_amount()
        self.counter = self.count_transactions()
        self.header = self.lines[0]
        self.transactions = self.read_transactions()
        self.footer = self.lines[-1]

    def add_transaction(self, amount, currency):
        self.write_data_to_transaction(amount, currency)
        self.write_data_to_footer()
        self.commit()

    def commit(self):
        lines=[self.header]
        lines = lines + self.transactions
        lines.append(self.footer)
        with open(self.file, "w") as f:
            f.writelines(lines)

    def write_data_to_header(self, name, surname, patronymics, address):
        self.header = f"01{name[:28]:>28}{surname[:30]:>30}{patronymics[:30]:>30}{address[:30]:>30}\n"

    def write_data_to_transaction(self, amount, currency, reserved=""):
        if self.counter < 20000:
            self.amount += int(amount)
            self.counter += 1
            transaction = f"02{str(self.counter)[:6]:>06}{amount[:12]:>012}{currency[:3]:>3}{reserved[:97]:>97}\n"
            self.transactions.append(transaction)
        else:
            return "Max transaction limit exceeded"

    def write_data_to_footer(self, reserved=""):
        total = self.amount
        footer = f"03{str(self.counter)[:6]:>06}{str(total)[:12]:>012}{reserved[:100]:>100}"
        self.footer = footer

    def read_invoice(self):
        with open(self.file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_header(self):
        return self.header

    def read_transactions(self):
        transactions = list(map(str.strip, self.lines[1:-1]))
        return [tr+"\n" for tr in transactions]

    def read_transaction(self, transaction_number):
        searched_transaction = ""
        transactions = self.read_transactions()
        for transaction in transactions:
            searched_transaction = re.search("02(\d\d\d\d\d\d)0000000(\d\d\d\d\d)([a-zA-Z]+)" ,transaction)
            print(searched_transaction.group(1))
            if transaction_number == searched_transaction.group(1).lstrip("0"):
                break
        return searched_transaction.string

    def read_footer(self):
        return self.footer

    def modify_header(self, new_data):
        header = self.header
        header_data = re.search("01\s+([a-zA-Z]+)\s+([a-zA-Z]+)\s+([a-zA-Z]+)\s+([a-zA-Z]+)", header)
        current_name = header_data.group(1)
        current_surname = header_data.group(2)
        current_patronymic = header_data.group(3)
        current_address = header_data.group(4)
        for key, value in new_data.items():
            if key == "name":
                current_name = value
            if key == "surname":
                current_surname = value
            if key == "patronymic":
                current_patronymic = value
            if key == "address":
                current_address = value
        self.header = f"01{current_name[:28]:>28}{current_surname[:30]:>30}{current_patronymic[:30]:>30}{current_address[:30]:>30}\n"
        self.write_data_to_footer()
        self.commit()
        # self.update_invoice(header, new_header)

    def modify_transaction(self, id, modyfication):
        transaction = self.read_transaction(id)
        transaction_data = re.search("02(\d\d\d\d\d\d)0000000(\d\d\d\d\d)([a-zA-Z]+)" ,transaction)
        counter = transaction_data.group(1)
        current_amount = transaction_data.group(2)
        print(type(current_amount))
        current_currency = transaction_data.group(3)
        current_reserved = ""
        for key, value in modyfication.items():
            if key == "amount":
                self.amount -= int(current_amount)
                self.amount += int(value)
                current_amount = value
            if key == "currency":
                current_currency = value
        new_transaction = f"02{str(counter)[:6]:>06}{current_amount[:12]:>012}{current_currency[:3]:>3}{current_reserved[:97]:>97}\n"
        self.transactions = [new_transaction if x == transaction else x for x in self.transactions]
        self.write_data_to_footer()
        self.commit()
        # self.update_invoice(transaction, new_transaction)

    def count_transactions(self):
        return len(self.read_transactions())

    def calculate_amount(self):
        transactions = self.read_transactions()
        amount = 0
        for transaction in transactions:
            transaction_data = re.search("02(\d\d\d\d\d\d)0000000(\d\d\d\d\d)([a-zA-Z]+)([a-zA-Z]+)", transaction)
            amount += int(transaction_data.group(2))
        return amount

    # def update_invoice(self, old_value, new_value):
    #     self.write_data_to_footer()
    #     with open(self.file, "w") as f:
    #         for line in self.lines:
    #             if line.strip() == old_value.strip():
    #                 f.write(new_value)
    #                 f.write("\n")
    #             else:
    #                 f.write(line)

    def read_value_of_specific_field(self):
        field = input("What kind of field? [(H)eader : (T)ransactions : (F)ooter]\n")
        if field == "H":
            header = self.read_header()
            value = input("What kind of Value? [(N)ame : (S)urname : (P)atronymic : (A)ddress]\n")
            if value == "N":
                print(header[3:30].strip())
                return header[3:30].strip()
            elif value == "S":
                print(header[31:60].strip())
                return header[31:60].strip()
            elif value == "P":
                print(header[61:90].strip())
                return header[61:90].strip()
            elif value == "A":
                print(header[91:].strip())
                return header[91:].strip()
            else:
                print("Wrong input")

        elif field == "T":
            transaction_number = input("What transaction are you interested in? [1..20000]\n")
            transaction = self.read_transaction(transaction_number)
            print(transaction)
            if transaction:
                value = input("What kind of Value? [(C)ounter : (A)mount : (Cu)rrency : (R)eserved]\n")
                if value == "C":
                    print(transaction[3:8].lstrip("0"))
                    return transaction[3:8].lstrip("0")
                elif value == "A":
                    print(transaction[9:20].lstrip("0"))
                    return transaction[9:20].lstrip("0")
                elif value == "Cu":
                    print(transaction[20:23])
                    return transaction[20:23]
                elif value == "R":
                    print(transaction[23:])
                    return transaction[23:]
                else:
                    print("Wrong input")

        elif field == "F":
            footer = self.read_footer()
            value = input("What kind of Value? [(T)otal Counter : (C)ontrol Sum : (R)eserved]\n")
            if value == "T":
                print(footer[3:8].lstrip("0"))
                return footer[3:8].lstrip("0")
            elif value == "C":
                print(footer[8:20].lstrip("0"))
                return footer[8:20].lstrip("0")
            elif value == "R":
                print(footer[21:])
                return footer[21:]
            else:
                print("Wrong input")
        else:
            print("Wrong input")





class GUI:
    def __init__(self):
        self.program()

    def program(self):
        print("Hello, what would you like to do?")
        print("1. Create invoice")
        print("2. Operate on existing one")
        print("3. Exit\n")
        command = input()
        while command != 4:
            if command == "1":
                print("--------------------------------")
                print("------Creating new invoice------")
                print("--------------------------------")
                invoice = Invoice(input("Pass invoice name[.txt]\n"))
                invoice_handler = InvoiceHandler(invoice.file)
                name = input("Name?")
                surname = input("Surname?")
                patronymic = input("Patronymic?")
                address = input("Address?")
                invoice_handler.write_data_to_header(name, surname, patronymic, address)
                print("--------------------------------")
                add_transaction = input("Do you want to add transaction? [y/n]\n")
                add_transaction = add_transaction.lower()
                while add_transaction == "y":
                    amount = input("Amount?")
                    currency = input("Currency?")
                    invoice_handler.write_data_to_transaction(amount, currency)
                    add_transaction = input("Do you want to add transaction? [y/n]\n")
                    add_transaction = add_transaction.lower()
                invoice_handler.write_data_to_footer()
                invoice_handler.commit()
                print("!!!Invoice created!!!")
            elif command == "2":
                print("--------------------------------")
                print("------  Opening  invoice  ------")
                print("--------------------------------")
                invoice = input("Pass name[.txt] of existing invoice\n")
                invoice_handler = InvoiceHandler(invoice)
                invoice_handler.read_invoice_data()
                print("1. Print invoice")
                print("2. Modify invoice")
                print("3. Add transaction")
                print("4. Exit")
                internal_command = input()
                while (internal_command != "4"):
                    if internal_command == "1":
                        print("--------------------------------")
                        print("------  Printing invoice  ------")
                        print("--------------------------------")

                        print("What would you like to print?")
                        print("1. Invoice")
                        print("2. Header")
                        print("3. Transaction")
                        print("4. All transactions")
                        print("5. Footer")
                        print("6. Specific field")
                        print("7. Exit")
                        printing_option = input()
                        if printing_option == "1":
                            lines = invoice_handler.read_invoice()
                            for line in lines:
                                print(line)
                        elif printing_option == "2":
                            print(invoice_handler.read_header())
                        elif printing_option == "3":
                            transaction_id = input("ID of transaction")
                            print(invoice_handler.read_transaction(transaction_id))
                        elif printing_option == "4":
                            transactions = invoice_handler.read_transactions()
                            for transaction in transactions:
                                print(transaction)
                        elif printing_option == "5":
                            print(invoice_handler.read_footer())
                        elif printing_option == "6":
                            invoice_handler.read_value_of_specific_field()
                        elif printing_option == "7":
                            print("Operation cancelled")
                        else:
                            print("Wrong input")
                    elif internal_command == "2":
                        print("Which resource do you want to modify?")
                        print("1. Header")
                        print("2. Transaction")
                        print("3. Exit")
                        modify_command = input("\n")
                        if modify_command == "1":
                            print("!!!If you dont want to modify specific field just press enter!!!")
                            name = input("Name?\n")
                            surname = input("Surname?\n")
                            address = input("Address?\n")
                            patronymic = input("Patronymic?\n")
                            modyfication = dict()
                            if name:
                                modyfication["name"] = name
                            if surname:
                                modyfication["surname"] = surname
                            if address:
                                modyfication["address"] = address
                            if patronymic:
                                modyfication["patronymic"] = patronymic
                            invoice_handler.modify_header(modyfication)
                        elif modify_command == "2":
                            print("!!!If you dont want to modify specific field just press enter!!!")
                            transaction_id = input("Transaction ID?")
                            amount = input("Amount?")
                            currency = input("Currency?")
                            modyfication = dict()
                            if amount:
                                modyfication["amount"] = amount
                            if currency:
                                modyfication["currency"] = currency
                            invoice_handler.modify_transaction(transaction_id, modyfication)
                        elif modify_command == "3":
                            print("Closing")
                        else:
                            print("Invalid command, closing.")
                    elif internal_command == "3":
                        amount = input("Amount?")
                        currency = input("Currency?")
                        invoice_handler.add_transaction(amount, currency)

                    elif internal_command == "4":
                        print("Closing invoice")
                        break
                    else:
                        print("Wrong input")

                    print("1. Print invoice")
                    print("2. Modify invoice")
                    print("3. Add transaction")
                    print("4. Exit")
                    internal_command = input()

            elif command == "3":
                print("Exiting program")
                break

            else:
                print("Wrong command")
            print("What would you like to do?")
            print("1. Create invoice")
            print("2. Operate on existing one")
            print("3. Exit")
            command = input()

if __name__ == "__main__":
    gui = GUI()
    # invoice_handler = InvoiceHandler("new2.txt")
    # print(invoice_handler.read_transactions())
    # # print(invoice_handler.modify_header(name="Maciej", surname="GREEEEEEEEEEeeeeeEEEELA"))
    # print(invoice_handler.modify_transaction(id="1", amount="600", currency="EUR"))