## Vedit-MCP
This is an MCP service for `video editing`, which can achieve basic editing operations with just one sentence.

English | [中文](README_CN.md)
## Quick Start

### 1. Install Dependencies

#### 1.1 Clone this project or directly download the zip package

#### 1.2 Configure the Python environment

1. It is recommended to use uv for installation
```bash
cd vedit-mcp
uv pip install -r requirements.txt
```
2. Or install directly using pip
```bash
pip install -r requirements.txt
```

#### 1.3 Configure ffmpeg

`vedit-mcp.py` relies on `ffmpeg` for implementation. Therefore, please configure ffmpeg.

```bash
# For Mac
brew install ffmpeg
# For Ubuntu
sudo apt update
sudo apt install ffmpeg
``` 

### 2. Start the Service

#### 2.1. It is recommended to use `google-adk` to build your own project

- Please refer to [adk-sample](sample/adk_sample.py)

##### Before executing this sample script

1. Please ensure that the path format is at least as follows

> - sample
>     - kb
>         - raw/test.mp4   // This is the original video you need to process
>     - adk_sample.py
> - vedit_mcp.py

2. Please install the following two dependencies
```python
# # adk-sample pip install requirements
# google-adk==0.3.0
# litellm==1.67.2
```
3. Please set the api-key and api-base

Currently, this script uses the API of the [`Volcano Ark Platform`](https://www.volcengine.com/product/ark), and you can go there to configure it by yourself.

After obtaining the API_KEY, please configure the API_KEY as an environment variable.

```bash
export OPENAI_API_KEY="your-api-key"
```

4. Execute the script

```bash
cd sample
python adk_sample.py
```

5. End of execution

After this script is executed correctly and ends, a video result file will be generated in kb/result, and a log file will be generated and the result will be output.

If you need secondary development, you can choose to add `vedit_mcp.py` to your project for use.

#### 2.2 Or build using `cline`

To be supplemented

#### 2.3. Execute using the stramlit web interface

To be supplemented 