import numpy as np

def gaussian_kernel1d(sigma, radius=None):
    if radius is None:
        radius = int(3 * sigma + 0.5)
    x = np.arange(-radius, radius + 1)
    k = np.exp(-(x**2) / (2 * sigma**2))
    k /= k.sum()
    return k

def sep_conv2d(img, k):
    # Reflect padding; apply 1D conv horizontally then vertically
    pad = len(k) // 2
    def conv1d_axis(a, axis):
        a_pad = np.pad(a, [(pad, pad) if ax==axis else (0,0) for ax in range(a.ndim)], mode='reflect')
        # stride trick: manual 1D conv sliding window along the axis
        shape = list(a_pad.shape)
        shape[axis] = a.shape[axis]
        shape.insert(axis+1, len(k))
        strides = list(a_pad.strides)
        strides.insert(axis+1, strides[axis])
        from numpy.lib.stride_tricks import as_strided
        windows = as_strided(a_pad, shape=shape, strides=strides)
        return np.tensordot(windows, k, axes=([axis+1],[0]))
    out = conv1d_axis(img, axis=1)  # width
    out = conv1d_axis(out, axis=0)  # height
    return out

def blur_image(img, sigma=1.5):
    k = gaussian_kernel1d(sigma)
    x = img.astype(np.float32)
    if x.ndim == 3:
        x = np.stack([sep_conv2d(x[..., c], k) for c in range(x.shape[2])], axis=-1)
    else:
        x = sep_conv2d(x, k)
    if img.dtype == np.uint8:
        x = np.clip(x, 0, 255).astype(np.uint8)
    return x