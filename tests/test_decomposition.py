import emgdecompy as emg
import numpy as np
from scipy.io import loadmat
from scipy import linalg

def test_normalize():
    """
    Run unit test on normalize function from EMGdecomPy.
    """
    for i in range(0, 10):

        # initialize array
        x = np.random.randint(1, 1000)
        y = np.random.randint(1, 1000)

        fake_data = np.random.rand(x, y)

        # calculate Frobenius norm manually
        squared = fake_data ** 2
        summed = squared.sum()
        frob_norm = np.sqrt(summed)

        # this is how the normalize() calculates Frobenius norm
        fx_norm = np.linalg.norm(fake_data)

        assert np.allclose(frob_norm, fx_norm), "Frobenius norm incorrectly calculated."

        # normalize
        normalized = fake_data / frob_norm

        fx = emg.decomposition.normalize(fake_data)

        assert np.allclose(normalized, fx), "Array normalized incorrectly."

def test_separation():
    """
    Run unit test on separation function from EMGdecomPy.
    """
    Tolx = 10e-4
    random_state = np.random.randint(100, 1000)
    gl_10 = loadmat('data/raw/GL_10.mat')
    signal = gl_10["SIG"]
    signal = emg.preprocessing.flatten_signal(signal)
    x = emg.preprocessing.center_matrix(signal)
    x = emg.preprocessing.extend_all_channels(signal, 16)
    z = emg.preprocessing.whiten(x)

    n = 0
    np.random.seed(random_state)
    w_curr = np.random.rand(z.shape[0])
    w_prev = np.random.rand(z.shape[0])
    B = np.zeros((1088, 1))
    max_iter = 10

    while linalg.norm(np.dot(w_curr.T, w_prev) - 1) > Tolx:
        b = np.dot(w_prev, z)
        g_b = emg.contrast.apply_contrast(b)
        A = (emg.contrast.apply_contrast(b, der=True)).mean()
        w_curr = (z * g_b).mean(axis=1) - A * w_prev
        w_curr = emg.decomposition.orthogonalize(w_curr, B)
        w_curr = emg.decomposition.normalize(w_curr)
        w_prev = w_curr
        n += 1
        if n > max_iter:
            break
                
    assert (w_curr == emg.decomposition.separation(z, B, Tolx, emg.contrast.skew, max_iter, random_state)).all(), "Separation vector incorrectly calculated."