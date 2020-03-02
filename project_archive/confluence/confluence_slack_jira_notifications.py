import urllib
import json
import requests
import os
import db_confluence_spaces
from jira import JIRA
from dotenv import load_dotenv
project_folder = os.path.expanduser('/home/project_archive') #change as necessary
load_dotenv(os.path.join(project_folder, '.env'))

inactive_spaces  = db_confluence_spaces.confluence_spaces()
HEADERS = {
        'project': {'key': 'project_key'},
        'issuetype': {'name': 'issuetype_name'},
        'reporter': {'name': 'username'},
        }
jira = JIRA(basic_auth=(os.environ.get("JIRA_LOGIN"), os.environ.get("JIRA_PASS")), options={'server': os.environ.get("JIRA_SERVER")})
if   inactive_spaces: #json is not empty
        scope_of_spaces = ''
        for spaces in inactive_spaces:
# I have two extra loops, because I didn't find a way to convert jsom from sql in right format
                for i in spaces:
                        for a in i:
                                summary =  a['spacename'] + ' '  + 'Space Archive'
                                search_string = "summary ~\"{}\" and statuscategory!=done ".format(summary)
                                issues = jira.search_issues(search_string, maxResults=25)
                                if issues:
                                        jira.add_comment(issues[0].key, "Please, provide an update [~{}]".format (a['usernames'][0]))  #if issue already exist on jira server - add a comment instead of creation.
                                else:

                                        url_spacename = urllib.quote_plus( a['spacename'])
                                        url = 'https://confluence_url.com/confluence/display' + '/' + a['spacekey'] +'/' + url_spacename  #generate Confluence URL
                                        issue_dict = HEADERS
                                        issue_dict['summary'] = a['spacename'] + ' '  + 'Space Archive'
                                        issue_dict['description'] = 'Please, approve space archive' + ' '  + a['spacename'] + ' '  + url
                                        issue_dict['assignee'] = {'name': a['usernames'][0]}
                                        if len(a['usernames']) == 1: #if admins is more than one, add first to assignee, add other to CC
                                                new_issue = jira.create_issue(fields=issue_dict)
                                                scope_of_spaces += a['spacename'] + ' - ' +  'https://jira_url.com/jira/browse/'  + new_issue.key  + '\n'
                                                print (new_issue.key)
                                        else:
                                                userlist = ["[~" +  item + "]" + ", " for item in a['usernames']]
                                                CC = ''.join(userlist)
                                                issue_dict['description'] = 'Please, approve project archive' + ' '  + a['spacename'] + ' '  + url + '\n' + 'CC:' + CC
                                                new_issue = jira.create_issue(fields=issue_dict)
                                                scope_of_spaces += a['spacename'] + ' - ' +  'https://jira_url.com/jira/browse/'  + new_issue.key  + '\n'
                                                print (new_issue.key)
        if scope_of_spaces: #if string is not empty - send notification to slack. 
                payload = {'text': "Confleunce Space(s) without activity for 180 days: \n {} ".format(scope_of_spaces) }
                r = requests.post("https://hooks.slack.com/services/slack/incoming/webhook", data=json.dumps(payload))
