import json
import requests
import os
import db_bitbucket_licenses
from dotenv import load_dotenv
import crowd
from crowd import CrowdServer
project_folder = os.path.expanduser('/home/bitbucket_cleanup_licenses')
load_dotenv(os.path.join(project_folder, '.env'))

inactive_users  = db_bitbucket_licenses.bitbucket_licenses()
print inactive_users
app_url = 'http://crowd.com/crowd'
app_user = 'crowd app user, not admin user'
app_pass = 'pass'

cs = crowd.CrowdServer(app_url, app_user, app_pass)
if   inactive_users:

        scope_of_users = ''
        for project in inactive_users:
                for users in project:
                        for inactive in users: #we have two groups per user, that why I exicuted it twice
                                req = cs.remove_user_from_group(username = inactive['user_name'],groupname = inactive['group_name'][0])
                                req = cs.remove_user_from_group(username = inactive['user_name'],groupname = inactive['group_name'][1])
                                if len (inactive_users) == 1:
                                        scope_of_users += inactive['display_name']  + ' was removed from groups' + ' ' + inactive['group_name'][0] + ', ' + inactive['group_name'][1] + '\n'
                                        print scope_of_users
                                else:
                                        scope_of_users += inactive['display_name']  + ' were removed from groups' + ' ' + inactive['group_name'][0] + ', ' + inactive['group_name'][1] + '\n'
        if scope_of_users:
                payload = {'text': "Bitbucket user(s) {} due to inactivity for 60 days \n ".format(scope_of_users) }
                print payload
                r = requests.post("https://hooks.slack.com/services/slack/incoming/webhook", data=json.dumps(payload))
