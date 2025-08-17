# Project Overview

This project is a command-line flashcard application written in Python. It helps users study and memorize terms and definitions using a spaced repetition system inspired by the Leitner system.

The flashcard data is stored in a simple YAML file (`cards.yaml`), making it easy to add, edit, and manage the content. The application tracks the user's progress, prioritizing cards that the user struggles with.

## Key Technologies

*   **Python 3:** The core application logic is written in Python.
*   **PyYAML:** Used for parsing the `cards.yaml` data file.
*   **JSON:** User's progress and state are stored in a JSON file (`~/.sdi_cards_state.json`).

## Architecture

The application consists of two main Python scripts:

*   `sdi-cards.py`: This is the main entry point and contains all the application logic, including:
    *   Loading and parsing the YAML card data.
    *   Filtering cards by tags.
    *   Implementing the quiz logic with normal and reversed modes (term -> definition or definition -> term).
    *   Tracking user progress (correct/incorrect answers, streaks, and box levels) using a state file.
    *   A scoring system to prioritize cards that are due for review.
*   `main.py`: A simple script that prints a "Hello" message. The core functionality is in `sdi-cards.py`.

The card data is stored in `cards.yaml`, and the user's learning progress is saved in `~/.sdi_cards_state.json`.

# Building and Running

This project does not require a complex build process.

## Dependencies

This project uses `uv` for dependency management. The dependencies are `PyYAML` and `rich`.
You can install them by running:

```bash
uv sync
```

## Running the Application

To run the flashcard quiz, execute the `sdi-cards.py` script:

```bash
python sdi-cards.py
```

### Command-line Options

You can customize the quiz with the following options:

*   `-f, --file`: Specify the path to the YAML file (default: `cards.yaml`).
*   `-t, --tags`: Filter the cards by one or more tags.
*   `-n, --count`: Set the number of questions per quiz (default: 15).
*   `-r, --reverse`: Reverse the quiz direction (show definition, ask for the term).
*   `--list`: List all available cards and their tags without starting a quiz.

**Example:**

To start a quiz with 10 questions tagged with "gcp" and "db":

```bash
python sdi-cards.py -n 10 -t gcp db
```

# Development Conventions

*   **Code Style:** The code follows standard Python conventions (PEP 8).
*   **Data Management:** Flashcard content is managed in `cards.yaml`. This separation of data and logic makes it easy to update the content without modifying the code.
*   **State Management:** User progress is stored locally in the user's home directory, allowing the learning state to persist across sessions.
*   **Testing:** There are no automated tests in the project.
