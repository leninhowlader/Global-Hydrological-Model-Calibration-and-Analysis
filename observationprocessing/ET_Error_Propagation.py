import numpy as np, os

os.chdir(os.path.join(os.getcwd(), 'observationprocessing'))

def error_propagation(errors):
    if not type(errors) is np.ndarray: errors = np.array(errors)
    return np.sqrt(np.sum(errors**2))

