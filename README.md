# SDI Flashcards

This project is a command-line flashcard application written in Python, designed to help users study and memorize terms and definitions using a spaced repetition system. The flashcard data is organized into multiple YAML files, allowing for easy management and categorization by genre. The application tracks user progress to prioritize cards due for review.

## Key Technologies

*   **Python 3:** Core application logic.
*   **PyYAML:** Used for parsing YAML card data.
*   **rich:** For rich text and beautiful terminal output.
*   **uv:** For efficient dependency management.
*   **JSON:** User's progress and state are stored in a JSON file (`~/.sdi_cards_state.json`).

## Architecture

The application's core logic resides in `sdi-cards.py`. Flashcard data is stored in YAML files within the `cards/` directory (e.g., `cards/general.yaml`, `cards/network.yaml`). The application can load cards from multiple YAML files within a specified directory, allowing for categorization of flashcards by topic or genre. User learning progress is persisted across sessions in a local JSON state file.

## Building and Running

### Dependencies

This project uses `uv` for dependency management. The required libraries are `PyYAML` and `rich`. You can install them by running:

```bash
uv sync
```

### Running the Application

To run the flashcard quiz, execute the `sdi-cards.py` script:

```bash
.venv/bin/python sdi-cards.py
```

### Command-line Options

You can customize the quiz with the following options:

*   `-f, --file`: Specify the path to the YAML file or directory containing YAML files (default: `cards/`).
*   `-t, --tags`: Filter the cards by one or more tags (space-separated).
*   `-n, --count`: Set the number of questions per quiz (default: 15).
*   `-r, --reverse`: Reverse the quiz direction (show definition, ask for the term).
*   `-v, --verbose`: Show long description, notes, and URLs for each card.
*   `--list`: List all available cards and their tags without starting a quiz.
*   `--stats`: Show learning statistics.

**Examples:**

To start a quiz with 10 questions tagged with "gcp" and "db" from the default `cards/` directory:

```bash
.venv/bin/python sdi-cards.py -n 10 -t gcp db
```

To start a quiz with verbose output, showing long descriptions, notes, and URLs:

```bash
.venv/bin/python sdi-cards.py -n 1 -v
```

## Development Conventions

*   **Code Style:** The code follows standard Python conventions (PEP 8).
*   **Data Management:** Flashcard content is managed in YAML files within the `cards/` directory. Each YAML file can contain multiple cards.
    *   **`meta.deck`**: The deck name is now an object with `ja` (Japanese) and `en` (English) keys, allowing for bilingual representation.
    *   **`notes`**: The `notes` field is a list of strings, allowing for multiple distinct notes per card.
    *   **`url`**: The `url` field is also a list of strings, enabling the inclusion of multiple reference URLs (e.g., official website, GitHub repository).
*   **State Management:** User progress is stored locally in the user's home directory (`~/.sdi_cards_state.json`), allowing the learning state to persist across sessions.
*   **Testing:** There are no automated tests in the project. Manual verification is performed by running the application with various options.
