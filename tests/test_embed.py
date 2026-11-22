import numpy as np

from app.embed import embed_texts


def test_onnx_backend_returns_normalised_vectors(monkeypatch):
    monkeypatch.setenv("EMBED_BACKEND", "onnx")
    monkeypatch.setattr("app.embed.get_onnx_model", lambda: (lambda texts: [[3.0, 4.0] for _ in texts]))
    out = embed_texts(["saline soil", "drought"])
    assert out.shape == (2, 2)
    assert np.allclose(out[0], [0.6, 0.8])  # (3, 4) scaled to length 1
    assert np.allclose(np.linalg.norm(out, axis=1), 1.0)