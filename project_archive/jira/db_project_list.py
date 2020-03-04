import psycopg2
import datetime
import os
import json
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
project_folder = os.path.expanduser('/home/project_archive/jira')
load_dotenv(os.path.join(project_folder, '.env'))
def project_list():
        try:
                connection = psycopg2.connect(user = os.environ.get("JIRA_DATABASE_LOGIN"),
                                  password = os.environ.get("JIRA_DATABASE_PASSWORD"),
                                  host = os.environ.get("HOST"),
                                  port = "5432",
                                  database = os.environ.get("JIRA_DATABASE_NAME"))
                cursor = connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""Select pname, lead, pkey from (
                                  SELECT DISTINCT p.pkey,p.LEAD,MAX(i.UPDATED) as lastupdate, p.pname
                                  FROM jiraissue i
                                  INNER JOIN project p
                                  ON p.ID = i.PROJECT
                                  where p.pname not like '[Archived]%'
                                  GROUP BY p.pkey,p.LEAD,p.pname
                                  ORDER BY MAX(i.UPDATED) ASC) a
                                  where lastupdate < now() - INTERVAL '90 DAY';""")

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
