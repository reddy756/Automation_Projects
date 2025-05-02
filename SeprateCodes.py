import os
import shutil

# Path to the folder containing your Python files
source_dir = 'C:\\Users\\Abdullah.Habeeb\\Downloads\\Nexgile_py_files_complete\\Nexgile_py_files_complete'
single_line_dir = os.path.join(source_dir, 'single_line_scripts')
multi_line_dir = os.path.join(source_dir, 'multi_line_scripts')

# Create folders if they don't exist
os.makedirs(single_line_dir, exist_ok=True)
os.makedirs(multi_line_dir, exist_ok=True)

def count_lines_after_main(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    main_index = None
    for i, line in enumerate(lines):
        if 'if __name__' in line and '__main__' in line:
            main_index = i
            break

    if main_index is None:
        return -1  # No main block found

    # Count indented lines after main block
    count = 0
    for line in lines[main_index + 1:]:
        stripped = line.strip()
        if stripped and (line.startswith(' ') or line.startswith('\t')):
            count += 1
        elif stripped:
            break  # Stop if a new non-indented block starts

    return count

# Walk through files and move accordingly
for filename in os.listdir(source_dir):
    if filename.endswith('.py'):
        filepath = os.path.join(source_dir, filename)
        count = count_lines_after_main(filepath)
        if count == 1:
            shutil.move(filepath, os.path.join(single_line_dir, filename))
        elif count > 1:
            shutil.move(filepath, os.path.join(multi_line_dir, filename))
