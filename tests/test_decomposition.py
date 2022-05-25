import emgdecompy as emg
import numpy as np
from scipy.io import loadmat
from scipy import linalg
from test_preprocessing import create_emg_data

def test_initialize_w():
    """
    Run unit tests on initialize_w function from EMGdecomPy.
    """
    x = np.array([[1, 2, 3, 4,], [5, 7, 9, 11], [12, 15, 18, 21]])
    assert (emg.decomposition.initialize_w(x) == np.array([4, 11, 21])).all(), "Returned wrong column."

    x = np.zeros((5, 5))
    assert emg.decomposition.initialize_w(x).shape == np.zeros(5).shape, "Output contains wrong dimensions."

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
    max_iter = 10

    # Call and process EMG data
    gl_10 = loadmat('data/raw/GL_10.mat')
    signal = gl_10["SIG"]
    # signal = create_emg_data(q=215473)

    x = emg.preprocessing.flatten_signal(signal)
    x = emg.preprocessing.center_matrix(x)
    x = emg.preprocessing.extend_all_channels(x, 16)
    z = emg.preprocessing.whiten(x)

    n = 0

    # Initialize separation vectors and matrix B
    w_curr = emg.decomposition.initialize_w(z)
    w_prev = emg.decomposition.initialize_w(z)
    B = np.zeros((1088, 1))

    while linalg.norm(np.dot(w_curr.T, w_prev) - 1) > Tolx:

        # Calculate separation vector
        b = np.dot(w_prev, z)
        g_b = emg.contrast.apply_contrast(b)
        A = (emg.contrast.apply_contrast(b, der=True)).mean()
        w_curr = (z * g_b).mean(axis=1) - A * w_prev

        # Orthogonalize and normalize separation vector
        w_curr = emg.decomposition.orthogonalize(w_curr, B)
        w_curr = emg.decomposition.normalize(w_curr)

        # Set previous separation vector to current separation vector
        w_prev = w_curr

        # If n exceeds max iteration exit while loop
        n += 1
        if n > max_iter:
            break
                
    assert (w_curr == emg.decomposition.separation(z, B, Tolx, emg.contrast.skew, max_iter)).all(), "Separation vector incorrectly calculated."
        
def test_orthogonalize():
    """
    Run unit tests on orthogonalize() function from EMGdecomPy.
    """
    for i in range(0, 10):
        x = np.random.randint(1, 100)
        y = np.random.randint(1, 100)
        z = np.random.randint(1, 100) 

        w = np.random.randn(x, y) * 1000 
        b = np.random.randn(x, z) * 1000

        assert b.T.shape[1] == w.shape[0], "Dimensions of input arrays are not compatible."

        # orthogonalize by hand 
        ortho = w - b @ (b.T @ w)

        fx = emg.decomposition.orthogonalize(w, b)

        assert np.array_equal(ortho, fx), "Manually calculated array not equivalent to emg.orthogonalize()"
        assert fx.shape == w.shape, "The output shape of w is incorrect."
