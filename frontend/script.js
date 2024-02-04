// Define the server URL
const MY_Server = "http://127.0.0.1:8000";
let currentBookId = null; // Initialize a variable to hold the current book ID, used later in book-related operations
let booksList = [] // Initialize an empty array to store the list of books fetched from the server

// Function to submit the login form
function submitLoginForm(event) {
    event.preventDefault(); // Prevent the default form submission behavior, which reloads the page

    const form = document.getElementById('loginForm'); // Get the login form element by its ID
    const formData = new FormData(form); // Create a new FormData object from the form, which allows us to easily access form fields

    // Convert FormData to a plain object to easily convert it to JSON later
    const formObject = {};
    formData.forEach((value, key) => { // Iterate over FormData entries
        formObject[key] = value; // Assign each form field's value to a corresponding property in the object
    });

    // Send the login data to the server using Axios, a promise-based HTTP client
    axios.post(`${MY_Server}/login`, formObject, {
        withCredentials: true, // Include credentials in the request for sessions/cookies
        headers: {
            'Content-Type': 'application/json', // Set the content type header to inform the server about the data format
        },
    })
        .then(response => {
            // Handle successful login
            console.log('Login successful');
            const token = response.data.access_token; // Extract the access token from the response
            localStorage.setItem('access_token', token); // Store the access token in the browser's local storage
            console.log('Access Token:', token);
            window.location.href = './index.html'; // Redirect the user to the home page
        })
        .catch(error => {
            // Handle login failure
            console.error('Login failed:', error.response.data); // Log the error response from the server

            // Display the error message to the user
            const errorMessageContainer = document.getElementById('errorMessage');
            errorMessageContainer.textContent = error.response.data.error;

            // Optionally clear the error message after 5 seconds
            setTimeout(() => {
                errorMessageContainer.textContent = ''; // Clear the error message
            }, 5000);
        });
}

function submitSignupForm(event) {
    event.preventDefault(); // Prevent the default form submission behavior
    debugger // Trigger a breakpoint for debugging purposes
    const form = document.getElementById('signupForm'); // Get the signup form element by its ID
    const formData = new FormData(form); // Create a new FormData object from the form

    // Convert FormData to a plain object
    const formObject = {};
    formData.forEach((value, key) => { // Iterate over FormData entries
        formObject[key] = value; // Assign each form field's value to a corresponding property in the object
    });

    // Additional logic for admin account type
    const isAdmin = formObject['account'] === 'admin'; // Check if the account type selected is 'admin'
    if (isAdmin) {
        const adminPassword = prompt('Enter Admin Password:'); // Prompt the user to enter the admin password
        if (adminPassword === null) { // Check if the user cancelled the prompt
            return; // Exit the function if the prompt was cancelled
        }
        formObject['admin_pass'] = adminPassword; // Add the admin password to the form object
    }

    // Send the signup data to the server
    axios.post(`${MY_Server}/signup`, formObject, {
        headers: {
            'Content-Type': 'application/json', // Set the content type header
        },
    })
        .then(response => {
            // Handle successful signup
            console.log('Signup successful');
            window.location.href = './login.html'; // Redirect the user to the login page
        })
        .catch(error => {
            // Handle signup failure
            console.error('Signup failed:', error.response.data); // Log the error response from the server

            // Display the error message to the user
            const errorMessageContainer = document.getElementById('errorMessage');
            errorMessageContainer.textContent = error.response.data.error;

            // Optionally clear the error message after 5 seconds
            setTimeout(() => {
                errorMessageContainer.textContent = ''; // Clear the error message
            }, 5000);
        });
}

// Function to handle logout
function logout() {
    localStorage.clear() // Clear all data stored in the browser's local storage, including the access token
    window.location.href = './login.html'; // Redirect the user to the login page
}



function renderBooks(books) {
    const cardsContainer = document.getElementById('booksContainer');
    cardsContainer.innerHTML = '';  // Clear existing cards

    // Determine if the current page is manage_book.html
    const isManageBookPage = window.location.pathname.includes('manage_book.html');
    const isLoanedBook = window.location.pathname.includes('loaned_books.html');

    // Iterate through books and create cards
    books.forEach(book => {
        const card = createBookCard(book, isManageBookPage, isLoanedBook);

        cardsContainer.appendChild(card);
    });
}





// Defines a function to create a card element for a book with dynamic content based on the page context.
function createBookCard(book, isManagePage, isLoanedBook, userWhoLoaned) {
    // Creates a new <div> element to serve as the card container.
    const card = document.createElement('div');
    // Adds the 'col' class to the card for styling purposes, assuming a grid layout.
    card.classList.add('col');

    // Specifies a placeholder image path to use when no image is provided for the book.
    const placeholderImage = '../backend/uploads/placeholder-image.jpg';

    // Determines the class to apply to the loan status text based on whether the book is late.
    const lateClass = book.late ? 'text-danger' : '';
    // Sets the text to display regarding the loan status of the book.
    const lateText = book.late ? 'Late for Return' : '';

    // Constructs the inner HTML of the card using template literals and conditional rendering.
    card.innerHTML = `
        <div class="card shadow-sm">
            <img src="${book.image ? `../backend/${book.image}` : placeholderImage}" alt="${book.name}" class="bd-placeholder-img card-img-top" width="100%" height="300">
            <div class="card-body">
                <h4 class="card-title">${book.name}</h4>
                <h6>${book.author}</h6>
                <small class="text-body-secondary">${book.year_published}</small>
                <p class="card-text">${book.description}</p>
                <p class="${lateClass}">${lateText}</p>
                ${userWhoLoaned ? `<p>User ID: ${userWhoLoaned}</p>` : ''}
                <div class="d-flex justify-content-between align-items-center">
                    <div class="btn-group">
                        ${isManagePage
            ? `
                                    <button type="button" class="btn btn-sm btn-outline-primary" onclick="openEditModal(${book.id})">Edit</button>
                                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteBook(${book.id})">Delete</button>
                                  `
            : isLoanedBook
                ? `
                                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="returnBook(${book.id})">Return</button>
                                      `
                : `
                                        <button type="button" class="btn btn-sm btn-outline-light" onclick="viewBookDetails(${book.id})">Loan</button>
                                      `
        }
                    </div>
                </div>
            </div>
        </div>
    `;

    // Attaches the book ID to the card element for easy access in event handlers.
    card.dataset.bookId = book.id;

    // Returns the fully constructed card element.
    return card;
}



// Defines a function that takes a book ID as an argument to fetch and display its details for editing.
function openEditModal(bookId) {
    // Retrieves the JWT token stored in localStorage, which is used for authentication in the API request.
    const token = localStorage.getItem('access_token');

    // Uses Axios to make a GET request to the server, fetching details of a book by its ID.
    axios.get(`${MY_Server}/books/${bookId}`, {
        withCredentials: true, // Ensures credentials are sent with the request for sessions or cookies to work.
        headers: {
            Authorization: `Bearer ${token}` // Sets the Authorization header with the Bearer token for secure access.
        }
    })
        .then(response => {
            // Extracts the book data from the server's response.
            const book = response.data.book;

            // Checks if the book object is successfully retrieved from the response before proceeding.
            if (book) {
                // Stores the current book ID globally to be used for editing submission.
                currentBookId = book.id;
                // Populates the form fields with the retrieved book details for editing.
                document.getElementById('editBookName').value = book.name;
                document.getElementById('editBookDescription').value = book.description;
                document.getElementById('editBookAuthor').value = book.author; // Populates the author field.
                document.getElementById('editBookYear').value = book.year_published; // Populates the publication year field.

                // Selects the appropriate radio button for the book's loan type based on the retrieved data.
                const loanTypeRadio = document.querySelector(`input[name="loan_type"][value="${book.loan_type}"]`);
                if (loanTypeRadio) {
                    loanTypeRadio.checked = true;
                }

                // Initializes and shows the modal window containing the edit form pre-filled with the book's details.
                const editBookModal = new bootstrap.Modal(document.getElementById('editBookModal'));
                editBookModal.show();
            } else {
                // Logs an error message if the book data is undefined, indicating a problem with the server response.
                console.error('Error: Book data is undefined.');
            }
        })
        .catch(error => {
            // Logs an error message if there's an issue fetching the book details, including network issues or server errors.
            console.error('Error fetching book details:', error.response.data);
        });
}





// Defines a function to update the information of a book.
function updateBookInfo() {
    // Retrieves the book ID stored in a global variable after opening the edit modal.
    const bookId = currentBookId;
    // Retrieves the JWT token from localStorage, used for authentication in the API request.
    const token = localStorage.getItem('access_token');

    // Collects the updated book information from the form fields.
    const updatedBook = {
        name: document.getElementById('editBookName').value,
        description: document.getElementById('editBookDescription').value,
    };

    // Checks if a new image file has been selected for upload.
    const newImageInput = document.getElementById('editBookImage');
    if (newImageInput.files.length > 0) {
        updatedBook.image = newImageInput.files[0]; // Adds the new image file to the `updatedBook` object if present.
    }

    // Initializes a new FormData object for the PUT request payload.
    const formData = new FormData();
    formData.append('name', updatedBook.name); // Appends the updated book name to the FormData.
    formData.append('description', updatedBook.description); // Appends the updated description to the FormData.
    if (updatedBook.image) {
        formData.append('image', updatedBook.image); // Appends the new image file to the FormData if present.
    }

    // Sends a PUT request to the server with the updated book information and the image file if available.
    axios.put(`${MY_Server}/books/edit/${bookId}`, formData, {
        withCredentials: true,
        headers: {
            'Content-Type': 'multipart/form-data', // Sets the content type for file upload.
            Authorization: `Bearer ${token}`, // Adds the Authorization header with the Bearer token.
        },
    })
        .then(response => {
            // Logs a message to the console upon successful book update.
            console.log('Book updated successfully:', response.data);

            // Closes the edit book modal after the update is successful.
            const editBookModal = new bootstrap.Modal(document.getElementById('editBookModal'));
            editBookModal.hide();
        })
        .catch(error => {
            // Logs an error message to the console if the update fails.
            console.error('Error updating book:', error.response.data);
        });
}




// Defines a function to handle the submission of the add book form.
function submitAddBookForm(event) {
    event.preventDefault(); // Prevents the default form submission behavior to handle the submission with JavaScript.

    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from localStorage for authentication.
    const form = document.getElementById('addBookForm'); // Gets the form element by its ID.
    const formData = new FormData(form); // Creates a FormData object from the form, useful for sending form data including files.

    // Sends an AJAX POST request to the server endpoint for adding a new book, using the FormData object.
    axios.post(`${MY_Server}/books/add`, formData, {
        withCredentials: true, // Ensures credentials/cookies are sent with the request if the request is to the same domain.
        headers: {
            'Content-Type': 'multipart/form-data', // Indicates that the request body format is FormData, necessary for file upload.
            Authorization: `Bearer ${token}`, // Includes the JWT token in the Authorization header for access control.
        },
    })
        .then(response => {
            // Logs the server's response to the console upon successful book addition.
            console.log('Add Book Response:', response.data);

            // Closes the modal dialog used for adding a book.
            const addBookModal = new bootstrap.Modal(document.getElementById('addBookModal'));
            addBookModal.hide();

            form.reset(); // Resets the form fields to their default values, clearing the input fields.
        })
        .catch(error => {
            // Logs an error message to the console if the book addition fails, e.g., due to validation errors or server issues.
            console.error('Error adding the book:', error.response.data);

        });
}



// This function handles the deletion of a book based on its ID.
function deleteBook(bookId) {
    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from local storage for authentication.

    // Confirms with the user if they really want to delete the book.
    if (confirm('Are you sure you want to delete this book?')) {
        // Sends a DELETE request to the server endpoint for deleting a specific book by its ID.
        axios.delete(`${MY_Server}/books/delete/${bookId}`, {
            withCredentials: true, // Ensures credentials/cookies are sent with the request if the request is to the same domain.
            headers: {
                Authorization: `Bearer ${token}`, // Attaches the JWT token in the Authorization header for access control.
            },
        })
            .then(response => {
                // Logs a success message to the console indicating the book was deleted successfully.
                console.log('Book deleted successfully:', response.data);

            })
            .catch(error => {
                // Logs an error message to the console if there was a problem deleting the book.
                console.error('Error deleting book:', error.response.data);

            });
    }
}



// This function filters the list of books based on a search query.
function filterBooks(query) {
    // Filters the global array of books based on whether the book's name or description includes the search query.
    // The search is case-insensitive.
    return booksList.filter(book =>
        book.name.toLowerCase().includes(query.toLowerCase()) || // Checks if the book name includes the query.
        book.description.toLowerCase().includes(query.toLowerCase()) // Checks if the book description includes the query.
    );
    // Returns an array of books that match the search query.
}



// This function is used to fetch and display details of a specific book in a modal.
function viewBookDetails(bookId) {
    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from local storage for authentication.

    // Fetches the book details using the bookId with an Axios GET request.
    axios.get(`${MY_Server}/books/${bookId}`, {
        withCredentials: true, // Ensures credentials/cookies are sent with the request if the request is to the same domain.
        headers: {
            Authorization: `Bearer ${token}` // Attaches the JWT token in the Authorization header for access control.
        }
    })
        .then(response => {
            console.log('Loan Modal Response:', response.data.book); // Logs the entire response for debugging.

            const book = response.data.book; // Extracts the book details from the response.
            currentBookId = bookId; // Updates the currentBookId with the ID of the book being viewed.

            // Checks if book details are defined before attempting to access its properties.
            if (book) {
                // Populates the modal with book details.
                document.getElementById('loanBookName').textContent = book.name;
                document.getElementById('loanBookDescription').textContent = book.description;
                document.getElementById('loanBookAuthor').textContent = `Author: ${book.author}`;
                document.getElementById('loanBookYear').textContent = `Year Published: ${book.year_published}`;

                // Determines and displays the loan duration based on the book's loan type.
                let loanDuration;
                switch (book.loan_type) {
                    case 1:
                        loanDuration = 'Maximum Loan Duration: 10 days';
                        break;
                    case 2:
                        loanDuration = 'Maximum Loan Duration: 5 days';
                        break;
                    case 3:
                        loanDuration = 'Maximum Loan Duration: 2 days';
                        break;
                    default:
                        loanDuration = 'Maximum Loan Duration: Unknown';
                        break;
                }
                document.getElementById('loanBookLoanType').textContent = loanDuration;
                document.getElementById('loanBookStatus').textContent = `Orginal: ${book.status}`;
                document.getElementById('loanBookcopyStatus').textContent = `Copy: ${book.copyStatus}`;

                // Displays the modal with the book details.
                const loanBookModal = new bootstrap.Modal(document.getElementById('loanBookModal'));
                loanBookModal.show();
            } else {
                // Logs an error if the book data is undefined.
                console.error('Error: Book data is undefined.');
            }
        })
        .catch(error => {
            // Logs an error if there's a problem fetching book details.
            console.error('Error fetching book details:', error.response.data);
        });
}



// This function is called to loan a book based on its ID.
function loanBook() {
    bookId = currentBookId; // Uses the global variable 'currentBookId' set when viewing book details, as the ID of the book to loan.
    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from local storage for authentication.

    // Makes an Axios POST request to the server endpoint to loan the specified book.
    axios.post(`${MY_Server}/loan/${bookId}`, null, { // The second parameter is 'null' because we don't need to send any body data for this request.
        withCredentials: true, // Ensures credentials/cookies are sent with the request if the request is to the same domain.
        headers: {
            Authorization: `Bearer ${token}` // Attaches the JWT token in the Authorization header for access control.
        }
    })
        .then(response => {
            console.log('Loan Book Response:', response.data); // Logs the response for debugging, indicating the loan operation was successful.

            // Handle the successful loan operation, such as displaying a success message or refreshing the page.
            const loanBookModal = new bootstrap.Modal(document.getElementById('loanBookModal')); // Retrieves the modal instance.
            loanBookModal.hide(); // Hides the modal after successfully loaning the book.
        })
        .catch(error => {
            document.getElementById('loanError').textContent = error.response.data.error; // Displays an error message in the 'loanError' element if the loan operation fails.
            console.error('Error loaning the book:', error.response.data); // Logs the error details for debugging.
        });
}




// This function is responsible for rendering the loaned books in the UI.
function renderLoanedBooks(loanedBooks) {
    const container = document.getElementById('booksContainer'); // Retrieves the HTML element where the books will be displayed.
    container.innerHTML = ''; // Clears any existing content in the container to ensure a fresh render of loaned books.

    // Iterates over each loaned book object in the 'loanedBooks' array.
    loanedBooks.forEach(book => {
        const userWhoLoaned = book.user_id; // Extracts the user ID who loaned the book. This could be used for additional context or verification.

        // Calls 'createBookCard' for each loaned book to generate its HTML card representation.
        // The function is called with parameters indicating it is not a manage page, it is a loaned book, and includes the user ID who loaned the book.
        const card = createBookCard(book, false, true, userWhoLoaned);

        // Appends the generated book card to the 'container', making it visible in the UI.
        container.appendChild(card);
    });
}




function fetchUserLoanedBooks() {
    // Retrieves the authentication token stored in the browser's local storage, which is needed for API calls requiring authentication.
    const token = localStorage.getItem('access_token');

    // Initiates a GET request to the server endpoint responsible for fetching the loaned books of the currently logged-in user.
    axios.get(`${MY_Server}/user/loans`, {
        headers: {
            Authorization: `Bearer ${token}`, // Attaches the retrieved token in the Authorization header for secure access.
        },
    })
        .then(response => {
            const account = response.data.account // Extracts the account type (e.g., admin or user) from the response data.

            // Checks if the logged-in user is an admin.
            if (account.toLowerCase() === 'admin') {
                // If the user is an admin, invokes another function to fetch all loaned books across all users.
                fetchAllLoanedBooks(token);
            } else {
                // If the user is not an admin, processes the loaned books data for the current user.
                const loanedBooks = response.data.loans; // Extracts the list of loaned books from the response.
                booksList = loanedBooks // Stores the loaned books in a global variable for further use.
                console.log(booksList); // Logs the list of loaned books to the console for debugging.
                renderLoanedBooks(loanedBooks); // Calls a function to render the fetched loaned books in the UI.
            }
        })
        .catch(error => {
            // Logs any errors encountered during the API call to the console.
            console.error('Error fetching user\'s loaned books:', error.response.data);
        });

}



// Function to fetch all loaned books for admins
function fetchAllLoanedBooks(token) {
    // Initiates a GET request to the server endpoint that provides information on all books loaned across the system. This endpoint is typically accessible only to administrators.
    axios.get(`${MY_Server}/admin/loans`, {
        headers: {
            Authorization: `Bearer ${token}`, // Includes the JWT token in the Authorization header to authenticate the request. This token is passed as a parameter to the function.
        },
    })
        .then(response => {
            const loanedBooks = response.data.loans; // Extracts the array of loaned books from the response data. Each item in the array contains details about a loaned book.
            // console.log(loanedBooks); 
            booksList = loanedBooks // Assigns the retrieved array of loaned books to a global variable `booksList` for further use within the application.
            renderLoanedBooks(loanedBooks); // Calls a function `renderLoanedBooks` with the array of loaned books as an argument, which will display these books on the webpage.
        })
        .catch(error => {
            // If the request fails (e.g., due to a network error or if the server responds with an error status), this block of code will execute.
            console.error('Error fetching all loaned books:', error.response.data); // Logs a detailed error message to the console, including information provided by the server's response.

        });

}



function returnBook(bookId) {
    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from local storage, used for authentication in the API request.
    // Initiates a GET request to fetch detailed information about a specific book based on its ID.
    axios.get(`${MY_Server}/books/${bookId}`, {
        withCredentials: true, // Ensures credentials are included in the request, necessary for sessions or authentication.
        headers: {
            Authorization: `Bearer ${token}` // Sets the Authorization header with the JWT token to authenticate the request.
        }
    })
        .then(response => {
            // Extracts the book details from the server's response.
            const book = response.data.book;

            // Populates modal elements with the retrieved book details if the book data is available.
            if (book) {
                document.getElementById('returnBookName').textContent = book.name;
                document.getElementById('returnBookDescription').textContent = book.description;
                document.getElementById('returnBookAuthor').textContent = `Author: ${book.author}`;
                document.getElementById('returnBookYear').textContent = `Year Published: ${book.year_published}`;
                document.getElementById('returnBookReturnDate').textContent = `Must return before: ${book.return_date}`;

                // Displays the modal to the user, enabling them to confirm the return of the book.
                const returnBookModal = new bootstrap.Modal(document.getElementById('returnBookModal'));
                returnBookModal.show();

                // Attaches an event listener to the "Return Book" button within the modal.
                document.getElementById('returnBookButton').addEventListener('click', () => {
                    performReturnBook(book.loan_id); // Calls a function to execute the book return process using the loan ID.
                });
            } else {
                // Logs an error if the book data is undefined, indicating a problem with the API response.
                console.error('Error: Book data is undefined.');
            }
        })
        .catch(error => {
            // Logs an error if the request fails, providing feedback on the issue encountered.
            console.error('Error fetching book details:', error.response.data);
        });
}

function performReturnBook(loanId) {
    const token = localStorage.getItem('access_token'); // Retrieves the JWT token from local storage for authentication.

    // Initiates a POST request to a specific endpoint designed to handle the return of a book, identified by its loan ID.
    axios.post(`${MY_Server}/return/${loanId}`, null, {
        withCredentials: true, // Ensures credentials are included in the request.
        headers: {
            Authorization: `Bearer ${token}` // Sets the Authorization header with the JWT token for authentication.
        }
    })
        .then(response => {
            // Handles the successful return of the book, potentially performing actions such as displaying a success message.
            console.log('Return Book Response:', response.data);
            const returnBookModal = new bootstrap.Modal(document.getElementById('returnBookModal'));
            returnBookModal.hide(); // Closes the return book modal upon successful operation.

            fetchUserLoanedBooks(); // Refreshes the list of loaned books to reflect the return.
        })
        .catch(error => {
            // Handles any errors encountered during the return process, such as authorization issues or server errors.
            console.error('Error returning the book:', error.response.data);
        });
}


function applyBookFilter(filterValue) {
    let filteredBooks = []; // Initializes an array to hold the filtered set of books.

    // Uses a switch statement to determine the filtering criteria based on the 'filterValue' parameter.
    switch (filterValue) {
        case 'all':
            // If the filter is set to 'all', no filtering is applied, and all books are included.
            filteredBooks = booksList;
            break;
        case 'available':
            // Filters the books list for those with a 'status' of 'available'.
            filteredBooks = booksList.filter(book => book.status === 'available');
            break;
        case 'taken':
            // Filters for books that are currently loaned out ('taken').
            filteredBooks = booksList.filter(book => book.status === 'taken');
            break;
        case 'true':
            // Filters for books that are marked as 'late'.
            filteredBooks = booksList.filter(book => book.late === 'true');
            break;
        default:
            // If the filter value doesn't match any case, it defaults to showing all books.
            filteredBooks = booksList;
            break;
    }
    // Calls the 'renderBooks' function with the 'filteredBooks' array to update the UI accordingly.
    renderBooks(filteredBooks);
}


// Wait for the DOM to fully load before running the script.
document.addEventListener('DOMContentLoaded', function () {
    // Retrieve the token from local storage to manage user session.
    const token = localStorage.getItem('access_token');

    // Get references to various forms on the website.
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const editBookForm = document.getElementById('editBookForm');
    const addBookForm = document.getElementById('addBookForm');

    // Attach event listeners to the signup and login forms if on their respective pages.
    if (window.location.pathname.includes('/register.html')) {
        signupForm.addEventListener('submit', submitSignupForm);
    }

    if (window.location.pathname.includes('/login.html')) {
        loginForm.addEventListener('submit', submitLoginForm);
    }

    // For pages other than login, register, and loaned_books, fetch and display books.
    if (!window.location.pathname.includes('/login.html') &&
        !window.location.pathname.includes('/register.html') &&
        !window.location.pathname.includes('/loaned_books.html')) {

        // Exclude the customers page from fetching books.
        if (!window.location.pathname.includes('/customers.html')) {
            axios.get(`${MY_Server}/books`, { withCredentials: true })
                .then(response => {
                    if (response.data && response.data.books) {
                        // Populate the global booksList and render books.
                        booksList = response.data.books;
                        renderBooks(booksList);
                    } else {
                        console.error('Invalid or missing data in server response:', response.data);
                    }
                })
                .catch(error => {
                    console.error('Error fetching books:', error);
                });
        }

        // Search functionality: filter displayed books based on the search query.
        document.getElementById('searchInput').addEventListener('input', function () {
            const searchQuery = this.value.toLowerCase();
            const filteredBooks = filterBooks(searchQuery);
            renderBooks(filteredBooks);
        });
    }

    // On the loaned_books page, fetch and display the user's loaned books.
    if (window.location.pathname.includes('/loaned_books.html')) {
        fetchUserLoanedBooks();
    }

    // Filters for books based on the dropdown selection (e.g., all, available, taken).
    document.querySelectorAll('.dropdown-menu a').forEach(item => {
        item.addEventListener('click', function (e) {
            e.preventDefault(); // Prevent the default anchor behavior.
            const filterValue = this.getAttribute('data-value');
            applyBookFilter(filterValue); // Apply the selected filter.
        });
    });

    // Redirect unauthorized users to the login page when trying to access protected pages.
    if (window.location.pathname.includes('/index.html')) {
        if (!token) {
            window.location.href = './login.html';
        }
    }

    // Manage book page: set up form submissions for adding and editing books.
    if (window.location.pathname.includes('/manage_book.html')) {
        addBookForm.addEventListener('submit', submitAddBookForm);
        editBookForm.addEventListener('submit', function (event) {
            event.preventDefault(); // Prevent default form submission.
            updateBookInfo(); // Call the function to update the book information.
        });
    }
});

