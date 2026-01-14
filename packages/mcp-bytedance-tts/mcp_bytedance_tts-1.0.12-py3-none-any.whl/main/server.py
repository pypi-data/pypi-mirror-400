import os
import sys
import logging
import json
import time
import random
import base64
from pathlib import Path
from typing import Dict, Any

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

 

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_encoding():
    """配置 UTF-8 编码以实现跨平台兼容性。"""
    if sys.platform == "win32":
        try:
            # Reconfigure all standard streams for UTF-8 on Windows
            sys.stdin.reconfigure(encoding='utf-8', errors='replace')
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
            os.environ['PYTHONIOENCODING'] = 'utf-8'
        except Exception as e:
            logger.warning(f"重新配置标准流失败: {e}")





# Initialize server
server = Server("McpBytedanceTTS")

def load_config() -> Dict[str, Any]:
    """从 config.json 文件加载配置。"""
    config_path = Path(__file__).parent / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件未找到: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Load configuration from config.json
config_from_file = load_config()

config = {
    "appid": config_from_file.get("appid", ""),
    "accessToken": config_from_file.get("accessToken", ""),
    "secretKey": config_from_file.get("secretKey", ""),
    "defaultVoiceType": config_from_file.get("defaultVoiceType", ""),
    "defaultAudioEncoding": config_from_file.get("defaultAudioEncoding", "wav"),
    "uid": config_from_file.get("uid", "uid")
}

def get_api_base_url(explicit_url: str | None) -> str:
    import urllib.parse
    base = explicit_url or config.get("api_base_url", "http://127.0.0.1")
    parsed = urllib.parse.urlparse(base)
    scheme = parsed.scheme or "http"
    hostname = parsed.hostname or "127.0.0.1"
    port = parsed.port
    if port is None:
        cfg_port = int(config.get("api_port", 80 if scheme == "http" else 443))
        default_port = 443 if scheme == "https" else 80
        if cfg_port != default_port:
            port = cfg_port
    netloc = f"{hostname}:{port}" if port else hostname
    return f"{scheme}://{netloc}"


def split_text(text: str, limit: int) -> list[str]:
    import re
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) <= limit:
        return [text]
    delimiters = r'[。！!？?\n\r,，、；;:.：]'
    parts = re.split(f'({delimiters})', text)
    combined = []
    buffer = ''
    for i in range(0, len(parts), 2):
        segment = parts[i]
        punct = parts[i + 1] if i + 1 < len(parts) else ''
        candidate = (buffer + segment + punct).strip()
        if len(candidate) <= limit:
            buffer = candidate + ' '
        else:
            if buffer.strip():
                combined.append(buffer.strip())
            buffer = (segment + punct).strip() + ' '
    if buffer.strip():
        combined.append(buffer.strip())
    final = []
    for s in combined:
        if len(s) <= limit:
            final.append(s)
        else:
            for j in range(0, len(s), limit):
                final.append(s[j:j + limit])
    return [x for x in final if x]


def build_ffmpeg_list(chunk_paths: list[Path], list_file: Path):
    lines = [f"file '{p.resolve().as_posix()}'" for p in chunk_paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")


def concat_wav_files(chunk_paths: list[Path], output_path: Path):
    import wave
    # Open the first WAV file to get the parameters
    with wave.open(str(chunk_paths[0]), 'rb') as first_wav:
        params = first_wav.getparams()
        
        # Create the output WAV file with the same parameters
        with wave.open(str(output_path), 'wb') as output_wav:
            output_wav.setparams(params)
            
            # Read and write frames from each chunk file
            for chunk_path in chunk_paths:
                with wave.open(str(chunk_path), 'rb') as chunk_wav:
                    # Verify that the parameters match
                    if chunk_wav.getparams() != params:
                        raise ValueError(f"WAV file parameters don't match: {chunk_path}")
                    # Read all frames and write them to the output file
                    frames = chunk_wav.readframes(chunk_wav.getnframes())
                    output_wav.writeframes(frames)


def ensure_ready():
    if not config.get("appid") or not config.get("accessToken"):
        raise RuntimeError("appid 或 accessToken 未配置")
    if not config.get("defaultVoiceType"):
        raise RuntimeError("defaultVoiceType 未配置")

def generate_filename(output_dir: Path) -> Path:
    ts = int(time.time())
    rnd = random.randint(10000, 99999)
    return output_dir / f"{ts}_{rnd}.wav"

def generate_reqid() -> str:
    ts = int(time.time())
    rnd = random.randint(10000, 99999)
    return f"id{ts}_{rnd}"

def load_voice_config() -> dict:
    try:
        voice_config_path = Path(__file__).parent / "voice-types.json"
        if not voice_config_path.exists():
            return {}
        with open(voice_config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def resolve_voice_type(name_or_id: str) -> str:
    if not name_or_id:
        return config["defaultVoiceType"]
    mapping = load_voice_config()
    logger.info(f"加载的音色映射: {mapping}")
    logger.info(f"要解析的音色名称: {name_or_id}")
    if isinstance(mapping, dict) and name_or_id in mapping:
        v = mapping.get(name_or_id)
        logger.info(f"找到映射: {name_or_id} -> {v}")
        if isinstance(v, str) and v:
            return v
    logger.info(f"未找到映射，返回原始值或默认值: {name_or_id if isinstance(name_or_id, str) and name_or_id else config['defaultVoiceType']}")
    return name_or_id if isinstance(name_or_id, str) and name_or_id else config["defaultVoiceType"]

def request_bytedance_tts(voice_type: str, text: str, use_ssml: bool = False) -> bytes:
    """
    调用字节跳动 OpenSpeech TTS 的 HTTP 接口生成音频字节。
    - 仅使用 HTTP（requests.post），不使用 WebSocket
    - 输入：voice_type（音色 ID）、text（待合成文本）、use_ssml（是否使用SSML格式）
    - 输出：WAV 等编码的音频二进制（从返回的 base64 data 解码）
    """
    import requests
    url = "https://openspeech.bytedance.com/api/v1/tts"
    headers = {
        "Authorization": f"Bearer;{config['accessToken']}",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "User-Agent": "mcp-bytedance-tts/1.0"
    }
    payload = {
        "app": {
            "appid": config["appid"],
            "token": config["accessToken"],
            "cluster": "volcano_tts"
        },
        "user": {
            "uid": config.get("uid", "uid")
        },
        "audio": {
            "voice_type": voice_type,
            "encoding": config.get("defaultAudioEncoding", "wav"),
            "speed_ratio": 1.0
        },
        "request": {
            "reqid": generate_reqid(),
            "text": text,
            "operation": "query"
        }
    }
    
    # Add text_type: ssml to the request if useSSML is true
    if use_ssml:
        payload["request"]["text_type"] = "ssml"
    
    # Log the request for debugging
    logger.info(f"请求Bytedance TTS API - URL: {url}")
    logger.info(f"请求头: {dict((k, v if k != 'Authorization' else '***REDACTED***') for k, v in headers.items())}")
    logger.info(f"请求体: {payload}")
    
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    logger.info(f"API响应状态码: {r.status_code}")
    logger.info(f"API响应内容: {r.text}")
    
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text}")
    obj = r.json()
    data_b64 = obj.get("data")
    if not data_b64:
        raise RuntimeError("响应缺少音频数据")
    return base64.b64decode(data_b64)


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="mcp_bytedance_tts_generate_audio",
            description="根据输入文本生成语音音频文件。当需要把文字朗读为音频时调用我。参数：text（必填）、outputDir（必填）、voiceType（可选，可使用音色名称）、useSSML（可选，是否使用SSML格式）。未提供 voiceType 时使用默认音色，未提供 useSSML 时默认为 false。处理完成后返回最终 WAV 文件的路径文本。",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要转换为语音的文本"},
                    "voiceType": {"type": "string", "description": "音色名称"},
                    "outputDir": {"type": "string", "description": "输出目录"},
                    "useSSML": {"type": "boolean", "description": "是否使用SSML格式，当值为true时在请求中添加text_type:ssml"}
                },
                "required": ["text", "outputDir"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.EmbeddedResource]:
    logger.info(f"工具被调用: {name} 参数: {arguments}")
    try:
        if not arguments:
            raise ValueError("缺少参数")
        if name != "mcp_bytedance_tts_generate_audio":
            raise ValueError(f"未知工具: {name}")

        text = arguments.get("text")
        provided_voice = arguments.get("voiceType")
        voice_type = resolve_voice_type(provided_voice) if provided_voice else config["defaultVoiceType"]
        logger.info(f"使用的音色: {voice_type}")
        output_dir = arguments.get("outputDir")
        use_ssml = arguments.get("useSSML", False)
        if not text or not isinstance(text, str):
            raise ValueError("text 参数必需")
        if not output_dir:
            raise ValueError("outputDir 参数必需")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        audio_bytes = request_bytedance_tts(voice_type, text, use_ssml)
        final_wav = generate_filename(output_path)
        final_wav.write_bytes(audio_bytes)
        msg = f"音频生成成功: {final_wav}"
        logger.info(msg)
        return [types.TextContent(type="text", text=msg)]

    except Exception as e:
        logger.error(f"执行工具 {name} 时出错: {e}")
        return [types.TextContent(type="text", text=f"错误: {str(e)}")]


async def run_server():
    logger.info("启动 McpBytedanceTTS - 文本生成音频 MCP 服务器...")
    setup_encoding()
    ensure_ready()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="McpBytedanceTTS",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
