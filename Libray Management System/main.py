# main.py
from library import Library
from models import Book, Member
from utils import parse_int
from datetime import datetime
import sys

def print_menu():
    print("\n=== Library Management ===")
    print("1. Add book")
    print("2. List books")
    print("3. Search books")
    print("4. Remove book")
    print("5. Add member")
    print("6. List members")
    print("7. Remove member")
    print("8. Borrow book")
    print("9. Return book")
    print("10. List borrowed records")
    print("11. List overdue")
    print("0. Exit")

def main():
    lib = Library()
    while True:
        print_menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            isbn = input("ISBN: ").strip()
            title = input("Title: ").strip()
            author = input("Author: ").strip()
            year = parse_int(input("Year (optional): ").strip() or None)
            copies = parse_int(input("Copies: ").strip())
            if not copies or copies <= 0:
                print("Copies must be a positive integer.")
                continue
            bid = lib.add_book(isbn, title, author, year, copies)
            print(f"Book added with ID {bid}.")
        elif choice == "2":
            books = lib.list_books()
            print(f"\nTotal books: {len(books)}")
            for b in books:
                print(f"{b.id}: {b.title} by {b.author} (ISBN:{b.isbn}) — {b.copies_available}/{b.copies_total} available")
        elif choice == "3":
            q = input("Search term (title/author/isbn): ").strip()
            res = lib.search_books(q)
            if not res:
                print("No books found.")
            else:
                for b in res:
                    print(f"{b.id}: {b.title} by {b.author} (ISBN:{b.isbn}) — {b.copies_available}/{b.copies_total}")
        elif choice == "4":
            bid = parse_int(input("Book ID to remove: "))
            if not bid:
                print("Invalid ID.")
            else:
                lib.remove_book(bid)
                print("Book removed (if existed).")
        elif choice == "5":
            name = input("Member name: ").strip()
            email = input("Email: ").strip()
            phone = input("Phone (optional): ").strip() or None
            mid = lib.add_member(name, email, phone)
            print(f"Member added with ID {mid}.")
        elif choice == "6":
            members = lib.list_members()
            print(f"\nTotal members: {len(members)}")
            for m in members:
                print(f"{m.id}: {m.name} — {m.email} — joined {m.join_date}")
        elif choice == "7":
            mid = parse_int(input("Member ID to remove: "))
            if not mid:
                print("Invalid ID.")
            else:
                lib.remove_member(mid)
                print("Member removed (if existed).")
        elif choice == "8":
            book_id = parse_int(input("Book ID to borrow: "))
            member_id = parse_int(input("Member ID borrowing: "))
            days = parse_int(input("Days for loan (default 14): ").strip() or 14)
            try:
                ok = lib.borrow_book(book_id, member_id, days)
                if ok:
                    print("Borrow recorded.")
                else:
                    print("No copies available.")
            except Exception as e:
                print("Error:", e)
        elif choice == "9":
            borrow_id = parse_int(input("Borrow record ID to return: "))
            if not borrow_id:
                print("Invalid ID.")
                continue
            try:
                ok = lib.return_book(borrow_id)
                if ok:
                    print("Return processed.")
                else:
                    print("Record already returned.")
            except Exception as e:
                print("Error:", e)
        elif choice == "10":
            recs = lib.list_borrowed()
            if not recs:
                print("No borrow records.")
            else:
                for r in recs:
                    print(f"Borrow ID {r['borrow_id']}: '{r['title']}' borrowed by {r['member_name']} on {r['borrow_date']} due {r['due_date']} returned: {r['return_date']}")
        elif choice == "11":
            overdue = lib.list_overdue()
            if not overdue:
                print("No overdue records.")
            else:
                for r in overdue:
                    print(f"Borrow ID {r['borrow_id']}: '{r['title']}' borrowed by {r['member_name']} on {r['borrow_date']} due {r['due_date']}")
        elif choice == "0":
            print("Bye.")
            sys.exit(0)
        else:
            print("Invalid option, try again.")

if __name__ == "__main__":
    main()
