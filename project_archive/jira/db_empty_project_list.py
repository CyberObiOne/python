import psycopg2
import datetime
import os
import json
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
project_folder = os.path.expanduser('/home/project_archive/jira')
load_dotenv(os.path.join(project_folder, '.env'))
def empty_projects():
        try:
                connection = psycopg2.connect(user = os.environ.get("JIRA_DATABASE_LOGIN"),
                                  password = os.environ.get("JIRA_DATABASE_PASSWORD"),
                                  host = os.environ.get("HOST"),
                                  port = "5432",
                                  database = os.environ.get("JIRA_DATABASE_NAME"))
                cursor = connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("""(select p.pname, p.lead, p.pkey from audit_log al
                                  join project p ON p.id::varchar = al.object_id
                                  WHERE al.SUMMARY = 'Project created' and al.created < now() - INTERVAL '90 DAY' and p.pname not like '[Archived]%' )
                                  EXCEPT
                                 (Select pname, lead, pkey  from
                                 (SELECT DISTINCT p.pkey,p.LEAD,MAX(i.UPDATED) as "Last Updated" ,p.pname
                                  FROM jiraissue i
                                  INNER JOIN project p
                                  ON p.ID = i.PROJECT
                                  where p.pname not like '[Archived]%'
                                  GROUP BY p.pkey,p.LEAD,p.pname
                                  ORDER BY MAX(i.UPDATED) ASC) a);""")

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
