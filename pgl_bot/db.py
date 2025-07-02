import psycopg2
import os

def get_connection():
    return psycopg2.connect(
        dbname="tg_base",
        user="postgres",
        password="MatvaFd09",
        host="localhost",
        port="5432"
    )
