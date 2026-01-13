import json
import sysconfig
from pathlib import Path

import numpy as np
import onnxruntime as ort

MAX_LEN = 200


class Classifier:
    def __init__(
        self,
        session: ort.InferenceSession = None,
        stoi: dict = None,
        idx2label: dict = None,
    ):
        data_path = Path(sysconfig.get_paths()["data"]) / "models"

        if stoi is None or idx2label is None:
            model_path = data_path / "model.onnx"
            meta_path = data_path / "meta.json"

            if not meta_path.exists():
                raise RuntimeError(
                    "Metadata not found. Ensure correct installation or manually specify 'stoi' and 'idx2label.'"
                )

            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
            self.stoi = meta["stoi"]
            self.idx2label = meta["idx2label"]
        else:
            self.stoi = stoi
            self.idx2label = idx2label

        if session is None:
            model_path = data_path / "model.onnx"

            if not model_path.exists():
                raise RuntimeError(
                    "Model not found. Ensure correct installation or manually specify 'session.'"
                )

            self.session = ort.InferenceSession(model_path)
        else:
            self.session = session

    def _extract_bigrams(self, text: str):
        if len(text) < 2:
            return [text]
        return [text[i : i + 2] for i in range(len(text) - 1)]

    def _encode_bigrams(self, text: str):
        bigrams = self._extract_bigrams(text)
        tokens = [self.stoi.get(bg, 0) for bg in bigrams[:MAX_LEN]]
        if len(tokens) < MAX_LEN:
            tokens += [0] * (MAX_LEN - len(tokens))
        x = np.array(tokens, dtype=np.int64)[None, :]
        l = np.array([min(len(bigrams), MAX_LEN)], dtype=np.float32)  # noqa: E741
        return x, l

    def predict(self, text: str):
        x, l = self._encode_bigrams(text)  # noqa: E741
        outputs = self.session.run(None, {"input_text": x, "input_length": l})
        logits = np.array(outputs[0], dtype=np.float32)
        exps = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = (exps / np.sum(exps, axis=1, keepdims=True)).squeeze(0)
        top_indices = probs.argsort()[::-1][:3]
        return [(self.idx2label[str(i)], float(probs[i])) for i in top_indices]
