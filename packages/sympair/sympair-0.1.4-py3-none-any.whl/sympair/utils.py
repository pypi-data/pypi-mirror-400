import numpy as np

def index_of_true(arr):
    """
    Get the indices of all True values in an array.
    
    Parameters:
    arr (np.ndarray): Input boolean array.
    
    Returns:
    np.ndarray: Indices where the array is True.
    """
    if not isinstance(arr, np.ndarray) or arr.dtype != bool:
        raise ValueError("Input must be a numpy array with dtype=bool")
    # only allow 1D arrays
    if arr.ndim != 1:
        raise ValueError("Input must be a 1D array")
    # for 2D arrays, the np.where output a tuple of arrays, which is the index of the 1st and 2nd dimension.
    return np.where(arr)[0]

def test_index_of_true():
    """
    Test the index_of_true function for 1D and 2D arrays.
    """
    # Test 1D arrays
    assert np.array_equal(index_of_true(np.array([True, False, True])), np.array([0, 2]))
    assert np.array_equal(index_of_true(np.array([False, False, False])), np.array([]))
    
    # Test 2D arrays
    assert np.array_equal(index_of_true(np.array([[True, False], [False, True]])), np.array([[0,0],[1,1]]))
    assert np.array_equal(index_of_true(np.array([[False, False], [False, False]])), np.array([]))

def symbol_number(symbols):
    """
    Append a number to each symbol indicating its occurrence order.
    
    Parameters:
    symbols (list): List of chemical symbols.
    
    Returns:
    list: Symbols with appended numbers.
    """
    symbol_dict = {}
    new_symbols = []
    for s in symbols:
        if s not in symbol_dict:
            symbol_dict[s] = 1
        else:
            symbol_dict[s] += 1
        new_symbols.append(s + str(symbol_dict[s]))
    return new_symbols

def test_symbol_number():
    """
    Test the symbol_number function.
    """
    symbols = ["Sr", "Ti", "O", "O", "O"]
    assert symbol_number(symbols) == ["Sr1", "Ti1", "O1", "O2", "O3"]
    assert symbol_number(["Sr", "Sr", "Sr"]) == ["Sr1", "Sr2", "Sr3"]
    assert symbol_number(["Sr", "O", "Sr"]) == ["Sr1", "O1", "Sr2"]

def inverse_ijR(i, j, R):
    """
    Return the inverse of (i, j, R).
    
    Parameters:
    i, j (int): Indices.
    R (tuple): Tuple representing a vector.
    
    Returns:
    tuple: Inverted indices and negated vector.
    """
    return j, i, tuple(-Rq for Rq in R)

def standardize_ijR(i, j, R):
    """
    Return a standardized form of (i, j, R).
    
    Parameters:
    i, j (int): Indices.
    R (tuple): Tuple representing a vector.
    
    Returns:
    tuple: Standardized indices and vector, with a boolean indicating if reversed.
    """
    for v, Rv in enumerate(R):
        if Rv < 0:
            return (j, i, tuple(-Rq for Rq in R)), True
        elif Rv > 0:
            return (i, j, R), False
    if R == (0, 0, 0) and i > j:
        return (j, i, R), True
    return (i, j, R), False

def is_identity_matrix(matrix, atol=1e-6):
    """
    Check if a matrix is an identity matrix considering floating point errors.
    
    Parameters:
    matrix (list or np.ndarray): Input matrix.
    atol (float): Absolute tolerance for comparison.
    
    Returns:
    bool: True if the matrix is an identity matrix.
    """
    matrix = np.array(matrix)
    return np.allclose(matrix, np.eye(matrix.shape[0]), atol=atol)

def test_is_identity_matrix():
    """
    Test the is_identity_matrix function.
    """
    assert is_identity_matrix([[1, 0], [0, 1]])
    assert is_identity_matrix([[1, 0], [0, 1]], atol=1e-7)
    assert not is_identity_matrix([[1, 0], [1e-6, 1]], atol=1e-8)
    assert not is_identity_matrix([[1, 0], [0, 1.0001]])
    assert is_identity_matrix([[1, 0], [0, 1.0001]], atol=1e-3)

def test_standardize_ijR():
    """
    Test the standardize_ijR function.
    """
    assert standardize_ijR(0, 1, (0, 0, 0)) == ((0, 1, (0, 0, 0)), False)
    assert standardize_ijR(1, 0, (0, 0, 0)) == ((0, 1, (0, 0, 0)), True)
    # Additional test cases for edge conditions
    assert standardize_ijR(2, 3, (-1, -1, -1)) == ((3, 2, (1, 1, 1)), True)

if __name__ == "__main__":
    test_symbol_number()
    test_standardize_ijR()
    test_is_identity_matrix()
    test_index_of_true()  # Added call to the new test function
