import subprocess
import secrets
import getpass
import os
import requests
import urllib.parse
import time
from google.colab import files, drive, auth
from google.cloud import storage
import glob

def connect(LOG_DIR = '/log/fit'):
    print('It may take a few seconds for processing. Please wait.')
    root_password = secrets.token_urlsafe()
    subprocess.call('apt-get update -qq', shell=True)
    subprocess.call('apt-get install -qq -o=Dpkg::Use-Pty=0 openssh-server pwgen > /dev/null', shell=True)
    subprocess.call(f'echo root:{root_password} | chpasswd', shell=True)
    subprocess.call('mkdir -p /var/run/sshd', shell=True)
    subprocess.call('echo "PermitRootLogin yes" >> /etc/ssh/sshd_config', shell=True)
    subprocess.call('echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config', shell=True)    
    get_ipython().system_raw('/usr/sbin/sshd -D &')

    subprocess.call('mkdir -p /content/ngrok-ssh', shell=True)
    os.chdir('/content/ngrok-ssh')
    subprocess.call('wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip -O ngrok-stable-linux-amd64.zip', shell=True)
    subprocess.call('unzip -u ngrok-stable-linux-amd64.zip', shell=True)
    subprocess.call('cp /content/ngrok-ssh/ngrok /ngrok', shell=True)
    subprocess.call('chmod +x /ngrok', shell=True)
    print("Copy&paste your authtoken from https://dashboard.ngrok.com/auth")
    authtoken = getpass.getpass()
    get_ipython().system_raw(f'/ngrok authtoken {authtoken} &')

    _create_tunnels()

    get_ipython().system_raw(f'tensorboard --logdir {LOG_DIR} --host 0.0.0.0 --port 6006 &')  

    time.sleep(3) # synchronize.

    with open('/content/ngrok-ssh/ngrok-tunnel-info.txt', 'w') as f:
        url, port = urllib.parse.urlparse(_get_ngrok_url('ssh')).netloc.split(':')
        # f.write('Run the command below on local machines to SSH into the Colab instance:\n')
        f.write(f'ssh -p {port} root@{url}\n')
        f.write('Password:\n')
        f.write(f'{root_password}\n')
        if 'COLAB_TPU_ADDR' in os.environ:
          tpu_address = 'grpc://' + os.environ['COLAB_TPU_ADDR']
          f.write(f"""Copy and paste the commands below to the beginning of your TPU program:
    import tensorflow as tf
    resolver = tf.distribute.cluster_resolver.TPUClusterResolver(tpu='{tpu_address}') 
    tf.config.experimental_connect_to_cluster(resolver)
    tf.tpu.experimental.initialize_tpu_system(resolver)
    strategy = tf.distribute.experimental.TPUStrategy(resolver)""")
        url_tensorboard = _get_ngrok_url('tensorboard')
        # f.write(f'To view tensorboard, visit {url_tensorboard}')  
        f.write(f'Tensorboard: {url_tensorboard}')  
        # f.write('after running the following two commands on the Colab notebook:\n')
        # f.write(f'  %load_ext tensorboard')
        # f.write(f'  %tensorboard --logdir {LOG_DIR}')
        # f.write('Run kill() to close all the tunnels.\n')
    # print('SSH connection is successfully established. Run info() for connection configuration.')

def info():
    with open('/content/ngrok-ssh/ngrok-tunnel-info.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            print(line)

def kill():
    os.system("kill $(ps aux | grep ngrok | awk '{print $2}')")
    print('Done.')

def _create_tunnels():
    with open('/content/ngrok-ssh/ssh.yml', 'w') as f:
        f.write('tunnels:\n')
        f.write('  ssh:\n')
        f.write('    proto: tcp\n')
        f.write('    addr: 22')
    with open('/content/ngrok-ssh/tensorboard.yml', 'w') as f:
        f.write('tunnels:\n')
        f.write('  tensorboard:\n')
        f.write('    proto: http\n')
        f.write('    addr: 6006\n')
        f.write('    inspect: false\n')
        f.write('    bind_tls: true')
    with open('/content/ngrok-ssh/http8080.yml', 'w') as f:
        f.write('tunnels:\n')
        f.write('  http8080:\n')
        f.write('    proto: http\n')
        f.write('    addr: 8080\n')
        f.write('    inspect: false\n')
        f.write('    bind_tls: true')
    with open('/content/ngrok-ssh/tcp8080.yml', 'w') as f:
        f.write('tunnels:\n')
        f.write('  tcp8080:\n')
        f.write('    proto: tcp\n')
        f.write('    addr: 8080')
    if 'COLAB_TPU_ADDR' in os.environ:
        with open('/content/ngrok-ssh/tpu.yml', 'w') as f:
            COLAB_TPU_ADDR = os.environ['COLAB_TPU_ADDR']
            f.write('tunnels:\n')
            f.write('  tpu:\n')
            f.write('    proto: tcp\n')
            f.write(f'    addr: {COLAB_TPU_ADDR}')
    with open('/content/ngrok-ssh/run_ngrok.sh', 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('set -x\n')
        if 'COLAB_TPU_ADDR' in os.environ:
            f.write('/ngrok start --config ~/.ngrok2/ngrok.yml --config /content/ngrok-ssh/ssh.yml --log=stdout --config /content/ngrok-ssh/tensorboard.yml --config /content/ngrok-ssh/http8080.yml --config /content/ngrok-ssh/tcp8080.yml --config /content/ngrok-ssh/tpu.yml "$@"')
        else:
            f.write('/ngrok start --config ~/.ngrok2/ngrok.yml --config /content/ngrok-ssh/ssh.yml --log=stdout --config /content/ngrok-ssh/tensorboard.yml --config /content/ngrok-ssh/http8080.yml --config /content/ngrok-ssh/tcp8080.yml "$@"')
    if 'COLAB_TPU_ADDR' in os.environ:
        get_ipython().system_raw('bash /content/ngrok-ssh/run_ngrok.sh ssh tensorboard tcp8080 tpu &')
    else:
        get_ipython().system_raw('bash /content/ngrok-ssh/run_ngrok.sh ssh tensorboard tcp8080 &')     

def _get_ngrok_info():
    return requests.get('http://localhost:4040/api/tunnels').json()

def _get_ngrok_tunnels():
    for tunnel in _get_ngrok_info()['tunnels']:
        name = tunnel['name']
        yield name, tunnel

def _get_ngrok_tunnel(name):
    for name1, tunnel in _get_ngrok_tunnels():
        if name == name1:
            return tunnel

def _get_ngrok_url(name, local=False):
    if local:
        return _get_ngrok_tunnel(name)['config']['addr']
    else:
        return _get_ngrok_tunnel(name)['public_url']            

def kaggle(data='tabular-playground-series-mar-2021', output='/kaggle/input'):        
    subprocess.call('sudo apt -q update', shell=True)
    subprocess.call('sudo apt -q install unar nano less p7zip', shell=True)
    subprocess.call('pip install -q --upgrade --force-reinstall --no-deps kaggle kaggle-cli', shell=True)
    subprocess.call('mkdir -p /root/.kaggle', shell=True)
    os.chdir('/root/.kaggle')
    if 'kaggle.json' not in os.listdir('/root/.kaggle'):
        print('Upload your kaggle API token')
        files.upload()
        subprocess.call('chmod 600 /root/.kaggle/kaggle.json', shell=True)
    subprocess.call(f'mkdir -p {output}', shell=True)
    os.chdir(f'{output}')
    subprocess.call(f'kaggle competitions download -c {data}', shell=True)
    subprocess.call(f'7z x {data}.zip -o{output}', shell=True)
    print(f'\nUnzipped {data}.zip to {output}.')
    subprocess.call('mkdir -p /kaggle/working', shell=True)
    os.chdir('/kaggle/working')

def google_drive(dir='/gdrive'):
    print(f'\nGoogle Drive authentication starts...')
    drive.mount(dir)

def GCSconnect(key_file=None):
    if key_file:
        if not os.path.exists('/root/.kaggle/'):
            os.makedirs('/root/.kaggle/')        
        print('Upload your Google Storage API token')
        os.chdir('/root/.kaggle/')
        files.upload()
        subprocess.call(f'chmod 600 /root/.kaggle/{key_file}', shell=True)        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f'/root/.kaggle/{key_file}' 
        subprocess.call('echo $GOOGLE_APPLICATION_CREDENTIALS', shell=True)
    else:
        print('\nGCS authentication starts...')
        auth.authenticate_user()

def _create_bucket(project, bucket_name):
    storage_client = storage.Client(project=project)
    bucket = storage_client.bucket(bucket_name)
    bucket.create(location='US')
    print(f'bucket {bucket.name} created.')

def _list_blobs(project, bucket_name):
    storage_client = storage.Client(project=project)
    blobs = storage_client.list_blobs(bucket_name)
    blist = []
    for blob in blobs:
        blist.append(blob.name)
    if not len(blist):
        print('empty bucket!')
    else:
        print('\n'.join(blist))

def create_bucket(project, bucket_name):
    try:
        _create_bucket(project, bucket_name)
    except Exception as e:
        print(f"create_bucket('{bucket_name}') fails. Code:", e)

def list_blobs(project, bucket_name):
    try:
        _list_blobs(project, bucket_name)
    except Exception as e:
        print(f"list_blobs('{bucket_name}') fails. Code:", e)


def upload_to_gcs(project, bucket_name, destination_blob, source_directory):
# Upload file(s) from Google Colaboratory to GCS Bucket.
# type: {string} project name
#       {string} bucket name
#       {string} source directory
# rtype: None
# usage:
#   upload_to_gcs("strategic-howl-123", "gcs-station-16", 'temp8/a.pkl', '/a.pkl')
# note: DON'T put a leading slash in the third argument. 
    storage_client = storage.Client(project=project)
    bucket = storage_client.get_bucket(bucket_name)
    # paths = glob.glob(os.path.join(source_directory, file if file else f'*.{ext}'))
    # for path in paths:
    #     filename = os.path.join(source_directory, file) if file else path.split('/')[-1] 
    #     blob = bucket.blob(filename)
    #     blob.upload_from_filename(path)
    #     print(f'{path} uploaded to {os.path.join(bucket_name, filename)}')
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(source_directory)  

def download_to_colab(project, bucket_name, destination_directory, remote_blob_path='', local_file_name=''):
# Download file(s) from Google Cloud Storage Bucket to Colaboratory.
# type: {string} project name
#       {string} bucket name
#       {string} destination directory
#       {string} (optional) filename: If set, the target file is downloaded.
# rtype: None
# usage:
#   project = "strategic-howl-123456522" 
#   bucket_name = "gcs-station-168" 
#   >>> download_to_colab(project, bucket_name, '/temp8')
#   >>> download_to_colab(project, bucket_name, destination_directory = '/temp9/fun', remote_blob_path='tps-apr-2021-label/data_fare_age.pkl', local_file_name='data_fare_age.pkl')
    storage_client = storage.Client(project=project)
    os.makedirs(destination_directory, exist_ok = True)
    if local_file_name and remote_blob_path:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(remote_blob_path)
        blob.download_to_filename(os.path.join(destination_directory, local_file_name))
        print('download finished.')
    else:
        from pathlib import Path
        os.chdir(destination_directory)
        blobs = storage_client.list_blobs(bucket_name)
        count = 1
        for blob in blobs:
            if blob.name.endswith("/"): continue # 
            file_split = blob.name.split("/")
            directory = "/".join(file_split[0:-1])
            Path(directory).mkdir(parents=True, exist_ok=True) # (2)
            blob.download_to_filename(blob.name) 
            des = os.path.join(destination_directory, directory)
            if count==1: print(f"Destination: {des}")
            print(f'{count}. {blob.name.split("/")[-1]:>50s}')
            count += 1

    


