# MCP Bytedance TTS 语音生成器

本项目是一个 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 服务器，基于字节跳动 OpenSpeech TTS 的 HTTP 接口，将文本转换为语音音频。
遵循"只使用 HTTP，不使用 WebSocket"的约定。

## ✨ 功能特性

- 文本转语音：调用 Bytedance OpenSpeech TTS HTTP 接口生成音频
- 音色管理：支持通过 voice-types.json 将可读名称映射到官方 voice_type
- 简单集成：暴露 MCP 工具，Agent 直接调用生成 WAV 文件
- 跨平台运行：Windows、Linux、macOS

## 调用示例
```txt
使用"京腔侃爷（多情感）"的音色,创建如下内容的音频:

林芝海关关长王存瑞介绍道，我们依托智慧海关“高原特色产品出口”场景链建设，落实“随报、随检、随放”便利举措，大幅压缩报检时间，让高原蜂蜜以最优品质、最快速度抵港，不仅能让香江的同胞品尝到独特的“高原风味”，也是助力农民致富、乡村振兴的“甜蜜事业”。
```

## 🚀 安装

### 使用 uvx（推荐）

```bash
uvx mcp-bytedance-tts@latest  # 直接运行、更新，无需安装
```

或者使用 pipx 安装：

```bash
pipx install mcp-bytedance-tts
```

### 使用 uvx 运行（推荐）

```bash
uvx mcp-bytedance-tts
```

### 构建和发布
```bash
rm -rf dist && pip install build && python -m build && pip install twine && twine upload dist/*
```

## ⚙️ 配置

在 [config.json](src/main/config.json) 中填写以下字段：
- appid：控制台获取的应用 ID
- accessToken：控制台获取的访问令牌（用于 Authorization）
- secretKey：控制台获取的密钥（当前 HTTP 方案不直接使用）
- defaultVoiceType：默认的 voice_type（如 zh_male_xxx）
- defaultAudioEncoding：音频编码（默认 wav）
- uid：用户标识

可选在项目 src/ 目录放置 voice-types.json，将“可读名称”映射到“官方 voice_type ID”。当调用时传入名称会自动解析为 ID。

安全提示：请勿将密钥、令牌提交到版本库。

## 🖥️ MCP 客户端配置

在 MCP 客户端（例如 Claude Desktop、Cursor）的配置中添加：

使用 uvx（推荐）
```json
{
  "mcpServers": {
    "McpByteDanceTTS": {
      "command": "uvx",
      "args": ["mcp-bytedance-tts"]
    }
  }
}
```

## 🛠️ 可用工具

### mcp_bytedance_tts_generate_audio

使用字节跳动 OpenSpeech TTS 的 HTTP 接口（仅 HTTP）将文本生成音频文件。

参数
- text（string，必填）：要转换为语音的文本
- voiceType（string，可选）：音色名称或 voice_type ID；未提供时使用 defaultVoiceType
- outputDir（string，必填）：输出目录
- useSSML（boolean，可选）：是否使用SSML格式，当值为true时在请求中添加text_type:ssml；未提供时默认为 false

```json
{
  "name": "mcp_bytedance_tts_generate_audio",
  "arguments": {
    "text": "请将这段文字合成为语音文件",
    "voiceType": "zh_male_yuanboxiaoshu_moon_bigtts",
    "outputDir": "./output",
    "useSSML": true
  }
}
```

返回值
- 文本：生成成功消息，包含最终 WAV 文件路径（例如 ./output/1767514828_93829.wav）

工具定义位置：[server.py](src/main/server.py#L215-L231)

## ⚡ 快速开始

```bash
uvx mcp-bytedance-tts
```

## 💡 使用示例

配置完成后，你可以直接让 AI 助手：
- "将这段中文生成音频文件"
- "指定音色 温柔女神 生成语音"
- "把文本生成 WAV 并保存到 ./output"

### 音色映射

音色名称到 ID 的映射关系存储在 [voice-types.json](src/main/voice-types.json) 中。
例如，"温柔女神" 映射到 "ICL_zh_female_wenrounvshen_239eff5e8ffa_tob"。

## 💻 开发

### 设置开发环境

```bash
git clone https://github.com/aardpro/mcp-bytedance-tts.git
cd mcp-bytedance-tts
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 📂 项目结构

```
mcp-bytedance-tts/
├── src/
│   └── main/
│       ├── __init__.py
│       ├── __main__.py
│       ├── server.py
│       └── config.json
├── voice-types.json
├── pyproject.toml
├── requirements.txt
├── README.md
├── APIDOC.md
└── LICENSE
```

## ❓ 常见问题

### 配置问题

请确保已正确填写 [config.json](src/main/config.json) 的 appid 与 accessToken，并设置 defaultVoiceType。

### 音频生成失败

如果音频生成失败，请检查：
1. appid 与 accessToken 是否有效
2. voiceType 是否存在或映射正确
3. outputDir 是否有写入权限

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Pull Request 来改进这个项目！
