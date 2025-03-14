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
   
    In project we use user 'root' with password '123456' and database name 'bookstore'
   
    You can configure the database in salebook/`__init__.py` using the following syntax:
   
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://<your_database_user>:%s@localhost/<your_database_name>?charset=utf8mb4" % quote('<your_database_password>')

4. **Create the `bookstore` database**:

    Once you are inside the MySQL shell, run the following commands:

    Run file salebook/`models.py`
   
## Runing project

   Run file salebook/`index.py`

## Accout
1. **Admin:** http://`<your-localhost>`/admin
    
   Username: admin
   
   Password: 123
   
2. **Inventory Manager:** http://`<your-localhost>`/import_book
   
   Username: importer
   
   Password: 123
   
3. **Employee:** http://`<your-localhost>`/sale_book
   
   Username: employee

   Password: 123
   
4. **User:**
   Register new accout
   

