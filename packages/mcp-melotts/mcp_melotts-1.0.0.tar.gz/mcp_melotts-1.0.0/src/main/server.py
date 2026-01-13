import os
import sys
import logging
import json
import time
import random
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
server = Server("McpMeloTTS")

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
    "default_language": config_from_file.get("default_language", "ZH"),
    "default_speed": config_from_file.get("default_speed", 1.0),
    "default_device": config_from_file.get("default_device", "cpu"),
    "default_speaker": config_from_file.get("default_speaker", "ZH"),
    "chunk_size_limit": config_from_file.get("chunk_size_limit", 300),
    "api_base_url": config_from_file.get("api_base_url", "http://localhost"),
    "api_port": config_from_file.get("api_port", 9900)
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
    lines = [f"file '{str(p.resolve()).replace('\\', '/')}'" for p in chunk_paths]
    list_file.write_text("\n".join(lines), encoding="utf-8")


def concat_wav_files(chunk_paths: list[Path], output_path: Path):
    import subprocess
    list_file = output_path.parent / "list.txt"
    build_ffmpeg_list(chunk_paths, list_file)
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    finally:
        try:
            list_file.unlink(missing_ok=True)
        except Exception:
            pass


def ensure_ready():
    import shutil
    import socket
    import urllib.parse
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("未检测到 ffmpeg，请确保已安装并在 PATH 中")
    base = config.get("api_base_url", "http://127.0.0.1")
    parsed = urllib.parse.urlparse(base)
    host = parsed.hostname or "127.0.0.1"
    port = int(config.get("api_port", (parsed.port or (443 if parsed.scheme == "https" else 80))))
    try:
        s = socket.create_connection((host, port), timeout=2)
        s.close()
    except Exception:
        raise RuntimeError(f"未检测到 MeloTTS HTTP 服务，请在 {host}:{port} 启动")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="mcp_melotts_generate_audio",
            description="将文本生成语音文件。适用于“根据文本生成音频文件”等请求。支持自动分段与 ffmpeg 无损拼接，支持两种调用模式：本地 melo.api 与 Docker Gradio HTTP 接口。必需参数：text、output_dir。可选参数：language、speaker、speed、device、split_sentences；HTTP 模式需 use_http_api=true 与 api_base_url。输出：最终 WAV 文件路径文本。",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "要转换为语音的文本"},
                    "language": {"type": "string", "description": "语言代码，如 ZH/EN/JP/ES"},
                    "speaker": {"type": "string", "description": "说话人标签"},
                    "speed": {"type": "number", "description": "语速"},
                    "device": {"type": "string", "description": "cpu 或 cuda:0"},
                    "split_sentences": {"type": "boolean", "description": "是否自动分段"},
                    "output_dir": {"type": "string", "description": "输出目录"},
                    "target_filename": {"type": "string", "description": "最终输出文件名"},
                    "use_http_api": {"type": "boolean", "description": "是否使用Docker暴露的HTTP接口调用"},
                    "api_base_url": {"type": "string", "description": "HTTP接口基础地址，如 http://localhost:9900"},
                    "fn_index": {"type": "number", "description": "Gradio函数索引，默认1"},
                    "session_hash": {"type": "string", "description": "Gradio会话哈希，不提供则自动生成"}
                },
                "required": ["text", "output_dir"]
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
        if name != "mcp_melotts_generate_audio":
            raise ValueError(f"未知工具: {name}")

        text = arguments.get("text")
        language = arguments.get("language", config["default_language"])
        # 不再强制使用默认说话人，以便根据语言自动选择
        speaker_tag = arguments.get("speaker")
        speed = float(arguments.get("speed", config["default_speed"]))
        device = arguments.get("device", config["default_device"])
        split_sentences = bool(arguments.get("split_sentences", True))
        output_dir = arguments.get("output_dir")
        target_filename = arguments.get("target_filename")
        use_http_api = bool(arguments.get("use_http_api", False))
        api_base_url = arguments.get("api_base_url")
        fn_index = int(arguments.get("fn_index", 1))
        session_hash = arguments.get("session_hash")

        if not text or not isinstance(text, str):
            raise ValueError("text 参数必需")
        if not output_dir:
            raise ValueError("output_dir 参数必需")
        if use_http_api and not api_base_url:
            raise ValueError("使用 HTTP 接口时必须提供 api_base_url")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        ts = int(time.time())
        rnd = random.randint(10000, 99999)
        import re as _re
        if target_filename:
            safe_name = _re.sub(r'[<>:"/\\|?*]', '_', target_filename).strip()
            if not safe_name.lower().endswith(".wav"):
                safe_name += ".wav"
            final_wav = output_path / safe_name
        else:
            final_wav = output_path / f"{ts}_{rnd}.wav"

        def _gen_session_hash() -> str:
            import random, string
            return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(12))

        def _http_generate_chunk(seg_text: str, save_to: Path):
            try:
                import requests
            except Exception as e:
                raise RuntimeError(f"缺少 requests 库，无法使用 HTTP 接口: {e}")
            base = get_api_base_url(api_base_url).rstrip('/')
            sess = session_hash or _gen_session_hash()
            payload = {
                "data": [language, seg_text, speed, speaker_tag or language],
                "event_data": None,
                "fn_index": fn_index,
                "trigger_id": random.randint(1, 1000000),
                "session_hash": sess
            }
            join_url = f"{base}/queue/join?"
            r = requests.post(join_url, json=payload, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP 接口 join 失败: {r.status_code} {r.text}")
            ev = r.json()
            if "event_id" not in ev:
                raise RuntimeError(f"HTTP 接口返回不含 event_id: {ev}")
            data_url = f"{base}/queue/data?session_hash={sess}"
            with requests.get(data_url, headers={"Accept": "text/event-stream"}, stream=True, timeout=300) as s:
                s.raise_for_status()
                audio_url = None
                for line in s.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    if "process_completed" in line:
                        # 提取 JSON 部分
                        try:
                            import json as _json
                            # 行可能是 'message\t{...json...}'
                            parts = line.split('\t', 1)
                            body = parts[1] if len(parts) > 1 else line
                            obj = _json.loads(body)
                        except Exception:
                            # 尝试兼容 'data: {...}'
                            try:
                                if line.startswith("data: "):
                                    import json as _json
                                    obj = _json.loads(line[6:])
                                else:
                                    obj = {}
                            except Exception:
                                obj = {}
                        try:
                            outputs = obj.get("output", {}).get("data", [])
                            if outputs and isinstance(outputs[0], dict):
                                audio_url = outputs[0].get("url")
                        except Exception:
                            audio_url = None
                        break
                if not audio_url:
                    raise RuntimeError("未获取到生成的音频URL")
                # 下载音频
                ar = requests.get(audio_url, timeout=120)
                ar.raise_for_status()
                save_to.write_bytes(ar.content)

        segments = [text.strip()] if not split_sentences else split_text(text, int(config["chunk_size_limit"]))
        chunk_paths: list[Path] = []
        width = max(3, len(str(len(segments))))
        if use_http_api:
            for idx, seg in enumerate(segments, start=1):
                chunk_name = f"chunk_{str(idx).zfill(width)}.wav"
                chunk_path = output_path / chunk_name
                _http_generate_chunk(seg, chunk_path)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"分段音频生成失败: {chunk_path}")
                chunk_paths.append(chunk_path)
        else:
            try:
                from melo.api import TTS
            except Exception as e:
                raise RuntimeError(f"meloTTS 未安装或导入失败: {e}")
            model = TTS(language=language, device=device)
            try:
                spk2id = model.hps.data.spk2id
            except AttributeError:
                spk2id = getattr(getattr(model, "hps", None), "data", None)
                if spk2id:
                    spk2id = getattr(spk2id, "spk2id", {})
                else:
                    spk2id = {}
            target_key = speaker_tag if speaker_tag else language
            speaker_id = spk2id.get(target_key)
            if speaker_id is None and not speaker_tag:
                if language in spk2id:
                    speaker_id = spk2id[language]
                elif spk2id:
                    first_key = list(spk2id.keys())[0]
                    speaker_id = spk2id[first_key]
                    logger.warning(f"未找到语言 '{language}' 的默认说话人，使用第一个可用说话人: {first_key}")
            if speaker_id is None:
                available_speakers = list(spk2id.keys())
                raise ValueError(f"无效的说话人。请求: '{target_key}'。可用说话人: {available_speakers}")
            for idx, seg in enumerate(segments, start=1):
                chunk_name = f"chunk_{str(idx).zfill(width)}.wav"
                chunk_path = output_path / chunk_name
                model.tts_to_file(seg, speaker_id, str(chunk_path), speed=speed)
                if not chunk_path.exists() or chunk_path.stat().st_size == 0:
                    raise RuntimeError(f"分段音频生成失败: {chunk_path}")
                chunk_paths.append(chunk_path)

        if len(chunk_paths) == 1:
            chunk_paths[0].rename(final_wav)
        else:
            concat_wav_files(chunk_paths, final_wav)
            for p in chunk_paths:
                try:
                    p.unlink(missing_ok=True)
                except Exception:
                    pass

        msg = f"音频生成成功: {final_wav}"
        logger.info(msg)
        return [types.TextContent(type="text", text=msg)]

    except Exception as e:
        logger.error(f"执行工具 {name} 时出错: {e}")
        return [types.TextContent(type="text", text=f"错误: {str(e)}")]


async def run_server():
    logger.info("启动 McpMeloTTS - 文本生成音频 MCP 服务器...")
    setup_encoding()
    ensure_ready()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="McpMeloTTS",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
