# Book Store Project

This is a Flask web application for a book store.

## Features
1. **User**
- Login/Register
- Buy books online
- Pre-order books for in-store pickup
- Add books to the shopping cart
- View personal purchase history
2. **Importer**
- Add new books to the system
- View personal book import history
3. **Employee**
- Create new invoices for in-store purchases
- Confirm orders when customers pick up pre-ordered books
 - View personal sales history
4. **Admin**
- Manage users (view, edit, delete User, Importer, Employee accounts)
- View sales and inventory reports

## Prerequisites

- Python 3.x
- Flask 3.x or later
- pip (Python package installer)
- Stripe
- Cloudinary 

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/VanThanh09/salebook
    cd salebook
    ```

2. **Create and activate a virtual environment:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

## Database Setup
1. **Install MySQL** (if you don't have it installed):

    - For Linux:

        ```sh
        sudo apt-get install mysql-server
        ```

    - For Windows: Download and install MySQL from [here](https://dev.mysql.com/downloads/installer/).

2. **Login to MySQL as root**:
   
    Open your terminal or command prompt and log in to MySQL as the root user.

    ```sh
    mysql -u root -p
    ```

    When prompted for a password, enter `123456`.
    If password isn't `123456`, you must change password database in salebook/`__init__.py`

4. **Create the `bookstore` database**:

    Once you are inside the MySQL shell, run the following commands:

    Run file salebook/`models.py`
   
## Runing project

   Run file salebook/`index.py`

## Accout
1. **Admin**
   Username: admin
   Password: 123
2. **Inventory Manager**
   Username: importer
   Password: 123
3. **Employee**
   Username: employee
   Password: 123
4. **User**
   Register new accout
   

