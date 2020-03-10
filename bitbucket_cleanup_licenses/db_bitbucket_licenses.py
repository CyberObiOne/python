import psycopg2
import datetime
import os
import json
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
project_folder = os.path.expanduser('/home/bitbucket_cleanup_licenses')#change if need
load_dotenv(os.path.join(project_folder, '.env'))
def bitbucket_licenses():
        try:
                connection = psycopg2.connect(user = os.environ.get("BITBUCKET_DATABASE_LOGIN"),
                                  password = os.environ.get("BITBUCKET_DATABASE_PASSWORD"),
                                  host = os.environ.get("HOST"),
                                  port = "5432",
                                  database = os.environ.get("BITBUCKET_DATABASE"))
                cursor = connection.cursor()
                #find inactive users for 60 days
                cursor.execute("""select json_agg (user_name::jsonb || group_name::jsonb || display_name::jsonb) from (
SELECT distinct to_timestamp(CAST(cua.attribute_value as double precision)/1000)
        ,jsonb_build_object( 'group_name',json_agg(cm.parent_name)) as group_name
        ,jsonb_build_object ( 'user_name',cu.user_name) as user_name
        ,jsonb_build_object ( 'display_name',cu.display_name) as display_name
FROM cwd_user_attribute cua
INNER JOIN cwd_user cu ON cua.user_id = cu.id
INNER JOIN cwd_membership cm ON cm.lower_child_name = cu.lower_user_name
WHERE cua.attribute_name = 'lastAuthenticationTimestamp' and cm.parent_name in
(select cg.group_name from cwd_group cg where group_name like 'stash-%'  and is_active ='T')
and cu.is_active ='T' and cm.directory_id = '1146881' and cu.directory_id='1146881'
group by cu.user_name,cua.attribute_value,cu.display_name) a
where to_timestamp < now() - INTERVAL '60 DAY';""")

                record = cursor.fetchall()
                #return record
                return eval(json.dumps(record))
        except (Exception, psycopg2.Error) as error :
                print ("Error while connecting to PostgreSQL", error)
        finally:
        #closing database connection.
                if(connection):
                        cursor.close()
                        connection.close()
                        print("PostgreSQL connection is closed")
