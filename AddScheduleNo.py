import os
import re


def update_function_call_in_folder(folder_path, new_argument):
    for filename in os.listdir(folder_path):
        if filename.endswith('.py'):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'r') as f:
                lines = f.readlines()

            inside_target_block = False
            modified_lines = []
            for line in lines:
                stripped = line.strip()

                # Detect the "if URLSNoList:" block
                if stripped.startswith("if URLSNoList"):
                    inside_target_block = True
                    modified_lines.append(line)
                    continue

                # Exit block when indentation drops (assumes consistent indentation)
                if inside_target_block and not line.startswith((' ', '\t')):
                    inside_target_block = False

                if inside_target_block and 'DBRepo.getCompaniesbyURLSNoList' in stripped:
                    # Add the new argument only if not already present
                    if new_argument not in line:
                        line = re.sub(r'\(([^)]*)\)', r'(\1, {})'.format(new_argument), line)

                modified_lines.append(line)

            with open(filepath, 'w') as f:
                f.writelines(modified_lines)


# Example usage
folder = 'C:\\Users\\Abdullah.Habeeb\\OneDrive - GlobalData PLC\\Desktop\\NexgileDataNotYielding\\jobsgenericwebcrawlerapp\\Testing'  # Update this to your actual folder path
update_function_call_in_folder(folder, '127')
