#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import serial
import time
import signal
import threading

import pymysql
import datetime
import pandas as pd
import numpy
import unicodedata

import imp

imp.reload(sys)



line = [] #라인 단위로 데이터 가져올 리스트 변수

#port = '/dev/tty.usbserial-14440' # 시리얼 포트
port = '/dev/ttyUSB0' # 시리얼 포트
baud = 115200 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수



board_db = pymysql.connect(
    host='wonderdb.c03rvmbon7t9.ap-northeast-2.rds.amazonaws.com',
    user='admin',
    password='admin1234qwer',
    database='one',
    charset='utf8mb4'
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
sql_findName  = "select user_name from user_band where bandId = %s"
sql_sw_total_s_insert = "insert into sw_score_total (log_name, log_time_s) VALUES (%s, %s)" 
sql_sw_total_s_update = "update sw_score_total set log_time_f = %s, log_score = %s where log_time_s = %s" 
sql_sw_score_update = "update sw_score set log_name = %s, log_score = %s" 

sql_sw_check_update = "update sw_check set c_score = %s, c_name = %s, c_runtime = %s" 
sql_climbing_check_update = "update climbing_check set i1_cs = %s, i2_cs = %s, i3_cs = %s, i4_cs = %s, i5_cs = %s" 

sql_sw_check_get_phone = "select * from user_band where bandId = %s" 
sql_sw_check_get_score = "select log_score from sw_score_total where log_name = %s and log_phone=%s order by log_time_f DESC limit 1" 
sql_climbing_check_get_score = "select log_item1_time, log_item2_time, log_item3_time, log_item4_time, log_item5_time from climbing_score_total where log_name = %s and log_phone=%s order by log_time DESC limit 1" 
sql_sp_check_get_score = "select c_name, c_tag_num, c_score, c_time, c_runtime from sp_score_total where log_name = %s and log_phone=%s order by log_time DESC limit 1" 


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

    if startorfinish == '8': # '1' 
        print('check')
        #cursor.execute(sql_findName,bandId) 
        #result = cursor.fetchall()
        #df = pd.DataFrame(result)
        #user_name = df.iloc[0,0]
        #print(user_name)

        cursor.execute(sql_sw_check_get_phone,(bandId)) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        #print(df)
        user_name = df.iloc[0,1]
        user_phone = df.iloc[0,3]
        user_loginTime = df.iloc[0,4]
        print(type(user_loginTime))
        print(user_phone, user_loginTime)

        c_time = datetime.datetime.strptime(ct,'%Y-%m-%d %H:%M:%S')
        c_logtime = datetime.datetime.strptime(str(user_loginTime),'%Y-%m-%d %H:%M:%S')
        c_runtime = c_time - c_logtime

        if itemNo == '002':     # skywork
            print("002")

            cursor.execute(sql_sw_check_get_score,(bandId, user_phone)) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            print(df)
            df['log_score'] = df['log_score'].astype(str).map(lambda x: x[7:])
            user_score = df.iloc[0,0]
            print(type(user_score))
            print(user_score)

            #sql_sw_check_update = "update sw_check set c_score = %s, c_name = %s, c_runtime = %s" 
            cursor.execute(sql_sw_check_update,(user_score, user_name, c_runtime)) 
            board_db.commit()


        elif itemNo == '001':     # climbing
            print("001")
            #sql_climbing_check_get_score
            cursor.execute(sql_climbing_check_get_score,(bandId, user_phone)) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            print(df)
            df['log_item1_time'] = df['log_item1_time'].astype(str).map(lambda x: x[7:])
            df['log_item2_time'] = df['log_item2_time'].astype(str).map(lambda x: x[7:])
            df['log_item3_time'] = df['log_item3_time'].astype(str).map(lambda x: x[7:])
            df['log_item4_time'] = df['log_item4_time'].astype(str).map(lambda x: x[7:])
            df['log_item5_time'] = df['log_item5_time'].astype(str).map(lambda x: x[7:])

            item1_time = df.iloc[0,0]
            item2_time = df.iloc[0,1]
            item3_time = df.iloc[0,2]
            item4_time = df.iloc[0,3]
            item5_time = df.iloc[0,4]

            cursor.execute(sql_climbing_check_update,(item1_time, item2_time, item3_time, item4_time, item5_time)) 
            board_db.commit()

        elif itemNo == '003':     # speed tap
            print("003")



 

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



