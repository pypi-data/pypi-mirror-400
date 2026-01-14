import numpy as np

# --- JPEG standard quantization tables ---
_QY = np.array([
    [16,11,10,16,24,40,51,61],
    [12,12,14,19,26,58,60,55],
    [14,13,16,24,40,57,69,56],
    [14,17,22,29,51,87,80,62],
    [18,22,37,56,68,109,103,77],
    [24,35,55,64,81,104,113,92],
    [49,64,78,87,103,121,120,101],
    [72,92,95,98,112,100,103,99]
], dtype=np.float32)

_QC = np.array([
    [17,18,24,47,99,99,99,99],
    [18,21,26,66,99,99,99,99],
    [24,26,56,99,99,99,99,99],
    [47,66,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99],
    [99,99,99,99,99,99,99,99]
], dtype=np.float32)

def _scale_table(Q, quality):
    # quality: 1..100 (higher = better)
    q = max(1, min(100, int(quality)))
    if q < 50:
        s = 5000 / q
    else:
        s = 200 - 2*q
    T = np.floor((Q * s + 50) / 100).astype(np.float32)
    T[T < 1] = 1
    T[T > 255] = 255
    return T

def _dct_matrix(n=8):
    # Orthogonal DCT-II matrix
    C = np.zeros((n, n), dtype=np.float32)
    for u in range(n):
        for x in range(n):
            C[u, x] = np.cos(((2*x + 1) * u * np.pi) / (2*n))
    C[0, :] *= 1/np.sqrt(2)
    C *= np.sqrt(2/n)
    return C

_DCT8 = _dct_matrix(8)

def _rgb_to_ycbcr(img):
    # img: uint8 HxWx3
    x = img.astype(np.float32)
    # BT.601 full-range conversion
    R, G, B = x[...,0], x[...,1], x[...,2]
    Y  =  0.299*R + 0.587*G + 0.114*B
    Cb = -0.168736*R - 0.331264*G + 0.5*B + 128.0
    Cr =  0.5*R - 0.418688*G - 0.081312*B + 128.0
    return Y, Cb, Cr

def _ycbcr_to_rgb(Y, Cb, Cr):
    # inverse BT.601
    R = Y + 1.402*(Cr - 128.0)
    G = Y - 0.344136*(Cb - 128.0) - 0.714136*(Cr - 128.0)
    B = Y + 1.772*(Cb - 128.0)
    out = np.stack([R, G, B], axis=-1)
    return np.clip(out, 0, 255).astype(np.uint8)

def _pad_to_block(x, block=8):
    H, W = x.shape
    Hp = (H + block - 1) // block * block
    Wp = (W + block - 1) // block * block
    if Hp==H and Wp==W:
        return x, H, W
    y = np.zeros((Hp, Wp), dtype=x.dtype)
    y[:H, :W] = x
    # simple edge replication
    if H < Hp: y[H:,:] = y[H-1:H,:]
    if W < Wp: y[:,W:] = y[:,W-1:W]
    return y, H, W

def _process_channel(channel, Q):
    # channel: float32, padded HxW, level-shifted around 128 if chroma
    H, W = channel.shape
    out = np.empty_like(channel)
    C = _DCT8
    Ct = C.T
    for i in range(0, H, 8):
        for j in range(0, W, 8):
            block = channel[i:i+8, j:j+8]
            d = C @ (block - 128.0) @ Ct
            q = np.round(d / Q) * Q
            r = Ct @ q @ C + 128.0
            out[i:i+8, j:j+8] = r
    return out

def _downsample_420(x):
    # 4:2:0 by 2x2 average
    H, W = x.shape
    Hp = H // 2 * 2
    Wp = W // 2 * 2
    x = x[:Hp, :Wp]
    return 0.25*(x[0::2,0::2] + x[1::2,0::2] + x[0::2,1::2] + x[1::2,1::2])

def _upsample_420(x, H, W):
    # nearest-neighbor back to HxW
    return np.repeat(np.repeat(x, 2, axis=0), 2, axis=1)[:H, :W]

def jpeg_artifacts_numpy(img_rgb_uint8, quality=20, subsampling=True, repeats=1):
    """
    Simulate JPEG-like compression artifacts using only NumPy.
    - quality: 1..100 (lower = more artifacts)
    - subsampling: if True, apply 4:2:0 chroma subsampling
    - repeats: do multiple compress-decompress passes to amplify artifacts
    """
    assert img_rgb_uint8.dtype == np.uint8 and img_rgb_uint8.ndim == 3 and img_rgb_uint8.shape[2] == 3
    out = img_rgb_uint8.copy()

    QY = _scale_table(_QY, quality)
    QC = _scale_table(_QC, quality)

    for _ in range(max(1, int(repeats))):
        Y, Cb, Cr = _rgb_to_ycbcr(out)

        # Subsample chroma if requested
        if subsampling:
            Cb_ds = _downsample_420(Cb)
            Cr_ds = _downsample_420(Cr)
        else:
            Cb_ds, Cr_ds = Cb, Cr

        # Pad channels to multiples of 8
        Yp, H, W = _pad_to_block(Y, 8)
        Cbp, Hc, Wc = _pad_to_block(Cb_ds, 8)
        Crp, _, _ = _pad_to_block(Cr_ds, 8)

        # Process with DCT + quantization
        Yq  = _process_channel(Yp.astype(np.float32),  QY)
        Cbq = _process_channel(Cbp.astype(np.float32), QC)
        Crq = _process_channel(Crp.astype(np.float32), QC)

        # Unpad back
        Yr = Yq[:H, :W]
        if subsampling:
            Cbr = _upsample_420(Cbq[:Hc, :Wc], Y.shape[0], Y.shape[1])
            Crr = _upsample_420(Crq[:Hc, :Wc], Y.shape[0], Y.shape[1])
        else:
            Cbr = Cbq[:Y.shape[0], :Y.shape[1]]
            Crr = Crq[:Y.shape[0], :Y.shape[1]]

        out = _ycbcr_to_rgb(Yr, Cbr, Crr)

    return out