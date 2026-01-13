import numpy as np

def gmm_em(X, K, max_iters=100):
    """
    Train GMM using EM algorithm.
    X: D x N
    K: int
    Returns: w (1xK), mu (DxK), sigma (DxK)
    """
    D, N = X.shape
    
    # Initialization
    # Use random choice instead of random permutation of all N
    indices = np.random.choice(N, K, replace=False)
    mu = X[:, indices].copy() # D x K
    
    global_var = np.var(X, axis=1, ddof=0)
    sigma = np.tile(global_var[:, np.newaxis], (1, K)) # D x K
    
    w = np.ones(K) / K
    
    min_sigma = 1e-6
    last_ll = -np.inf
    
    for iteration in range(max_iters):
        # E-step
        # Compute log responsibilities
        log_rho = np.zeros((K, N))
        
        term1 = D * np.log(2 * np.pi)
        
        for k in range(K):
            # bsxfun minus equivalent
            diff = X - mu[:, [k]] # D x N
            # sum((diff.^2) ./ sigma)
            sq_diff_norm = np.sum((diff**2) / sigma[:, [k]], axis=0) # descriptor-wise sum -> 1 x N
            log_det = np.sum(np.log(sigma[:, k]))
            
            log_rho[k, :] = np.log(w[k]) - 0.5 * (term1 + log_det + sq_diff_norm)
        
        # Log-sum-exp
        max_log_rho = np.max(log_rho, axis=0)
        rho = np.exp(log_rho - max_log_rho)
        sum_rho = np.sum(rho, axis=0)
        gamma = rho / sum_rho # K x N
        
        current_ll = np.sum(np.log(sum_rho) + max_log_rho)
        
        if iteration > 0 and abs(current_ll - last_ll) < 1e-4 * abs(last_ll):
            print(f"GMM converged at iteration {iteration+1}")
            break
        last_ll = current_ll
        
        # M-step
        Nk = np.sum(gamma, axis=1) # K
        
        w = Nk / N
        
        for k in range(K):
            # Update mu
            # X * gamma' -> (D x N) * (N x 1)
            mu[:, k] = np.dot(X, gamma[k, :]) / Nk[k]
            
            # Update sigma
            diff = X - mu[:, [k]]
            # Weighted sum of squared diffs
            sigma[:, k] = np.dot(diff**2, gamma[k, :]) / Nk[k]
            
            # Regularize
            sigma[:, k] = np.maximum(sigma[:, k], min_sigma)
            
    return w, mu, sigma

def fv_train(X, K, pca_dim=None):
    """
    Train PCA and GMM.
    X: D x N
    """
    D, N = X.shape
    
    pca_transform = np.eye(D)
    pca_mean = np.zeros(D)
    
    if pca_dim is not None and pca_dim < D:
        print(f"Training PCA ({D} -> {pca_dim})...")
        pca_mean = np.mean(X, axis=1)
        X_centered = X - pca_mean[:, np.newaxis]
        
        # Covariance
        C = np.dot(X_centered, X_centered.T) / (N - 1)
        U, S, Vh = np.linalg.svd(C)
        
        pca_transform = U[:, :pca_dim].T # pca_dim x D
        
        X = np.dot(pca_transform, X_centered)
        
    print(f"Training GMM (K={K})...")
    w, mu, sigma = gmm_em(X, K)
    
    return w, mu, sigma, pca_transform, pca_mean

def fv_encode(X, w, mu, sigma):
    """
    Encode Fisher Vector.
    X: D x N (descriptors)
    """
    D, N = X.shape
    K = len(w)
    
    # Compute posteriors (same logic as E-step)
    log_rho = np.zeros((K, N))
    term1 = D * np.log(2 * np.pi)
    
    for k in range(K):
        diff = X - mu[:, [k]]
        sq_diff_norm = np.sum((diff**2) / sigma[:, [k]], axis=0)
        log_det = np.sum(np.log(sigma[:, k]))
        log_rho[k, :] = np.log(w[k]) - 0.5 * (term1 + log_det + sq_diff_norm)
        
    max_log_rho = np.max(log_rho, axis=0)
    rho = np.exp(log_rho - max_log_rho)
    sum_rho = np.sum(rho, axis=0)
    gamma = rho / sum_rho
    
    # Handle NaNs
    gamma[np.isnan(gamma)] = 1.0 / K
    
    fv_u = np.zeros((D, K))
    fv_v = np.zeros((D, K))
    
    for k in range(K):
        diff = X - mu[:, [k]]
        gamma_k = gamma[k, :] # N
        
        S0 = np.sum(gamma_k)
        S1 = np.dot(diff, gamma_k) # D
        S2 = np.dot(diff**2, gamma_k) # D
        
        sq_w = np.sqrt(w[k])
        sq_sigma = np.sqrt(sigma[:, k])
        
        fv_u[:, k] = S1 / (sq_w * sq_sigma)
        fv_v[:, k] = (S2 - S0 * sigma[:, k]) / (sq_w * np.sqrt(2) * sigma[:, k])
        
    # Concatenate [u1 ... uK v1 ... vK]
    # MATLAB: [fv_u(:); fv_v(:)] -> column major flatten
    # We want consistent output, let's flatten column-major ('F')
    fv = np.concatenate([fv_u.flatten(order='F'), fv_v.flatten(order='F')])
    
    # Power normalization
    fv = np.sign(fv) * np.sqrt(np.abs(fv))
    
    # L2 normalization
    norm_val = np.linalg.norm(fv)
    if norm_val > 0:
        fv = fv / norm_val
        
    return fv[:, np.newaxis] # Return column vector
