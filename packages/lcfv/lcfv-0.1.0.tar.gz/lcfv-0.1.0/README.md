# Label Consistent Fisher Vectors (LCFV)

[![View Label Consistent Fisher Vectors (LCFV) on File Exchange](https://www.mathworks.com/matlabcentral/images/matlab-file-exchange.svg)](https://www.mathworks.com/matlabcentral/fileexchange/47730-label-consistent-fisher-vectors-lcfv)
[![Octave application](https://github.com/wq2012/LCFV/actions/workflows/octave.yml/badge.svg)](https://github.com/wq2012/LCFV/actions/workflows/octave.yml)

## Table of Contents

- [Overview](#overview)
- [Video demo](#video-demo)
- [Matlab / Octave Implementation](#matlab--octave-implementation)
  - [Installation](#installation)
  - [Demos](#demos)
  - [Usage](#usage)
- [Python Implementation](#python-implementation)
  - [Installation](#installation-1)
  - [Usage](#usage-1)
- [Copyright and Citation](#copyright-and-citation)

## Overview

Label Consistent Fisher Vectors (LCFV) is a method for adding supervised information to Fisher vectors. This package provides implementations in both **MATLAB/Octave** and **Python**.

This package provides a complete pipeline for:
1.  **Feature Extraction**: Dense SIFT descriptors.
2.  **Encoding**: Fisher Vector encoding (GMM + PCA).
3.  **Optimization**: Learning the LCFV transformation matrix.

![LCFV Logo](resources/LCFV_logo.png)

## Video demo

[![YouTube Demo](resources/youtube_demo.jpg)](https://www.youtube.com/watch?v=GTSMONLaRAg)

## Matlab / Octave Implementation

### Installation

Simply clone the repository. The code is written in pure MATLAB/Octave and requires no external compilation.

```bash
git clone https://github.com/wq2012/LCFV.git
```

### Demos

We provide three levels of demos:

1.  **Synthetic End-to-End**: `code/run_synthetic_end2end_demo.m`
    -   Generates synthetic data, trains GMM, computes FV, and applies LCFV.
2.  **CIFAR-10 Subset Real World**: `code/run_cifar10_end2end_demo.m`
    -   Extracts Dense SIFT from a subset of CIFAR-10 images, computes FV, and applies LCFV.
3.  **LCFV Core**: `code/run_LCFV_demo.m`
    -   Shows how to use `solve_LCFV1` and `solve_LCFV2` on pre-computed descriptors.

### Usage

#### 1. Extract Features & Compute Fisher Vectors

You can use the built-in tools in `code/fisher_vector/` to generate features from images.

```matlab
addpath(genpath('code'));

% 1. Extract Dense SIFT from an image
img = imread('image.jpg');
descs = compute_dense_sift(img); % 128 x N matrix

% 2. Train GMM and PCA (using a set of training descriptors)
% all_descs: 128 x N_total matrix
K = 64; % Number of Gaussian components
pca_dim = 64; % PCA dimension
[w, mu, sigma, pca_transform, pca_mean] = fv_train(all_descs, K, pca_dim);

% 3. Encode Fisher Vector for a new image
% img_descs: 128 x N descriptors for the image
% Apply PCA projection first
img_descs_pca = pca_transform * bsxfun(@minus, img_descs, pca_mean);
% Encode
fv = fv_encode(img_descs_pca, w, mu, sigma);
```

#### 2. Apply Label Consistent Fisher Vectors (LCFV)

Once you have Fisher Vectors for your training set, you can learn the LCFV transformation.

```matlab
% G: D x N matrix of Fisher Vectors (column vectors)
% labels: N x 1 vector of class labels
% alpha: Regularization parameter (e.g., 10)

% Create label comparison matrix
C1 = repmat(labels, 1, length(labels));
C2 = repmat(labels', length(labels), 1);
C = double(C1 == C2);

% LCFV-1 (Sparse)
[M1, W1] = solve_LCFV1(G, C, alpha);
lcfv_features = M1 * G;

% LCFV-2 (Dense)
M2 = solve_LCFV2(G, C, alpha);
lcfv_features = M2 * G;
```

## Python Implementation

We provide a mirror implementation in Python located in the `python/` directory.

### Installation

Install from source:

```bash
cd python
pip install .
```

Or install from PyPI:

```
pip install lcfv
```


### Usage

```python
import numpy as np
import cv2
from lcfv import compute_dense_sift, fv_encode, solve_lcfv1, fv_train

# 1. Feature Extraction
# compute_dense_sift expects HxW or HxWx3 image
img = cv2.imread('image.jpg')
descs = compute_dense_sift(img) # 128 x N numpy array

# 2. Train GMM/PCA
# all_descs: 128 x N_total
K = 64
w, mu, sigma, pca_transform, pca_mean = fv_train(all_descs, K, pca_dim=64)

# 3. Encode
# Apply PCA first
descs_centered = all_descs - pca_mean[:, None]
descs_pca = np.dot(pca_transform, descs_centered)

fv = fv_encode(descs_pca, w, mu, sigma) # (2*D*K) x 1

# 4. LCFV
# G: D x N matrix of FVs
# C: Label consistency matrix
M1, W1 = solve_lcfv1(G, C, alpha=10)
lcfv_feats = np.dot(M1, G)
```

## Copyright and Citation

```
Copyright (C) 2012 Quan Wang <wangq10@rpi.edu>,
Signal Analysis and Machine Perception Laboratory,
Department of Electrical, Computer, and Systems Engineering,
Rensselaer Polytechnic Institute, Troy, NY 12180, USA
```

This software was developed as part of the following research. If you use this software in your research, please cite:

**Plain Text:**

> Quan Wang, Xin Shen, Meng Wang, and Kim L. Boyer.
"Label consistent fisher vectors for supervised feature aggregation."
In 2014 22nd International Conference on Pattern Recognition, pp. 3588-3593. IEEE, 2014.

> Quan Wang.
Exploiting Geometric and Spatial Constraints for Vision and Lighting Applications.
Ph.D. dissertation, Rensselaer Polytechnic Institute, 2014.

**BibTeX:**

```bibtex
@inproceedings{wang2014label,
  title={Label consistent Fisher vectors for supervised feature aggregation},
  author={Wang, Quan and Shen, Xin and Wang, Meng and Boyer, Kim L},
  booktitle={Pattern Recognition (ICPR), 2014 22nd International Conference on},
  pages={2507--2512},
  year={2014},
  organization={IEEE}
}

@phdthesis{wang2014exploiting,
  title={Exploiting Geometric and Spatial Constraints for Vision and Lighting Applications},
  author={Quan Wang},
  year={2014},
  school={Rensselaer Polytechnic Institute},
}
```

This library is also available at MathWorks:
https://www.mathworks.com/matlabcentral/fileexchange/47730-label-consistent-fisher-vectors-lcfv

