import mysql.connector
import os
from dotenv import load_dotenv
load_dotenv()


db = mysql.connector.connect(
    host=os.environ.get('HOST_NAME'),
    user= os.environ.get('DB_USER'),
    password= os.environ.get('DB_PASSWORD'),
    database= os.environ.get('DB_NAME')

)