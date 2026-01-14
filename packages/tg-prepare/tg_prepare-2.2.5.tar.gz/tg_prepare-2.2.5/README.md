# TG Prepare

`tg_prepare` is a user interface (UI) designed to visually prepare TextGrid imports. It integrates with the [`tg_model`](https://gitlab.gwdg.de/textplus/textplus-io/tg_model) project and provides tools for managing projects, uploading files, and publishing to TextGrid.

## Features

- **Project Management**: Create, edit, and delete projects.
- **TextGrid Integration**: Publish projects to a TextGrid test instance.
- **XPath Support**: Validate and edit XPath expressions.
- **File Uploads**: Upload and manage files within a project.
- **Nextcloud Integration**: Download files from Nextcloud.
- **Git Integration**: Clone Git repositories directly into a project.
- **Configurable Settings**: Customize the application via `config.ini`.

## Requirements

- Python 3.8 or higher
- Dependencies listed in [`setup.py`](setup.py)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/tg_prepare.git
    cd tg_prepare
    ```

2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install .
    ```

4. Configure the application:
    - Copy the example configuration file:
        ```bash
        cp config.ini.example config.ini
        ```
    - Edit `config.ini` to suit your environment.

5. Run the application:
    ```bash
    tgp_app
    ```

6. Open the application in your browser at `http://localhost:5000`.

## Usage

### Configuring the Application
Modify the `config.ini` file to set up:
- TextGrid API credentials
- File storage paths
- Other application-specific settings

### Creating Projects
1. Navigate to the homepage.
2. Click "Create New Project."
3. Enter a project name and confirm.

### Uploading Files
1. Open a project.
2. Go to the "Files" tab.
3. Select files and click "Upload."

### Publishing to TextGrid
1. Ensure you have a valid TextGrid session ID.
2. Select a project and click "Publish."
3. Follow the instructions to upload the project to the TextGrid test instance.

## Project Structure

The project is organized into two main subpackages:

### `tgp_ui`
- Contains the Flask-based user interface.
- Includes HTML templates and static assets.

### `tgp_backend`
- Implements the backend logic for project management, file handling, and TextGrid API integration.

### Configuration
- `config.ini`: Central configuration file for the application.

## License

This project is licensed under the Apache License 2.0. See the [`LICENSE`](LICENSE) file for details.

## Authors

- **Ralf Klammer** - TU Dresden
- **Moritz Wilhelm** - TU Dresden

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitLab](https://gitlab.gwdg.de/textplus/textplus-io/tg_prepare/-/issues).

---

Enjoy working with [tg_prepare](https://gitlab.gwdg.de/textplus/textplus-io/tg_prepare)!