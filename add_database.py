'''
 this script will load tables pulled from 
 pull_petfinder.py into a pSQL database
 
'''

import sqlalchemy
import pandas as pd
import csv
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
#import config #save sql information to file 


def main():
    username = 'kamrine'
    host = 'localhost'
    dbname = 'kitty_db'
#    engine = create_engine('postgres://%(user)s@%(host)s/%(dbname)s' % config.database) # connect to server #for when you have your config file set
    engine = create_engine('postgres://%s@%s/%s' %(username,host,dbname))
    
    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))

    name_data = pd.read_csv('names.txt',
                            names=['id','name','picture'])
#description_data = pd.DataFrame.from_csv("descriptions.txt")
    contact_info = pd.read_csv('website.txt',
                               names=['id','city','email','phone','shelterID','zip'])
    name_data.to_sql('name_data_table', 
                     engine, 
                     if_exists='replace')
    contact_info.to_sql('contact_info_data_table',
                        engine,if_exists='replace')
    
if __name__ == "__main__":
    main()