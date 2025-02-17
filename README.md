# Book Store Project

This is a Flask web application for a book store.

## Prerequisites

- Python 3.x
- Flask 3.x or later
- pip (Python package installer)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/VanThanh09/salebook
    cd salebook
    ```

2. Create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:

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

3. **Create the `bookstore` database**:

    Once you are inside the MySQL shell, run the following commands:

    ```sql
    CREATE DATABASE bookstore;
    ```    
