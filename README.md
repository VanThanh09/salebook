# Mobile Store Project

This is a Flask web application for a book store.

## Prerequisites

- Python 3.x
- Flask 3.x or later
- pip (Python package installer)

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/duyan77/mobile-store.git
    cd mobile-store
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

1. Apply the migrations:

    ```sh
    python manage.py migrate
    ```

2. Create a superuser:

    ```sh
    python manage.py createsuperuser
    ```

3. Load data:
    ```sh
    python manage.py loaddata data.json
    ```
    
## Admin User Account

- **Username:** duyan
- **Email:** anbui5948@gmail.com
- **Password:** 123

## Running the Server

1. Start the development server:

    ```sh
    python manage.py runserver
    ```

2. Open your web browser and go to `http://127.0.0.1:8000/` to see the application.

## Project Structure

- `store/urls.py`: URL routing for the store app.
- `store/views.py`: View functions for the store app.
- `store/templates/store/store.html`: Template for the store view.
- `store/templates/store/base.html`: Base template for the project.

## Usage

- Navigate to the home page to see the store.
- Use the navigation bar to explore different categories and functionalities.

## License

This project is licensed under the MIT License.# mobile-app
