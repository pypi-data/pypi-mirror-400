from sai_rl.benchmark.blur import blur_image
from dataclasses import dataclass
import numpy as np

@dataclass
class NoiseConfig:
    something: str

def add_perception_noise(state: np.ndarray | dict, info: dict, noise: list[NoiseConfig]):
    for n in noise:
        if "path" not in n or "scale" not in n:
            # Must have both
            continue

        if "include" in n and "exclude" in n:
            # Cannot have both
            continue

        path_split = n["path"].split(".")

        if path_split[0] not in ["state", "info"]:
            # Only support for state and info
            continue

        current = state
        if path_split[0] == "info":
            current = info

        while len(path_split) > 1:
            path_split.pop(0)
            current = current[path_split[0]]

        mask = np.ones_like(current, dtype=bool)
        if "exclude" in n:
            mask[n["exclude"]] = False
        elif "include" in n:
            mask = np.zeros_like(current, dtype=bool)
            mask[n["include"]] = True

        dtype = current.dtype
        sampled_noise = np.random.normal(loc=0, scale=n["scale"], size=current[mask].shape)
        
        if dtype == np.uint8:
            tmp = current.astype(np.float32)
            tmp[mask] += sampled_noise
            np.clip(tmp, 0, 255, out=tmp)
            current[:] = tmp.astype(np.uint8)
        else:
            current[mask] += sampled_noise

        if "min" in n:
            current = np.maximum(current, n["min"])
        if "max" in n:
            current = np.minimum(current, n["max"])