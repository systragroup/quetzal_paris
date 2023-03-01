import sys
import os

sys.path.insert(0, os.path.abspath('quetzal'))
from subprocess import Popen, PIPE, STDOUT

def handler(event, context):
    notebook = event['notebook_path']
    arg = event['launcher_arg']

    file = os.path.join('/tmp', os.path.basename(notebook).replace('.ipynb', '.py'))
    os.system('jupyter nbconvert --to python %s --output %s' % (notebook, file))
    cwd = os.path.dirname(notebook)

    command_list = ['python', file] +[arg['scenario']]

    my_env = os.environ.copy()
    my_env['PYTHONPATH'] = os.pathsep.join(sys.path)
    process = Popen(command_list, stdout=PIPE, stderr=STDOUT, env=my_env, cwd=cwd)
    process.wait(timeout=500)

    content = process.stdout.read().decode("utf-8")
    print(content)

    if 'Error' in content and "end_of_notebook" not in content:
        raise RuntimeError("Error on execution")

    return event