"""
BudiajiMatrix - Library pengolahan matrix lengkap untuk Python
Cocok untuk keperluan time series, GSTAR, VARIMA, dan analisis statistik lainnya.
"""

from .operations import *

__version__ = "1.0.0"
__author__ = "Budi Aji"
__all__ = [
    # Operasi Dasar
    'add', 'subtract', 'multiply', 'element_multiply', 'scalar_multiply', 'divide',
    # Transformasi
    'transpose', 'inverse', 'pseudo_inverse', 'conjugate', 'adjoint',
    # Dekomposisi
    'cholesky', 'qr_decomposition', 'lu_decomposition', 'svd', 'eigendecomposition', 'schur',
    # Nilai Karakteristik
    'determinant', 'trace', 'rank', 'norm', 'condition_number', 'eigenvalues', 'eigenvectors',
    # Properti Matrix
    'is_symmetric', 'is_positive_definite', 'is_orthogonal', 'is_singular', 'is_diagonal',
    # Matrix Khusus
    'identity', 'zeros', 'ones', 'diagonal', 'random_matrix',
    # Statistik
    'mean', 'variance', 'std', 'covariance', 'correlation',
    # Operasi Baris/Kolom
    'row_sum', 'col_sum', 'row_mean', 'col_mean', 'normalize_rows', 'normalize_cols', 'standardize',
    # Solving Systems
    'solve_linear_system', 'least_squares',
    # Matrix Power
    'matrix_power', 'matrix_exp', 'matrix_log', 'matrix_sqrt',
    # Distance/Similarity
    'frobenius_distance', 'cosine_similarity'
]
