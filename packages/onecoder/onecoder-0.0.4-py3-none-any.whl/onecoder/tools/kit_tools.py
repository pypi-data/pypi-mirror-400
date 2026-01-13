# onecoder/tools/kit_tools.py

import subprocess
import json


def kit_index_tool(directory: str = ".") -> str:
    """
    Uses kit to build and return a comprehensive index of the repository.

    Args:
        directory: The path to the repository directory to index.

    Returns:
        A JSON string containing the repository index, or an error message.
    """
    try:
        # Run kit index command
        result = subprocess.run(
            ["kit", "index", "."],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode == 0:
            # Parse and return the JSON
            try:
                index_data = json.loads(result.stdout)
                return json.dumps(index_data, indent=2)
            except json.JSONDecodeError:
                return (
                    f"Kit index completed but output is not valid JSON: {result.stdout}"
                )
        else:
            return f"Error running kit index: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: kit index command timed out"
    except FileNotFoundError:
        return "Error: kit command not found. Make sure kit is installed."
    except Exception as e:
        return f"An error occurred while running kit index: {e}"


def kit_file_tree_tool(directory: str = ".") -> str:
    """
    Uses kit to get the file tree structure of a repository.

    Args:
        directory: The path to the repository directory.

    Returns:
        A string containing the file tree structure, or an error message.
    """
    import tempfile
    import os

    try:
        # Create a temporary file to store the output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as tmp:
            tmp_path = tmp.name

        result = subprocess.run(
            ["kit", "file-tree", directory, "--output", tmp_path], 
            capture_output=True, 
            text=True, 
            timeout=10
        )

        if result.returncode == 0:
            with open(tmp_path, 'r') as f:
                content = f.read()
            os.remove(tmp_path)
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return f"Error: Invalid JSON from kit: {content}"
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            return f"Error running kit file-tree: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: kit file-tree command timed out"
    except Exception as e:
        return f"An error occurred while running kit file-tree: {e}"


def kit_symbols_tool(directory: str = ".") -> str:
    """
    Uses kit to extract code symbols from the repository.

    Args:
        directory: The path to the repository directory.

    Returns:
        A JSON string containing code symbols, or an error message.
    """
    try:
        result = subprocess.run(
            ["kit", "symbols", directory, "--format", "json"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            try:
                symbols_data = json.loads(result.stdout)
                return json.dumps(symbols_data, indent=2)
            except json.JSONDecodeError:
                return f"Kit symbols completed but output is not valid JSON: {result.stdout}"
        else:
            return f"Error running kit symbols: {result.stderr}"

    except subprocess.TimeoutExpired:
        return "Error: kit symbols command timed out"
    except Exception as e:
        return f"An error occurred while running kit symbols: {e}"
