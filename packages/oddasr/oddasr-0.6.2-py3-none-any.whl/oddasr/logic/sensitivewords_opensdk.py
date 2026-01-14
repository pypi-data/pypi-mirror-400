import json
import os
import platform
import os.path

from oddasr.log import logger

from oddasr.logic import sensitivewords
import oddasr.odd_asr_config as config


def get_sensitive_words_from_file():
    path = ''
    res = {}
    if platform.system() != "Windows":
        path = os.path.join(config.odd_asr_slp_cfg['sensitive_words']['path'], 'sensitivewords.txt')
    else:
        path = os.getcwd()
        path = os.path.join(path, '.\\download', '.\\sensitivewords.txt')
    logger.info(path)
    words = []
    if os.path.isfile(path):
        file = open(path, 'r', encoding='utf-8')
        lines = file.readlines()

        for line in lines:
            logger.info(line)
            line = line.strip()
            if len(line) != 0:
                words.append(line)
        file.close()
    if len(words) == 0 and platform.system() == "Windows":
        words.append('默认值1')
        words.append('默认值2')
    return words

def get_sensitive_words(sens_id):
    words = sensitivewords.SensitiveWordManage.get_sensitive_word(sens_id)
    rows = []
    if words:
        i = 1
        for word in json.loads(words['sensitive_word']):
            rows.append({'id': i, 'word': word})
            i = i + 1
    total = len(rows)
    res = {'total': total, 'rows': rows}
    return res


def save_sensitive_words(words):
    path = ''
    if platform.system() != "Windows":
        path = os.path.join(config.odd_asr_slp_cfg['sensitive_words']['path'], 'sensitivewords.txt')
    else:
        print(words)
        path = os.getcwd()
        path = os.path.join(path, '.\\download', '.\\sensitivewords.txt')
    file = open(path, 'w', encoding='utf-8')
    for word in words:
        word = word.strip()
        if len(word) != 0:
            file.write(word + '\n')
    file.close()
    return True

def update_sensitive_words(words):
    res = save_sensitive_words(words)
    return res

def merge_sensitive_words(unique_id, sensitive_word):
    logger.info("+++++++++++++++++++++")
    data = sensitivewords.SensitiveWordManage.set_sensitive_word(unique_id, sensitive_word)
    logger.info(f"set words{data}")
    '''
    敏感词通知到jdlserver
    '''
    # sensitive_words_ntf = {'msg_type': 'SENSITIVEWORDS_NTF', 'msg_id': '', 'service_type': 'ASR_MANAGER',
    #                        'msg_data': {'unique_id': unique_id}}

    # sync_send_to_jdl_server_ws(json_data=json.dumps(sensitive_words_ntf), reply=False)

    return True


def sync_sensitive_words(words):
    #jdlserver read from file, no need sync.
    return

if __name__ == '__main__':
    print(get_sensitive_words())