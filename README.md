# Apache Airflow Data Science Stack

This repo runs Apache Airflow `2.9.3` on Python `3.12` with a custom Docker
image that installs common data science libraries:

- `numpy==1.26.4`
- `pandas==2.1.4`
- `scikit-learn==1.4.2`
- `mlflow==2.13.0`

The image is based on `apache/airflow:2.9.3-python3.12`, pins
`apache-airflow==2.9.3` during dependency installation, and installs Python
packages with `pip install --no-cache-dir`. The Docker build also runs
`pip check` to catch incompatible dependency resolution early.

## Project Layout

```text
.
├── dags/                 # Airflow DAGs
├── logs/                 # Airflow task and scheduler logs
├── plugins/              # Optional Airflow plugins
├── config/               # Optional local Airflow config
├── mlruns/               # Local MLflow tracking artifacts
├── Dockerfile            # Custom Airflow image
└── docker-compose.yaml   # Local Airflow stack
```

## Prerequisites

- Docker Engine or Docker Desktop
- Docker Compose v2, available as `docker compose`
- At least 4 GB RAM available to Docker

## Configure Environment

Create the local folders used by Docker bind mounts:

```bash
mkdir -p dags logs plugins config mlruns
```

Create `.env` if it does not already exist:

```bash
cat > .env <<EOF
AIRFLOW_UID=$(id -u)
FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF
```

On Windows, use this instead:

```text
AIRFLOW_UID=50000
FERNET_KEY=<generated-fernet-key>
```

You can generate a Fernet key with:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Build the Airflow Image

Build the custom image:

```bash
docker compose build
```

For a completely fresh build without Docker layer cache:

```bash
docker compose build --no-cache
```

## Initialize Airflow

Run the one-time database migration and admin user creation:

```bash
docker compose up airflow-init
```

The default Airflow login is:

```text
Username: airflow
Password: airflow
```

Override these in `.env` if needed:

```text
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

## Start Airflow

Start the full local stack:

```bash
docker compose up -d
```

Open the Airflow web UI:

```text
http://localhost:8080
```

The included DAGs in `dags/` should appear in the UI after the scheduler parses
them.

## Verify Installed Packages

Check the Airflow and data science package imports inside the custom image:

```bash
docker compose run --rm --no-deps airflow-cli python -c "import airflow, numpy, pandas, sklearn, mlflow; print('airflow', airflow.__version__)"
```

Expected Airflow version:

```text
airflow 2.9.3
```

## MLflow Tracking

The compose file sets:

```text
MLFLOW_TRACKING_URI=file:/opt/airflow/mlruns
```

This maps to the local `mlruns/` directory so DAG tasks can write MLflow runs and
artifacts without needing a separate MLflow tracking server.

## Useful Commands

View container status:

```bash
docker compose ps
```

Follow logs:

```bash
docker compose logs -f airflow-scheduler airflow-webserver airflow-worker
```

Stop containers:

```bash
docker compose down
```

Stop containers and remove the Postgres metadata volume:

```bash
docker compose down --volumes --remove-orphans
```

## Notes

- `docker-compose.yaml` uses `CeleryExecutor`, backed by Postgres and Redis.
- Airflow example DAGs are disabled with `AIRFLOW__CORE__LOAD_EXAMPLES=false`.
- Avoid using `_PIP_ADDITIONAL_REQUIREMENTS` for normal development. Add Python
  dependencies to `Dockerfile`, rebuild the image, then restart the stack.
