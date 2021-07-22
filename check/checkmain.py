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
sql_findName  = "select user_name, user_phone, sex from user_band where bandId = %s"
sql_sw_total_s_insert = "insert into sw_score_total (log_name, log_time_s) VALUES (%s, %s)" 
sql_sw_total_s_update = "update sw_score_total set log_time_f = %s, log_score = %s where log_time_s = %s" 
sql_sw_score_update = "update sw_score set log_name = %s, log_score = %s" 

sql_sw_check_update = "update sw_check set c_score = %s, c_name = %s, c_runtime = %s" 
sql_sw_check_update_r = "update sw_check set n01_n = %s, n01_s = %s, n02_n = %s, n02_s = %s, n03_n = %s, n03_s = %s, n04_n = %s, n04_s = %s, n05_n = %s, n05_s = %s" 
sql_sw_check_update_mtop = "update sw_check set m01_n = %s, m01_s = %s, m02_n = %s, m02_s = %s, m03_n = %s, m03_s = %s, m04_n = %s, m04_s = %s, m05_n = %s, m05_s = %s" 
sql_climbing_check_update = "update climbing_check set i1_cs = %s, i2_cs = %s, i3_cs = %s, i4_cs = %s, i5_cs = %s" 

sql_sw_check_get_phone = "select * from user_band where bandId = %s" 
sql_sw_check_get_score = "select log_score from sw_score_total where log_name = %s and log_phone=%s order by log_time_f DESC limit 1" 
sql_climbing_check_get_score = "select log_item1_time, log_item2_time, log_item3_time, log_item4_time, log_item5_time from climbing_score_total where log_name = %s and log_phone=%s order by log_time DESC limit 1" 
sql_sp_check_get_score = "select tag_num, score, labtime from sp_score_rank where user_name = %s and user_phone=%s order by log_time DESC limit 1" 
sql_sp_check_get_score_r = "select user_name, tag_num, labtime, score from sp_score_rank order by log_time DESC limit 5" 
sql_sw_check_get_score_top = "select log_name, log_score from sw_score_total where log_sex= %s order by log_score ASC limit 5" 
sql_sw_check_get_score_r = "select log_name, log_score from sw_score_total order by log_score DESC limit 5" 

sql_sp_check_cupdate = "update sp_check set c_name = %s, c_tag_num = %s, c_score = %s, c_time = %s, c_runtime = %s" 
sql_sp_check_n1update = "update sp_check set n1_n = %s, n1_tag_num = %s, n1_score = %s, n1_time = %s" 
sql_sp_check_n2update = "update sp_check set n2_n = %s, n2_tag_num = %s, n2_score = %s, n2_time = %s" 
sql_sp_check_n3update = "update sp_check set n3_n = %s, n3_tag_num = %s, n3_score = %s, n3_time = %s" 
sql_sp_check_n4update = "update sp_check set n4_n = %s, n4_tag_num = %s, n4_score = %s, n4_time = %s" 
sql_sp_check_n5update = "update sp_check set n5_n = %s, n5_tag_num = %s, n5_score = %s, n5_time = %s" 

sql_sp_check_m1top_update = "update sp_check set m1_n = %s, m1_s = %s, m2_n = %s, m2_s = %s, m3_n = %s, m3_s = %s, m4_n = %s, m4_s = %s, m5_n = %s, m5_s = %s" 
sql_sp_check_m6top_update = "update sp_check set m6_n = %s, m6_s = %s, m7_n = %s, m7_s = %s, m8_n = %s, m8_s = %s, m9_n = %s, m9_s = %s, m10_n = %s, m10_s = %s" 
sql_sp_check_m11top_update = "update sp_check set m11_n = %s, m11_s = %s, m12_n = %s, m12_s = %s, m13_n = %s, m13_s = %s, m14_n = %s, m14_s = %s, m15_n = %s, m15_s = %s" 

sql_sp_check_w1top_update = "update sp_check set w1_n = %s, w1_s = %s, w2_n = %s, w2_s = %s, w3_n = %s, w3_s = %s, w4_n = %s, w4_s = %s, w5_n = %s, w5_s = %s" 


sql_sp_check_get_score_top = "select user_name, score_sum from sp_score_rank where sex= %s order by score_sum DESC limit 15" 


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
        cursor.execute(sql_findName,bandId) 
        result = cursor.fetchall()
        df = pd.DataFrame(result)
        if df.empty:
            print('DataFrame is empty!')
            return
        user_name = df.iloc[0,0]
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

            cursor.execute(sql_sw_check_get_score,(user_name, user_phone)) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            print(df)
            if df.empty:
                print('DataFrame is empty!')
                return

            df['log_score'] = df['log_score'].astype(str).map(lambda x: x[7:])
            user_score = df.iloc[0,0]
            print(type(user_score))
            print(user_score)

            #sql_sw_check_update = "update sw_check set c_score = %s, c_name = %s, c_runtime = %s" 
            cursor.execute(sql_sw_check_update,(user_score, user_name, c_runtime)) 
            board_db.commit()

            cursor.execute(sql_sw_check_get_score_r) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            df['log_score'] = df['log_score'].astype(str).map(lambda x: x[7:])

            cursor.execute(sql_sw_check_update_r,(df.iloc[0,0], df.iloc[0,1], df.iloc[1,0], df.iloc[1,1], df.iloc[2,0], df.iloc[2,1], df.iloc[3,0], df.iloc[3,1], df.iloc[4,0], df.iloc[4,1]))
            board_db.commit() 

            cursor.execute(sql_sw_check_get_score_top,("1")) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            df['log_score'] = df['log_score'].astype(str).map(lambda x: x[7:])

            cursor.execute(sql_sw_check_update_mtop,(df.iloc[0,0], df.iloc[0,1], df.iloc[1,0], df.iloc[1,1], df.iloc[2,0], df.iloc[2,1], df.iloc[3,0], df.iloc[3,1], df.iloc[4,0], df.iloc[4,1]))
            board_db.commit() 


        elif itemNo == '001':     # climbing
            print("001")
            #sql_climbing_check_get_score
            cursor.execute(sql_climbing_check_get_score,(user_name, user_phone)) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            print(df)
            if df.empty:
                print('DataFrame is empty!')
                return

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

            print("item1_time", item1_time)
            print("item2_time", item2_time)
            print("item3_time", item3_time)
            print("item4_time", item4_time)
            print("item5_time", item5_time)

            cursor.execute(sql_climbing_check_update,(item1_time, item2_time, item3_time, item4_time, item5_time)) 
            board_db.commit()

        elif itemNo == '003':     # speed tap
            print("003")
            #tag_num, score, labtime
            cursor.execute(sql_sp_check_get_score,(user_name, user_phone)) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            print(df)  
            if df.empty:
                print('DataFrame is empty!')
                return 
            df['labtime'] = df['labtime'].astype(str).map(lambda x: x[7:])
            tag_num = df.iloc[0,0]
            score = df.iloc[0,1]    
            labtime = df.iloc[0,2]

            cursor.execute(sql_sp_check_cupdate,(user_name, tag_num, score, labtime, c_runtime)) 
            board_db.commit() 

            #user_name, tag_num, labtime, score
            cursor.execute(sql_sp_check_get_score_r) 
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            #print(df)  
            print("tag_num", df.iloc[0,1])
            print("labtime", df.iloc[0,2])
            print("score", df.iloc[0,3])
            df['labtime'] = df['labtime'].astype(str).map(lambda x: x[7:])


            cursor.execute(sql_sp_check_n1update,(df.iloc[0,0], df.iloc[0,1], df.iloc[0,3], str(df.iloc[0,2]))) 
            cursor.execute(sql_sp_check_n2update,(df.iloc[1,0], df.iloc[1,1], df.iloc[1,3], str(df.iloc[1,2]))) 
            cursor.execute(sql_sp_check_n3update,(df.iloc[2,0], df.iloc[2,1], df.iloc[2,3], str(df.iloc[2,2]))) 
            cursor.execute(sql_sp_check_n4update,(df.iloc[3,0], df.iloc[3,1], df.iloc[3,3], str(df.iloc[3,2]))) 
            cursor.execute(sql_sp_check_n5update,(df.iloc[4,0], df.iloc[4,1], df.iloc[4,3], str(df.iloc[4,2]))) 
            board_db.commit() 

            
            cursor.execute(sql_sp_check_get_score_top, "1") 
            result = cursor.fetchall()
            df = pd.DataFrame(result)

            cursor.execute(sql_sp_check_m1top_update,(df.iloc[0,0], df.iloc[0,1], df.iloc[1,0], df.iloc[1,1], df.iloc[2,0], df.iloc[2,1], df.iloc[3,0], df.iloc[3,1], df.iloc[4,0], df.iloc[4,1]))
            cursor.execute(sql_sp_check_m6top_update,(df.iloc[5,0], df.iloc[5,1], df.iloc[6,0], df.iloc[6,1], df.iloc[7,0], df.iloc[7,1], df.iloc[8,0], df.iloc[8,1], df.iloc[9,0], df.iloc[9,1]))
            #cursor.execute(sql_sp_check_m11top_update,(df.iloc[10,0], df.iloc[10,1], df.iloc[11,0], df.iloc[11,1], df.iloc[12,0], df.iloc[12,1], df.iloc[13,0], df.iloc[13,1], df.iloc[14,0], df.iloc[14,1]))
            
            board_db.commit() 

            
            cursor.execute(sql_sp_check_get_score_top, "2") 
            result = cursor.fetchall()
            df = pd.DataFrame(result)

            cursor.execute(sql_sp_check_w1top_update,(df.iloc[0,0], df.iloc[0,1], df.iloc[1,0], df.iloc[1,1], df.iloc[2,0], df.iloc[2,1], df.iloc[3,0], df.iloc[3,1], df.iloc[4,0], df.iloc[4,1]))
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



