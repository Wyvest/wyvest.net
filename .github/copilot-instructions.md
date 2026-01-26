# Copilot Instructions for wyvest.net

This repository hosts a personal landing page and a data collection project under `impasta/`.

## Project Structure
- **Root**: Contains the static landing page (`index.html`) and GitHub Pages config (`CNAME`).
- **impasta/**: Contains data files for a category/word association project.
  - `data.json`: The main structured data file.
  - `lol.txt`: Raw text source for categories and words.

## Data Management (`impasta/`)
When working with `data.json`:
- **Structure**: The root is an object with a `categories` array.
- **Category Object**:
  - `name`: Display name (string).
  - `id`: Unique identifier (snake_case representation of name, e.g., "Video Games" -> `video_games`).
  - `words`: Array of strings (if it's a leaf category).
  - `categories`: Array of sub-category objects (if it has sub-sections).
- **Source**: Updates often come from scraping or parsing `lol.txt`.
- **IDs**: Always generate descriptive snake_case IDs. handle special characters (replace `&` with `and`, `/` with `_`, etc.).

## Development Workflow
- **Tech Stack**: Pure HTML for the root site. JSON for data storage.
- **No Build Process**: Files are static. Changes to `index.html` or `data.json` are immediate.
- **Scripts**: Python scripts (like `update_data.py`) may be used ad-hoc for data migration/scraping but are not part of the core runtime.

## Coding Style
- **JSON**: Indent with 2 spaces. Ensure valid encoding.
- **HTML**: Standard semantic HTML5.
