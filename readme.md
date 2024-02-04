# Library Management System (LMS)

The Library Management System is a Flask-based web application for managing books, users, and loans in a library. It provides a user-friendly interface for both library administrators and users, allowing them to perform various tasks such as borrowing and returning books, adding new books, and managing user accounts.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)


## Features


### 1. **User Registration and Authentication**
   - Users can create accounts, log in, and log out. Authentication is handled securely using JWT (JSON Web Tokens).

### 2. **User Roles**
   - The system supports two user roles: regular users and administrators. Administrators have additional privileges, such as adding and editing books, managing user accounts, and viewing loan history.

### 3. **Book Management**
   - Administrators can add new books, edit book details, and delete books from the library's collection. Books can be categorized by their availability status.

### 4. **Loan Management**
   -  Users can borrow books, view their active loans, and return books. Administrators can also view all loan records in the system.

### 5. **Image Upload**
   - Books can be associated with images by uploading book covers. Images are stored in the 'uploads' directory.

### 6. **Loan Duration**
   - Different loan types are available, each with its own loan duration. 

### 7. **Search and Filter**
   - Users can search for a book by it's name, author, description.
   - Books can be filterd by availabilty, and loaned books can be filterd for late books.

### 8. **Books copies**
   - Each book has a copy, so if a book was borrowed by another user, user can borrow a copy of the same book.

### 9. **Admin Pages**
   - The website provide admin users with admin only pages, such as: managing books, viewing all loaned books with the ability to return them, viewing all customers/ users with delete functionality.
   - Admin pages are protected from normal users access. 

### 10. **API documentation**
- All API endpoints are documented with the route, required parameters, and what each API returns.
- Check the usage section for how to get to the documentation.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MyxaAkkari/LMS.git
2. Navigate to the project directory:
    ```bash
    cd LMS
    cd backend
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
4. Run the application:
    ```bash
    py app.py // for windows
    python3 app.py // for macos 

## Usage

1. Access the API documentation by visiting [http://localhost:8000/](http://localhost:8000/) in your web browser.
2. Open index.html manually or open live server in vscode [http://localhost:5500/](http://localhost:5500/) to access the website.
3. Register a new account or log in if you already have one, you can use admin account: admin@gmail.com, pwd: admin, or user account: test@gmail.com, pwd: 123.



## Contributing

Contributions are welcome! If you find a bug or have a feature request, please open an issue.

1. Fork the repository.
2. Create your feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Open a pull request.

Enjoy managing your Library collection with "LMS"!
