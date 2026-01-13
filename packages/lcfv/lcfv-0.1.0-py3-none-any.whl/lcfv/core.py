import numpy as np
from scipy import linalg

def cholcov2(Sigma):
    """
    Cholesky-like decomposition for covariance matrix.
    Returns T such that T' * T approx Sigma.
    """
    # Simply use standard Cholesky if positive definite
    # Unlike MATLAB, numpy.linalg.cholesky returns lower triangular L where L*L.T = Sigma
    # MATLAB chol(Sigma) returns upper triangular R where R'*R = Sigma
    
    # We want T s.t. T.T @ T = Sigma. (MATLAB T=R).
    # If we get L, then L @ L.T = Sigma.
    # So T = L.T is a candidate if we follow MATLAB convention.
    
    try:
        L = np.linalg.cholesky(Sigma)
        return L.T
    except np.linalg.LinAlgError:
        # Not PD. Use eigenvalue decomposition.
        w, v = np.linalg.eigh(Sigma)
        
        # Keep positive eigenvalues
        idx = w > 0
        p = np.sum(idx)
        
        if p == 0:
            return np.zeros(Sigma.shape)
            
        w_pos = w[idx]
        v_pos = v[:, idx]
        
        # Sigma approx V * diag(w) * V'
        # = (V * sqrt(w)) * (sqrt(w) * V')
        # So T = diag(sqrt(w)) * V'
        
        T = np.dot(np.diag(np.sqrt(w_pos)), v_pos.T)
        return T

def solve_lcfv1(G, C, alpha):
    """
    Solve LCFV1 (Sparse).
    G: d x n feature matrix
    C: n x n label matrix
    alpha: regularization
    Returns M, W
    """
    d, n = G.shape
    
    # MATLAB: sv_t = 0.0000001
    sv_t = 1e-7
    
    if n >= d: # Over-determined
        # E = (G' \ C) / G -> MATLAB
        # E * G = G' \ C  => G' * E' * G = C' => G' * E * G = C (since C symmetric)
        # We need E such that G.T @ E @ G approx C
        
        # Using least squares logic from MATLAB implementation:
        # E = (G' \ C) / G
        # Step 1: X = G' \ C => Solve G' * X = C
        X, _, _, _ = np.linalg.lstsq(G.T, C, rcond=None)
        
        # Step 2: E = X / G => Solve E * G = X => G' * E' = X'
        Y, _, _, _ = np.linalg.lstsq(G.T, X.T, rcond=None)
        E = Y.T
        
    else: # Under-determined
        U, S, Vh = np.linalg.svd(G, full_matrices=False)
        # S is vector of singular values
        nn = np.sum(S > sv_t)
        
        S = S[:nn]
        U = U[:, :nn]
        Vh = Vh[:nn, :]
        V = Vh.T
        
        # C = V' * C * V
        C_prime = list_sq_mult(V.T, list_sq_mult(C, V)) # Just dot products
        C_prime = np.dot(V.T, np.dot(C, V))
        
        Sinv = np.diag(1.0 / S)
        Z1 = np.dot(Sinv, np.dot(C_prime, Sinv))
        
        # Construct Z
        # Z = [Z1 zeros; zeros zeros] matches sizes
        # Z is d x d
        Z = np.zeros((d, d))
        Z[:nn, :nn] = Z1
        
        E = np.dot(U, np.dot(Z, U.T))
        
    W = np.eye(d) + E
    # M = cholcov2((W + W')/2)
    M = cholcov2((W + W.T) / 2)
    
    return M, W

def solve_lcfv2(G, C, alpha):
    """
    Solve LCFV2 (Dense).
    """
    d, n = G.shape
    sv_t = 1e-7
    
    # A = cholcov2(C)
    A = cholcov2(C) # l x n
    l = A.shape[0]
    
    if n >= d: # Over-determined
        # E = A / G => E * G = A => G' * E' = A'
        Y, _, _, _ = np.linalg.lstsq(G.T, A.T, rcond=None)
        E = Y.T
    else: # Under-determined
        U, S, Vh = np.linalg.svd(G, full_matrices=False)
        nn = np.sum(S > sv_t)
        
        S = S[:nn]
        U = U[:, :nn]
        Vh = Vh[:nn, :]
        V = Vh.T
        
        # A = A * V
        A_prime = np.dot(A, V)
        Sinv = np.diag(1.0 / S)
        
        Z1 = np.dot(A_prime, Sinv) # l x nn
        
        # Z needs to be l x d
        Z = np.zeros((l, d))
        Z[:, :nn] = Z1
        
        E = np.dot(Z, U.T)
        
    # M = [eye(d); E]
    M = np.vstack([np.eye(d), E])
    return M

def list_sq_mult(A, B):
    return np.dot(A, B)
