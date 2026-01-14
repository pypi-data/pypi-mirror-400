由于我在做的小落同学（https://x.oddmeta.net)项目需要用到ASR功能，之前针对 FunASR、FireRedAsr、Vosk等ASR项目也做了一些评测，但是总体跑下来发现还是FunASR的整体表现最好，所以我就将FunASR给封装了一下，做了一个OddAsr的项目。

而考虑到ASR功能的用途广泛，之前也有一些朋友私下问过我相关的一些使用和封装的问题，尤其是流式ASR的支持（github上有好多FunASR的API封装，但是全是离线文件转写的，没有一个同时支持离线文件转写和流式转写的API封装项目），想了一下干脆直接把它开源出来吧。希望对有ASR需求的同学有帮助。

ASR引擎测试：FireRedASR只能说小红书的诚意不够，https://www.oddmeta.net/archives/144
ASR引擎测试：FunASR，必须给阿里点一个赞，https://www.oddmeta.net/archives/165
可能是最紧凑、最轻量级的ASR模型：Vosk实战解析，https://www.oddmeta.net/archives/201

## 项目简介
OddASR是一个简单的ASR API服务器，基于强大的开源语音识别库FunASR构建。FunASR由ModelScope开发，提供了丰富的预训练模型和工具，可用于各种语音识别任务。
OddASR的目标是简化FunASR的部署，满足非实时音频处理的需求，同时也为实时流式转写提供了支持。

项目具有以下特点：
- **简化部署**：提供易于使用的REST API，方便进行ASR转录。
- **本地参考**：有独立的Python实现，可在本地进行ASR转录。
- **Docker支持**：提供GPU和CPU部署的Dockerfile，简化服务器部署。
- **易于使用**：通过简单的API请求即可实现音频文件转录。

## 安装步骤
### 1. 克隆仓库
```bash
git clone https://github.com/oddmeta/oddasr.git
cd oddasr
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法
### 1. 启动REST API服务器
```bash
python main_server.py
```
服务器将在`http://127.0.0.1:12340`上启动。

### 2. 测试文件ASR API
使用`testAPI.py`脚本测试API：
```bash
python testAPI.py test_en_steve_jobs_10s.wav txt
```
也可以使用`curl`命令发送音频文件到REST API：
```bash
curl -X POST -F "audio=@path/to/audio.wav" http://127.0.0.1:12340/v1/v1/asr
```

### 3. 测试流ASR API
使用`testStreamAPI.py`脚本测试API：
```bash
python testStreamAPI.py 111.pcm
```

### 4. 示例输出
- **text模式**
```bash
是开始这个呃实时的一个转写。 
对， 然后是转写的一个效果， 大概大概就是这个样子。 
然后的话那个在这里边你也可以去给他那个加一个人。 
比如说是嗯我随便给他取一个名字， 
就是连云端的还是自己算的连云端的吧。 
```

- **spk模式**
```bash
发言人 0: 是开始这个呃实时的一个转写。
发言人 0: 对，
发言人 0: 然后是转写的一个效果，
发言人 0: 大概大概就是这个样子。
发言人 0: 然后的话那个在这里边你也可以去给他那个加一个人。
发言人 0: 比如说是嗯我随便给他取一个名字，
发言人 1: 就是连云端的还是自己算的连云端的吧。
发言人 0: 呃本地的本地的本地的对，
发言人 0: 不用连看能调吧。
发言人 2: 这个还有对呀，
发言人 0: 然后这里边可以给他加格。
```

- **srt模式**
```bash
0 00:00:01,010 --> 00:00:04,865 发言人 0: 是开始这个呃实时的一个转写。 
1 00:00:06,040 --> 00:00:06,280 发言人 0: 对， 
2 00:00:06,640 --> 00:00:08,660 发言人 0: 然后是转写的一个效果， 
3 00:00:08,680 --> 00:00:10,280 发言人 0: 大概大概就是这个样子。 
4 00:00:10,280 --> 00:00:14,500 发言人 0: 然后的话那个在这里边你也可以去给他那个加一个人。 
5 00:00:14,660 --> 00:00:19,665 发言人 0: 比如说是嗯我随便给他取一个名字， 
6 00:00:20,440 --> 00:00:23,200 发言人 1: 就是连云端的还是自己算的连云端的吧。 
7 00:00:23,240 --> 00:00:25,340 发言人 0: 呃本地的本地的本地的对， 
8 00:00:25,340 --> 00:00:27,275 发言人 0: 不用连看能调吧。 
9 00:00:29,120 --> 00:00:31,480 发言人 2: 这个还有对呀， 
10 00:00:32,130 --> 00:00:33,885 发言人 0: 然后这里边可以给他加格。 
```

### 5. Docker部署
- **GPU部署**
```bash
docker build -t asr-service-gpu:v0.1.0.
docker run --gpus all -d -p 12340:12340 --name asr-service asr-service-gpu:v0.1.0
```

- **CPU部署**
```bash
docker build -f Dockerfile_CPU -t asr-service-cpu:v0.1.0.
docker run -d -p 12340:12340 --name asr-service asr-service-cpu:v0.1.0
```

## 项目待办事项
- **添加更多模型和功能**：不断丰富模型库，提供更多实用功能。
- **支持实时ASR**：进一步优化实时流式转写的性能。
- **添加更多自定义选项**：如`--mode`、`--output_format`、`--hotword`等。
- **简单UI展示**：开发简单的用户界面，方便用户使用。
- **支持声纹识别**：满足特定场景下的声纹识别需求。
- **其他增强功能**：如设置并发发送线程数、支持不同格式的音频输入等。

## 参考资料
- [FunASR](https://github.com/modelscope/FunASR)：本项目使用的ASR框架。
- [Flask](https://github.com/pallets/flask)：用于构建REST API的Web框架。
- [funasr-python-api](https://github.com/open-yuhaoz/funasr-python-api)：FunASR服务器的Python API。

如果你对语音识别技术感兴趣，不妨试试OddASR。它简单易用，功能强大，能为你的语音转文字工作带来极大的便利。快来体验吧！
