import requests
from pathlib import Path
from typing import Dict, List, Literal, Iterable

import numpy as np
import lameenc
from result import Result, Ok, Err


class TTSClient:
    def __init__(self, base_url: str, headers: Dict = None):
        super().__init__()
        self.base_url = base_url
        self.headers = headers

    def server_info(self) -> Result[Dict, str]:
        url = self.base_url + "/server_info"
        res = requests.get(url=url, headers=self.headers)
        if res.status_code != 200:
            return Err(f"获取服务信息失败, 状态码: {res.status_code}, 响应: {res.text}")
        return Ok(res.json())

    def list_speakers(self) -> Result[List[str], str]:
        url = self.base_url + "/audio_roles"
        res = requests.get(url=url, headers=self.headers)
        if res.status_code != 200:
            return Err(f"获取音色列表失败, 状态码: {res.status_code}, 响应: {res.text}")
        return Ok(res.json()["roles"])

    def delete_speaker(self, speaker: str) -> Result[None, str]:
        url = self.base_url + "/delete_speaker"
        data = {"name": speaker}
        res = requests.post(url=url, data=data, headers=self.headers)
        if res.status_code != 200:
            return Err(f"删除音色失败, 状态码: {res.status_code}, 响应: {res.text}")
        return Ok(None)

    def add_speaker(
        self, audio_path: str | Path, speaker_name: str | None = None
    ) -> Result[None, str]:
        url = self.base_url + "/add_speaker"
        audio_path = Path(audio_path)
        audio_format = audio_path.suffix
        if not speaker_name:
            speaker_name = audio_path.stem
        files = {
            "audio_file": (audio_path, open(audio_path, "rb"), f"audio/{audio_format}")
        }
        data = {"name": speaker_name, "audio_file": str(audio_path)}
        res = requests.post(url=url, data=data, files=files, headers=self.headers)
        if res.status_code != 200:
            return Err(f"上传音色失败, 状态码: {res.status_code}, 响应: {res.text}")
        return Ok(None)

    def speak(
        self,
        text: str,
        speaker: str,
        save_path: str | None = None,
        pitch: Literal["very_low", "low", "moderate", "high", "very_high"] = "moderate",
        speed: Literal["very_low", "low", "moderate", "high", "very_high"] = "moderate",
        sample_rate: int = 16000,
    ) -> Result[np.ndarray, str]:
        url = self.base_url + "/speak"
        data = {
            "text": text,
            "name": speaker,
            "pitch": pitch,
            "speed": speed,
            "stream": True,
            "response_format": "pcm",
            "sample_rate": sample_rate,
        }
        res = requests.post(url=url, headers=self.headers, json=data, stream=True)
        buffer = b""
        for chunk in res.iter_content(chunk_size=1024):
            buffer += chunk
        if res.status_code != 200:
            return Err(f"合成失败, 状态码: {res.status_code}, 响应: {res.text}")
        audio = np.frombuffer(buffer, dtype=np.int16)
        if save_path is not None:
            enc = lameenc.Encoder()
            enc.set_bit_rate(128)
            enc.set_in_sample_rate(sample_rate)
            enc.set_channels(audio.shape[1] if audio.ndim > 1 else 1)
            enc.set_quality(2)

            mp3_bytes = enc.encode(audio.tobytes()) + enc.flush()

            with open(save_path, "wb") as f:
                f.write(mp3_bytes)
        return Ok(audio)

    def speak_stream(
        self,
        text: str,
        speaker: str,
        pitch: Literal["very_low", "low", "moderate", "high", "very_high"] = "moderate",
        speed: Literal["very_low", "low", "moderate", "high", "very_high"] = "moderate",
        sample_rate: int = 16000,
    ) -> Iterable[np.ndarray]:
        url = self.base_url + "/speak"
        data = {
            "text": text,
            "name": speaker,
            "pitch": pitch,
            "speed": speed,
            "stream": True,
            "response_format": "pcm",
            "sample_rate": sample_rate,
        }
        res = requests.post(url=url, headers=self.headers, json=data, stream=True)
        buffer = b""
        for chunk in res.iter_content(chunk_size=1024):
            buffer += chunk
            valid_len = len(buffer) - (len(buffer) % 2)
            audio = np.frombuffer(buffer=buffer[:valid_len], dtype=np.int16)
            yield audio
            buffer = buffer[valid_len:]
        if len(buffer) > 0:
            audio = np.frombuffer(buffer, dtype=np.int16)
            yield audio
