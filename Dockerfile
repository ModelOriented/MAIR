FROM continuumio/anaconda3

RUN apt-get update -y \
    && apt-get install apt-transport-https ca-certificates gnupg -y

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" >> /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - \
    && apt-get update -y \
    && apt-get install google-cloud-sdk -y

RUN conda install python=3.8 -y
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="/root/.poetry/bin:${PATH}"
WORKDIR /home/sgizinski/MAIR
# TODO: change do $HOME
ADD pyproject.toml .
ADD poetry.lock .

RUN poetry install
