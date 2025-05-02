# server.py
from flask import Flask, Response
import subprocess
import os
import shutil

app = Flask(__name__)

@app.route('/run-script')
def run_script():
    # Paths
    network_script_path = r"\\zpro\Jobs\Test\3124522.py"
    template_directory = r"\\taurus\punna\Jobs\Python JEs\Gokul\jobsgenericwebcrawlerapp\ScheduleNo-1"
    venv_python = r"\\taurus\punna\Jobs\Python JEs\Gokul\jobsgenericwebcrawlerapp\.venv\Scripts\python.exe"
    script_name = os.path.basename(network_script_path)
    destination_script_path = os.path.join(template_directory, script_name)

    # Copy the script
    try:
        shutil.copy(network_script_path, destination_script_path)
    except Exception as e:
        return f"Error copying file: {e}"

    # Define generator to stream logs
    def generate():
        process = subprocess.Popen(
            [venv_python, script_name],
            cwd=template_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        for line in process.stdout:
            yield line.replace('\n', '<br>\n')  # Convert to HTML format
        process.stdout.close()
        process.wait()

    return Response(generate(), mimetype='text/html')

if __name__ == '__main__':
    app.run(port=5000)
