# Air-Quality-Data-Analytics

This guide provides instructions for setting up a Python development environment on your local machine to see Air Quality Data Analytics by Dicoding Course

## Prerequisites

- Operating System: Windows, macOS, or Linux
- Internet connection to download Python and packages

## Installation Steps

### 1. Install Python
1. **Download Python**:
   - Visit the [official Python website](https://www.python.org/downloads/) and download the latest version (e.g., Python 3.11).
   - Ensure you select the appropriate installer for your operating system.

2. **Install Python**:
   - Run the installer.
   - **Important**: Check the box to **Add Python to PATH** during installation.
   - Follow the prompts to complete the installation.

3. **Verify Installation**:
   Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and run:
   ```bash
   python --version

## Setup Environment

   Open a terminal (Command Prompt on Windows, Terminal on macOS/Linux) and run:
   ```bash
   mkdir proyek_analisis_data
   cd proyek_analisis_data
   pipenv install
   pipenv shell
   pip install -r requirements.txt
   ```

## Run Streamlit App

   ```bash
   streamlit run main_dashboard.py
   ```
