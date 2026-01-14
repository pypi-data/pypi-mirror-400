import sys
sys.path.append('../')
from logic.minutes import CStorageMinutes
import uuid
import time

if __name__ == '__main__':
    
    ## add 
    strUuidId = str(uuid.uuid1())
    strRank = "0"
    strUniqueId = "123456"
    strFileName = "test.mp3"
    strBeginTime  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(CStorageMinutes.addOpenFileMeeting(strUuidId , strRank , strUniqueId,strFileName,strBeginTime))

    print(CStorageMinutes.getOpenFileMeetingInfo(strUuidId))
    
    
    ## start
    meeting = CStorageMinutes.getOpenFileMeetingInfoByPriority()
    print(meeting)
    strAliTaskId = ''
    print(CStorageMinutes.updateOpenFileMeetingStart(meeting['uuid'] , strAliTaskId))

    print(CStorageMinutes.getOpenFileMeetingInfo(strUuidId))
    
    ## finish
    strEndTime  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    texts = []
    item1 = {'session_id':meeting['uuid'],'text_bg_time':123,'text_ed_time':456 , 'text_content':'item1'}
    texts.append(item1)
    item2 =  {'session_id':meeting['uuid'],'text_bg_time':123,'text_ed_time':456 , 'text_content':'item2'}
    texts.append(item2)

    print(CStorageMinutes.updateOpenFileMeetingEnd(meeting['uuid'],strEndTime , texts))

    print(CStorageMinutes.getOpenFileMeetingInfo(strUuidId))
    ## if failed test
    
    strUuidId = str(uuid.uuid1())
    strRank = "0"
    strUniqueId = "123456"
    strFileName = "test.mp3"
    strBeginTime  = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    print(CStorageMinutes.addOpenFileMeeting(strUuidId , strRank , strUniqueId,strFileName,strBeginTime))

    
    meeting = CStorageMinutes.getOpenFileMeetingInfoByPriority()
    strAliTaskId = ''
    print(CStorageMinutes.updateOpenFileMeetingStart(meeting['uuid'] , strAliTaskId))
    print(meeting)

    #failed
    print(CStorageMinutes.updateOpenFileMeetingByRevert(meeting['uuid']))
    print(CStorageMinutes.getOpenFileMeetingInfoByPriority())