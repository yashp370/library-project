import mysql.connector
from datetime import date, datetime, timedelta

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="newyash"
)

cursor = db.cursor()

# Admin 
def admin_login():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password))
    admin = cursor.fetchone()

    if admin:
        print("Login successful!")
        return True
    else:
        print("Invalid credentials!")
        return False

# Add new user 
def add_user(name, email, phone, address):
    query = "INSERT INTO users (name, email, phone, address) VALUES (%s, %s, %s, %s)"
    values = (name, email, phone, address)
    cursor.execute(query, values)
    db.commit()
    print(f"User '{name}' added successfully.")

# View users
def view_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    print("Users:")
    print("ID , Name , Email , Phone , Address")
    
    for user in users:
        print(f"{user[0]} , {user[1]} , {user[2]} , {user[3]} , {user[4]}")

# Add new book
def add_book(title, author, year, Book_Number,category,available):
    query = "INSERT INTO books (title, author, year, Book_Number,category,available) VALUES (%s, %s, %s, %s,%s,%s)"
    values = (title, author, year, Book_Number,category,available)
    cursor.execute(query, values)
    db.commit()
    print(f"Book '{title}' added successfully.")

#view book
def view_books():
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    
    print("Books:")
    print("ID , Title , Author , Year , Book_Number , Category , Available")
    
    for book in books:
        
        if book[6] == 1:
            availability_status = "This book is available."
        elif book[6] == 0:
            availability_status = "This book is not available."
        else:
            availability_status = "Unknown"

        
        print(f"{book[0]} , {book[1]} , {book[2]} , {book[3]} , {book[4]} , {book[5]} , {book[6]}")
        print(availability_status)

             

# Borrow book 
def borrow_book(user_id, book_id, return_date):
    cursor.execute("SELECT available FROM books WHERE id = %s", (book_id,))
    book = cursor.fetchone()
    
    if book and book[0]:
        query = "INSERT INTO submit_date (user_id, book_id, borrow_date, return_date) VALUES (%s, %s, %s, %s)"
        values = (user_id, book_id, date.today(), return_date)
        cursor.execute(query, values)
        cursor.execute("UPDATE books SET available = FALSE WHERE id = %s", (book_id,))
        db.commit()
        print("Book borrowed successfully. Return by:", return_date)
    else:
        print("Book is not available.")
        
# Return book 
def return_book(user_id, book_id, actual_return_date):
    try:
        # Retrieve the expected return date from the database
        cursor.execute("SELECT return_date FROM submit_date WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        record = cursor.fetchone()

        if not record:
            print("No record found for the borrowed book.")
            return

        return_date = record[0]

        # Initialize fine amount
        fine = 0

        # Convert actual_return_date to a date object if passed as a string
        if isinstance(actual_return_date, str):
            actual_return_date = datetime.strptime(actual_return_date, "%Y-%m-%d").date()

        # Calculate fine if the book is returned late
        if actual_return_date > return_date:
            late_days = (actual_return_date - return_date).days
            fine = late_days * 10  # Assuming the fine is 10 RS per day
            print(f"Book is returned late by {late_days} days. Fine:RS {fine} ₹.")
        else:
            print("Book returned on time. No Fine.")

        # Update the return date and fine in the database
        query = "UPDATE submit_date SET actual_return_date = %s, fine = %s WHERE user_id = %s AND book_id = %s"
        values = (actual_return_date, fine, user_id, book_id)
        cursor.execute(query, values)

        # Update the availability of the book
        cursor.execute("UPDATE books SET available = TRUE WHERE id = %s", (book_id,))
        
        
        db.commit()
        print("Book returned successfully.")

    except mysql.connector.Error as err:
        # Handle database errors    
        print(f"Error: {err}")
        db.rollback()

# View borrowed books
def view_borrowed_books():
    query = """
    SELECT users.name, books.title, submit_date.borrow_date, submit_date.return_date, submit_date.actual_return_date, submit_date.fine
    FROM submit_date
    JOIN users ON submit_date.user_id = users.id
    JOIN books ON submit_date.book_id = books.id
    """
    cursor.execute(query)
    borrowed_books = cursor.fetchall()
    
    print("Borrowed Books:")
    print("User Name , Book Title , Borrow Date , Return Date , Actual Return Date,fine")
   
    for record in borrowed_books:
        actual_return_date = record[4] if record[4] else "Not Returned"
        print(f"{record[0]} , {record[1]} , {record[2]} , {record[3]} , {actual_return_date},{record[5]} ")

# Main Menu
def menu():
    if not admin_login():
        return

    while True:
        print("\nLibrary Management System")
        print("1. Add User")
        print("2. View Users")
        print("3. Add Book")
        print("4. View Books")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. View Borrowed Books")
        print("8. Exit")

        i = input("Enter choice: ")

        if i == '1':
            name = input("Enter user name: ")
            email = input("Enter user email: ")
            phone = input("Enter user phone: ")
            address = input("Enter user address: ")
            add_user(name, email, phone, address)

        elif i == '2':
            view_users()

        elif i == '3':
            title = input("Enter book title: ")
            author = input("Enter book author: ")
            year = int(input("Enter book year: "))
            book_number = input("Enter book number: ")
            catalogue = input("Enter book catalogue (e.g., Engineering, Physics, Chemistry, Law): ")
            available = input("Enter availability (1 for available, 0 for not available): ")
            add_book(title, author, year, book_number,catalogue,available)

        elif i == '4':
            view_books()

        elif i == '5':
            user_id = int(input("Enter user ID: "))
            book_id = int(input("Enter book ID: "))
            return_date = input("Enter return date (YYYY-MM-DD): ")
            return_date = datetime.strptime(return_date, "%Y-%m-%d").date()
            borrow_book(user_id, book_id, return_date)

        elif i == '6':
            user_id = int(input("Enter user ID: "))
            book_id = int(input("Enter book ID: "))
            actual_return_date = input("Enter actual return date (YYYY-MM-DD): ")
            return_book(user_id, book_id, actual_return_date)

        elif i == '7':
            view_borrowed_books()

        elif i == '8':
            print("Exiting...")
            print("Thanks for using our library management system!")
            print("Have a great day!")
            print("Developed by:YASH PAREKH")
            

            
            break

        else:
            print("Invalid choice.Please try again.")
            print("Please enter a number between 1 and 8.")
            

if __name__ == "__main__":
    menu()


cursor.close()
db.close()

