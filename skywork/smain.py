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
sql_sw_total_s_update = "update sw_score_total set log_time_f = %s, log_score = %s, log_sex = %s, log_phone = %s where log_time_s = %s" 
sql_sw_score_update = "update sw_score set log_name = %s, log_score = %s" 


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

    if startorfinish == '1': # '1' 
        print('start')
        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        user_name = df.iloc[0,0]
        #print(user_name)

        score = 0
        cursor.execute(sql_sw_score_update,(user_name, score)) 
        board_db.commit()

        dicTime[bandId] = ct
        print(ct)
        cursor.execute(sql_sw_total_s_insert,(user_name, ct)) 
        board_db.commit()
        dicTime[bandId]=ct
        print(dicTime)

    elif startorfinish == '9': # '9' 
        print('finish')
        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        user_name = df.iloc[0,0]
        user_phone = df.iloc[0,1]
        sex = df.iloc[0,3]
        #print(user_name)

        print(dicTime)
        if dicTime.get(bandId):
            print("has key")
        else:
            return
        
        print(ct)
        finish_time = datetime.datetime.strptime(ct,'%Y-%m-%d %H:%M:%S')
        start_time = datetime.datetime.strptime(dicTime[bandId],'%Y-%m-%d %H:%M:%S')
        score = finish_time - start_time
        print(score)
        print(finish_time, start_time)
        cursor.execute(sql_sw_total_s_update,(ct, score, dicTime[bandId]), sex, user_phone) 
        board_db.commit()
 
        cursor.execute(sql_sw_score_update,(user_name, score)) 
        board_db.commit()
        del dicTime[bandId]

 

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



