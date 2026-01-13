import os


def append_line_to_file(file_path, text_line):
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as file:
                file.write(text_line + "\n")
        else:
            with open(file_path, 'a') as file:
                file.write(text_line + '\n')
    except Exception as e:
        print(f"An error occurred adding metadata for {file_path}: {e}")
