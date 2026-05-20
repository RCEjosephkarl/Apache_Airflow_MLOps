ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.12

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ARG AIRFLOW_VERSION=2.9.3
ARG PYTHON_VERSION=3.12

ENV PIP_NO_CACHE_DIR=1

USER airflow

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    numpy==1.26.4 \
    pandas==2.1.4 \
    scikit-learn==1.4.2 \
    mlflow==2.13.0 \
    && pip check
