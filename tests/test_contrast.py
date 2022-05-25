from emgdecompy import contrast as emg
import numpy as np

def test_skew():
    """
    Run unit tests on skew() function from EMGdecomPy.
    """
    for i in range(0, 10):
        x = np.random.randint(1,1000)
        y = np.random.randint(1,1000)

        test_arr = np.random.choice(np.arange(-1000, 1000), size=(x, y)) # np.random.rand(x, y)

        # test base version of contrast function 
        manual_calc = np.power(test_arr, 3) / 3 # calculate by hand 
        emg_no_deriv = emg.skew(test_arr)    

        assert np.array_equal(manual_calc, emg_no_deriv), "Contrast function incorrectly applied."

        # reverse calculate initial values in input 
        reverse_calc = np.cbrt(emg_no_deriv[-1][-1] * 3)
        
        assert np.isclose(reverse_calc, test_arr[-1][-1]), "Contrast function incorrectly applied."

        # test first derivative of contrast function 
        manual_calc_deriv = np.power(test_arr, 2) # first derivative of x^3/3 = x^2
        emg_deriv = emg.skew(test_arr, der=True)

        assert np.allclose(manual_calc_deriv, emg_deriv), "First derivative not calculated correctly."

        # reverse calculate initial values in input 
        reverse_calc_der = np.sqrt(emg_deriv[-1][-1])
        abs_test_value = abs(test_arr[-1][-1]) # absolute because +/- is lost in back calculation
        
        assert np.isclose(reverse_calc_der, abs_test_value), "Contrast function incorrectly applied."

def test_log_cosh():
    """
    Run unit tests on log_cosh() function from EMGdecomPy.
    """
    
    for i in range (0, 5):

        x = np.random.randint(0, 709) 
        assert x <= 709, "X is too large, will result in calculation overflow."

        # test base contrast function, log(cosh(x))
        x_cosh = 1/2 * (np.exp(x) + np.exp(-x))  # manually calculate cosh(x) 
        x_log = np.log(x_cosh)

        assert x_log == emg.log_cosh(x), "Base contrast function incorrectly calculated."

        # test first derivative of contrast function, tanh(x)
        x_tanh = np.sinh(x)/np.cosh(x) # manually calculate tanh(x)

        assert np.isclose(x_tanh, emg.log_cosh(x, der=True)), "1st derivative fx incorrectly calculated."

def test_exp_sq():
    """
    Run unit tests on exp_sq() function from EMGdecomPy.
    """
    
    for i in range (0, 10):

        x = np.random.randint(0, 703)

        # base function = exp((-x^2/2))
        # calculate inner part of function
        fx = - np.power(x, 2) / 2

        # test base contrast function, no derivative
        exp_fx = np.exp(fx)
        assert emg.exp_sq(x) == exp_fx, "Base contrast function incorrectly calculated."

        # test first derivative of base contrast function using exponent power rule
        der_fx = np.exp(fx / 2) * np.exp(fx / 2) * -x 
        assert np.isclose(emg.exp_sq(x, der = True), der_fx), "First derivative function incorrectly calculated."
