#use with python3
import shlex, subprocess
import os
import sys

"""
A simple program to install the dependencies required to run the Testbed
"""

def run_command(command):
    returncode = subprocess.run(command.split()).returncode
    if returncode != 0:
        print(f'failed to run:\n{command}')
        exit(0)

setup_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'tools')

if os.path.exists(setup_path) == False:
    print('Creating tools directory!')
    os.mkdir(setup_path)

os.chdir(setup_path)

print("Step 1. Install prerequisites")

run_command('sudo  apt-get -y install ansible  git  aptitude  gcc  python3-dev  libffi-dev  libssl-dev  libxml2-dev  libxslt1-dev  zlib1g-dev  openjdk-8-jre  adduser  libfontconfig1  debian-keyring  debian-archive-keyring  apt-transport-https')
run_command('sudo  apt-get -y install  tmux')
run_command('python3  -m  pip  install  pyyaml')
run_command('python3  -m  pip  install  pandas')
run_command('python3  -m  pip  install  matplotlib')
run_command('python3  -m  pip  install  networkx')
run_command('python3  -m  pip  install  Flask')

print("Step 2. Install ContainerNET")

if os.path.exists("containernet") == False:
    run_command('git  clone  https://github.com/containernet/containernet.git')
    os.chdir('containernet/ansible')
    run_command('sudo  ansible-playbook  -i  \"localhost\"  -c  local  install.yml')
    os.chdir(os.path.join(setup_path, 'containernet'))
    run_command('sudo make develop')
    os.chdir(setup_path)

print("Step 3. Install RYU")

if os.path.exists("ryu") == False:
    run_command('git  clone  https://github.com/faucetsdn/ryu.git')
    os.chdir("ryu")
    run_command('python3 -m pip install .')
    os.chdir(setup_path)

print("Step 4. Install SFLOW")

if os.path.exists("sflow-rt") == False:
    run_command('wget  https://inmon.com/products/sFlow-RT/sflow-rt.tar.gz')
    run_command('tar  -xvzf  sflow-rt.tar.gz')
    run_command('sflow-rt/get-app.sh sflow-rt mininet-dashboard')
    os.chdir(setup_path)

print("Step 5. Install GRAFANA")

if os.path.exists("grafana_7.4.3_amd64.deb") == False:
    run_command('wget  https://dl.grafana.com/oss/release/grafana_7.4.3_amd64.deb')
    run_command('sudo dpkg  -i  grafana_7.4.3_amd64.deb')
    run_command('sudo  systemctl  daemon-reload')

print("Step 6. Run the GRAFANA Server")

run_command('sudo  systemctl  daemon-reload')
run_command('sudo  systemctl  start  grafana-server')
run_command('sudo  systemctl  is-active  grafana-server')

print("Step 7. Install Prometheus")

if os.path.exists("prometheus-2.26.0.linux-amd64") == False:
    run_command('wget  https://github.com/prometheus/prometheus/releases/download/v2.26.0/prometheus-2.26.0.linux-amd64.tar.gz')
    run_command('tar  -xvzf  prometheus-2.26.0.linux-amd64.tar.gz')
    os.chdir(setup_path)
    run_command('sudo cp prometheus.yml tools/prometheus-2.26.0.linux-amd64/')

print("installation completed !!!")
