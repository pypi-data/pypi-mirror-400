from itertools import zip_longest
import subprocess
from typing import Callable, Any, Optional, cast

import gymnasium as gym
import imageio
import os
from imageio_ffmpeg import get_ffmpeg_exe
import numpy as np
import platform
import multiprocessing as mp
import time
from pathlib import Path

from pydantic import BaseModel
from sai_rl.error import RecordingError


class EpisodeType(BaseModel):
    seed: int
    actions: list[Any]
    output_path: str
    resolve_path_fn: Optional[Callable[[float, list[float]], str]] = None


def get_temp_path(path_name: str):
    split_name = path_name.split("/")
    return f"{'/'.join(split_name[:-1])}/tmp_{split_name[-1]}"

def get_videos_to_swap(scores, episodes):
    swap_data = {}
    video_name_swap = {}
    for idx, e in enumerate(episodes):
        new_name = e.resolve_path_fn(scores[idx], scores)
        if new_name != e.output_path:
            video_name_swap[e.output_path] = new_name
            swap_data[e.seed] = {
                "old_key": e.output_path.split("/")[-1],
                "new_key": new_name.split("/")[-1],
                "video_score": scores[idx]
            }
    return video_name_swap, swap_data

def apply_video_name_swap(name_swap, episodes):
    paths_to_override = {}
    if name_swap is not None:
        for e in episodes:
            if e.output_path in name_swap:
                old_path = Path(e.output_path)
                if old_path.exists():
                    new_path_name = name_swap[e.output_path]
                    temp_path_name = get_temp_path(new_path_name)
                    temp_path = Path(temp_path_name)
                    os.rename(old_path, temp_path)
                    e.output_path = new_path_name
                    paths_to_override[temp_path_name] = new_path_name

        for tmp_path_name, new_path_name in paths_to_override.items():
            os.rename(Path(tmp_path_name), Path(new_path_name))    


def record_episodes(
    env_creator: Callable[[], gym.Env], 
    episodes: list[EpisodeType], 
    get_actions: Optional[Callable] = None,
    record_model_fallback: Optional[bool] = False
) -> bool:
    env = env_creator()
    render_modes = env.metadata.get("render_modes", [])
    env.close()

    valid = True
    if "rgb_array" in render_modes:
        record_output = record_episodes_with_rgb_array(env_creator, episodes, get_actions, record_model_fallback)
    elif "human" in render_modes:
        record_output = record_episodes_with_human(env_creator, episodes, get_actions, record_model_fallback)
    else:
        valid = False

    return { "valid": valid, "used_model_actions": record_output[0], "swap_data": record_output[1] }


def record_episodes_with_human(
    env_creator: Callable[[], gym.Env],
    episodes: list[EpisodeType],
    get_actions: Optional[Callable] = None,
    record_model_fallback: Optional[bool] = False,
    use_virtual_display=True,
) -> None:
    # NEED TO ADD ABILITY TO USE `get_actions` in the fallback 
    for episode in episodes:
        env = cast(gym.Env, env_creator(render_mode="human"))
        env.reset(seed=episode.seed)

        fps = env.metadata.get("render_fps", 60)
        width = env.metadata.get("width", "1280")
        height = env.metadata.get("height", "720")
        capture_size = f"{width}x{height}"

        os.makedirs(
            os.path.dirname(episode.output_path) or ".",
            exist_ok=True,
        )

        ffmpeg_process = None
        original_sdl = os.environ.get("SDL_VIDEODRIVER")

        if use_virtual_display:
            os.environ["SDL_VIDEODRIVER"] = "dummy"

        try:
            if "DISPLAY" not in os.environ:
                raise RecordingError("No DISPLAY for human mode recording.")
            ffmpeg_exe = get_ffmpeg_exe()
            cmd = [
                ffmpeg_exe,
                "-f",
                "x11grab",
                "-s",
                capture_size,
                "-r",
                str(fps),
                "-i",
                os.environ["DISPLAY"],
                "-c:v",
                "libx264",
                "-preset",
                "ultrafast",
                "-pix_fmt",
                "yuv420p",
                "-y",
                episode.output_path,
            ]
            ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            time.sleep(1.5)
            if ffmpeg_process.poll() is not None:
                out, err = ffmpeg_process.communicate()
                raise RecordingError(
                    f"FFmpeg error {ffmpeg_process.returncode}\n{out}\n{err}"
                )

            env.render()

            for i, action in enumerate(episode.actions):
                _, _, terminated, truncated, _ = env.step(action)
                env.render()

        except Exception:
            if ffmpeg_process and ffmpeg_process.poll() is None:
                ffmpeg_process.terminate()
                try:
                    ffmpeg_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    ffmpeg_process.kill()
                    ffmpeg_process.wait()
                ffmpeg_process.communicate()
            raise

        finally:
            if ffmpeg_process:
                if ffmpeg_process.poll() is None:
                    ffmpeg_process.terminate()
                    try:
                        ffmpeg_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        ffmpeg_process.kill()
                        ffmpeg_process.wait()
                try:
                    ffmpeg_process.communicate(timeout=5)
                except Exception:
                    pass

            env.close()
            if use_virtual_display:
                if original_sdl is None:
                    os.environ.pop("SDL_VIDEODRIVER", None)
                else:
                    os.environ["SDL_VIDEODRIVER"] = original_sdl
    return False, None


def record_episodes_with_rgb_array(
    env_creator: Callable[[], gym.Env], 
    episodes: list[EpisodeType],
    get_actions: Optional[Callable] = None,
    record_model_fallback: Optional[bool] = False
) -> None:
    envs: Optional[gym.vector.VectorEnv] = None
    writers: list[Any] = []
    
    use_model_action = record_model_fallback and get_actions is not None
    swap_data = None
    video_name_swap = None

    try:
        is_windows = platform.system() == "Windows"
        if is_windows:
            mp.set_start_method("spawn", force=True)
        else:
            mp.set_start_method("fork", force=True)

        # Create the Environments
        # -> We found issues with the AsyncVectorEnv on Windows, so we use SyncVectorEnv instead
        #    for now. We should revisit this later to improve performance.
        if is_windows:
            envs = gym.vector.SyncVectorEnv(
                [
                    lambda i=i: env_creator(i, render_mode="rgb_array")
                    for i in range(len(episodes))
                ],
                copy=False,
            )
        else:
            envs = gym.vector.AsyncVectorEnv(
                [
                    lambda i=i: env_creator(i, render_mode="rgb_array")
                    for i in range(len(episodes))
                ],
                shared_memory=True,
                copy=False,
                autoreset_mode=gym.vector.vector_env.AutoresetMode.DISABLED
            )

        if envs is None:
            raise RuntimeError("Failed to create environment")

        fps: int = envs.metadata.get("render_fps", 30)

        seeds: list[int] = []
        actions_per_env: list[list[Any]] = []
        for episode in episodes:
            os.makedirs(os.path.dirname(episode.output_path) or ".", exist_ok=True)
            writers.append(imageio.get_writer(episode.output_path, fps=fps))
            seeds.append(episode.seed)
            actions_per_env.append(list(episode.actions))

        # Align actions across envs to the longest episode length
        # Use None as placeholder which we'll replace with a valid filler action
        actions_by_time: list[tuple[Any, ...]] = list(
            zip_longest(*actions_per_env, fillvalue=None)
        )

        # Build a filler action per env based on the action space
        space = envs.single_action_space
        if isinstance(space, gym.spaces.Box):
            base_filler = np.zeros(space.shape, dtype=space.dtype)
        elif isinstance(space, gym.spaces.Discrete):
            base_filler = 0
        elif isinstance(space, gym.spaces.MultiDiscrete):
            base_filler = np.zeros(space.nvec.shape, dtype=space.nvec.dtype)
        elif isinstance(space, gym.spaces.MultiBinary):
            base_filler = np.zeros(space.n, dtype=np.int64)
        else:
            base_filler = space.sample()

        # Track last valid action per-env to enable hold-last-action padding
        # Seed each env's last action with its first provided action when available
        last_actions: list[Any] = []
        if not use_model_action:
            for i in range(len(episodes)):
                if len(actions_per_env[i]) > 0:
                    last_actions.append(actions_per_env[i][0])
                else:
                    last_actions.append(base_filler)

        obs, info = envs.reset(seed=seeds)

        # Capture initial frame after reset
        frames = envs.render()
        if isinstance(frames, (list, tuple)):
            frames_list = frames
        else:
            frames_list = [frames[i] for i in range(len(episodes))]
        for idx, writer in enumerate(writers):
            frame = frames_list[idx]
            if frame is not None:
                writer.append_data(frame)

        scores = np.zeros(len(seeds), float)
        has_died = np.array([False for _ in range(len(seeds))])
        for timestep_actions in actions_by_time:
            step_actions: list[Any] = []
            should_write: list[bool] = []
            if not use_model_action:
                for idx, a in enumerate(timestep_actions):
                    if a is None:
                        step_actions.append(last_actions[idx])
                        should_write.append(False)  # do not write beyond recorded length
                    else:
                        last_actions[idx] = a
                        step_actions.append(a)
                        should_write.append(True)
            else:
                step_actions = get_actions(obs, info)

            # Step environments with a full batch of actions
            obs, rewards, terms, truns, info = envs.step(step_actions)

            if use_model_action:
                scores += rewards * (~has_died).astype(float)
                for i in range(len(terms)):
                    if terms[i] or truns[i]:
                        if not has_died[i]:
                            has_died[i] = True
                    should_write.append(has_died[i] == False)

            # Render frames for all envs
            frames = envs.render()
            if isinstance(frames, (list, tuple)):
                frames_list = frames
            else:
                # Assume first dimension corresponds to envs
                frames_list = [frames[i] for i in range(len(episodes))]

            for idx, writer in enumerate(writers):
                if not should_write[idx]:
                    continue
                frame = frames_list[idx]
                if frame is not None:
                    writer.append_data(frame)
        
        if use_model_action:
            video_name_swap, swap_data = get_videos_to_swap(scores, episodes)

    finally:
        for writer in writers:
            try:
                writer.close()
            except Exception as e:
                raise RecordingError("Couldn't save the recorded videos") from e

        apply_video_name_swap(video_name_swap, episodes)

        if envs is not None:
            try:
                envs.close()
            except Exception as e:
                raise RecordingError("Coudn't close the environments") from e

    return use_model_action, swap_data
