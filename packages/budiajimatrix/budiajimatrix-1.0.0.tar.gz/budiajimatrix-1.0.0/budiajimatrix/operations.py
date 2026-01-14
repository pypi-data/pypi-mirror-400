"""
BudiajiMatrix - Library pengolahan matrix lengkap untuk Python
Author: Budi Aji
"""

import numpy as np
from scipy import linalg


# ========== OPERASI DASAR ==========
def add(matrix1, matrix2):
    """Penjumlahan matrix"""
    return matrix1 + matrix2


def subtract(matrix1, matrix2):
    """Pengurangan matrix"""
    return matrix1 - matrix2


def multiply(matrix1, matrix2):
    """Perkalian matrix"""
    return np.dot(matrix1, matrix2)


def element_multiply(matrix1, matrix2):
    """Perkalian elemen per elemen (Hadamard product)"""
    return np.multiply(matrix1, matrix2)


def scalar_multiply(matrix, scalar):
    """Perkalian matrix dengan skalar"""
    return scalar * matrix


def divide(matrix, scalar):
    """Pembagian matrix dengan skalar"""
    return matrix / scalar


# ========== TRANSFORMASI ==========
def transpose(matrix):
    """Transpose matrix"""
    return np.transpose(matrix)


def inverse(matrix):
    """Inverse matrix"""
    return np.linalg.inv(matrix)


def pseudo_inverse(matrix):
    """Moore-Penrose pseudo-inverse (untuk matrix singular)"""
    return np.linalg.pinv(matrix)


def conjugate(matrix):
    """Konjugat matrix (untuk complex numbers)"""
    return np.conjugate(matrix)


def adjoint(matrix):
    """Adjoint matrix (conjugate transpose)"""
    return np.conjugate(np.transpose(matrix))


# ========== DEKOMPOSISI ==========
def cholesky(matrix):
    """Dekomposisi Cholesky (untuk matrix positif definit)"""
    return np.linalg.cholesky(matrix)


def qr_decomposition(matrix):
    """Dekomposisi QR"""
    Q, R = np.linalg.qr(matrix)
    return Q, R


def lu_decomposition(matrix):
    """Dekomposisi LU"""
    P, L, U = linalg.lu(matrix)
    return P, L, U


def svd(matrix):
    """Singular Value Decomposition"""
    U, S, Vt = np.linalg.svd(matrix)
    return U, S, Vt


def eigendecomposition(matrix):
    """Dekomposisi Eigen (eigenvalues dan eigenvectors)"""
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    return eigenvalues, eigenvectors


def schur(matrix):
    """Dekomposisi Schur"""
    T, Z = linalg.schur(matrix)
    return T, Z


# ========== NILAI-NILAI KARAKTERISTIK ==========
def determinant(matrix):
    """Determinan matrix"""
    return np.linalg.det(matrix)


def trace(matrix):
    """Trace matrix (jumlah diagonal utama)"""
    return np.trace(matrix)


def rank(matrix):
    """Rank matrix"""
    return np.linalg.matrix_rank(matrix)


def norm(matrix, ord=None):
    """Norm matrix (Frobenius, L1, L2, dll)"""
    return np.linalg.norm(matrix, ord=ord)


def condition_number(matrix):
    """Condition number (untuk cek stabilitas numerik)"""
    return np.linalg.cond(matrix)


def eigenvalues(matrix):
    """Eigenvalues (akar ciri)"""
    return np.linalg.eigvals(matrix)


def eigenvectors(matrix):
    """Eigenvectors (vektor ciri)"""
    _, eigenvectors = np.linalg.eig(matrix)
    return eigenvectors


# ========== PROPERTI MATRIX ==========
def is_symmetric(matrix, tol=1e-10):
    """Cek apakah matrix simetris"""
    return np.allclose(matrix, matrix.T, atol=tol)


def is_positive_definite(matrix):
    """Cek apakah matrix positif definit"""
    try:
        np.linalg.cholesky(matrix)
        return True
    except np.linalg.LinAlgError:
        return False


def is_orthogonal(matrix, tol=1e-10):
    """Cek apakah matrix orthogonal (Q @ Q.T = I)"""
    identity = np.eye(matrix.shape[0])
    return np.allclose(matrix @ matrix.T, identity, atol=tol)


def is_singular(matrix):
    """Cek apakah matrix singular (det = 0)"""
    return np.abs(np.linalg.det(matrix)) < 1e-10


def is_diagonal(matrix, tol=1e-10):
    """Cek apakah matrix diagonal"""
    return np.allclose(matrix, np.diag(np.diagonal(matrix)), atol=tol)


# ========== MATRIX KHUSUS ==========
def identity(n):
    """Buat identity matrix n x n"""
    return np.eye(n)


def zeros(shape):
    """Buat matrix nol"""
    return np.zeros(shape)


def ones(shape):
    """Buat matrix satu"""
    return np.ones(shape)


def diagonal(values):
    """Buat diagonal matrix dari array"""
    return np.diag(values)


def random_matrix(shape, distribution='uniform'):
    """Buat random matrix"""
    if distribution == 'uniform':
        return np.random.rand(*shape)
    elif distribution == 'normal':
        return np.random.randn(*shape)
    else:
        raise ValueError("distribution harus 'uniform' atau 'normal'")


# ========== STATISTIK ==========
def mean(matrix, axis=None):
    """Mean matrix (rata-rata)"""
    return np.mean(matrix, axis=axis)


def variance(matrix, axis=None):
    """Variance matrix"""
    return np.var(matrix, axis=axis)


def std(matrix, axis=None):
    """Standard deviation matrix"""
    return np.std(matrix, axis=axis)


def covariance(matrix):
    """Covariance matrix"""
    return np.cov(matrix.T)


def correlation(matrix):
    """Correlation matrix"""
    return np.corrcoef(matrix.T)


# ========== OPERASI BARIS/KOLOM ==========
def row_sum(matrix):
    """Jumlah per baris"""
    return np.sum(matrix, axis=1)


def col_sum(matrix):
    """Jumlah per kolom"""
    return np.sum(matrix, axis=0)


def row_mean(matrix):
    """Rata-rata per baris"""
    return np.mean(matrix, axis=1)


def col_mean(matrix):
    """Rata-rata per kolom"""
    return np.mean(matrix, axis=0)


def normalize_rows(matrix):
    """Normalisasi per baris (setiap baris jadi unit vector)"""
    row_norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / row_norms


def normalize_cols(matrix):
    """Normalisasi per kolom"""
    col_norms = np.linalg.norm(matrix, axis=0, keepdims=True)
    return matrix / col_norms


def standardize(matrix):
    """Standardisasi matrix (mean=0, std=1)"""
    return (matrix - np.mean(matrix, axis=0)) / np.std(matrix, axis=0)


# ========== SOLVING SYSTEMS ==========
def solve_linear_system(A, b):
    """Solve Ax = b"""
    return np.linalg.solve(A, b)


def least_squares(A, b):
    """Least squares solution"""
    return np.linalg.lstsq(A, b, rcond=None)[0]


# ========== MATRIX POWER ==========
def matrix_power(matrix, n):
    """Matrix pangkat n"""
    return np.linalg.matrix_power(matrix, n)


def matrix_exp(matrix):
    """Matrix exponential"""
    return linalg.expm(matrix)


def matrix_log(matrix):
    """Matrix logarithm"""
    return linalg.logm(matrix)


def matrix_sqrt(matrix):
    """Matrix square root"""
    return linalg.sqrtm(matrix)


# ========== DISTANCE/SIMILARITY ==========
def frobenius_distance(matrix1, matrix2):
    """Jarak Frobenius antara dua matrix"""
    return np.linalg.norm(matrix1 - matrix2, ord='fro')


def cosine_similarity(vector1, vector2):
    """Cosine similarity antara dua vektor"""
    return np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
