from collections import UserDict, defaultdict
from datetime import datetime, timedelta
import os
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def __init__(self, birthday):
        super().__init__(birthday)

class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone):
        if not phone.isdigit() or len(phone) != 10:
            print(f"Wrong phone number {phone}. Format - 10 digit.")
            #use empty phone number
            #phone = ""
        super().__init__(phone)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = ""

    def add_birthday(self, birthday):
        try:
            # перевірка відповідності формату
            datetime.strptime(birthday, "%d.%m.%Y")
            self.birthday = birthday
            print("Birthday added.")
        except ValueError:
            print("Only format DD.MM.YYYY")

    
    def show_birthday(self):
        return self.birthday


    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                self.phones.remove(i)
                return

    def edit_phone(self, old_phone, new_phone):
        if not old_phone.isdigit() or len(old_phone) != 10:
            print(f"Wrong phone number {old_phone}. It must contain only digits and have a length of 10.")
            return
        if not new_phone.isdigit() or len(new_phone) != 10:
            print(f"Wrong phone number {new_phone}. It must contain only digits and have a length of 10.")
            return
        for i in self.phones:
            if i.value == old_phone:
                i.value = new_phone
                print("Contact updated.")
                return

    def find_phone(self, phone):
        for i in self.phones:
            if i.value == phone:
                return i.value

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            self.data.pop(name)
    
    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            pickle.dump(self.data, file)

    def load_from_file(self, filename):
        try:
            with open(filename, "rb") as file:
                file_size = os.path.getsize(filename)
                if file_size > 0:
                    self.data = pickle.load(file)
                else:
                    print(f"File {filename} is empty. Create your Address book.")
        except FileNotFoundError:
            # якщо файл відсутній - пустий словник
            self.data = {}

def get_birthdays_list(users):
    birthday_dict = defaultdict()
    
    data_today = datetime.now()
    for num_user in users:
        name = num_user["name"]
        birthday = num_user["birthday"].date()  
        birthday_this_year = birthday.replace(year = data_today.year)

        day_of_week_today = data_today.weekday()
        
        data_today_friday = data_today + timedelta(days = 4 - day_of_week_today)
        
        #якщо буде кінець року, то +1 рік допоможе отримати правильний результат
        if birthday_this_year < data_today_friday.date():
            birthday_this_year = birthday.replace(year = data_today.year + 1)
    
        delta_days = (birthday_this_year - data_today_friday.date()).days

        #потрібно відфільтрувати з різницею в днях тиждень+субота+неділля поточного тижня
        if delta_days < 8:
            #якщо субота поточного тижня чи неділля чи понеділок - обєднуємо в понеділок
            week_day = "Monday" if delta_days < 4 else birthday_this_year.strftime("%A")
            if birthday_dict.get(week_day):
                birthday_dict[week_day].append(name)
            else:
                birthday_dict[week_day] = [name]
    #використовуємо сортування, щоб отримали по дням тижня
    for day in sorted(birthday_dict.keys(), key=lambda x: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'].index(x)):
        print(f"{day}: {", ".join(birthday_dict[day])}")

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    
    # назва файлу для збереження
    filename = "address_book_data.bin"

    # Створення нової адресної книги
    book = AddressBook()
    book.load_from_file(filename)

    print("Welcome to the assistant bot!")
    print("""
          HELP:
          hello => Hi from bot
          add name number => new contact with phone number
          change name number => change phone number
          phone name => show phone
          all => show all contacts
          add-birthday name birthday DD.MM.YYYY  => add birthday
          show-birthday name  => show birthday
          birthdays  => show comming birthdays
          close or exit
          """)
    
    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            name, phone = args                 
            name_contact = Record(name)
            name_contact.add_phone(phone)
            book.add_record(name_contact)
            print("Contact added.")
        elif command == "change":
            name, phone = args
            name_contact = book.find(name)
            name_contact.edit_phone(name_contact.phones[0].value, phone)            
        elif command == "all":
            for name, record in book.data.items():
                print(record)
        elif command == "phone":
            name = args[0]
            name_contact = book.find(name)
            found_phone = name_contact.find_phone(name_contact.phones[0].value)
            print(f"{name_contact.name}'s phone number: {found_phone}")
        elif command == "add-birthday":
            name, birthday = args
            name_contact = book.find(name)
            name_contact.add_birthday(birthday)
        elif command == "show-birthday":
            name = args[0]
            name_contact = book.find(name)
            date_birthday = name_contact.show_birthday()
            print(f"{name_contact.name}: date of birthday {date_birthday}")
        elif command == "birthdays":
            users = []
            my_dict = {}
            for name in book.data.values():  
                if name.birthday:
                    my_dict["name"] = name.name.value
                    my_dict["birthday"] = datetime.strptime(name.birthday, "%d.%m.%Y")
                    users.append(my_dict)
                    my_dict = {} 
            get_birthdays_list(users)     
        else:
            print("Wrong command.")

    # зберігаємо в файл
    book.save_to_file(filename)


if __name__ == "__main__":
    main()