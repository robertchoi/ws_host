#-*- coding:utf-8 -*-
import sys
import serial
import time
import signal
import threading

import pymysql
import datetime
import pandas as pd
import numpy
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)  #gpio 모드 셋팅
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_UP)       #Button 입력 GPIO23

line = [] #라인 단위로 데이터 가져올 리스트 변수

#port = '/dev/tty.usbserial-14440' # 시리얼 포트
port = '/dev/ttyUSB0' # 시리얼 포트
baud = 115200 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수

entryCnt = 0

board_db = pymysql.connect(
    host='wonderdb.c03rvmbon7t9.ap-northeast-2.rds.amazonaws.com',
    user='admin',
    password='admin1234qwer',
    database='one',
    charset='utf8'
)

dicBand = {
    "406D9FDAE":"user1",
    "60A9A5DAE":"user2",
    "608FA3DAE":"user3",
    "D066A3DAE":"user4",
    "E061A7DAE":"user5",
    "50CADBA6E":"user6",
    "B0E9DDAE":"user7",
    "60D0A5DAE":"user8",
    "8067A6DAE":"user9",
    "46CAA22E":"user10"
}


dicScore = {
    "1":"S",
    "2":"20",
    "3":"30",
    "4":"40",
    "5":"50",
    "6":"60",
    "7":"70",
    "8":"80",
    "9":"F"
}

dicTime = {
    "1":"S",
}

cursor = board_db.cursor(pymysql.cursors.DictCursor)
sql = "select * from sw_score;"
sql_insert = "insert into score (id, timelog, tagvalue, tagname) VALUES (%s, %s, %s, %s)" 
sql_findName  = "select user_name, user_phone, sex from user_band where bandId = %s"
sql_sw_total_s_insert = "insert into sw_score_total (log_name, log_time_s) VALUES (%s, %s)" 
sql_sw_total_s_update = "update sw_score_total set log_time_f = %s, log_score = %s where log_time_s = %s" 
sql_sw_score_update = "update sw_score set log_name = %s, log_score = %s" 


sql_climbing_init = "UPDATE climbing_score SET `item161_score` = '0', `item061_score` = '0', `item111_score` = '0', `item011_score` = '0', `user20_name` = 'user20', `user10_name` = 'user10', `user15_name` = 'user15', `user05_name` = 'user5', `user19_name` = 'user19', `user09_name` = 'user9', `user14_name` = 'user14', `user04_name` = 'user4', `item201_score` = '0', `item101_score` = '0', `item151_score` = '0', `item051_score` = '0', `user18_name` = 'user18', `user08_name` = 'user8', `user13_name` = 'user13', `user03_name` = 'user3', `item202_score` = '0', `item102_score` = '0', `item152_score` = '0', `item052_score` = '0', `item191_score` = '0', `item091_score` = '0', `item141_score` = '0', `item041_score` = '0', `item203_score` = '0', `item103_score` = '0', `item153_score` = '0', `item053_score` = '0', `user17_name` = 'user17', `user07_name` = 'user7', `user12_name` = 'user12', `user02_name` = 'user2', `item204_score` = '0', `item104_score` = '0', `item154_score` = '0', `item054_score` = '0', `item192_score` = '0', `item092_score` = '0', `item142_score` = '0', `item042_score` = '0', `item205_score` = '0', `item105_score` = '0', `item155_score` = '0', `item055_score` = '0', `item181_score` = '0', `item081_score` = '0', `item131_score` = '0', `item031_score` = '0', `item193_score` = '0', `item093_score` = '0', `item143_score` = '0', `item043_score` = '0', `user16_name` = 'user16', `user06_name` = 'user6', `user11_name` = 'user11', `user01_name` = 'user1', `item194_score` = '0', `item094_score` = '0', `item144_score` = '0', `item044_score` = '0', `item182_score` = '0', `item082_score` = '0', `item132_score` = '0', `item032_score` = '0', `item195_score` = '0', `item095_score` = '0', `item145_score` = '0', `item045_score` = '0', `item171_score` = '0', `item071_score` = '0', `item121_score` = '0', `item021_score` = '0', `item184_score` = '0', `item084_score` = '0', `item134_score` = '0', `item034_score` = '0', `item172_score` = '0', `item072_score` = '0', `item122_score` = '0', `item022_score` = '0', `item185_score` = '0', `item085_score` = '0', `item135_score` = '0', `item035_score` = '0', `item162_score` = '0', `item062_score` = '0', `item112_score` = '0', `item012_score` = '0', `item173_score` = '0', `item073_score` = '0', `item123_score` = '0', `item023_score` = '0', `item163_score` = '0', `item063_score` = '0'"
sql_climbing_init01 = "UPDATE climbing_score SET `user01_name` = 'user01', `item011_score` = '0', `item012_score` = '0', `item013_score` = '0', `item014_score` = '0', `item015_score` = '0'"
sql_climbing_init02 = "UPDATE climbing_score SET `user02_name` = 'user02', `item021_score` = '0', `item022_score` = '0', `item023_score` = '0', `item024_score` = '0', `item025_score` = '0'"
sql_climbing_init03 = "UPDATE climbing_score SET `user03_name` = 'user03', `item031_score` = '0', `item032_score` = '0', `item033_score` = '0', `item034_score` = '0', `item035_score` = '0'"
sql_climbing_init04 = "UPDATE climbing_score SET `user04_name` = 'user04', `item041_score` = '0', `item042_score` = '0', `item043_score` = '0', `item044_score` = '0', `item045_score` = '0'"
sql_climbing_init05 = "UPDATE climbing_score SET `user05_name` = 'user05', `item051_score` = '0', `item052_score` = '0', `item053_score` = '0', `item054_score` = '0', `item055_score` = '0'"
sql_climbing_init06 = "UPDATE climbing_score SET `user06_name` = 'user06', `item061_score` = '0', `item062_score` = '0', `item063_score` = '0', `item064_score` = '0', `item065_score` = '0'"
sql_climbing_init07 = "UPDATE climbing_score SET `user07_name` = 'user07', `item071_score` = '0', `item072_score` = '0', `item073_score` = '0', `item074_score` = '0', `item075_score` = '0'"
sql_climbing_init08 = "UPDATE climbing_score SET `user08_name` = 'user08', `item081_score` = '0', `item082_score` = '0', `item083_score` = '0', `item084_score` = '0', `item085_score` = '0'"
sql_climbing_init09 = "UPDATE climbing_score SET `user09_name` = 'user09', `item091_score` = '0', `item092_score` = '0', `item093_score` = '0', `item094_score` = '0', `item095_score` = '0'"
sql_climbing_init10 = "UPDATE climbing_score SET `user10_name` = 'user10', `item101_score` = '0', `item102_score` = '0', `item103_score` = '0', `item104_score` = '0', `item105_score` = '0'"
sql_climbing_init11 = "UPDATE climbing_score SET `user11_name` = 'user11', `item111_score` = '0', `item112_score` = '0', `item113_score` = '0', `item114_score` = '0', `item115_score` = '0'"
sql_climbing_init12 = "UPDATE climbing_score SET `user12_name` = 'user12', `item121_score` = '0', `item122_score` = '0', `item123_score` = '0', `item124_score` = '0', `item125_score` = '0'"
sql_climbing_init13 = "UPDATE climbing_score SET `user13_name` = 'user13', `item131_score` = '0', `item132_score` = '0', `item133_score` = '0', `item134_score` = '0', `item135_score` = '0'"
sql_climbing_init14 = "UPDATE climbing_score SET `user14_name` = 'user14', `item141_score` = '0', `item142_score` = '0', `item143_score` = '0', `item144_score` = '0', `item145_score` = '0'"
sql_climbing_init15 = "UPDATE climbing_score SET `user15_name` = 'user15', `item151_score` = '0', `item152_score` = '0', `item153_score` = '0', `item154_score` = '0', `item155_score` = '0'"
sql_climbing_init16 = "UPDATE climbing_score SET `user16_name` = 'user16', `item161_score` = '0', `item162_score` = '0', `item163_score` = '0', `item164_score` = '0', `item165_score` = '0'"
sql_climbing_init17 = "UPDATE climbing_score SET `user17_name` = 'user17', `item171_score` = '0', `item172_score` = '0', `item173_score` = '0', `item174_score` = '0', `item175_score` = '0'"
sql_climbing_init18 = "UPDATE climbing_score SET `user18_name` = 'user18', `item181_score` = '0', `item182_score` = '0', `item183_score` = '0', `item184_score` = '0', `item185_score` = '0'"
sql_climbing_init19 = "UPDATE climbing_score SET `user19_name` = 'user19', `item191_score` = '0', `item192_score` = '0', `item193_score` = '0', `item194_score` = '0', `item195_score` = '0'"
sql_climbing_init20 = "UPDATE climbing_score SET `user20_name` = 'user20', `item201_score` = '0', `item202_score` = '0', `item203_score` = '0', `item204_score` = '0', `item205_score` = '0'"



sql_climbing_total_logtime_insert = "insert into climbing_score_total (log_time, log_name, log_phone, log_sex) VALUES (%s, %s, %s, %s)"  
#sql_climbing_total_item1s_insert = "insert into climbing_score_total (log_name, log_item1_s) VALUES (%s, %s) where = %s" 
#sql_climbing_total_item2s_insert = "insert into climbing_score_total (log_name, log_item2_s) VALUES (%s, %s) where = %s" 
#sql_climbing_total_item3s_insert = "insert into climbing_score_total (log_name, log_item2_s) VALUES (%s, %s) where = %s" 
#sql_climbing_total_item4s_insert = "insert into climbing_score_total (log_name, log_item3_s) VALUES (%s, %s) where = %s" 
#sql_climbing_total_item5s_insert = "insert into climbing_score_total (log_name, log_item4_s) VALUES (%s, %s) where = %s" 

sql_climbing_total_item1s_insert = "UPDATE climbing_score_total SET log_item1_s=%s where log_time = %s and log_name=%s" 
sql_climbing_total_item2s_insert = "UPDATE climbing_score_total SET log_item2_s=%s where log_time = %s and log_name=%s" 
sql_climbing_total_item3s_insert = "UPDATE climbing_score_total SET log_item3_s=%s where log_time = %s and log_name=%s" 
sql_climbing_total_item4s_insert = "UPDATE climbing_score_total SET log_item4_s=%s where log_time = %s and log_name=%s" 
sql_climbing_total_item5s_insert = "UPDATE climbing_score_total SET log_item5_s=%s where log_time = %s and log_name=%s" 

sql_climbing_total_item1f_insert = "UPDATE climbing_score_total SET log_item1_f=%s, log_item1_time = %s where log_time = %s and log_name=%s" 
sql_climbing_total_item2f_insert = "UPDATE climbing_score_total SET log_item2_f=%s, log_item2_time = %s where log_time = %s and log_name=%s" 
sql_climbing_total_item3f_insert = "UPDATE climbing_score_total SET log_item3_f=%s, log_item3_time = %s where log_time = %s and log_name=%s" 
sql_climbing_total_item4f_insert = "UPDATE climbing_score_total SET log_item4_f=%s, log_item4_time = %s where log_time = %s and log_name=%s" 
sql_climbing_total_item5f_insert = "UPDATE climbing_score_total SET log_item5_f=%s, log_item5_time = %s where log_time = %s and log_name=%s" 

sql_climbing_user1_update = "update climbing_score set user01_name = %s"
sql_climbing_user2_update = "update climbing_score set user02_name = %s"
sql_climbing_user3_update = "update climbing_score set user03_name = %s"
sql_climbing_user4_update = "update climbing_score set user04_name = %s"
sql_climbing_user5_update = "update climbing_score set user05_name = %s"
sql_climbing_user6_update = "update climbing_score set user06_name = %s"
sql_climbing_user7_update = "update climbing_score set user07_name = %s"
sql_climbing_user8_update = "update climbing_score set user08_name = %s"
sql_climbing_user9_update = "update climbing_score set user09_name = %s"
sql_climbing_user10_update = "update climbing_score set user10_name = %s"
sql_climbing_user11_update = "update climbing_score set user11_name = %s"
sql_climbing_user12_update = "update climbing_score set user12_name = %s"
sql_climbing_user13_update = "update climbing_score set user13_name = %s"
sql_climbing_user14_update = "update climbing_score set user14_name = %s"
sql_climbing_user15_update = "update climbing_score set user15_name = %s"
sql_climbing_user16_update = "update climbing_score set user16_name = %s"
sql_climbing_user17_update = "update climbing_score set user17_name = %s"
sql_climbing_user18_update = "update climbing_score set user18_name = %s"
sql_climbing_user19_update = "update climbing_score set user19_name = %s"
sql_climbing_user20_update = "update climbing_score set user20_name = %s"

sql_climbing_score_011_update = "UPDATE climbing_score SET item011_score = %s"
sql_climbing_score_012_update = "UPDATE climbing_score SET item012_score = %s"
sql_climbing_score_013_update = "UPDATE climbing_score SET item013_score = %s"
sql_climbing_score_014_update = "UPDATE climbing_score SET item014_score = %s"
sql_climbing_score_015_update = "UPDATE climbing_score SET item015_score = %s"
sql_climbing_score_021_update = "UPDATE climbing_score SET item021_score = %s"
sql_climbing_score_022_update = "UPDATE climbing_score SET item022_score = %s"
sql_climbing_score_023_update = "UPDATE climbing_score SET item023_score = %s"
sql_climbing_score_024_update = "UPDATE climbing_score SET item024_score = %s"
sql_climbing_score_025_update = "UPDATE climbing_score SET item025_score = %s"
sql_climbing_score_031_update = "UPDATE climbing_score SET item031_score = %s"
sql_climbing_score_032_update = "UPDATE climbing_score SET item032_score = %s"
sql_climbing_score_033_update = "UPDATE climbing_score SET item033_score = %s"
sql_climbing_score_034_update = "UPDATE climbing_score SET item034_score = %s"
sql_climbing_score_035_update = "UPDATE climbing_score SET item035_score = %s"
sql_climbing_score_041_update = "UPDATE climbing_score SET item041_score = %s"
sql_climbing_score_042_update = "UPDATE climbing_score SET item042_score = %s"
sql_climbing_score_043_update = "UPDATE climbing_score SET item043_score = %s"
sql_climbing_score_044_update = "UPDATE climbing_score SET item044_score = %s"
sql_climbing_score_045_update = "UPDATE climbing_score SET item045_score = %s"
sql_climbing_score_051_update = "UPDATE climbing_score SET item051_score = %s"
sql_climbing_score_052_update = "UPDATE climbing_score SET item052_score = %s"
sql_climbing_score_053_update = "UPDATE climbing_score SET item053_score = %s"
sql_climbing_score_054_update = "UPDATE climbing_score SET item054_score = %s"
sql_climbing_score_055_update = "UPDATE climbing_score SET item055_score = %s"
sql_climbing_score_061_update = "UPDATE climbing_score SET item061_score = %s"
sql_climbing_score_062_update = "UPDATE climbing_score SET item062_score = %s"
sql_climbing_score_063_update = "UPDATE climbing_score SET item063_score = %s"
sql_climbing_score_064_update = "UPDATE climbing_score SET item064_score = %s"
sql_climbing_score_065_update = "UPDATE climbing_score SET item065_score = %s"
sql_climbing_score_071_update = "UPDATE climbing_score SET item071_score = %s"
sql_climbing_score_072_update = "UPDATE climbing_score SET item072_score = %s"
sql_climbing_score_073_update = "UPDATE climbing_score SET item073_score = %s"
sql_climbing_score_074_update = "UPDATE climbing_score SET item074_score = %s"
sql_climbing_score_075_update = "UPDATE climbing_score SET item075_score = %s"
sql_climbing_score_081_update = "UPDATE climbing_score SET item081_score = %s"
sql_climbing_score_082_update = "UPDATE climbing_score SET item082_score = %s"
sql_climbing_score_083_update = "UPDATE climbing_score SET item083_score = %s"
sql_climbing_score_084_update = "UPDATE climbing_score SET item084_score = %s"
sql_climbing_score_085_update = "UPDATE climbing_score SET item085_score = %s"
sql_climbing_score_091_update = "UPDATE climbing_score SET item091_score = %s"
sql_climbing_score_092_update = "UPDATE climbing_score SET item092_score = %s"
sql_climbing_score_093_update = "UPDATE climbing_score SET item093_score = %s"
sql_climbing_score_094_update = "UPDATE climbing_score SET item094_score = %s"
sql_climbing_score_095_update = "UPDATE climbing_score SET item095_score = %s"
sql_climbing_score_101_update = "UPDATE climbing_score SET item101_score = %s"
sql_climbing_score_102_update = "UPDATE climbing_score SET item102_score = %s"
sql_climbing_score_103_update = "UPDATE climbing_score SET item103_score = %s"
sql_climbing_score_104_update = "UPDATE climbing_score SET item104_score = %s"
sql_climbing_score_105_update = "UPDATE climbing_score SET item105_score = %s"
sql_climbing_score_111_update = "UPDATE climbing_score SET item111_score = %s"
sql_climbing_score_112_update = "UPDATE climbing_score SET item112_score = %s"
sql_climbing_score_113_update = "UPDATE climbing_score SET item113_score = %s"
sql_climbing_score_114_update = "UPDATE climbing_score SET item114_score = %s"
sql_climbing_score_115_update = "UPDATE climbing_score SET item115_score = %s"
sql_climbing_score_121_update = "UPDATE climbing_score SET item121_score = %s"
sql_climbing_score_122_update = "UPDATE climbing_score SET item122_score = %s"
sql_climbing_score_123_update = "UPDATE climbing_score SET item123_score = %s"
sql_climbing_score_124_update = "UPDATE climbing_score SET item124_score = %s"
sql_climbing_score_125_update = "UPDATE climbing_score SET item125_score = %s"
sql_climbing_score_131_update = "UPDATE climbing_score SET item131_score = %s"
sql_climbing_score_132_update = "UPDATE climbing_score SET item132_score = %s"
sql_climbing_score_133_update = "UPDATE climbing_score SET item133_score = %s"
sql_climbing_score_134_update = "UPDATE climbing_score SET item134_score = %s"
sql_climbing_score_135_update = "UPDATE climbing_score SET item135_score = %s"
sql_climbing_score_141_update = "UPDATE climbing_score SET item141_score = %s"
sql_climbing_score_142_update = "UPDATE climbing_score SET item142_score = %s"
sql_climbing_score_143_update = "UPDATE climbing_score SET item143_score = %s"
sql_climbing_score_144_update = "UPDATE climbing_score SET item144_score = %s"
sql_climbing_score_145_update = "UPDATE climbing_score SET item145_score = %s"
sql_climbing_score_151_update = "UPDATE climbing_score SET item151_score = %s"
sql_climbing_score_152_update = "UPDATE climbing_score SET item152_score = %s"
sql_climbing_score_153_update = "UPDATE climbing_score SET item153_score = %s"
sql_climbing_score_154_update = "UPDATE climbing_score SET item154_score = %s"
sql_climbing_score_155_update = "UPDATE climbing_score SET item155_score = %s"
sql_climbing_score_161_update = "UPDATE climbing_score SET item161_score = %s"
sql_climbing_score_162_update = "UPDATE climbing_score SET item162_score = %s"
sql_climbing_score_163_update = "UPDATE climbing_score SET item163_score = %s"
sql_climbing_score_164_update = "UPDATE climbing_score SET item164_score = %s"
sql_climbing_score_165_update = "UPDATE climbing_score SET item165_score = %s"
sql_climbing_score_171_update = "UPDATE climbing_score SET item171_score = %s"
sql_climbing_score_172_update = "UPDATE climbing_score SET item172_score = %s"
sql_climbing_score_173_update = "UPDATE climbing_score SET item173_score = %s"
sql_climbing_score_174_update = "UPDATE climbing_score SET item174_score = %s"
sql_climbing_score_175_update = "UPDATE climbing_score SET item175_score = %s"
sql_climbing_score_181_update = "UPDATE climbing_score SET item181_score = %s"
sql_climbing_score_182_update = "UPDATE climbing_score SET item182_score = %s"
sql_climbing_score_183_update = "UPDATE climbing_score SET item183_score = %s"
sql_climbing_score_184_update = "UPDATE climbing_score SET item184_score = %s"
sql_climbing_score_185_update = "UPDATE climbing_score SET item185_score = %s"
sql_climbing_score_191_update = "UPDATE climbing_score SET item191_score = %s"
sql_climbing_score_192_update = "UPDATE climbing_score SET item192_score = %s"
sql_climbing_score_193_update = "UPDATE climbing_score SET item193_score = %s"
sql_climbing_score_194_update = "UPDATE climbing_score SET item194_score = %s"
sql_climbing_score_195_update = "UPDATE climbing_score SET item195_score = %s"
sql_climbing_score_201_update = "UPDATE climbing_score SET item201_score = %s"
sql_climbing_score_202_update = "UPDATE climbing_score SET item202_score = %s"
sql_climbing_score_203_update = "UPDATE climbing_score SET item203_score = %s"
sql_climbing_score_204_update = "UPDATE climbing_score SET item204_score = %s"
sql_climbing_score_205_update = "UPDATE climbing_score SET item205_score = %s"
#쓰레드 종료용 시그널 함수
def handler(signum, frame):
     exitThread = True


#데이터 처리할 함수
def parsing_data(data):
    # 리스트 구조로 들어 왔기 때문에
    # 작업하기 편하게 스트링으로 합침
    tmp = ''.join(data)

    #print(dicBand.get(tmp[5:]))  
    now = datetime.datetime.now()
    ct = now.strftime('%Y-%m-%d %H:%M:%S')
    #myWindow.label.setText(dicBand.get(tmp[5:])+ " : " + str(ct))



    #cursor.execute(sql_insert,(dicBand.get(tmp[5:]), ct, dicScore.get(tmp[4]), tmp[1:4])) 
    #board_db.commit()

    #출력!
    #T0021041E8D3A467081E
    print(tmp)
    if len(tmp) == 20:
        itemNo = tmp[1:4]
        startorfinish = tmp[4:5]
        bandId = tmp[5:-1]
    else:
        itemNo = tmp[2:5]
        startorfinish = tmp[5:6]
        bandId = tmp[6:-1]
    print(itemNo)
    print(bandId)
    
    if startorfinish == '7':
        print('Enter')

        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        if df.empty:
            print('DataFrame is empty!')
            return

        user_name = df.iloc[0,0]
        user_phone = df.iloc[0,1]
        sex = df.iloc[0,2]
        #print("user_name", user_name)

        if bandId in dicTime: 
            print('already Enter!')
            return     

        global entryCnt
        entryCnt += 1
        if entryCnt <= 20:
            if entryCnt == 1:
                global ct_global
                dicTime['logTime'] = ct
                ct_global = ct
                #cursor.execute(sql_climbing_user1_update,bandId)
                cursor.execute(sql_climbing_user1_update,user_name)  
            elif entryCnt == 2:
                cursor.execute(sql_climbing_user2_update,user_name) 
            elif entryCnt == 3:
                cursor.execute(sql_climbing_user3_update,user_name) 
            elif entryCnt == 4:
                cursor.execute(sql_climbing_user4_update,user_name) 
            elif entryCnt == 5:
                cursor.execute(sql_climbing_user5_update,user_name) 
            elif entryCnt == 6:
                cursor.execute(sql_climbing_user6_update,user_name) 
            elif entryCnt == 7:
                cursor.execute(sql_climbing_user7_update,user_name) 
            elif entryCnt == 8:
                cursor.execute(sql_climbing_user8_update,user_name) 
            elif entryCnt == 9:
                cursor.execute(sql_climbing_user9_update,user_name) 
            elif entryCnt == 10:
                cursor.execute(sql_climbing_user10_update,user_name) 
            elif entryCnt == 11:
                cursor.execute(sql_climbing_user11_update,user_name) 
            elif entryCnt == 12:
                cursor.execute(sql_climbing_user12_update,user_name) 
            elif entryCnt == 13:
                cursor.execute(sql_climbing_user13_update,user_name) 
            elif entryCnt == 14:
                cursor.execute(sql_climbing_user14_update,user_name) 
            elif entryCnt == 15:
                cursor.execute(sql_climbing_user15_update,user_name) 
            elif entryCnt == 16:
                cursor.execute(sql_climbing_user16_update,user_name) 
            elif entryCnt == 17:
                cursor.execute(sql_climbing_user17_update,user_name) 
            elif entryCnt == 18:
                cursor.execute(sql_climbing_user18_update,user_name) 
            elif entryCnt == 19:
                cursor.execute(sql_climbing_user19_update,user_name) 
            else:
                cursor.execute(sql_climbing_user20_update,user_name) 
            
            board_db.commit()
            dicTime[bandId] = ct

            cursor.execute(sql_climbing_total_logtime_insert,(ct_global, user_name, user_phone, sex)) 
            board_db.commit()
            print(dicTime)


    elif startorfinish == '1': # '1' 
        print('start')
        if entryCnt == 0:
            print("Entry 0")
            return

        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        if df.empty:
            print('DataFrame is empty!')
            return

        value = dicTime.get(bandId)
        if value == None:
            print("Not Enter")
            return
        

        user_name = df.iloc[0,0]
        #print(user_name)

        dicTime[bandId] = ct
        print(ct)
        print("dicTime", dicTime)
        print(entryCnt)

        userIndex = list(dicTime.keys()).index(bandId)
        print("userIndex", userIndex)




        logTime = datetime.datetime.strptime(dicTime['logTime'],'%Y-%m-%d %H:%M:%S')

        print(type(logTime))
        if itemNo == '001':
            cursor.execute(sql_climbing_total_item1s_insert,(ct, logTime, user_name)) 
        elif itemNo == '002':
            cursor.execute(sql_climbing_total_item2s_insert,(ct, logTime, user_name)) 
        elif itemNo == '003':
            cursor.execute(sql_climbing_total_item3s_insert,(ct, logTime, user_name)) 
        elif itemNo == '004':
            cursor.execute(sql_climbing_total_item4s_insert,(ct, logTime, user_name)) 
        elif itemNo == '005':
            cursor.execute(sql_climbing_total_item4s_insert,(ct, logTime, user_name)) 
        else:
            cursor.execute(sql_climbing_total_item5s_insert,(ct, logTime, user_name)) 
        board_db.commit()
        dicTime[bandId]=ct
        print(dicTime)

    else:
        print('finish')

        if entryCnt == 0:
            print("Entry 0")
            return

        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        if df.empty:
            print('DataFrame is empty!')
            return

        value = dicTime.get(bandId)
        if value == None:
            print("Not Enter")
            return

        user_name = df.iloc[0,0]
        user_phone = df.iloc[0,1]
        sex = df.iloc[0,2]
        #print(user_name)
        
        print(ct)
        logTime = datetime.datetime.strptime(dicTime['logTime'],'%Y-%m-%d %H:%M:%S')
        finish_time = datetime.datetime.strptime(ct,'%Y-%m-%d %H:%M:%S')
        start_time = datetime.datetime.strptime(dicTime[bandId],'%Y-%m-%d %H:%M:%S')
        score = finish_time - start_time
        print(score)
        print(finish_time, start_time, score)
        if itemNo == '001':
            cursor.execute(sql_climbing_total_item1f_insert,(ct, score, logTime, user_name)) 
        elif itemNo == '002':
            cursor.execute(sql_climbing_total_item2f_insert,(ct, score, logTime, user_name)) 
        elif itemNo == '003':
            cursor.execute(sql_climbing_total_item3f_insert,(ct, score, logTime, user_name)) 
        elif itemNo == '004':
            cursor.execute(sql_climbing_total_item4f_insert,(ct, score, logTime, user_name)) 
        elif itemNo == '005':
            cursor.execute(sql_climbing_total_item4f_insert,(ct, score, logTime, user_name)) 
        else:
            cursor.execute(sql_climbing_total_item5f_insert,(ct, score, logTime, user_name)) 
        board_db.commit()
 
        userIndex = list(dicTime.keys()).index(bandId)
        print("userIndex", userIndex)

        if userIndex == 1:
            print("userIndex", userIndex)
            if itemNo == '001':
                cursor.execute(sql_climbing_score_011_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_012_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_013_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_014_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_014_update,score)  
            else:
                cursor.execute(sql_climbing_score_015_update,score)   
        elif userIndex == 2:
            print("userIndex", userIndex)
            if itemNo == '001':
                cursor.execute(sql_climbing_score_021_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_022_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_023_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_024_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_024_update,score)  
            else:
                cursor.execute(sql_climbing_score_025_update,score)    
        elif userIndex == 3:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_031_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_032_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_033_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_034_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_034_update,score)  
            else:
                cursor.execute(sql_climbing_score_035_update,score)    
        elif userIndex == 4:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_041_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_042_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_043_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_044_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_044_update,score)  
            else:
                cursor.execute(sql_climbing_score_045_update,score)    
        elif userIndex == 5:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_051_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_052_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_053_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_054_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_054_update,score)  
            else:
                cursor.execute(sql_climbing_score_055_update,score)    
        elif userIndex == 6:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_061_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_062_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_063_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_064_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_064_update,score)  
            else:
                cursor.execute(sql_climbing_score_065_update,score)    
        elif userIndex == 7:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_071_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_072_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_073_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_074_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_074_update,score)  
            else:
                cursor.execute(sql_climbing_score_075_update,score)    
        elif userIndex == 8:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_081_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_082_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_083_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_084_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_084_update,score)  
            else:
                cursor.execute(sql_climbing_score_085_update,score)   
        elif userIndex == 9:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_091_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_092_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_093_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_094_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_094_update,score)  
            else:
                cursor.execute(sql_climbing_score_095_update,score)    
        elif userIndex == 10:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_101_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_102_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_103_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_104_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_104_update,score)  
            else:
                cursor.execute(sql_climbing_score_105_update,score)                                                                                    
        elif userIndex == 11:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_111_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_112_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_113_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_114_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_114_update,score)  
            else:
                cursor.execute(sql_climbing_score_115_update,score)   
        elif userIndex == 12:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_121_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_122_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_123_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_124_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_124_update,score)  
            else:
                cursor.execute(sql_climbing_score_125_update,score)    
        elif userIndex == 13:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_131_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_132_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_133_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_134_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_134_update,score)  
            else:
                cursor.execute(sql_climbing_score_135_update,score)    
        elif userIndex == 14:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_141_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_142_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_143_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_144_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_144_update,score)  
            else:
                cursor.execute(sql_climbing_score_145_update,score)    
        elif userIndex == 15:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_151_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_152_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_153_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_154_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_154_update,score)  
            else:
                cursor.execute(sql_climbing_score_155_update,score)    
        elif userIndex == 16:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_161_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_162_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_163_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_164_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_164_update,score)  
            else:
                cursor.execute(sql_climbing_score_165_update,score)    
        elif userIndex == 17:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_171_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_172_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_173_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_174_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_174_update,score)  
            else:
                cursor.execute(sql_climbing_score_175_update,score)    
        elif userIndex == 18:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_181_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_182_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_183_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_184_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_184_update,score)  
            else:
                cursor.execute(sql_climbing_score_185_update,score)   
        elif userIndex == 19:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_191_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_192_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_193_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_194_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_194_update,score)  
            else:
                cursor.execute(sql_climbing_score_195_update,score)    
        else:
            if itemNo == '001':
                cursor.execute(sql_climbing_score_201_update,score) 
            elif itemNo == '002':  
                cursor.execute(sql_climbing_score_202_update,score)  
            elif itemNo == '003':
                cursor.execute(sql_climbing_score_203_update,score)  
            elif itemNo == '004':
                cursor.execute(sql_climbing_score_204_update,score)  
            elif itemNo == '005':
                cursor.execute(sql_climbing_score_204_update,score)  
            else:
                cursor.execute(sql_climbing_score_205_update,score)         
        board_db.commit()
            

 


#본 쓰레드
def readThread(ser):
    global line
    global exitThread
    global rxcnt
    cnt = 0
    rxcnt = 0


    # 쓰레드 종료될때까지 계속 돌림
    while not exitThread:
        #데이터가 있있다면
        
        for c in ser.read():
            #line 변수에 차곡차곡 추가하여 넣는다.
            rxcnt +=1
            if c==255:
                print(rxcnt, c)
                continue

            if c>=200:
                print(rxcnt, c)
                continue
            else:
                line.append(chr(c))

            if c == 84:         #'T'
                print(c)
                cnt = 0
            cnt = cnt + 1

            #print(cnt)
            if c == 69 and cnt == 20: #라인의 끝을 만나면.. 'E'

                if len(line) == 20:
                    #데이터 처리 함수로 호출
                    parsing_data(line)
                else:
                    print("ng str:", line)
                    print("ng len :",  len(line))
                    parsing_data(line[-20:])

                #line 변수 초기화
                rxcnt = 0
                del line[:]   



if __name__ == "__main__" :
        #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)

    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)

    #시리얼 읽을 쓰레드 생성
    thread = threading.Thread(target=readThread, args=(ser,))
    #시작!
    thread.start()

    

    try:
        while True:
            button_state = GPIO.input(23)  #버튼 상태 확인
            if button_state == False:      #눌러진상태면

                print('Button Pressed...')   
                entryCnt = 0
                dicTime.clear()
                cursor.execute(sql_climbing_init01) 
                cursor.execute(sql_climbing_init02)
                cursor.execute(sql_climbing_init03)
                cursor.execute(sql_climbing_init04)
                cursor.execute(sql_climbing_init05)
                cursor.execute(sql_climbing_init06)
                cursor.execute(sql_climbing_init07)
                cursor.execute(sql_climbing_init08)
                cursor.execute(sql_climbing_init09)
                cursor.execute(sql_climbing_init10)
                cursor.execute(sql_climbing_init11)
                cursor.execute(sql_climbing_init12)
                cursor.execute(sql_climbing_init13)
                cursor.execute(sql_climbing_init14)
                cursor.execute(sql_climbing_init15)
                cursor.execute(sql_climbing_init16)
                cursor.execute(sql_climbing_init17)
                cursor.execute(sql_climbing_init18)
                cursor.execute(sql_climbing_init19)
                cursor.execute(sql_climbing_init20)
                board_db.commit()

                
                time.sleep(0.5)
    except KeyboardInterrupt:       #ctrl-c 누를시
        GPIO.cleanup()