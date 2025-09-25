Car Price Prediction — ML Pipeline + Airflow (README.txt)

OVERVIEW
This repository provides a reproducible machine-learning pipeline to predict car price (or price category, depending on your target column). It contains:
- Training code that builds features, compares multiple scikit-learn models via cross-validation, fits the best one, and saves the full pipeline to disk.
- Batch inference code that loads the latest saved pipeline and produces a timestamped CSV with predictions for new samples.
- An optional Apache Airflow DAG that orchestrates a two-step workflow: train → predict.

The code runs locally from the command line and can also be scheduled under Airflow.

--------------------------------------------------------------------------------
REPOSITORY LAYOUT

dags/
  hw_dag.py              Airflow DAG with two tasks: training then prediction
modules/
  pipeline.py            Training script: feature engineering, CV model selection, fit, persist
  predict.py             Inference script: load latest model artifact, score inputs → CSV
data/                    (recommended local tree; create as needed)
  train/                 training dataset(s), e.g., CSV
  test/                  samples for inference, e.g., JSON files
  models/                saved pipelines (created by training)
  predictions/           prediction CSVs (created by inference)

Note: The repo may not include the data/ folder. Create it locally with the subfolders above.

--------------------------------------------------------------------------------
REQUIREMENTS

Python: 3.10+ recommended

Core packages:
  pandas
  scikit-learn
  dill        (for serializing the fitted pipeline)

Optional (for scheduling with Airflow):
  apache-airflow>=2.4   (pin to your Python minor version)

Install (example):
  python -m venv .venv
  # On macOS/Linux:
  source .venv/bin/activate
  # On Windows:
  .venv\Scripts\activate

  pip install -U pip
  pip install pandas scikit-learn dill

  # Optional: Airflow (pin constraints to your Python & Airflow version)
  # Example (Python 3.10 + Airflow 2.8.x):
  pip install "apache-airflow>=2.8,<3.0" ^
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.4/constraints-3.10.txt"

--------------------------------------------------------------------------------
DATA EXPECTATIONS

Training data:
  - A tabular file (e.g., CSV) under data/train/ that contains your target column
    (either a numeric price or a categorical label such as price_category) and
    relevant car listing attributes as features.

Inference data:
  - One or more records under data/test/ (e.g., JSON files), using the same
    feature names/types expected by the trained pipeline.
  - Columns dropped by the pipeline during training are ignored at inference.

Keep feature names and dtypes consistent between training and inference.

--------------------------------------------------------------------------------
QUICKSTART (LOCAL)

1) Create folders and place data:
   mkdir -p data/train data/test data/models data/predictions
   # Put your training CSV(s) into data/train/
   # Put one or more JSON samples into data/test/

2) Train a model:
   python modules/pipeline.py
   - Performs cross-validation to compare candidate models
   - Fits the best model on the full training data
   - Saves a timestamped pipeline into data/models/

3) Run batch predictions:
   python modules/predict.py
   - Loads the latest saved pipeline from data/models/
   - Scores all records from data/test/
   - Writes a timestamped CSV into data/predictions/

--------------------------------------------------------------------------------
AIRFLOW USAGE (OPTIONAL)

1) Make the repository importable by Airflow
   - Place the repo under AIRFLOW_HOME or add its path to PYTHONPATH (e.g., via
     an environment variable or Docker volume mount).

2) Put the DAG file into your Airflow DAGs folder
   - dags/hw_dag.py defines a simple two-task pipeline: train → predict.
   - Adjust the CRON schedule inside the DAG as needed (e.g., daily run).

3) Start Airflow
   - Run the scheduler and webserver.
   - Enable the DAG in the UI and monitor runs.

Paths:
   - If your data lives outside the repo, update paths in the scripts or expose
     them via environment variables and read them in your Airflow tasks.

--------------------------------------------------------------------------------
CONFIGURATION TIPS

- Paths and environment:
  Use a consistent project root and keep data/ subfolders as shown above. If you
  store data elsewhere, either edit script paths, add CLI args (if you extend the
  scripts), or provide environment variables and read them in code.

- Models and metrics:
  Adjust candidate models, hyperparameters, and scoring metric in modules/pipeline.py
  to fit your business objectives (e.g., accuracy vs. F1 for classification, or
  RMSE/MAE for regression if predicting numeric price).

- Schema changes:
  If input feature names or dtypes change, retrain and re-persist the pipeline
  to avoid inference-time errors or degraded performance.

--------------------------------------------------------------------------------
TROUBLESHOOTING

- FileNotFoundError:
  Ensure your training CSV exists under data/train/ and test files under data/test/.
  Also verify that data/models/ exists after training and contains at least one
  saved pipeline artifact.

- Empty predictions or key errors:
  Check that your test JSON files contain the expected fields and compatible types.

- Airflow import errors:
  Confirm that the repository path is importable by the Airflow worker(s) (via
  PYTHONPATH or Docker volume mounts). Verify the DAG file is visible in the UI.

--------------------------------------------------------------------------------
ROADMAP

- Add requirements.txt with pinned versions for reproducibility
- Provide a tiny sample training CSV and example JSON inputs
- Add unit tests and a minimal CI workflow
- Optional experiment tracking (e.g., MLflow or Weights & Biases)
- Dockerfile / Compose for one-command local runs

--------------------------------------------------------------------------------
LICENSE

Add a LICENSE file (e.g., MIT) to clarify usage and redistribution terms.
