# CodeVerse

CodeVerse is an online coding platform that allows users to solve coding problems, participate in contests, and contribute by adding their problems.

## Features

- Solve coding problems with an interactive editor.
- Participate in timed contests.
- Add new coding problems with test cases and editorials.
- Real-time C++ code compilation and execution.

## Installation and Setup

### Prerequisites

- Python 3.x
- Django
- Git

### Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CodeVerse.git

    cd CodeVerse
   
2. **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt

3. **Apply the database migrations:**

     ```bash
     python manage.py makemigrations
     python manage.py migrate

4. **Create a superuser to access the Django admin panel:**
      ```bash
      python manage.py createsuperuser

5. **Run the development server:**
      ```bash
      python manage.py runserver
