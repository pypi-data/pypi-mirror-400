import numpy as np
from scipy import signal

def compute_dense_sift(img, step_size=4, bin_size=4):
    """
    Extract Dense SIFT descriptors from an image.
    
    Args:
        img: HxW grayscale image or HxWx3 RGB image (numpy array).
        step_size: Stride for sliding window.
        bin_size: Size of a spatial bin in pixels.
        
    Returns:
        descs: 128 x N numpy array of descriptors.
    """
    if img.ndim == 3 and img.shape[2] == 3:
        # Simple RGB to Gray conversion matching MATLAB's rgb2gray weights roughly
        # Or just average for simplicity if dependencies are an issue, but standard is:
        # 0.2989 * R + 0.5870 * G + 0.1140 * B
        img = np.dot(img[...,:3], [0.2989, 0.5870, 0.1140])
    
    img = img.astype(float)
    H, W = img.shape
    
    # Simple gradient filters
    dx_filter = np.array([[1, 0, -1]])
    dy_filter = np.array([[1], [0], [-1]])
    
    # 'same' convolution
    Ix = signal.convolve2d(img, dx_filter, mode='same', boundary='symm')
    Iy = signal.convolve2d(img, dy_filter, mode='same', boundary='symm')
    
    mag = np.sqrt(Ix**2 + Iy**2)
    ori = np.arctan2(Iy, Ix) # -pi to pi
    
    # Quantize orientations
    ori = ori * 180 / np.pi
    ori[ori < 0] += 360
    
    num_bins = 8
    bin_width = 360 / num_bins
    ori_bin = np.floor(ori / bin_width).astype(int)
    ori_bin[ori_bin >= num_bins] = 0
    
    # Create magnitude images
    mag_cells = np.zeros((H, W, num_bins))
    for b in range(num_bins):
        mag_cells[:, :, b] = mag * (ori_bin == b)
        
    patch_size = 4 * bin_size
    
    # Grid
    x_range = np.arange(patch_size/2, W - patch_size/2 + 1, step_size)
    y_range = np.arange(patch_size/2, H - patch_size/2 + 1, step_size)
    
    # Meshgrid (x is col, y is row)
    xv, yv = np.meshgrid(x_range, y_range)
    x = np.round(xv).astype(int).flatten()
    y = np.round(yv).astype(int).flatten()
    
    num_kpts = len(x)
    
    if num_kpts == 0:
        return np.zeros((128, 0))
    
    # Pre-calculate cell offsets
    # 4x4 cells
    descs = []
    
    # Note: Python loops are slow, but for parity and simplicity we stick to logic similar to MATLAB version first.
    # Optimized numpy slicing is better.
    
    # Let's try to be a bit vectorized or efficient with slicing
    # Extract patches? No, sliding window logic
    
    for i in range(num_kpts):
        r = y[i]
        c = x[i]
        
        r_start = int(r - patch_size/2)
        c_start = int(c - patch_size/2)
        
        curr_desc = np.zeros(128)
        idx = 0
        
        for br in range(4):
            for bc in range(4):
                cr_start = r_start + br * bin_size
                cc_start = c_start + bc * bin_size
                cr_end = cr_start + bin_size
                cc_end = cc_start + bin_size
                
                # Check bounds
                if cr_start < 0 or cr_end > H or cc_start < 0 or cc_end > W:
                    # Skip or zero (already zero initialized)
                    idx += 8
                    continue
                
                # Sum magnitudes
                # mag_cells is H x W x 8
                # slice: [row, col, :]
                
                # cell_mags: bin_size x bin_size x 8
                cell_mags = mag_cells[cr_start:cr_end, cc_start:cc_end, :]
                # sum over spatial dims -> 8 values
                bins = np.sum(cell_mags, axis=(0, 1))
                
                curr_desc[idx:idx+8] = bins
                idx += 8
                
        # Normalize
        norm_val = np.linalg.norm(curr_desc)
        if norm_val > 0:
            curr_desc /= norm_val
            
        # Clamp
        curr_desc[curr_desc > 0.2] = 0.2
        
        # Renormalize
        norm_val = np.linalg.norm(curr_desc)
        if norm_val > 0:
            curr_desc /= norm_val
            
        descs.append(curr_desc)
        
    return np.array(descs).T # 128 x N
