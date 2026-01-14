from funasr import AutoModel


model = AutoModel(model="paraformer-zh-streaming", model_revision="v2.0.4")

import soundfile
import os

chunk_size = [0, 10, 5] #[0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4 #number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1 #number of encoder chunks to lookback for decoder cross-attention

def stream_asr():
    wav_file = "1.wav"
    speech, sample_rate = soundfile.read(wav_file)
    chunk_stride = chunk_size[1] * 960 # 600ms

    cache = {}
    total_chunk_num = int(len((speech)-1)/chunk_stride+1)

    print(f"total_chunk_num: {total_chunk_num}, chunk_stride: {chunk_stride}")

    for i in range(total_chunk_num):
        speech_chunk = speech[i*chunk_stride:(i+1)*chunk_stride]
        is_final = i == total_chunk_num - 1
        res = model.generate(input=speech_chunk, cache=cache, is_final=is_final, chunk_size=chunk_size, encoder_chunk_look_back=encoder_chunk_look_back, decoder_chunk_look_back=decoder_chunk_look_back)
        print(res)


def stream_asr2():
    file = "1.wav"
    import numpy as np

    total_text = []
    cache = {}

    # 假设 PCM 文件是 16 位有符号整数，采样率为 16000 Hz
    dtype = np.int16

    try:
        # 以二进制模式读取 PCM 文件
        with open(file, 'rb') as f:
            pcm_data = np.frombuffer(f.read(), dtype=dtype)
    except Exception as e:
        print(f"Error reading PCM file: {e}")
        exit(1)

    # 将 PCM 数据转换为浮点数，范围在 -1.0 到 1.0 之间
    speech = pcm_data.astype(np.float32) / 32768.0

    chunk_stride = chunk_size[1] * 960 # 600ms
    total_chunk_num = len(speech) // chunk_stride

    print(f"total_chunk_num: {total_chunk_num}, chunk_stride: {chunk_stride}")

    for i in range(total_chunk_num):
        start = i * chunk_stride
        end = start + chunk_stride
        audio_chunk = speech[start:end]

        # 标记是否为最后一个分片
        is_final = i == total_chunk_num - 1
        text = model.generate(input=audio_chunk, cache=cache, is_final=is_final, chunk_size=chunk_size, encoder_chunk_look_back=encoder_chunk_look_back, decoder_chunk_look_back=decoder_chunk_look_back)
        if text and isinstance(text, list) and len(text) > 0 and 'text' in text[0]:
            partial_text = text[0]['text']
            print(f"Partial result for chunk {i + 1}/{total_chunk_num}: {partial_text}")
            total_text.append(partial_text)
        else:
            print(f"Empty or invalid result for chunk {i + 1}/{total_chunk_num}")

    # 处理剩余不足 960 个样本的数据
    if len(speech) % chunk_stride != 0:
        remaining_audio = speech[total_chunk_num * chunk_stride:]
        text = model.generate(input=remaining_audio, cache=cache, is_final=True, chunk_size=chunk_size, encoder_chunk_look_back=encoder_chunk_look_back, decoder_chunk_look_back=decoder_chunk_look_back)
        if text and isinstance(text, list) and len(text) > 0 and 'text' in text[0]:
            partial_text = text[0]['text']
            print(f"Partial result for remaining chunk: {partial_text}")
            total_text.append(partial_text)
        else:
            print(f"Empty or invalid result for remaining chunk")

    final_text = ''.join(total_text)
    print(f"Final transcription result: {final_text}")

if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Your WAV file need to recoginze to text.")
    parser.add_argument("test_type", type=str, help="test type, 0 for stream_asr, 1 for stream_asr2.")
    args = parser.parse_args()

    print(f"test type: {args.test_type}")

    if args.test_type == "0":
        stream_asr()
    else:
        stream_asr2()
