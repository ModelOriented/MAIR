FROM continuumio/anaconda3

RUN conda install python=3.8

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
