## Vedit-MCP
这是一个视频编辑的MCP服务，能够实现一句话完成基本的剪辑操作。

[English](README.md) | 中文

## 快速开始

### 1. 安装依赖

#### 1.1 clone本项目获直接下载zip包

#### 1.2 配置python环境

1. 推荐使用uv安装
```bash
cd vedit-mcp
uv pip install -r requirements.txt
```
2. 或者直接pip安装
```bash
pip install -r requirements.txt
```

#### 1.3 配置ffmpeg

`vedit-mcp.py`依赖`ffmpeg`实现，因此请配置ffmpeg

```bash
# mac
brew install ffmpeg
# ubuntu
sudo apt update
sudo apt install ffmpeg
```


### 2. 启动服务


#### 2.1. 推荐使用`google-adk`来构建属于你的项目
    
- 请参考 [adk-sample](sample/adk_sample.py)



##### 在执行此样例脚本之前

1. 请保证路径格式至少如下

> - sample
>     - kb
>         - raw/test.mp4   // 这里是你要处理的原始视频
>     - adk_sample.py
> - vedit_mcp.py

2. 请安装以下两个依赖
```python
# # adk-sample pip install requirements
# google-adk==0.3.0
# litellm==1.67.2
```
3. 请设置api-key和api-base

目前本脚本采用的是[`火山方舟平台`](https://www.volcengine.com/product/ark)的api，您可以前往自行配置

获取API_KEY后，请配置API_KEY到环境变量

```bash
export OPENAI_API_KEY="your-api-key"
```

4. 执行脚本

```bash
cd sample
python adk_sample.py
```

5. 执行结束

此脚本执行结束且正确后，会在kb/result中生成视频结果文件，并生成日志文件并输出结果。

如需二次开发，你可以选择将`vedit_mcp.py`加入您的项目中使用。

#### 2.2 或者使用`cline`构建

首先请保证你的python环境以及ffmpeg配置正确
配置cline_mcp_settings.json如下
```json
{
  "mcpServers": {
    "vedit-mcp": {
      "command": "python",
      "args": [
        "vedit_mcp.py",
        "--kb_dir",
        "your-kb-dir-here"
      ]
    }
  }
}
```

#### 2.3. 使用stramlit web界面执行

待补充


### 3. 注意事项

1. 建议使用`thinking-model`来处理这类任务，目前测试`thinking-model`的对这类任务处理似乎性能更好？但没进行过更深入的测试，这只是一个直观的感受。
