from funasr import AutoModel
# from loguru import logger

import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("funasr").setLevel(logging.DEBUG)
logging.getLogger("onnxruntime").setLevel(logging.ERROR)
logging.getLogger("onnxruntime.capi.onnxruntime_pybind11_state").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


class FunASR:
    def __init__(self):
        self.__model = None

    def __init_model(self):
        if self.__model:
            return

        logger.debug("funasr :: init model start")
        self.__model = AutoModel(model="paraformer-zh",
                                 vad_model="fsmn-vad",
                                 punc_model="ct-punc",
                                 spk_model="cam++",
                                 log_level="error",
                                 hub="ms"  # hub：表示模型仓库，ms为选择modelscope下载，hf为选择huggingface下载。
                                 )
        logger.debug("funasr :: init model complete")

    def __convert_time_to_srt_format(self, time_in_milliseconds):
        hours = time_in_milliseconds // 3600000
        time_in_milliseconds %= 3600000
        minutes = time_in_milliseconds // 60000
        time_in_milliseconds %= 60000
        seconds = time_in_milliseconds // 1000
        time_in_milliseconds %= 1000

        return f"{hours:02}:{minutes:02}:{seconds:02},{time_in_milliseconds:03}"

    def __text_to_srt(self, idx, speaker_id, msg, start_microseconds, end_microseconds) -> str:
        start_time = self.__convert_time_to_srt_format(start_microseconds)
        end_time = self.__convert_time_to_srt_format(end_microseconds)

        msg = f"发言人 {speaker_id}: {msg}"
        srt = """%d
%s --> %s
%s
            """ % (
            idx,
            start_time,
            end_time,
            msg,
        )
        return srt

    def transcribe(self, audio_file: str, output_format: str = "txt"):
        self.__init_model()
        logger.info(f"funasr :: start transcribe audio file: {audio_file}")

        res = self.__model.generate(input=audio_file, batch_size_s=300)
        text = res[0]['text']
        logger.info(f"funasr :: complete transcribe audio file: {audio_file}")
        match output_format:
            case "srt":
                sentences = res[0]['sentence_info']
                subtitles = []

                for idx, sentence in enumerate(sentences):
                    sub = self.__text_to_srt(idx, sentence['spk'], sentence['text'], sentence['start'], sentence['end'])
                    subtitles.append(sub)

                return "\n".join(subtitles)
            case "txt":
                speaker_info = [f"发言人 {sentence['spk']}: {sentence['text']}" for sentence in res[0]['sentence_info']]
                return "\n".join(speaker_info)
            case _:
                return text


funasr = FunASR()

text=funasr.transcribe('aketao.wav', output_type="srt")

print(text)

