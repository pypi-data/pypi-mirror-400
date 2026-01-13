import numpy as np
import scipy.linalg
from sklearn.linear_model import OrthogonalMatchingPursuit
import cvxpy as cp

def solve_A_fullrank(X, Y):
    """
    Solve Y = AX for A using standard pseudo-inverse.
    
    Args:
        X: [m, N] input matrix
        Y: [l, N] output matrix
        
    Returns:
        A: [l, m] recovered matrix
    """
    # Y.T = X.T @ A.T -> solve for A.T
    # scipy.linalg.lstsq solves A x = B
    # We want AX = Y => X.T A.T = Y.T
    # So lstsq(X.T, Y.T) gives A.T
    
    solution, residuals, rank, s = scipy.linalg.lstsq(X.T, Y.T)
    return solution.T

def solve_A_Fnorm(X, Y):
    """
    Solve Y = AX for A by minimizing Frobenius norm of changes (low rank approx).
    
    Args:
        X: [m, N]
        Y: [l, N]
        
    Returns:
        A: [l, m]
    """
    threshold = 0.01
    l = Y.shape[0]
    m = X.shape[0]
    
    # SVD of X: X = U * S * V.T
    U, s_vals, Vt = scipy.linalg.svd(X, full_matrices=True)
    
    # Remove small singular values
    mask = s_vals > threshold
    nn = np.sum(mask)
    
    S_reduced = s_vals[:nn]
    V_reduced = Vt[:nn, :].T # V in MATLAB is V from SVD (m x m), here we need V corresponding to X's columns?
    # Python svd returns Vt (transposed).
    # X (m x N) = U (m x K) * S (K) * Vt (K x N)
    # In MATLAB: [U, S, V] = svd(X) => X = U * S * V'.
    # So Python's Vt is MATLAB's V'.
    # MATLAB: V = V(:, 1:nn). Python: Vt = Vt[:nn, :] => V = Vt.T
    
    V_reduced = Vt[:nn, :].T # shape [N, nn]
    
    # Regression
    # Y = Y * V
    Y_proj = Y @ V_reduced
    
    # Sinv = diag(1 ./ diag(S))
    Sinv = np.diag(1.0 / S_reduced)
    
    # Z1 = Y * Sinv
    Z1 = Y_proj @ Sinv
    
    # Z = [Z1, zeros(l, m - nn)]
    # Wait, Z1 is [l, nn]. We need [l, m].
    # So we pad columns.
    Z = np.hstack([Z1, np.zeros((l, m - nn))])
    
    # A = Z * U'
    A = Z @ U.T
    
    return A

def solve_A_0norm(X, Y):
    """
    Solve Y = AX for A by minimizing L0-norm using OMP.
    
    Args:
        X: [m, N]
        Y: [l, N]
        
    Returns:
        A: [l, m]
    """
    m, N = X.shape
    l = Y.shape[0]
    
    # Construct Kronecker product
    # vec(AX) = (X.T \kron I) vec(A) = vec(Y)
    # XX = kron(X', eye(l))
    # In Python, X.T has shape [N, m]. Eye is [l, l].
    # Kron results in [N*l, m*l].
    
    XX = np.kron(X.T, np.eye(l))
    YY = Y.flatten(order='F') # MATLAB vec(Y) is column-major
    
    # Solve strictly speaking: YY = XX @ vec(A)
    # OMP
    # We need to pick tolerance or n_nonzero_coefs.
    # The MATLAB wrapper around SparseLab SolveOMP likely uses a default or max iterations.
    # checking MATLAB code: AA = SolveOMP(XX, YY, m1 * m2);
    # m1*m2 is the max cardinality (all atoms). 
    # If passed as cardinality, it solves exactly? 
    # But usually OMP is for sparse recovery.
    # Let's use sklearn OMP.
    # Sklearn OMP requires `n_nonzero_coefs` or `tol`.
    # If we want to recover *any* solution, we might as well use lstsq if it's not sparse.
    # Assuming we want sparse solution.
    # Since we don't have the param, let's look at what MATLAB code effectively does.
    # It passes m1*m2 as 'cardinality' (3rd arg). 
    # In SparseLab, SolveOMP(A, y, k) runs k iterations.
    # If k = total dimensions, it finds a full solution (dense).
    # That defeats the purpose of '0norm' optimization if it just runs to completion.
    # HOWEVER, maybe it stops earlier if residual is 0?
    
    # For now, let's assume we want substantial sparsity or good fit.
    # Let's set tol=None and n_nonzero_coefs=min(m*l, N*l) ? 
    # Actually, let's try to match behavior: run until residual is small?
    
    omp = OrthogonalMatchingPursuit(n_nonzero_coefs=None, tol=1e-6)
    omp.fit(XX, YY)
    
    AA = omp.coef_
    
    # Reshape back to A
    A = AA.reshape((l, m), order='F')
    return A

def solve_A_1norm(X, Y):
    """
    Solve Y = AX for A by minimizing L1-norm (Basis Pursuit).
    
    Args:
        X: [m, N]
        Y: [l, N]
        
    Returns:
        A: [l, m]
    """
    m, N = X.shape
    l = Y.shape[0]
    
    XX = np.kron(X.T, np.eye(l))
    YY = Y.flatten(order='F')
    
    # Define variable (flattened A)
    n_vars = m * l
    a_vec = cp.Variable(n_vars)
    
    # Minimize L1 norm subject to XX @ a_vec == YY
    objective = cp.Minimize(cp.norm(a_vec, 1))
    constraints = [XX @ a_vec == YY]
    
    prob = cp.Problem(objective, constraints)
    prob.solve()
    
    AA = a_vec.value
    A = AA.reshape((l, m), order='F')
    
    return A
