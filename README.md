
# ssh-Colab
ssh-Colab is a Python module to facilitate remote access to Google Colaboratory
(Colab) through Secure Shell (SSH) connections, secured by a third-party
software, ngrok. sshColab automates the tedious routine to set up ngrok
tunnels needed for TPU runtime applications and services like TensorBoard. It also
includes the function to facilitate the routine of Kaggle API installation/authentication
and competition data downloads.

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)
![python version](https://img.shields.io/badge/python-3.6%2C3.7%2C3.8-blue?logo=python)

# Prerequisites
- [ngrok](https://ngrok.com/) tunnel authtoken.
- Google account to access a [Colab](https://colab.research.google.com/notebooks/intro.ipynb) notebook.
- Local code editors such as VS Code or PyCharm to make the most of coding on Colab.

# Usage
1. Launch a Colab notebook. Choose a runtime type you prefer.

2. Install sshColab. Type and run the following command in a notebook cell:
   ```shell
   !pip install sshColab
   ```
   
3. Initiate the establishment of tunnels:
   ```python
   import sshColab
   sshColab.connect()
   ```
   The default TensorBoard log directory is `/log/fit`. You can reset it by
   passing into `connect()` the new value `LOG_DIR=/new/path/to/log`.
   
4. Retrieve information that is used for establishing the SSH connection:
   ```python
   sshColab.info()
   ```
   If you are using non-TPU runtimes, the setup instruction of TPU resolver is
   ignored.

5. Run function `kaggle()` to automate Kaggle API installation/authentication 
   and data downloads. The data is unzipped to the destination folder `/kaggle/input`. 
   ```python
   sshColab.kaggle([data='name-of-competition'])
   ```
   Note that the default competition name is "tabular-playground-series-mar-2021."

   

6. To disable ngrok tunnels created, run the command below:
   ```python
   sshColab.kill()
   ```

# Quickstart
A quickstart Colab notebook template is provided in the link below. Users can
find a simple end-to-end application starting from sshColab installation, SSH
tunnel creation, to the use of TensorBoard after training a 3-layer MNIST
convolutional neural network. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1TKM6Zqk4oY8RrFqGzrM-QEt92iQ0zxwm?usp=sharing) 

What's missed in this quickstart is how to may our way to Colab instances from
local machines. The reference listed below can be a start point for interested
users:

1. [Remote development over SSH on local VS Code](https://code.visualstudio.com/docs/remote/ssh-tutorial)
2. [Run SSH terminal on local PyCharm](https://www.jetbrains.com/help/pycharm/running-ssh-terminal.html)

# Release 

Version 0.2.0: Addition of Google Drive mounting.

Version 0.1.3: Addition of Kaggle API installation/authentication and competition data downloading function.


# Feedback
Comments and suggestions are welcome and appreciated. They can be sent to
lipin.juan02@gmail.com.

