import pymysql

board_db = pymysql.connect(
    user='root', 
    passwd='root1234', 
    host='ec2-13-125-221-229.ap-northeast-2.compute.amazonaws.com',
    db='board_db', 
    charset='utf8'
)

cursor = board_db.cursor(pymysql.cursors.DictCursor)
sql = "select * from score;"
sql_insert = "insert into score (idx, id, timeLog, timeValue, tagName) VALUES (%s, %s)" 
#cursor.execute(sql)

#res = cursor.fetchall() 
#for data in res: 
#        print(data) 

cursor.execute(sql_insert,("developer_lim@limsee.com", "AI")) 


board_db.commit()
board_db.close()




