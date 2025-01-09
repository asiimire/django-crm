import mysql.connector

dataBase = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    passwd = '7521patz',

)

# prepare a cursor object
cursorObject = dataBase.cursor()

# create the database
cursorObject.execute("CREATE DATABASE yoursms")

print("All done!")