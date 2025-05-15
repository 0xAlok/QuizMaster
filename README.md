# Flask Quiz Application

This is a web application built with Flask for creating and taking quizzes.

## Project Structure

```
.
├── app.py              # Main application entry point
├── create_db.py        # Script to initialize the database
├── requirements.txt    # Python dependencies
├── wsgi.py             # WSGI entry point for deployment
├── app/                # Main application package
│   ├── __init__.py     # Core application configuration and setup
│   ├── controllers/    # Route handlers (views)
│   │   ├── admin.py
│   │   ├── api.py
│   │   ├── auth.py
│   │   ├── forms.py
│   │   └── user.py
│   ├── models/         # Database models
│   │   ├── __init__.py
│   │   ├── chapter.py
│   │   ├── question.py
│   │   ├── quiz.py
│   │   ├── score.py
│   │   ├── subject.py
│   │   └── user.py
│   ├── static/         # Static files (CSS, JS, images)
│   │   └── css/
│   │       └── style.css
│   └── templates/      # HTML templates
│       ├── base.html
│       ├── admin/
│       ├── auth/
│       └── user/
└── instance/           # Instance folder (e.g., for database file)
```

## Features

*   User registration and login
*   Admin dashboard for managing subjects, chapters, quizzes, questions, and users.
*   User dashboard to view available subjects and quizzes.
*   Quiz taking functionality.
*   Quiz result display and history.

## Technologies Used

*   Python
*   Flask
*   Flask-SQLAlchemy (assumed, based on models)
*   Flask-WTF (assumed, based on forms.py)
*   HTML
*   CSS

## Setup and Running

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository-url>
    cd <project-directory>
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database (if needed):**
    *   Check `create_db.py` or application initialization logic. You might need to run:
        ```bash
        flask shell
        >>> from app import db
        >>> db.create_all()
        >>> exit()
        ```
    *   Or potentially run the `create_db.py` script directly:
        ```bash
        python create_db.py
        ```

5.  **Run the application:**
    ```bash
    flask run
    ```

    The application should be accessible at `http://127.0.0.1:5000` (or the configured port).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/) (Or specify your chosen license)
