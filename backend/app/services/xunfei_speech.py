import asyncio
import base64
import hashlib
import hmac
import json
import os
import struct
from datetime import datetime
from typing import Optional
from urllib.parse import urlencode, urlparse

import websockets


def _load_xunfei_config() -> dict:
    cfg_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "xunfei.json"
    )
    try:
        with open(cfg_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except FileNotFoundError:
        return {}
    except Exception:
        return {}
    return {}


def extract_pcm_from_wav(wav_data: bytes) -> bytes:
    if len(wav_data) < 44:
        raise RuntimeError("WAV文件格式无效")
    
    if wav_data[:4] != b'RIFF' or wav_data[8:12] != b'WAVE':
        raise RuntimeError("不是有效的WAV文件")
    
    audio_format = struct.unpack('<H', wav_data[20:22])[0]
    num_channels = struct.unpack('<H', wav_data[22:24])[0]
    sample_rate = struct.unpack('<I', wav_data[24:28])[0]
    bits_per_sample = struct.unpack('<H', wav_data[34:36])[0]
    
    if audio_format != 1:
        raise RuntimeError(f"WAV文件不是PCM格式 (format={audio_format})")
    
    if sample_rate != 16000:
        raise RuntimeError(f"采样率必须是16000Hz (当前: {sample_rate})")
    
    if num_channels != 1:
        raise RuntimeError(f"必须是单声道 (当前: {num_channels}声道)")
    
    if bits_per_sample != 16:
        raise RuntimeError(f"必须是16位采样 (当前: {bits_per_sample}位)")
    
    return wav_data[44:]


class XunfeiSpeechRecognizer:
    def __init__(self):
        cfg = _load_xunfei_config()
        self.appid = os.getenv("XUNFEI_APPID", "").strip() or cfg.get("appid", "")
        self.api_secret = os.getenv("XUNFEI_API_SECRET", "").strip() or cfg.get("apiSecret", "") or cfg.get("api_secret", "")
        self.api_key = os.getenv("XUNFEI_API_KEY", "").strip() or cfg.get("apiKey", "") or cfg.get("api_key", "")
        
        if not all([self.appid, self.api_secret, self.api_key]):
            raise RuntimeError(
                "讯飞语音识别配置缺失：请配置 backend/config/xunfei.json 或设置环境变量 XUNFEI_APPID, XUNFEI_API_SECRET, XUNFEI_API_KEY"
            )
        
        self.ws_url = "wss://iat-api.xfyun.cn/v2/iat"
        self.result_text = ""
        self.ws = None
    
    def _create_url(self) -> str:
        now = datetime.utcnow()
        date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
        
        signature_origin = f"host: ws-api.xfyun.cn\ndate: {date}\nGET /v2/iat HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode("utf-8"),
            signature_origin.encode("utf-8"),
            digestmod=hashlib.sha256
        ).digest()
        signature = base64.b64encode(signature_sha).decode(encoding="utf-8")
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature}"'
        authorization = base64.b64encode(authorization_origin.encode("utf-8")).decode(encoding="utf-8")
        
        params = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        
        return self.ws_url + "?" + urlencode(params)
    
    async def recognize(self, audio_data: bytes) -> str:
        self.result_text = ""
        url = self._create_url()
        
        pcm_data = extract_pcm_from_wav(audio_data)
        
        if len(pcm_data) < 1600:
            raise RuntimeError("录音时间太短，请至少录制1秒")
        
        try:
            async with websockets.connect(
                url,
                ping_interval=None,
                ping_timeout=None
            ) as ws:
                self.ws = ws
                
                audio_base64 = base64.b64encode(pcm_data).decode("utf-8")
                
                frame = {
                    "common": {"app_id": self.appid},
                    "business": {
                        "language": "zh_cn",
                        "domain": "iat",
                        "accent": "mandarin",
                        "vad_eos": 3000,
                        "ptt": 1
                    },
                    "data": {
                        "status": 2,
                        "format": "audio/L16;rate=16000",
                        "encoding": "raw",
                        "audio": audio_base64
                    }
                }
                
                await ws.send(json.dumps(frame))
                
                while True:
                    try:
                        result = await asyncio.wait_for(ws.recv(), timeout=10.0)
                        result_json = json.loads(result)
                        
                        if result_json.get("code", 0) != 0:
                            raise RuntimeError(f"讯飞识别错误: {result_json.get('message', '未知错误')}")
                        
                        if result_json.get("data", {}).get("result"):
                            ws_result = result_json["data"]["result"]
                            for item in ws_result.get("ws", []):
                                for cw in item.get("cw", []):
                                    self.result_text += cw.get("w", "")
                        
                        if result_json.get("data", {}).get("status") == 2:
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                return self.result_text
                
        except Exception as e:
            raise RuntimeError(f"讯飞语音识别失败: {e}")
    
    async def close(self):
        if self.ws:
            await self.ws.close()


def recognize_speech_sync(audio_data: bytes) -> str:
    recognizer = XunfeiSpeechRecognizer()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(recognizer.recognize(audio_data))
        return result
    finally:
        loop.close()
