import os
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import torch
import torchaudio
import numpy as np

def extract_embedding(audio_path, model_name='damo/speech_campplus_sv_zh-cn_16k-common'):
    """提取音频文件的声纹特征向量"""
    # 加载声纹提取模型
    sv_pipeline = pipeline(
        task=Tasks.speaker_verification,
        model=model_name
    )
    
    # 提取特征
    result = sv_pipeline(audio_path)
    
    # 返回特征向量
    return result['embedding']

def calculate_similarity(embedding1, embedding2):
    """计算两个声纹特征向量的余弦相似度"""
    # 将特征向量转换为numpy数组
    embedding1 = np.array(embedding1)
    embedding2 = np.array(embedding2)
    
    # 计算余弦相似度
    similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    
    return similarity

def verify_speaker(reference_audio, test_audio, threshold=0.7, model_name='damo/speech_campplus_sv_zh-cn_16k-common'):
    """验证两个音频是否来自同一个说话人"""
    # 提取两个音频的声纹特征
    ref_embedding = extract_embedding(reference_audio, model_name)
    test_embedding = extract_embedding(test_audio, model_name)
    
    # 计算相似度
    similarity = calculate_similarity(ref_embedding, test_embedding)
    
    # 判断是否为同一说话人
    is_same_speaker = similarity >= threshold
    
    return {
        'is_same_speaker': is_same_speaker,
        'similarity': similarity,
        'threshold': threshold
    }

def batch_identify_speakers(reference_dir, test_audio, threshold=0.7, model_name='damo/speech_campplus_sv_zh-cn_16k-common'):
    """在多个参考说话人中识别测试音频的说话人"""
    # 获取参考目录中的所有音频文件
    reference_files = [f for f in os.listdir(reference_dir) if f.endswith(('.wav', '.mp3'))]
    
    results = []
    
    for ref_file in reference_files:
        ref_path = os.path.join(reference_dir, ref_file)
        print(f"ref_file={ref_path}, test_audio={test_audio}")
        result = verify_speaker(ref_path, test_audio, threshold, model_name)
        result['reference_file'] = ref_file
        results.append(result)
    
    # 按相似度排序
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    return results

# 使用示例
if __name__ == "__main__":
    # 选择模型：Cam++ 或 ERes2Net
    # Cam++模型
    model_name = 'damo/speech_campplus_sv_zh-cn_16k-common'
    
    # ERes2Net模型
    # model_name = 'damo/speech_eres2net_sv_zh-cn_16k-common'
    
    # 验证两个音频是否来自同一说话人
    reference_audio = "sv_references/jacky-16k-16bits-mono.wav" # 'reference_audio.wav'
    test_audio = 'jacky.wav' # 'test_audio.wav'
    
    verification_result = verify_speaker(reference_audio, test_audio, model_name=model_name)
    print(f"声纹验证结果: {'是同一说话人' if verification_result['is_same_speaker'] else '不是同一说话人'}")
    print(f"相似度得分: {verification_result['similarity']:.4f}")
    print(f"阈值: {verification_result['threshold']}")
    
    # 批量识别说话人
    reference_dir = 'sv_references'
    batch_results = batch_identify_speakers(reference_dir, test_audio, model_name=model_name)
    
    print("\n批量识别结果:")
    for i, result in enumerate(batch_results):
        print(f"{i+1}. {result['reference_file']}: 相似度 {result['similarity']:.4f}, {'匹配' if result['is_same_speaker'] else '不匹配'}")
