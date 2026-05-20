"""
ml_pipeline.py
--------------
A minimal ML pipeline DAG demonstrating the TaskFlow API.

Design decisions:
- @dag + @task decorators (TaskFlow API) are preferred over legacy
  PythonOperator because they handle XCom serialisation automatically.
- catchup=False prevents Airflow from backfilling all missed daily runs
  since start_date — important for ML pipelines with expensive compute.
- tags make DAGs filterable in the Web UI across large projects.
"""
from __future__ import annotations

from datetime import datetime

from airflow.decorators import dag, task


@dag(
    dag_id="ml_pipeline",
    schedule="@daily",                    # or use a cron string: "0 2 * * *"
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["mlops", "demo"],
    doc_md=__doc__,
)
def ml_pipeline() -> None:

    @task()
    def extract_data() -> dict:
        """Simulate reading raw data from a data lake."""
        return {"rows": 1_000, "features": 20, "source": "s3://bucket/raw/"}

    @task()
    def preprocess(data: dict) -> dict:
        """Apply feature engineering. Returns processed dataset metadata."""
        print(f"Processing {data['rows']} rows with {data['features']} features")
        return {**data, "processed": True, "split": 0.8}

    @task()
    def train_model(data: dict) -> str:
        """
        Train model. In production, replace with:
          - BashOperator calling a Python training script, or
          - KubernetesPodOperator for GPU-accelerated training.
        """
        print(f"Training on {int(data['rows'] * data['split'])} training rows")
        return "models/model_v1.pkl"

    @task()
    def evaluate(model_path: str) -> None:
        """Compute metrics and log to MLflow (add MLflowClient here)."""
        print(f"Evaluating model at: {model_path}")
        metrics = {"accuracy": 0.93, "f1": 0.91}
        print(f"Metrics: {metrics}")

    # ── Define the pipeline graph ──────────────────────────────────────────
    raw_data  = extract_data()
    processed = preprocess(raw_data)
    model     = train_model(processed)
    evaluate(model)


ml_pipeline()
