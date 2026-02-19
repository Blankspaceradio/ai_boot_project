import os
from google.genai import types

def write_file(working_directory, file_path, content):
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        if not valid:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        if os.path.isdir(target_dir):
            return f'Error: Cannot write to "{file_path}" as it is a directory'
        folder_to_create = os.path.dirname(target_dir)

        os.makedirs(folder_to_create, exist_ok=True)
        with open(target_dir, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f"Error: {e}"


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes text content to a specified file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
            type=types.Type.STRING,
            description="Path to the file to write, relative to the working directory",
            ),
            "content": types.Schema(
            type=types.Type.STRING,
            description="The text content to write to the file",
        ),
        },
        required=["file_path","content"],
    ),
)