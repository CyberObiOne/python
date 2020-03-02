import urllib
import json
import requests
import os
import db_orphaned_spaces
from jira import JIRA
from dotenv import load_dotenv
project_folder = os.path.expanduser('/home/project_archive') #change as necessary
load_dotenv(os.path.join(project_folder, '.env'))

orphaned_spaces = db_orphaned_spaces.confluence_spaces() #get json from SQL query
#print inactive_projects
HEADERS = {
        'project': {'key': 'TOOL'},
        'issuetype': {'name': 'issuetype'},
        'reporter': {'name': 'user_name'},
        'assignee': {'name': 'user_name'}
        }
jira = JIRA(basic_auth=(os.environ.get("JIRA_LOGIN"), os.environ.get("JIRA_PASS")), options={'server': os.environ.get("JIRA_SERVER")})
if   orphaned_spaces: #json is not empty
        scope_of_projects = ''
        for spaces in inactive_projects:
# I have two extra loops, because I didn't find a way to convert jsom from sql in right format
                for i in spaces:
                        for a in i:
                                summary =  a['spacename'] + ' '  + 'Space Archive'
                                search_string = "summary ~\"{}\" and statuscategory!=done ".format(summary)
                                issues = jira.search_issues(search_string, maxResults=25)
                                if issues: #if issue already exist on jira server - add a comment instead of creation.
                                        jira.add_comment(issues[0].key, "Please, provide an update [~{}]".format (HEADERS['assignee']['name']))
                                else:

                                        url_spacename = urllib.quote_plus( a['spacename'])
                                        url = 'https://confluence_url.com/confluence/display' + '/' + a['spacekey'] +'/' + url_spacename
                                        issue_dict = HEADERS
                                        issue_dict['summary'] = a['spacename'] + ' '  + 'Space Archive'
                                        issue_dict['description'] = 'Please, approve space archive' + ' '  + a['spacename'] + ' '  + url
                                        new_issue = jira.create_issue(fields=issue_dict) # create new jira issue with predifined variables
                                        scope_of_projects += a['spacename'] + ' - ' +  'https://jira_url.com/jira/browse/'  + new_issue.key  + '\n' #generate payload to Slack
                                        print (new_issue.key)
        if scope_of_projects: #if strin is not empty - send notification to slack. 
                payload = {'text': "Orphaned Confleunce Space(s) without activity for 180 days: \n {} ".format(scope_of_projects) }
                r = requests.post("https://hooks.slack.com/services/channel/incomming/webhook_here", data=json.dumps(payload))
