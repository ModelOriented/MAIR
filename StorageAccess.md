Google cloud storage is already configured in repository in file [.dvc/config](.dvc/config)
```
[core]
    remote = google-cloud
['remote "google-cloud"']
    url = gs://mair-dvc-storage
```
# Pre-requirements
* python 3.8
* poetry
## Installation instruction
### Python
The easies way to install python 3.8 is to install miniconda
1. Download [miniconda installer](https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh)
2. Run it (`./Miniconda3-latest-Linux-x86_64.sh`)
3. Initialize conda `conda init`
### Poetry
Download and install poetry by running command:
```
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
```
Reopen your current shell to load poetry to `$PATH`.
# Instruction for downloading artifacts
1. In repository folder run: 
```
poetry install
poetry shell
```
2. Install Google Cloud SDK following https://cloud.google.com/sdk/docs/install
3. Authenticate google cloud with:
`gcloud auth application-default login`
4. Then you should be able to download artifacts
`dvc pull <artfact name>`
