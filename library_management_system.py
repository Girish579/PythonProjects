import datetime
import pickle

# Constants
BORROW_PERIOD = 7  # Days
FINE_PER_DAY = 2  # Fine for overdue books

# Book class
class Book:
    def __init__(self, name, author, cost, copies):
        self.name = name
        self.author = author
        self.cost = cost
        self.copies = copies
        self.borrow_count = 0  # Tracks how often the book has been borrowed

# User class
class User:
    def __init__(self, name, subscription_type, subscription_id, subscription_date):
        self.name = name
        self.subscription_type = subscription_type
        self.subscription_id = subscription_id
        self.subscription_date = subscription_date
        self.borrowed_books = []  # Currently borrowed books [(Book, Borrow Date)]
        self.borrowed_history = []  # History of all transactions [(Book, Borrow Date, Return Date, Fine)]

    def max_books(self):
        return 5 if self.subscription_type == "Basic" else 10

    def add_to_history(self, book, borrow_date, return_date, fine):
        self.borrowed_history.append({
            "book": book.name,
            "borrow_date": borrow_date,
            "return_date": return_date,
            "fine": fine
        })

# Library class
class Library:
    def __init__(self):
        self.books = []
        self.users = []

    def add_book(self, book):
        self.books.append(book)

    def register_user(self, user):
        self.users.append(user)

    def display_books(self):
        print("\nList of Available Books:")
        for book in self.books:
            if book.copies > 0:
                print(f"{book.name} by {book.author} - {book.copies} copies available")

    def borrow_book(self, user_id, book_name):
        user = self._find_user(user_id)
        if user and len(user.borrowed_books) < user.max_books():
            book = self._find_book(book_name)
            if book and book.copies > 0:
                book.copies -= 1
                book.borrow_count += 1  # Track borrow count
                borrow_date = datetime.datetime.now()
                user.borrowed_books.append((book, borrow_date))
                print(f"{user.name} borrowed '{book.name}'. Return by {borrow_date + datetime.timedelta(days=BORROW_PERIOD)}.")
            else:
                print("Book not available.")
        else:
            print("User not eligible to borrow more books.")

    def return_book(self, user_id, book_name):
        user = self._find_user(user_id)
        if user:
            for i, (book, borrow_date) in enumerate(user.borrowed_books):
                if book.name == book_name:
                    user.borrowed_books.pop(i)
                    book.copies += 1
                    return_date = datetime.datetime.now()
                    overdue_days = (return_date - borrow_date).days - BORROW_PERIOD
                    fine = max(overdue_days * FINE_PER_DAY, 0)
                    user.add_to_history(book, borrow_date, return_date, fine)
                    print(f"Book returned. Fine: ₹{fine}")
                    return
        print("Book not found in user's borrowed list.")

    def most_borrowed_books(self):
        print("\nMost Borrowed Books:")
        sorted_books = sorted(self.books, key=lambda x: x.borrow_count, reverse=True)
        for book in sorted_books:
            if book.borrow_count > 0:
                print(f"{book.name} by {book.author} - Borrowed {book.borrow_count} times")

    def view_borrowed_history(self, user_id):
        user = self._find_user(user_id)
        if user:
            print(f"\nBorrowed History for {user.name} (ID: {user.subscription_id}):")
            for entry in user.borrowed_history:
                print(
                    f"Book: {entry['book']}, "
                    f"Borrowed On: {entry['borrow_date'].strftime('%Y-%m-%d')}, "
                    f"Returned On: {entry['return_date'].strftime('%Y-%m-%d') if entry['return_date'] else 'Not Returned'}, "
                    f"Fine: ₹{entry['fine']}"
                )
        else:
            print("User not found.")

    def subscription_renewal_reminders(self):
        print("\nSubscription Renewal Reminders:")
        today = datetime.datetime.now()
        for user in self.users:
            expiry_date = user.subscription_date + datetime.timedelta(days=180)  # 6 months
            remaining_days = (expiry_date - today).days
            if remaining_days <= 30:
                print(f"{user.name} (ID: {user.subscription_id}) - Subscription expires in {remaining_days} days.")

    def calculate_fines(self):
        print("\nOverdue Fine Calculation:")
        today = datetime.datetime.now()
        for user in self.users:
            for book, borrow_date in user.borrowed_books:
                overdue_days = (today - borrow_date).days - BORROW_PERIOD
                if overdue_days > 0:
                    fine = overdue_days * FINE_PER_DAY
                    print(f"{user.name} has an overdue fine of ₹{fine} for '{book.name}'.")

    def save_data(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)
        print(f"Library data saved to {filename}.")

    @staticmethod
    def load_data(filename):
        try:
            with open(filename, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            print(f"No data file found. Starting with a new library.")
            return Library()

    def _find_book(self, name):
        for book in self.books:
            if book.name == name:
                return book
        return None

    def _find_user(self, user_id):
        for user in self.users:
            if user.subscription_id == user_id:
                return user
        return None

# Test the system
if __name__ == "__main__":
    # Load library data
    library = Library.load_data("library_data.pkl")

    # Add books to the library
    library.add_book(Book("Python Basics", "Girish", 500, 3))
    library.add_book(Book("Advanced Python", "Chandra", 800, 2))

    # Register users
    user1 = User("Kartikeya", "Basic", "U001", datetime.datetime(2024, 1, 1))
    user2 = User("Kaustubh", "Premium", "U002", datetime.datetime(2024, 1, 1))
    library.register_user(user1)
    library.register_user(user2)

    # Display books
    library.display_books()

    # Borrow books
    library.borrow_book("U001", "Python Basics")
    library.borrow_book("U002", "Advanced Python")

    # Return a book
    library.return_book("U001", "Python Basics")

    # View borrowed history
    library.view_borrowed_history("U001")
    library.view_borrowed_history("U002")

    # Generate reports
    library.most_borrowed_books()
    library.subscription_renewal_reminders()
    library.calculate_fines()

    # Save library data
    library.save_data("library_data.pkl")
