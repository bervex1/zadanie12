import pickle
from datetime import datetime, timedelta
from collections import UserDict


class Field:
    def __init__(self, value=None):
        self._value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.validate(new_value)
        self._value = new_value

    def validate(self, value):
        pass


class Name(Field):
    pass


class Phone(Field):
    def validate(self, value):
        if not value.isdigit() or len(value) != 9:
            raise ValueError("Invalid phone number. It should contain 9 digits.")


class Birthday(Field):
    def validate(self, value):
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")


class Record:
    def __init__(self, name_value, birthday_value=None):
        self.name = Name(name_value)
        self.birthday = Birthday(birthday_value) if birthday_value else None
        self.phones = []

    def add_phone(self, phone_value):
        phone = Phone(phone_value)
        self.phones.append(phone)

    def remove_phone(self, phone_value):
        for phone in self.phones:
            if phone.value == phone_value:
                self.phones.remove(phone)
                break

    def edit_phone(self, old_phone_value, new_phone_value):
        for phone in self.phones:
            if phone.value == old_phone_value:
                phone.value = new_phone_value
                break

    def days_to_birthday(self):
        if self.birthday:
            today = datetime.now().date()
            next_birthday = datetime(today.year, self.birthday.value.month, self.birthday.value.day).date()
            if today > next_birthday:
                next_birthday = datetime(today.year + 1, self.birthday.value.month, self.birthday.value.day).date()
            return (next_birthday - today).days
        return None

    def __str__(self):
        phones_str = ', '.join(str(phone) for phone in self.phones)
        birthday_str = f", Birthday: {self.birthday.value}" if self.birthday else ""
        return f"Name: {self.name}{birthday_str}, Phones: {phones_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def search_records(self, criteria):
        results = []
        for record in self.data.values():
            match = True
            for field, value in criteria.items():
                if field == 'name' and record.name.value != value:
                    match = False
                    break
                elif field == 'phone':
                    phone_match = any(phone.value == value for phone in record.phones)
                    if not phone_match:
                        match = False
                        break
            if match:
                results.append(record)
        return results

    def __iter__(self):
        return iter(self.data.values())

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, 'rb') as file:
                self.data = pickle.load(file)
        except FileNotFoundError:
            print("File not found. Creating a new address book.")
            self.data = {}


def main():
    address_book = AddressBook()

    # Load address book from file if it exists
    address_book.load_from_file("address_book.pkl")

    while True:
        command = input("Enter a command: ").lower()

        if command == "hello":
            print("How can I help you?")
        elif command.startswith("add"):
            _, name, *args = command.split()
            if name not in address_book.data:
                phones = [arg for arg in args if arg.isdigit()]
                birthday = [arg for arg in args if not arg.isdigit()]
                record = Record(name, birthday[0] if birthday else None)
                for phone in phones:
                    record.add_phone(phone)
                address_book.add_record(record)
                print(f"Contact {name} with phone {phones} added.")
            else:
                print(f"Contact {name} already exists. Use 'edit' to modify.")
        elif command.startswith("edit"):
            _, name, old_phone, new_phone = command.split()
            if name in address_book.data:
                record = address_book.data[name]
                record.edit_phone(old_phone, new_phone)
                print(f"Phone number for {name} changed to {new_phone}.")
            else:
                print(f"Contact {name} not found.")
        elif command.startswith("search"):
            _, field, value = command.split()
            criteria = {field: value}
            results = address_book.search_records(criteria)
            if results:
                for result in results:
                    print(result)
            else:
                print("No matching contacts found.")
        elif command == "show all":
            for record in address_book:
                print(record)
        elif command == "save":
            address_book.save_to_file("address_book.pkl")
            print("Address book saved successfully.")
        elif command in ["good bye", "close", "exit"]:
            address_book.save_to_file("address_book.pkl")
            print("Address book saved. Good bye!")
            break
        else:
            print("Invalid command. Please try again.")


if __name__ == "__main__":
    main()
