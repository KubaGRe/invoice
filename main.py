import re
import os


class Invoice:
    """
    Invoice Class, responsible for creating new empty file
    """

    def __init__(self, file: str) -> None:
        """
        Constructor for Invoice class
        :param file: path to file
        """
        self.file = file
        self.create_invoice()

    def create_invoice(self) -> None:
        """
        Method creating .txt file
        """
        with open(self.file, "w") as f:
            pass


class InvoiceHandler:
    """
    InvoiceHandler class responsible for writing to and reading from invoice
    """
    def __init__(self, file) -> None:
        """
        Constructor for InvoiceHandler class
        :param file: path to file
        """
        self.file = file
        self.counter = 0
        self.amount = 0
        self.lines = []
        self.invoice = []
        self.header = ""
        self.transactions = []
        self.footer = ""
        self.currency = ["PLN", "EUR", "USD"]

    def read_invoice_data(self) -> None:
        """
        Method responsible for reading data from existing invoice
        """
        self.lines = self.read_invoice()
        self.amount = self.calculate_amount()
        self.counter = self.count_transactions()
        self.header = self.lines[0]
        self.transactions = self.read_transactions()
        self.footer = self.lines[-1]

    def add_transaction(self, amount: str, currency: str) -> None:
        """
        Method responsible for adding new transaction
        :param amount: Amount added to transaction
        :param currency: Currency [PLN, USD, EUR]
        """
        self.write_data_to_transaction(amount, currency)
        self.write_data_to_footer()
        self.commit()

    def commit(self) -> None:
        """
        Method responsible for saving changes to file and updating cache
        """
        lines = [self.header]
        lines = lines + self.transactions
        lines.append(self.footer)
        self.lines = lines
        with open(self.file, "w") as f:
            f.writelines(lines)

    def write_data_to_header(self, name: str, surname: str, patronymics: str, address: str) -> None:
        """
        Method responsible for writing data to self.header
        :param name: Name passed to invoice
        :param surname: Surname passed to invoice
        :param patronymics: Patronymics added to invoice
        :param address: Address added to invoice
        """
        self.header = f"01{name[:28]:>28}{surname[:30]:>30}{patronymics[:30]:>30}{address[:30]:>30}\n"

    def write_data_to_transaction(self, amount: str, currency: str, reserved: str = "") -> None:
        """
        MEthod responsible for writing new data to self.transactions
        :param amount: Amount
        :param currency: Currency [PLN, USD, EUR]
        :param reserved: -
        :return:
        """
        if self.counter < 20000:
            self.amount += int(amount)
            self.counter += 1
            transaction = f"02{str(self.counter)[:6]:>06}{amount[:12]:>012}{currency[:3]:>3}{reserved[:97]:>97}\n"
            self.transactions.append(transaction)
        else:
            print("Max transaction limit exceeded")

    def write_data_to_footer(self, reserved: str = "") -> None:
        """
        Method responsible for writing/updating data to footer
        :param reserved: -
        """
        total = self.amount
        footer = f"03{str(self.counter)[:6]:>06}{str(total)[:12]:>012}{reserved[:100]:>100}"
        self.footer = footer

    def read_invoice(self) -> list:
        """
        Method responsible for reading invoice. Returns it as a list of lines
        :return:
        """
        with open(self.file, 'r') as f:
            lines = f.readlines()
        return lines

    def read_header(self) -> str:
        """
        Method responsible for returning header from invoice frokm cache
        :return:
        """
        return self.header

    def read_transactions(self) -> list:
        """
        Method responsible for returning lit of transactions from invoice from cache
        :return: List of transactions
        """
        transactions = list(map(str.strip, self.lines[1:-1]))
        return [tr+"\n" for tr in transactions]

    def read_transaction(self, transaction_number: str) -> str:
        """
        Method responsible for returning one specific transaction
        :param transaction_number: ID of transaction to return
        :return: Transaction as a string
        """
        index = int(transaction_number) - 1
        return self.transactions[index]

    def read_footer(self) -> str:
        """
        Method responsible for returning footer from invoice from cache
        :return: Footer
        """
        return self.footer

    def modify_header(self, new_data: dict) -> None:
        """
        Function which takes dict and parse it to modify current string
        :param new_data: Dict with data for header to be changed to
        """
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

    def modify_transaction(self, id: str, modyfication: dict) -> None:
        """
        Method to modify transaction with specific ID
        :param id: ID of transaction
        :param modyfication: Dict with data for transaction to be changed to
        """
        transaction = self.read_transaction(id)
        transaction_data = re.search("02(\d\d\d\d\d\d)0000000(\d\d\d\d\d)([a-zA-Z]+)", transaction)
        counter = transaction_data.group(1)
        current_amount = transaction_data.group(2)
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

    def count_transactions(self) -> int:
        """
        Method to count current number of transactions
        :return: Returns current number of transactions
        """
        return len(self.read_transactions())

    def calculate_amount(self) -> int:
        """
        Method to calculate current amount
        :return: return current amount number
        """
        transactions = self.read_transactions()
        amount = 0
        for transaction in transactions:
            transaction_data = re.search("02(\d\d\d\d\d\d)0000000(\d\d\d\d\d)([a-zA-Z]+)([a-zA-Z]+)", transaction)
            amount += int(transaction_data.group(2))
        return amount

    def read_field_from_header(self) -> str:
        """
        Read specific field from heder
        :return: Return specific field from header
        """
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

    def read_field_from_transactions(self) -> str:
        """
        Read specific field from transaction
        :return: Return specific field from transaction
        """
        transaction_number = input("What transaction are you interested in? [1..20000]\n")
        transaction = self.read_transaction(transaction_number)
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

    def read_field_from_footer(self) -> str:
        """
        Read specific field from footer
        :return: Return specific field from transaction
        """
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

    def read_value_of_specific_field(self) -> None:
        """
        Method responsible for reading specific field from invoice by calling other methods
        """
        field = input("What kind of field? [(H)eader : (T)ransactions : (F)ooter]\n")
        if field == "H":
            self.read_field_from_header()
        elif field == "T":
            self.read_field_from_transactions()
        elif field == "F":
            self.read_field_from_footer()
        else:
            print("Wrong input")


class APP:
    """
    APP Class responsible for launching program and controll it
    """
    def __init__(self) -> None:
        """
        APP Class constructor
        """
        self.program()
        self.invoice_handler = None

    def create_new_invoice(self) -> None:
        """
        Method responsible for gathering data from user to create new invoice
        :return: None
        """
        print("--------------------------------")
        print("------Creating new invoice------")
        print("--------------------------------")
        invoice = Invoice(input("Pass invoice name[.txt]\n"))
        self.invoice_handler = InvoiceHandler(invoice.file)
        name = input("Name?\n")
        surname = input("Surname?\n")
        patronymic = input("Patronymic?\n")
        address = input("Address?\n")
        if not name or not surname or not patronymic:
            print("Invalid input")
            return None
        self.invoice_handler.write_data_to_header(name, surname, patronymic, address)
        print("--------------------------------")
        add_transaction = self.ask_for_transaction()
        while add_transaction == "y":
            amount = input("Amount?\n")
            currency = input("Currency?\n")
            if not amount.isdigit() or currency not in self.invoice_handler.currency:
                print("Invalid amount or currency. Transaction not added")
                add_transaction = self.ask_for_transaction()
                continue
            self.invoice_handler.write_data_to_transaction(amount, currency)
            add_transaction = self.ask_for_transaction()
        self.invoice_handler.write_data_to_footer()
        self.invoice_handler.commit()
        print("!!!Invoice created!!!")

    def ask_for_transaction(self) -> str:
        """
        Method asking user to pass [y/n] to add new transaction
        :return: [y/n]
        """
        add_transaction = input("Do you want to add transaction? [y/n]\n")
        add_transaction = add_transaction.lower()
        return add_transaction

    def print_invoice(self) -> None:
        """
        Method responsible for printing whole invoice or part of it
        :return: None
        """
        self.print_invoice_menu()
        printing_option = input("\n")
        if printing_option == "1":
            lines = self.invoice_handler.read_invoice()
            for line in lines:
                print(line)
        elif printing_option == "2":
            print(self.invoice_handler.read_header())
        elif printing_option == "3":
            if self.invoice_handler.counter == 0:
                print("There are no transactions added yet")
                return None
            transaction_id = input("ID of transaction")
            if int(transaction_id) not in range(self.invoice_handler.counter+1):
                print("There is no transaction with this ID")
                return None
            print(self.invoice_handler.read_transaction(transaction_id))
        elif printing_option == "4":
            transactions = self.invoice_handler.read_transactions()
            for transaction in transactions:
                print(transaction)
        elif printing_option == "5":
            print(self.invoice_handler.read_footer())
        elif printing_option == "6":
            self.invoice_handler.read_value_of_specific_field()
        elif printing_option == "7":
            print("Operation cancelled")
        else:
            print("Wrong input")

    def modify_invoice(self) -> None:
        """
        Method responsible for modifying invoice
        :return: None
        """
        self.print_modify_invoice_menu()
        modify_command = input("\n")
        if modify_command == "1":
            print("!!!If you dont want to modify specific field just press enter!!!")
            name = input("Name?\n")
            surname = input("Surname?\n")
            address = input("Address?\n")
            patronymic = input("Patronymic?\n")

            modification = dict()
            if name:
                modification["name"] = name
            if surname:
                modification["surname"] = surname
            if address:
                modification["address"] = address
            if patronymic:
                modification["patronymic"] = patronymic
            self.invoice_handler.modify_header(modification)
        elif modify_command == "2":
            print("!!!If you dont want to modify specific field leave it empty!!!")
            if self.invoice_handler.counter == 0:
                print("There are no transactions added yet")
                return None
            transaction_id = input("Transaction ID?")
            if int(transaction_id) not in range(self.invoice_handler.counter+1):
                print("There is no transaction with this ID")
                return None
            amount = input("Amount?")
            currency = input("Currency?")
            if not amount.isdigit() or currency not in self.invoice_handler.currency:
                print("Invalid amount or currency. Transaction not added")
                return None
            modification = dict()
            if amount:
                modification["amount"] = amount
            if currency:
                modification["currency"] = currency
            self.invoice_handler.modify_transaction(transaction_id, modification)
        elif modify_command == "3":
            print("Closing")
        else:
            print("Invalid command, closing.")

    def open_invoice(self) -> None:
        """
        Method responsible for opening existing invoice
        :return: None
        """
        print("--------------------------------")
        print("------  Opening  invoice  ------")
        print("--------------------------------")
        invoice = input("Pass name[.txt] of existing invoice\n")
        if not os.path.exists(invoice):
            print("This file does not exists")
            return None
        self.invoice_handler = InvoiceHandler(invoice)
        self.invoice_handler.read_invoice_data()
        self.print_open_invoice_menu()
        internal_command = input()
        while internal_command != "4":
            if internal_command == "1":
                self.print_invoice()
            elif internal_command == "2":
                self.modify_invoice()
            elif internal_command == "3":
                amount = input("Amount?")
                currency = input("Currency?")
                if not amount.isdigit() or currency not in self.invoice_handler.currency:
                    print("Invalid amount or currency. Transaction not added")
                    self.print_open_invoice_menu()
                    internal_command = input()
                    continue
                self.invoice_handler.add_transaction(amount, currency)
            elif internal_command == "4":
                break
            else:
                print("Wrong input")
            self.print_open_invoice_menu()
            internal_command = input()
        print("Closing invoice")

    def program(self) -> None:
        """
        Main APP method
        """
        self.print_program_menu()
        command = input()
        while command != 3:
            if command == "1":
                self.create_new_invoice()
            elif command == "2":
                self.open_invoice()
            elif command == "3":
                print("Exiting program")
                break
            else:
                print("Wrong command")
            self.print_program_menu()
            command = input()

    def print_invoice_menu(self) -> None:
        """
        Method responsible for printing Invoice Print Option menu
        """
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

    def print_modify_invoice_menu(self) -> None:
        """
        Method responsible for printing Modify Invoice Menu
        """
        print("Which resource do you want to modify?")
        print("1. Header")
        print("2. Transaction")
        print("3. Exit")

    def print_open_invoice_menu(self) -> None:
        """
        Method responsible for printing menu while opening new invoice
        """
        print("1. Print invoice")
        print("2. Modify invoice")
        print("3. Add transaction")
        print("4. Exit")

    def print_program_menu(self) -> None:
        """
        Method responsible for printing main program menu
        """
        print("Hello, what would you like to do?")
        print("1. Create invoice")
        print("2. Operate on existing one")
        print("3. Exit\n")


if __name__ == "__main__":
    app = APP()
