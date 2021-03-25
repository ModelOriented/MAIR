Google cloud storage is already configured in repository in file [.dvc/config](.dvc/config)

## Instruction for downloading artifacts
1. Init poetry:
```
poetry install
poetry shell
```
2. Authenticate google cloud with:
`gcloud auth application-default login`
3. Then you should be able to download artifacts
`dvc pull <artfact name>`
