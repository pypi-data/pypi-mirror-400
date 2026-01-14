import time
import numpy as np
import subprocess as sp
import threading
from funasr import AutoModel


# Wakeup words
ODD_WAKEUP_WORD = ["你好小落,小落小落,小落同学"]

# Conference commands
ODD_CONF_COMMANDS = [
    "开始会议",
    "结束会议",
    "邀请参与者",
    "取消邀请",
    "静音参与者",
    "取消静音",
    "发送双流",
    "停止双流",
    "切换摄像头",
    "切换麦克风",
    "打开录音",
    "关闭录音",
]

# IOT commands
ODD_IOT_COMMANDS = [
    "打开灯光",
    "关闭灯光",
    "打开空调",
    "关闭空调",
    "打开窗帘",
    "关闭窗帘",
    "打开电视",
    "关闭电视",
    "打开终端",
    "关闭终端",
]

# Music control commands
ODD_MUSIC_COMMANDS = [
    "播放音乐",
    "增大音量",
    "减小音量",
    "继续播放",
    "暂停播放",
    "上一首",
    "下一首",
    "单曲循环",
    "随机模式",
    "列表循环",
]

# Map control commands
ODD_MAP_COMMANDS = [
    "取消导航",
    "退出导航",
    "放大地图",
    "查看全程",
    "缩小地图",
    "不走高速",
    "躲避拥堵",
    "避免收费",
    "高速优先",
]

# General commands
ODD_GENERAL_COMMANDS = [
    "上一页",
    "下一页",
    "上一个",
    "下一个",
    "换一批", 
    "返回",
    "退出",
    "帮助",
    "重启",
    "关机",
    "重启系统",
    "关机系统",
    "再见",
    "拜拜",
    "谢谢",
    "谢谢小落",
]

ODD_VOICE_COMMANDS = ODD_CONF_COMMANDS + ODD_IOT_COMMANDS + ODD_MUSIC_COMMANDS + ODD_MAP_COMMANDS + ODD_GENERAL_COMMANDS

# config
odd_voice_assist_cfg = {
    "commands": {
        "wakeup_word": ODD_WAKEUP_WORD,
        "voice_commands": ODD_VOICE_COMMANDS,
    },

    "audio_fmt": {
        "chunk_size_ms": 200,
        "stride_ms": 480,
        "sample_rate": 16000,
        "format": np.int16,
        "channels": 1,
        "audio_queue_len": 10, # 有检测到VAD后，会将chunk加入到队列中，此参数代表最大队列长度
    }
}


class OddVoiceAssistant:
    """
    Voice Assistant class
    """
    running: bool = False
    is_speaking: bool = False
    capture_thread: threading.Thread = None
    ffmpeg_proc = None
    ffmpeg_proc_event: threading.Event = None
    data_lock: threading.Lock = None

    def __init__(self, wakeup_word=["你好小落,小落小落,小落同学"]):
        
        self.ffmpeg_proc = None
        self.ffmpeg_proc_event = threading.Event()
        self._init_audio_buffers()
        self.data_lock = threading.Lock()

        wakeup_word = ','.join(ODD_VOICE_COMMANDS) if isinstance(wakeup_word, list) else wakeup_word
        self._load_model(wakeup_word)

    def _load_model(self, wakeup_word):
        """load models"""
        try:
            # init vad model
            self.vad_model = AutoModel(
                model="fsmn-vad",
                model_revision="v2.0.4",
                disable_pbar=True
            )
            
            # init kws model
            self.kws_model = AutoModel(
                model="iic/speech_charctc_kws_phone-xiaoyun",
                keywords=wakeup_word,
                output_dir="./outputs/debug",
                device='cpu',
                disable_pbar=True
            )
            
            # cache for vad model and kws_model
            self.vad_cache = {}
            self.kws_cache = {}
            
            # chunk size for vad model and kws model
            self.vad_chunk_samples = int(odd_voice_assist_cfg["audio_fmt"]["chunk_size_ms"] * odd_voice_assist_cfg["audio_fmt"]["sample_rate"] / 1000)
            self.kws_chunk_stride = int(odd_voice_assist_cfg["audio_fmt"]["stride_ms"] * odd_voice_assist_cfg["audio_fmt"]["sample_rate"] / 1000)
            
        except Exception as e:
            raise RuntimeError(f"init models failed: {str(e)}")


    def _init_audio_buffers(self):
        """init audio buffers"""
        self.raw_buffer = np.array([], dtype=np.float32)  # raw audio buffer
        self.wakeup_queue = []                            # wakeup model process queue
        self.MAX_QUEUE_SIZE = odd_voice_assist_cfg["audio_fmt"]["audio_queue_len"]

    def start(self):
        """start odd voice assistant"""
        # start audio capture thread
        self.capture_thread = threading.Thread(target=self._audio_capture_thread_wrapper, daemon=True)
        self.capture_thread.start()
        
        # wait for audio capture initialization
        if not self.ffmpeg_proc_event.wait(timeout=5):
            print("audio capture initialization timeout")
            return False
        
        # start process thread
        self.process_thread = threading.Thread(target=self._audio_process_thread_wrapper, daemon=True)
        self.process_thread.start()
        
        return True

    def _audio_capture_thread_wrapper(self):
        """audio capture thread"""
        try:
            FFMPEG_PATH = "ffmpeg"
            cmd = [
                FFMPEG_PATH,
                '-loglevel', '0',
                '-ar', str(odd_voice_assist_cfg["audio_fmt"]["sample_rate"]),
                '-ac', str(odd_voice_assist_cfg["audio_fmt"]["channels"]),
                '-f', 'pulse',
                '-i', 'default',
                '-fflags', 'nobuffer',
                '-flags', 'low_delay',
                '-f', 's16le',
                '-'
            ]
            
            self.ffmpeg_proc = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.DEVNULL, bufsize=1024*64)
            self.ffmpeg_proc_event.set()
            
            while self.running and self.ffmpeg_proc.poll() is None:
                time.sleep(0.1)
                
        except Exception as e:
            print(f"exception in audio capture thread: {str(e)}")
            self.running = False
        finally:
            self.ffmpeg_proc_event.set()

    def _audio_process_thread_wrapper(self):
        """audio process thread"""
        try:
            while self.running:
                # capture audio
                pcm_data = self.ffmpeg_proc.stdout.read(self.vad_chunk_samples * 2)
                if not pcm_data:
                    break
                
                # convert pcm to np array
                audio_array = np.frombuffer(pcm_data, dtype=odd_voice_assist_cfg["audio_fmt"]["format"])
                audio_array = audio_array.astype(np.float32) / np.iinfo(odd_voice_assist_cfg["audio_fmt"]["format"]).max

                # update audio buffers
                with self.data_lock:
                    self.raw_buffer = np.concatenate((self.raw_buffer, audio_array))

                chunk = None
                
                while len(self.raw_buffer) >= self.vad_chunk_samples:
                    with self.data_lock:
                        chunk = self.raw_buffer[:self.vad_chunk_samples]
                        self.raw_buffer = self.raw_buffer[self.vad_chunk_samples:]

                    if chunk is None:
                        continue

                    # run VAD detection
                    self._vad_detection(chunk)
                    
                    # process wakeup model if vad detected
                    if self.is_speaking:
                        self._process_wakeup(chunk)
                        
        except Exception as e:
            print(f"exception in audio process thread: {str(e)}")
        finally:
            self._cleanup()

    def _vad_detection(self, chunk):
        """run VAD detection"""
        vad_result = self.vad_model.generate(
            input=chunk,
            cache=self.vad_cache,
            is_final=False,
            chunk_size=odd_voice_assist_cfg["audio_fmt"]["chunk_size_ms"]
        )
        
        if vad_result and len(vad_result[0]["value"]) > 0:
            for value in vad_result[0]['value']:
                if value[1] == -1:  # VAD start
                    self.is_speaking = True
                    print(f"vad deteccted at: {value[0]}ms")
                else:  # VAD end
                    self.is_speaking = False
                    print(f"vad end: {value[1]}ms")

    def _process_wakeup(self, chunk):
        """process wakeup model"""
        self.wakeup_queue.append(chunk)
        
        # if queue size > MAX_QUEUE_SIZE, pop and drop the first chunk
        if len(self.wakeup_queue) > self.MAX_QUEUE_SIZE:
            self.wakeup_queue.pop(0)
            
        # execute kws model
        if len(self.wakeup_queue) >= 3:  # 至少3个chunk
            input_data = np.concatenate(self.wakeup_queue)
            res = self.kws_model.generate(
                input=input_data,
                cache=self.kws_cache,
                chunk_size=odd_voice_assist_cfg["audio_fmt"]["stride_ms"]
            )
            print(f"kws result: {res}")

            if res and res[0]['text'] != 'rejected':
                print(f"wakeup success: {res[0]}")
                self.wakeup_queue.clear()

    def _cleanup(self):
        """cleanup resources"""
        if self.ffmpeg_proc and self.ffmpeg_proc.poll() is None:
            self.ffmpeg_proc.terminate()
        if hasattr(self, 'capture_thread'):
            self.capture_thread.join(timeout=1)
        if hasattr(self, 'process_thread'):
            self.process_thread.join(timeout=1)

    def stop(self):
        """stop system"""
        self.running = False
        self._cleanup()

if __name__ == "__main__":
    system = OddVoiceAssistant()
    
    try:
        if system.start():
            print("system started, listening...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nstopping system...")
    finally:
        system.stop()
        print("system stopped")
    