import sys
import os

sys.path.insert(0, os.path.abspath('quetzal'))
from subprocess import Popen, PIPE, STDOUT

def handler(event, context):
    notebook = event['notebook_path']
    file = os.path.join('/tmp', os.path.basename(notebook).replace('.ipynb', '.py'))
    os.system('jupyter nbconvert --to python %s --output %s' % (notebook, file))
    cwd = os.path.dirname(notebook)
    if type(event['arg']) == tuple:
        command_list = ['python', file] +list(event['arg'])
    else:
        command_list = ['python', file] +[event['arg']]

    my_env = os.environ.copy()
    my_env['PYTHONPATH'] = os.pathsep.join(sys.path)
    process = Popen(command_list, stdout=PIPE, stderr=STDOUT, env=my_env, cwd=cwd)
    process.wait()
    print(process.stdout.read())

    return 0