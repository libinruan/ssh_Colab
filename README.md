
# ssh_Colab
ssh_Colab is a Python module to facilitate remote access to Google Colaboratory
(Colab) through Secure Shell (SSH) connections, secured by a third-party
software, ngrok. ssh_Colab automates the tedious routine to set up ngrok
tunnels needed for TPU runtime applications and services like TensorBoard. It also
includes the function to automate the routine of Kaggle API installation/authentication
and download competition data.

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)
![python version](https://img.shields.io/badge/python-3.6%2C3.7%2C3.8-blue?logo=python)

# Prerequisites
- [ngrok](https://ngrok.com/) tunnel authtoken.
- Google account to access a [Colab](https://colab.research.google.com/notebooks/intro.ipynb) notebook.
- Local code editors such as VS Code or PyCharm to make the most of coding on Colab.
# Usage
1. Launch a Colab notebook. Choose a runtime type you prefer.

2. Install ssh_Colab. Type and run the following command in a notebook cell:
   ```shell
   !pip install ssh_Colab
   ```
   
3. Initiate the establishment of tunnels:
   ```python
   import ssh_Colab
   ssh_Colab.connect()
   ```
   The default TensorBoard log directory is `/log/fit`. You can reset it by
   passing into `connect()` the new value `LOG_DIR=/new/path/to/log`.
   
4. Retrieve information that is used for establishing the SSH connection:
   ```python
   ssh_Colab.info()
   ```
   If you are using non-TPU runtimes, the setup instruction of TPU resolver is
   ignored.

5. Function `kaggle()` to automate most of the process of Kaggle API installation/authentication and download and unzip competition dataset to folder `/kaggle/input`. The default competition name is "tabular-playground-series-mar-2021."

   ```python
   ssh_Colab.kaggle([data='name-of-competition'])
   ```

   

6. To disable ngrok tunnels created, run the command below:
   ```python
   ssh_Colab.kill()
   ```

# Quickstart
A quickstart Colab notebook template is provided in the link below. Users can
find a simple end-to-end application starting from SSH-Colab installation, SSH
tunnel creation, to the use of TensorBoard after training a 3-layer MNIST
convolutional neural network. 

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1TKM6Zqk4oY8RrFqGzrM-QEt92iQ0zxwm?usp=sharing) 

What's missed in this quickstart is how to may our way to Colab instances from
local machines. The reference listed below can be a start point for interested
users:

1. [Remote development over SSH on local VS Code](https://code.visualstudio.com/docs/remote/ssh-tutorial)
2. [Run SSH terminal on local PyCharm](https://www.jetbrains.com/help/pycharm/running-ssh-terminal.html)


# Feedback
Comments and suggestions are welcome and appreciated. They can be sent to
lipin.juan02@gmail.com.

