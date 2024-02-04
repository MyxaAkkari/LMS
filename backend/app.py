# Importing necessary libraries
import time, os
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_cors import CORS
from flask import Flask, jsonify, request, abort, render_template
from functools import wraps
import jwt
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from icecream import ic # Debugging tool
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'secret-secret-key' # Secret key for encoding session cookies and JWTs
admin_password = "admin" # Password for admin user authentication

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret-secret-key'

# Initialize database, bcrypt for password hashing, JWT Manager, and CORS support
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, supports_credentials=True)

# Define User model for database
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), nullable = False)
    password = db.Column(db.String(100), nullable = False)
    city = db.Column(db.String(50), nullable = False)
    age = db.Column(db.Integer, nullable = False)
    account = db.Column(db.String(10), nullable = False)
    loans = relationship('Loans', back_populates='user')

# Define Book model for database
class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable = False)
    author = db.Column(db.String(50), nullable = False)
    year_published = db.Column(db.Integer, nullable = False)
    description = db.Column(db.String(500))
    image = db.Column(db.String(255))
    loan_type = db.Column(db.Integer, nullable = False)
    status = db.Column(db.String(20), nullable = False)
    copyStatus = db.Column(db.String(20), nullable = False)
    loan_info = relationship('Loans', back_populates='book')

# Define Loan model for database
class Loans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)
    user = relationship('Users', back_populates='loans')
    book = relationship('Books', back_populates='loan_info')

# Function to check if uploaded file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate JWT
def generate_token(user_id):
    expiration = int(time.time()) + 3600  # Token expiration set to 1 hour
    payload = {'user_id': user_id, 'exp': expiration}
    token = jwt.encode(payload, 'secret-secret-key', algorithm='HS256')
    return token

# Decorator to require token authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# Route to display API documentation page
@app.route('/')
def protected_index():
    return render_template('api_documentation.html')


@app.route('/signup', methods=['POST']) # Define a route for user signup with POST method.
def signup():
    global admin_password # Reference the global variable for the admin password.
    data = request.get_json() # Parse the JSON data sent with the POST request.
    # Extract required fields from the JSON data.
    user_name = data.get('username')
    email = data.get('email')
    password = data.get('password')
    city = data.get('city')
    age = data.get('age')
    account = data.get('account')
    admin_pass = data.get('admin_pass')

    # Validate email and password presence.
    if not email or not password:
        return jsonify({'error': 'Invalid input'}), 400

    # Check if the signup request is for an admin account and validate the admin password.
    if account.lower() == 'admin':
        if admin_pass != admin_password:
            return jsonify({"error": "Admin password is incorrect"}), 400

    # Hash the user's password before storing it in the database for security.
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create a new user instance with the provided data.
    new_user = Users(username=user_name, email=email, password=hashed_password, city=city, age=age, account=account)

    # Attempt to add the new user to the database.
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        print(str(e)) # Print the error if user creation fails.
        db.session.rollback() # Rollback the session to avoid partial changes.
        return jsonify({'error': 'Failed to create user'}), 500



@app.route('/login', methods=['POST']) # Define a route for user login with POST method.
def login():
    data = request.get_json() # Parse the JSON data sent with the POST request.
    email = data.get('email') # Extract the email from the JSON data.
    password = str(data.get('password')) # Extract the password from the JSON data.

    # Query the database for a user with the provided email.
    user = Users.query.filter_by(email=email).first()
    # Check if the user exists and the password matches.
    if user and bcrypt.check_password_hash(user.password, password):
        expires = timedelta(hours=1) # Set token expiration time.
        # Generate a JWT access token for the authenticated user.
        access_token = create_access_token(identity=user.id, expires_delta=expires)
        return jsonify({'message': 'Login successful', 'access_token':access_token}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

    
@app.route('/get-user-info', methods=['GET']) # Define a route to get the authenticated user's information.
@jwt_required() # Require JWT authentication to access this endpoint.
def get_user_info():
    current_user_id = get_jwt_identity() # Retrieve the user ID from the JWT token.
    user = db.session.get(Users, current_user_id) # Query the database for the user using the user ID.

    # Check if the user exists.
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Prepare and return the user's information.
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'city': user.city,
        'age': user.age,
        'account': user.account,
    }
    return jsonify(user_info), 200


@app.route('/books', methods=['GET'])  # Define a route to list all books using the GET method.
def get_books():
    books = Books.query.all()  # Query the database to get all books.
    book_list = []  # Initialize an empty list to hold book data.
    for book in books:  # Loop through each book in the query result.
        # Append each book's details as a dictionary to the book_list.
        book_list.append({
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'description': book.description,
            'status': book.status,
            'copyStatus': book.copyStatus,
            'image': book.image,
            'loan_type': book.loan_type
        })
    return jsonify({'books': book_list}), 200  # Return the list of books as JSON.



@app.route('/books/<int:book_id>', methods=['GET'])  # Define a route to get a specific book by its ID.
@jwt_required()  # Require JWT authentication to access this route.
def get_book(book_id):
    current_user = get_jwt_identity()  # Get the current user's ID from the JWT.
    book = db.session.get(Books, book_id)  # Query the database to get the book by its ID.
    
    if not book:  # Check if the book was found.
        abort(404, description="Book not found.")  # Return a 404 error if the book is not found.
    
    # Check if the book is currently loaned by querying the Loans table.
    loan = db.session.query(Loans).filter_by(book_id=book.id, user_id=current_user).first()
    user = db.session.get(Users, current_user)  # Get the user object for the current user.
    if user.account.lower() == 'admin':  # Check if the current user is an admin.
        # Admins get information on any loan for the book, not just their own.
        loan = db.session.query(Loans).filter_by(book_id=book.id).first()

    # Prepare the book data to return, including loan information if applicable.
    book_data = {
        'id': book.id,
        'name': book.name,
        'author': book.author,
        'year_published': book.year_published,
        'description': book.description,
        'status': book.status,
        'copyStatus': book.copyStatus,
        'image': book.image,
        'loan_type': book.loan_type
    }
    if loan:  # If there is a loan on the book, add loan details to the response.
        book_data['loan_id'] = loan.id
        book_data['return_date'] = loan.return_date.strftime('%Y-%m-%d %H:%M:%S')
        # Check if the book is late for return.
        current_datetime = datetime.now()
        book_data['late'] = loan.return_date < current_datetime
    return jsonify({'book': book_data}), 200  # Return the book data as JSON.


@app.route('/books/add', methods=['POST'])  # Define a route to add a new book.
@jwt_required()  # Require JWT authentication to ensure only logged-in users can access.
def add_book():
    current_user = get_jwt_identity()  # Get the current user's ID from the JWT.
    user = Users.query.get(current_user)  # Query the database for the current user.

    if user.account.lower() != 'admin':  # Check if the user is not an admin.
        abort(403, description="Permission Denied: Only admin users can add books.")  # Restrict access if not admin.

    data = request.form  # Get the form data submitted with the request.
    # Extract book details from the form data.
    name = data.get('name')
    author = data.get('author')
    year_published = data.get('year_published')
    description = data.get('description')
    loan_type = data.get('loan_type')
    image = request.files.get('image')  # Get the image file uploaded with the form.

    if image and allowed_file(image.filename):  # Check if an image was uploaded and if it's an allowed file type.
        filename = secure_filename(image.filename)  # Sanitize the filename.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Construct the file path.
        image.save(filepath)  # Save the image file.
    else:
        filepath = None  # Set filepath to None if no image or not allowed.

    # Create a new book instance with the provided details.
    new_book = Books(
        name=name,
        author=author,
        year_published=year_published,
        description=description,
        loan_type=loan_type,
        status='available',
        copyStatus='available',
        image=filepath,
    )

    # Attempt to add the new book to the database.
    try:
        db.session.add(new_book)
        db.session.commit()
        return jsonify({'message': 'Book added successfully'}), 201  # Return success message.
    except Exception as e:  # Catch any exceptions.
        print(str(e))  # Print the exception.
        db.session.rollback()  # Rollback the transaction.
        return jsonify({'error': 'Failed to add book'}), 500  # Return error message.




@app.route('/books/edit/<int:book_id>', methods=['PUT'])  # Define a route to edit an existing book.
@jwt_required()  # Require JWT authentication to ensure only logged-in users can access.
def edit_book(book_id):
    current_user = get_jwt_identity()  # Get the current user's ID from the JWT.
    user = Users.query.get(current_user)  # Query the database for the current user.

    if user.account.lower() != 'admin':  # Check if the user is not an admin.
        abort(403, description="Permission Denied: Only admin users can edit books.")  # Restrict access if not admin.

    book = Books.query.get(book_id)  # Query the database for the book to edit.
    if not book:  # Check if the book was found.
        abort(404, description="Book not found.")  # Return a 404 error if the book is not found.

    data = request.form  # Get the form data submitted with the request.
    # Update the book's details with the form data, using existing values as defaults.
    book.name = data.get('name', book.name)
    book.author = data.get('author', book.author)
    book.year_published = data.get('year_published', book.year_published)
    book.description = data.get('description', book.description)
    book.loan_type = data.get('loan_type', book.loan_type)

    new_image = request.files.get('image')  # Get the new image file, if uploaded.
    if new_image and allowed_file(new_image.filename):  # Check if an image was uploaded and if it's allowed.
        filename = secure_filename(new_image.filename)  # Sanitize the filename.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)  # Construct the file path.
        new_image.save(filepath)  # Save the new image file.
        book.image = filepath  # Update the book's image path.

    # Attempt to commit the updates to the database.
    try:
        db.session.commit()
        return jsonify({'message': 'Book edited successfully'}), 200  # Return success message.
    except Exception as e:  # Catch any exceptions.
        print(str(e))  # Print the exception.
        db.session.rollback()  # Rollback the transaction.
        return jsonify({'error': 'Failed to edit book'}), 500  # Return error message.



@app.route('/books/delete/<int:book_id>', methods=['DELETE'])  # Define a route to delete a book.
@jwt_required()  # Require JWT authentication to ensure only logged-in users can access.
def delete_book(book_id):
    current_user = get_jwt_identity()  # Get the current user's ID from the JWT.
    user = Users.query.get(current_user)  # Query the database for the current user.

    if user.account.lower() != 'admin':  # Check if the user is not an admin.
        abort(403, description="Permission Denied: Only admin users can delete books.")  # Restrict access if not admin.

    book = Books.query.get(book_id)  # Query the database for the book to delete.
    if not book:  # Check if the book was found.
        abort(404, description="Book not found.")  # Return a 404 error if the book is not found.

    # Attempt to delete the book from the database.
    try:
        db.session.delete(book)
        db.session.commit()
        return jsonify({'message': 'Book deleted successfully'}), 200  # Return success message.
    except Exception as e:  # Catch any exceptions.
        print(str(e))  # Print the exception.
        db.session.rollback()  # Rollback the transaction.
        return jsonify({'error': 'Failed to delete book'}), 500  # Return error message.



@app.route('/loan/<int:book_id>', methods=['POST'])  # Define a route for loaning a book with the book's ID as a parameter.
@jwt_required()  # Require JWT authentication to access this route.
def loan_book(book_id):
    current_user_id = get_jwt_identity()  # Get the ID of the current user from the JWT token.

    # Check if the book is already loaned by the current user.
    existing_loan = Loans.query.filter_by(user_id=current_user_id, book_id=book_id).first()
    if existing_loan:
        return jsonify({'error': 'You have already loaned this book.'}), 400  # Return error if the book is already loaned.

    book = Books.query.filter_by(id=book_id).first()  # Retrieve the book by its ID.
    if not book:
        return jsonify({'error': 'The book does not exist.'}), 404  # Return error if the book doesn't exist.

    # Check if the book is available to be loaned.
    if book.status != 'available' and book.copyStatus != 'available':
        return jsonify({'error': 'All copies of the book are currently on loan.'}), 400

    # If the book is available, mark it as taken.
    if book.status == 'available' or book.copyStatus == 'available':
        if book.status == 'available':
            book.status = 'taken'
        else:
            book.copyStatus = 'taken'

        # Determine the return date based on the book's loan type.
        loan_duration = {1: 10, 2: 5, 3: 2}  # Define loan durations for different types.
        return_days = loan_duration.get(book.loan_type)  # Get the return days from the loan_duration dict.
        if not return_days:
            return jsonify({'error': 'Invalid loan type.'}), 400  # Return error if the loan type is invalid.

        return_date = datetime.utcnow() + timedelta(days=return_days)  # Calculate the return date.

        # Create a new loan record for the book.
        new_loan = Loans(user_id=current_user_id, book_id=book_id, loan_date=datetime.utcnow(), return_date=return_date)
        try:
            db.session.add(new_loan)  # Add the new loan to the session.
            db.session.commit()  # Commit the transaction to save the loan record.
            return jsonify({'message': 'Book loaned successfully.'}), 200  # Return success message.
        except Exception as e:
            print(str(e))  # Print any exceptions to the console.
            db.session.rollback()  # Rollback the transaction in case of failure.
            return jsonify({'error': 'Failed to loan the book.'}), 500  # Return error message.




@app.route('/return/<int:loan_id>', methods=['POST'])  # Define a route for returning a loaned book using the loan's ID.
@jwt_required()  # Require JWT authentication to ensure only authenticated users can access this route.
def return_book(loan_id):
    current_user_id = get_jwt_identity()  # Get the current user's ID from the JWT.

    loan = Loans.query.get(loan_id)  # Retrieve the loan record by its ID.
    if not loan:
        return jsonify({'error': 'Loan record not found.'}), 404  # Return error if the loan record is not found.

    # Check if the current user is authorized to return the book.
    if loan.user_id != current_user_id and Users.query.get(current_user_id).account != 'admin':
        return jsonify({'error': 'You are not authorized to return this book.'}), 403

    db.session.delete(loan)  # Delete the loan record to mark the book as returned.

    book = Books.query.get(loan.book_id)  # Retrieve the book associated with the loan.
    if not book:
        return jsonify({'error': 'Associated book not found.'}), 404  # Return error if the book is not found.

    # Update the book's status to available once returned.
    if book.copyStatus == 'taken':
        book.copyStatus = 'available'
    elif book.status == 'taken':
        book.status = 'available'

    try:
        db.session.commit()  # Commit the changes to the database.
        return jsonify({'message': 'Book returned successfully.'}), 200  # Return success message.
    except Exception as e:
        print(str(e))  # Print any exceptions to the console.
        db.session.rollback()  # Rollback the transaction in case of failure.
        return jsonify({'error': 'Failed to return the book.'}), 500  # Return error message.

    

@app.route('/user/loans', methods=['GET'])  # Define a route to fetch loans for the current user.
@jwt_required()  # Require JWT authentication to access this route.
def get_user_loans():
    current_user_id = get_jwt_identity()  # Get the current user's ID from the JWT.

    # Query the database for loans associated with the current user.
    loans = db.session.query(Loans, Books).join(Books).filter(Loans.user_id == current_user_id).all()

    loaned_books = []  # Initialize a list to store loaned book data.
    for loan, book in loans:  # Loop through each loan and associated book.
        # Append book and loan details to the loaned_books list.
        loaned_books.append({
            'loan_id': loan.id,
            'id': book.id,
            'name': book.name,
            'author': book.author,
            'year_published': book.year_published,
            'description': book.description,
            'image': book.image,
            'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
            'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S') if loan.return_date else None,
            'late': loan.return_date < datetime.now() if loan.return_date else False  # Calculate if the book is late.
        })

    return jsonify({'loans': loaned_books, 'account': Users.query.get(current_user_id).account}), 200  # Return the list of loaned books and the user's account type.



@app.route('/admin/loans', methods=['GET'])  # Define a route to get all loaned books accessible only by admins.
@jwt_required()  # Require JWT authentication to ensure only authenticated users can access this route.
def get_all_loaned_books_for_admins():
    current_user_id = get_jwt_identity()  # Retrieve the current user's ID from their JWT.

    # Verify if the current user is an admin.
    user = db.session.get(Users, current_user_id)
    if user.account.lower() != 'admin':
        # If not an admin, deny access to the route.
        return jsonify({'error': 'Permission denied. Only admin users can access this endpoint.'}), 403

    # Query all loan records.
    loaned_books = Loans.query.all()
    loaned_books_data = []  # Initialize a list to store data about loaned books.

    for loan in loaned_books:  # Iterate over each loan record.
        book = db.session.get(Books, loan.book_id)  # Get the book associated with each loan.
        if book:  # If the book exists,
            user_who_loaned = db.session.get(Users, loan.user_id)  # Get the user who loaned the book.
            # Compile loan and book information into a dict.
            loan_data = {
                'loan_id': loan.id,
                'user_id': user_who_loaned.id,
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'year_published': book.year_published,
                'description': book.description,
                'image': book.image,
                'loan_date': loan.loan_date.strftime('%Y-%m-%d %H:%M:%S'),
                'return_date': loan.return_date.strftime('%Y-%m-%d %H:%M:%S')
            }
            # Determine if the loan is late based on the current date and return date.
            if loan.return_date and loan.return_date < datetime.now():
                loan_data['late'] = True
            else:
                loan_data['late'] = False
            loaned_books_data.append(loan_data)  # Add the loan data to the list.

    return jsonify({'loans': loaned_books_data}), 200  # Return the list of all loaned books as JSON.


@app.route('/customers', methods=['GET'])  # Define a route to get information about all customers/users.
@jwt_required()  # Require JWT authentication to ensure only authenticated users can access this route.
def get_all_customers():
    # Verify if the current user is an admin to access the customer data.
    current_user = db.session.get(Users, get_jwt_identity())
    if current_user.account.lower() != 'admin':
        return jsonify({'error': 'Permission denied. Only admin users can access this endpoint.'}), 403

    customers = Users.query.all()  # Query all user records from the database.
    customers_data = []  # Initialize a list to store user data.

    for customer in customers:  # Iterate over each user record.
        # Compile user information into a dict.
        customer_data = {
            'id': customer.id,
            'username': customer.username,
            'email': customer.email,
            'city': customer.city,
            'age': customer.age,
            'account': customer.account
        }
        customers_data.append(customer_data)  # Add the user data to the list.

    return jsonify(customers_data), 200  # Return the list of all users as JSON.




@app.route('/customers/<int:user_id>', methods=['GET', 'DELETE'])  # Define a route to either get information about a specific user or delete them.
@jwt_required()  # Require JWT authentication for this route.
def get_or_delete_customer(user_id):
    # Verify admin privileges before allowing access to user data or deletion capabilities.
    current_user = db.session.get(Users, get_jwt_identity())
    if current_user.account.lower() != 'admin':
        return jsonify({'error': 'Permission denied. Only admin users can access this endpoint.'}), 403

    customer = Users.query.get(user_id)  # Retrieve the specific user by their ID.
    if not customer:
        # If the user doesn't exist, return an error.
        return jsonify({'error': 'Customer not found.'}), 404

    if request.method == 'GET':  # If the method is GET, return the user's information.
        customer_data = {
            'id': customer.id,
            'username': customer.username,
            'email': customer.email,
            'city': customer.city,
            'age': customer.age,
            'account': customer.account
        }
        return jsonify(customer_data), 200
    elif request.method == 'DELETE':  # If the method is DELETE, remove the user from the database.
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully.'}), 200



#adding books for testing
# def add_books_for_testing():
#     books_data = [
#         {
#             'name': 'The Great Gatsby',
#             'author': 'F. Scott Fitzgerald',
#             'year_published': 1925,
#             'description': 'A novel by F. Scott Fitzgerald that captures the essence of the Jazz Age in America.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 1
#         },
#         {
#             'name': 'To Kill a Mockingbird',
#             'author': 'Harper Lee',
#             'year_published': 1960,
#             'description': 'Harper Lee\'s classic novel addressing racial injustice in the American South.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 2
#         },
#         {
#             'name': '1984',
#             'author': 'George Orwell',
#             'year_published': 1949,
#             'description': 'George Orwell\'s dystopian masterpiece exploring the dangers of totalitarianism.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 2
#         },
#         {
#             'name': 'The Catcher in the Rye',
#             'author': 'J.D. Salinger',
#             'year_published': 1951,
#             'description': 'J.D. Salinger\'s iconic novel narrated by the unforgettable Holden Caulfield.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 1
#         },
#         {
#             'name': 'Pride and Prejudice',
#             'author': 'Jane Austen',
#             'year_published': 1813,
#             'description': 'Jane Austen\'s timeless tale of love and manners in early 19th-century England.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 3
#         },
#         {
#             'name': 'The Hobbit',
#             'author': 'J.R.R. Tolkien',
#             'year_published': 1937,
#             'description': 'J.R.R. Tolkien\'s enchanting adventure of Bilbo Baggins and his quest for treasure.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 3
#         },
#         {
#             'name': 'Harry Potter and the Sorcerer\'s Stone',
#             'author': 'J.K. Rowling',
#             'year_published': 1997,
#             'description': 'The first book in J.K. Rowling\'s magical series about the young wizard Harry Potter.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 1
#         },
#         {
#             'name': 'The Lord of the Rings',
#             'author': 'J.R.R. Tolkien',
#             'year_published': 1954,
#             'description': 'J.R.R. Tolkien\'s epic fantasy trilogy filled with elves, dwarves, and the One Ring.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 2
#         },
#         {
#             'name': 'The Shining',
#             'author': 'Stephen King',
#             'year_published': 1977,
#             'description': 'Stephen King\'s chilling novel about a family isolated in a haunted hotel.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 3
#         },
#         {
#             'name': 'Moby-Dick',
#             'author': 'Herman Melville',
#             'year_published': 1851,
#             'description': 'Herman Melville\'s classic tale of Captain Ahab\'s obsessive quest for the white whale.',
#             'status': 'available',
#             'copyStatus': 'available',
#             'loan_type': 1
#         },
#     ]

#     for book_info in books_data:
#         new_book = Books(**book_info)
#         db.session.add(new_book)

#     try:
#         db.session.commit()
#         print('Books added successfully for testing.')
#     except Exception as e:
#         print(f'Failed to add books for testing: {str(e)}')
#         db.session.rollback()


# This conditional ensures that the following block of code runs only if the script is executed directly,
# and not when imported as a module in another script.
if __name__ == '__main__':
    # The `app.app_context()` provides an application context, which is necessary for certain operations like accessing the database.
    with app.app_context():
        # `db.create_all()` creates all tables in the database based on the models defined earlier in the script.
        # This is idempotent, meaning it only creates tables that don't already exist.
        db.create_all()
        # Here, the function to add books for testing is commented out.
        # add_books_for_testing()
    # `app.run()` starts the Flask application with debugging enabled and on port 8000.
    app.run(debug=True, port=8000)

    