# onecoder/tools/file_tools.py


def write_file_tool(filepath: str, content: str) -> str:
    """
    Writes content to a file at the given filepath.

    Args:
        filepath: The path to the file.
        content: The content to write to the file.

    Returns:
        A success message or an error message if the file cannot be written.
    """
    try:
        with open(filepath, "w") as f:
            f.write(content)

        # Trigger hooks
        try:
            from onecoder.hooks import hooks_manager
            hooks_manager.on_file_edit(filepath)
        except ImportError:
            pass # Ignore if hooks module is not available or has circular import
        except Exception as e:
            print(f"Warning: Failed to trigger hooks: {e}")

        return f"Successfully wrote content to {filepath}"
    except Exception as e:
        return f"An error occurred while writing to the file: {e}"


def read_file_tool(filepath: str) -> str:
    """
    Reads the contents of a file at the given filepath.

    Args:
        filepath: The path to the file.

    Returns:
        The content of the file, or an error message if the file cannot be read.
    """
    try:
        with open(filepath, "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"
    except Exception as e:
        return f"An error occurred while reading the file: {e}"


def list_directory_tool(directory: str = ".") -> str:
    """
    Lists the contents of a directory.

    Args:
        directory: The path to the directory to list.

    Returns:
        A string containing the directory listing, or an error message if the directory cannot be read.
    """
    import os

    try:
        items = os.listdir(directory)
        files = [
            item for item in items if os.path.isfile(os.path.join(directory, item))
        ]
        dirs = [item for item in items if os.path.isdir(os.path.join(directory, item))]
        result = f"Directory: {directory}\n"
        if dirs:
            result += f"Directories: {', '.join(dirs)}\n"
        if files:
            result += f"Files: {', '.join(files)}"
        return result
    except Exception as e:
        return f"An error occurred while listing directory {directory}: {e}"
