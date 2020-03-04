import psycopg2
import datetime
import os
import json
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
project_folder = os.path.expanduser('/home/project_archive') #change as necessary
load_dotenv(os.path.join(project_folder, '.env'))
def confluence_spaces():
        try:
                connection = psycopg2.connect(user = os.environ.get("CONFLUENCE_DATABASE_LOGIN"),
                                  password = os.environ.get("CONFLUENCE_DATABASE_PASSWORD"),
                                  host = os.environ.get("HOST"),
                                  port = "5432",
                                  database = os.environ.get("CONFLUENCE_DATABASE_NAME"))
                cursor = connection.cursor()
                cursor.execute("""select json_agg(hash::jsonb || projects::jsonb) from
                                  (SELECT s.SPACEKEY, s.SPACENAME,
                                  jsonb_build_object( 'usernames',json_agg(c.user_name)) as hash
                                  FROM SPACES s
                                  JOIN SPACEPERMISSIONS p ON s.SPACEID = p.SPACEID
                                  JOIN user_mapping u ON p.PERMUSERNAME = u.user_key
                                  JOIN cwd_user c ON u.username = c.user_name
                                  WHERE p.PERMTYPE = 'SETSPACEPERMISSIONS' and s.spacestatus != 'ARCHIVED' and c.active ='T'
                                  group by s.spacekey,s.SPACENAME
                                  order by s.spacekey) tbl1
                                  join
                                  (select  SPACEKEY,SPACENAME,jsonb_build_object( 'spacekey',SPACEKEY,'spacename',SPACENAME) as projects from (
                                  select  s.SPACEKEY, s.SPACENAME,MAX(cs.lastmoddate) as lastmoddate
                                  FROM SPACES s
                                  JOIN content cs on cs.spaceid = s.spaceid
                                  where s.spacestatus != 'ARCHIVED'
                                  group by s.spacekey,s.SPACENAME
                                  order by s.spacekey ) a
                                  where  lastmoddate < now() - INTERVAL '180 DAY'
                                  group by a.spacekey,a.spacename) tbl2
                                  on tbl1.SPACEKEY = tbl2.SPACEKEY
                                  and tbl1.SPACENAME = tbl2.SPACENAME;""")

                record = cursor.fetchall()
                return eval(json.dumps(record))
        except (Exception, psycopg2.Error) as error :
                print ("Error while connecting to PostgreSQL", error)
        finally:
        #closing database connection.
                if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
