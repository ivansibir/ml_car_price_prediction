import glob
import os
from datetime import datetime

import dill
import pandas as pd

PATH = os.environ.get('PROJECT_PATH', '.')


def _load_latest_model():
    models_dir = os.path.join(PATH, 'data', 'models')
    os.makedirs(models_dir, exist_ok=True)
    candidates = sorted(glob.glob(os.path.join(models_dir, 'cars_pipe_*.pkl')))
    if not candidates:
        raise FileNotFoundError(f'No model files in {models_dir}')
    latest = candidates[-1]
    with open(latest, 'rb') as f:
        model = dill.load(f)
    return model, latest


def _read_test():
    test_dir = os.path.join(PATH, 'data', 'test')
    files = sorted(glob.glob(os.path.join(test_dir, '*.json')))
    if not files:
        raise FileNotFoundError(f'No *.json files in {test_dir}')

    frames = []
    for fp in files:
        # each JSON is a single record with the same fields as in the training data
        s = pd.read_json(fp, typ='series')
        frames.append(s.to_frame().T)

    df = pd.concat(frames, ignore_index=True)
    return df


def predict():
    model, _ = _load_latest_model()
    X = _read_test()

    preds = model.predict(X)
    out = pd.DataFrame({
        'id': X.get('id', pd.RangeIndex(len(X))),
        'prediction': preds
    })

    out_dir = os.path.join(PATH, 'data', 'predictions')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f'predictions_{datetime.now().strftime("%Y%m%d%H%M")}.csv')
    out.to_csv(out_path, index=False)
    print(f'Saved: {out_path}')


if __name__ == '__main__':
    predict()
