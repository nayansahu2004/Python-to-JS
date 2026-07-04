# Python to JavaScript Conversion Project

## Overview

This project demonstrates the conversion of Python code to JavaScript, showcasing how to bridge Python and JavaScript environments. It includes practical examples of running JavaScript from Python, system information gathering, and API integration using the Groq API.

## Project Structure

### Files

- **main.js** - A simple JavaScript module with basic arithmetic operations (add function)
- **run.py** - Python script that executes the JavaScript file using subprocess and displays the output
- **system_info.py** - Utility module that gathers comprehensive system information including OS details, architecture, and installed package managers
- **project.ipynb** - Jupyter notebook that demonstrates:
  - System information collection
  - Integration with Groq API (LLM service)
  - API request handling and response processing

## Features

### 1. JavaScript Execution from Python
The `run.py` script demonstrates how to execute JavaScript code from Python using Node.js and capture the output.

### 2. System Information Gathering
The `system_info.py` module provides utilities to:
- Detect operating system (Windows, macOS, Linux)
- Retrieve system architecture and kernel information
- Identify Linux distribution details
- Detect WSL (Windows Subsystem for Linux) and Rosetta 2 environments
- Determine target triple from compilers

### 3. Groq API Integration
The Jupyter notebook integrates with the Groq API to:
- Send prompts to an LLM
- Process and display responses
- Handle system prompts for API requests

## Prerequisites

### Python Requirements
- Python 3.x
- Required packages:
  - `subprocess` (built-in)
  - `openai` (for Groq API integration)
  - Other standard library modules: `os`, `platform`, `shutil`

### JavaScript Requirements
- Node.js installed and accessible in PATH

### Optional Requirements
- Jupyter Notebook/JupyterLab (for running `project.ipynb`)
- Groq API key (for notebook functionality)

## Installation & Setup

### 1. Install Python Dependencies
```bash
pip install openai
```

### 2. Install Node.js
Download and install from [nodejs.org](https://nodejs.org)

### 3. Set Up Groq API (Optional)
- Get your API key from [Groq Console](https://console.groq.com)
- Store it in an environment variable or configuration file

## How to Execute

### Option 1: Run the Python Script (Simplest)
Execute the Python script that runs the JavaScript file:
```bash
python run.py
```

**Expected Output:**
```
2 + 3 = 5
```

### Option 2: Run JavaScript Directly
Execute the JavaScript file directly using Node.js:
```bash
node main.js
```

**Expected Output:**
```
2 + 3 = 5
```

### Option 3: Run the Jupyter Notebook
Start Jupyter and open `project.ipynb`:
```bash
jupyter notebook project.ipynb
```

Then execute cells in sequence to:
1. Load system information
2. Configure API credentials
3. Send requests to Groq API
4. Display responses

## Usage Examples

### Python to JavaScript Bridge
```python
# run.py demonstrates executing JavaScript from Python
result = subprocess.run(["node", "main.js"], capture_output=True, text=True)
print(result.stdout)  # Outputs: 2 + 3 = 5
```

### System Information Gathering
```python
from system_info import _os_block

# Get detailed system information
sys_info = _os_block()
print(sys_info)  # Returns dict with OS details
```

### Groq API Integration (via Notebook)
The notebook demonstrates:
- Initializing the Groq client
- Setting system prompts
- Making API calls with custom parameters
- Processing LLM responses

## Project Goals (Educational)

This project is part of a Udemy course demonstrating:
1. ✅ Fundamentals of JavaScript
2. ✅ Python-JavaScript interoperability
3. ✅ System-level programming tasks
4. ✅ API integration patterns
5. ✅ Jupyter notebook workflows

## Troubleshooting

### "node: command not found"
- **Solution:** Install Node.js or add it to your PATH

### Python subprocess errors
- **Solution:** Ensure the working directory is correct and main.js is in the same folder as run.py

### Groq API errors (in notebook)
- **Solution:** Verify API key is set and has proper permissions

### Import errors
- **Solution:** Install missing packages with `pip install -r requirements.txt` (if available) or manually install required packages

## Notes

- The project uses `capture_output=True` for safe subprocess execution
- System information gathering includes error handling for cross-platform compatibility
- All helper functions in `system_info.py` include fallback behavior for undetected values

## License

This project is for educational purposes as part of a Udemy course.

---

**Last Updated:** July 2026
