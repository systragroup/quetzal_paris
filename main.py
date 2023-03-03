import sys
import os
import boto3
import time

sys.path.insert(0, os.path.abspath('quetzal'))
from subprocess import Popen, PIPE, STDOUT
import subprocess

s3 = boto3.resource('s3') 

def download_s3_folder(bucket_name, s3_folder, local_dir=None):
    """
    Download the contents of a folder directory
    Args:
        bucket_name: the name of the s3 bucket
        s3_folder: the folder path in the s3 bucket
        local_dir: a relative or absolute directory path in the local file system
    """
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

def handler(event, context):
    bucket_name = os.environ['BUCKET_NAME']
    
    download_s3_folder(bucket_name, 'dev', local_dir='/tmp')

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

    sync_command = ['aws', 's3', 'sync', '/tmp/dev/', f's3://{bucket_name}/dev/']  
    process = subprocess.run(sync_command, stdout=PIPE, stderr=STDOUT)
    content = process.stdout.read().decode("utf-8")
    print(content)

    return event