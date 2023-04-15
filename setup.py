import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ssh-Colab",
    version="0.4.17",
    author="Li-Pin Juan",
    author_email="lipin.juan02@gmail.com",
    description="Google Colab secure shell connection helper that automates ngrok tunnels creation (for SSH, TPU, and TensorBoard) and facilitates the use of Google Cloud Storage, Google Drive, and Kaggle Data API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/libinruan/ssh_Colab",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords=['tpu', 'colab', 'ssh', 'tensorboard', 'kaggle', 'google drive', 'gcs', 'google cloud storage', 'secure shell']
)