#!/usr/local/bin/python
# Connect to MariaDB Platform
import mysql.connector #mariadb

try:
	#連線DB
	conn = mysql.connector.connect(
		user="root",
		password="",
		host="localhost",
		port=3306,
		database="auction"
	)
	#建立執行SQL指令用之cursor, 設定傳回dictionary型態的查詢結果 [{'欄位名':值, ...}, ...]
	cursor=conn.cursor(dictionary=True)
except mysql.connector.Error as e: # mariadb.Error as e:
	print(e)
	print("Error connecting to DB")
	exit(1)
	
def getList():
	sql="select * from users where 1"
	#param=('值',...)
	cursor.execute(sql)
	return cursor.fetchall()

def getAllItems():
    sql='''
    SELECT I.*, 
       COALESCE(MAX(B.bid_price), 0) AS max_price,
       (SELECT COUNT(*) FROM bids WHERE item_id = I.item_id) AS bid_count
    FROM items I 
    LEFT JOIN bids B ON I.item_id = B.item_id
    GROUP BY I.item_id;
    '''
    cursor.execute(sql)
    return cursor.fetchall()

#login to check account and password
def getLoginInfo(id,pwd):
	sql="select * from users where user_account=%s and user_password=%s"
	param=(id,pwd,)
	cursor.execute(sql,param)
	user = cursor.fetchone()
	if user:
		return user
	return None

#get individual item and render to it's page
def getItem(id):
    sql='''
    SELECT I.*, U.user_name, 
       (SELECT COALESCE(MAX(B.bid_price)) FROM bids B WHERE B.item_id = I.item_id) AS max_price
	FROM items I 
	JOIN users U ON I.user_id = U.user_id 
	WHERE I.item_id = %s;
    '''
    param = (id,)
    cursor.execute(sql,param)
    item = cursor.fetchone()
    if item:
        return item
    return None


#users to bid
def addBid(item_id,user_id,price,time):
	sql="INSERT INTO bids (item_id, user_id, bid_price, bid_time) VALUES (%s,%s,%s,%s)"
	param = (item_id,user_id,price,time,)
	cursor.execute(sql,param)
	conn.commit()
	return

#for list bid history
def getBidInfo(item_id):
    sql="SELECT B.*, U.user_name FROM bids B JOIN users U ON B.user_id = U.user_id where B.item_id = %s ORDER BY B.bid_time DESC"
    param = (item_id,)
    cursor.execute(sql,param)
    bid_info = cursor.fetchall()
    return bid_info


#add item to database from specific user
def addItemDB(item_name, start_price, dynasty, material, description, time, user_id):
    sql='''INSERT INTO items (item_name,start_price, dynasty, material, description,start_time,user_id) VALUES (%s,%s,%s,%s,%s,%s,%s);'''
    param = (item_name, start_price, dynasty, material, description, time, user_id,)
    cursor.execute(sql,param)
    conn.commit()
    item_id = cursor.lastrowid
    return item_id

#get current user's product
def getMyProduct(user_id):
    sql='''
    SELECT I.*, 
       COALESCE(MAX(B.bid_price), 0) AS max_price,
       (SELECT COUNT(*) FROM bids WHERE item_id = I.item_id) AS bid_count
    FROM items I 
    LEFT JOIN bids B ON I.item_id = B.item_id
    WHERE I.user_id = %s
    GROUP BY I.item_id;
    '''
    param = (user_id,)
    cursor.execute(sql,param)
    products = cursor.fetchall()
    return products

#get current user's bid product
def getMyBid(user_id):
    sql='''
    SELECT I.*, B.bid_price, B.user_id,(SELECT COUNT(*) FROM bids WHERE item_id = I.item_id) AS bid_count
	FROM Items I
	JOIN (
    	SELECT item_id, MAX(bid_price) AS bid_price, user_id
    	FROM Bids
    	WHERE user_id = %s
    	GROUP BY item_id
	) B ON I.item_id = B.item_id;
    '''
    param = (user_id,)
    cursor.execute(sql,param)
    products = cursor.fetchall()
    return products


#to check the highest price
def checkPrice(item_id):
    sql="SELECT COALESCE(MAX(bid_price),0) as max_price FROM bids WHERE item_id = %s"
    param = (item_id,)
    cursor.execute(sql,param)
    max_price = cursor.fetchone()
    return max_price

#for user to delete items
def deleteBid(item_id):
    sql="DELETE FROM bids WHERE item_id = %s;"
    param = (item_id,)
    cursor.execute(sql,param)
    conn.commit()
    return 

#delete item
def deleteItem(item_id):
    sql="DELETE FROM items WHERE item_id = %s;"
    param = (item_id,)
    cursor.execute(sql,param)
    conn.commit()
    return 

#revise item
def reviseDB(item_name, start_price, dynasty, material, description, time, item_id):
    sql='''
        UPDATE items 
        SET item_name = %s, 
            start_price = %s, 
            dynasty = %s, 
            material = %s, 
            description = %s, 
            start_time = %s 
        WHERE item_id = %s;
    '''
    param = (item_name, start_price, dynasty, material, description, time, item_id,)
    cursor.execute(sql,param)
    conn.commit()
    return


#register
def addUser(user_name,account,password):
    sql = "INSERT INTO users (user_name,user_account,user_password) VALUES (%s,%s,%s);"
    param = (user_name,account,password,)
    cursor.execute(sql,param)
    conn.commit()
    return


#search
def searchFromDB(search_input):
    sql = "SELECT * FROM items WHERE item_name LIKE %s;"
    param = (f"%{search_input}%",)
    cursor.execute(sql,param)
    items = cursor.fetchall()
    return items