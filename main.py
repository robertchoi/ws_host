import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic

import serial
import time
import signal
import threading

import pymysql
import datetime


line = [] #라인 단위로 데이터 가져올 리스트 변수

port = '/dev/tty.usbserial-14440' # 시리얼 포트
baud = 9600 # 시리얼 보드레이트(통신속도)

exitThread = False   # 쓰레드 종료용 변수

#UI파일 연결
#단, UI파일은 Python 코드 파일과 같은 디렉토리에 위치해야한다.
form_class = uic.loadUiType("main.ui")[0]


board_db = pymysql.connect(
    user='root', 
    passwd='root1234', 
    host='ec2-13-125-221-229.ap-northeast-2.compute.amazonaws.com',
    db='board_db', 
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

cursor = board_db.cursor(pymysql.cursors.DictCursor)
sql = "select * from score;"
sql_insert = "insert into score (id, timelog, tagvalue, tagname) VALUES (%s, %s, %s, %s)" 


#쓰레드 종료용 시그널 함수
def handler(signum, frame):
     exitThread = True


#데이터 처리할 함수
def parsing_data(data):
    # 리스트 구조로 들어 왔기 때문에
    # 작업하기 편하게 스트링으로 합침
    tmp = ''.join(data)

    print(dicBand.get(tmp[5:]))  
    ct = datetime.datetime.now()
    myWindow.label.setText(dicBand.get(tmp[5:])+ " : " + str(ct))



    cursor.execute(sql_insert,(dicBand.get(tmp[5:]), ct, dicScore.get(tmp[4]), tmp[1:4])) 
    board_db.commit()

    #출력!
    print(tmp)


#본 쓰레드
def readThread(ser):
    global line
    global exitThread

    # 쓰레드 종료될때까지 계속 돌림
    while not exitThread:
        #데이터가 있있다면
        for c in ser.read():
            #line 변수에 차곡차곡 추가하여 넣는다.
            line.append(chr(c))

            if c == 69: #라인의 끝을 만나면..
                #데이터 처리 함수로 호출
                parsing_data(line)

                #line 변수 초기화
                del line[:]   


#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.label.setText("--")

if __name__ == "__main__" :


        #종료 시그널 등록
    signal.signal(signal.SIGINT, handler)

    #시리얼 열기
    ser = serial.Serial(port, baud, timeout=0)

    #시리얼 읽을 쓰레드 생성
    thread = threading.Thread(target=readThread, args=(ser,))

    #시작!
    thread.start()


    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 


    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

