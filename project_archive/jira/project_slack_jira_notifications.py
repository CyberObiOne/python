#the same structure as for empty_projects, difference in SQL output and slack message.
import json
import requests
import os
import db_empty_project_list
from jira import JIRA
from dotenv import load_dotenv
project_folder = os.path.expanduser('/home/project_archive/jira') #change as necessary
load_dotenv(os.path.join(project_folder, '.env'))

inactive_projects  = db_empty_project_list.empty_projects()
print inactive_projects
HEADERS = {
        'project': {'key': 'TOOL'},
        'issuetype': {'name': 'issuetype'},
        'reporter': {'name': 'username'},
        }
jira = JIRA(basic_auth=(os.environ.get("JIRA_LOGIN"), os.environ.get("JIRA_PASS")), options={'server': os.environ.get("JIRA_SERVER")})
if   inactive_projects: #json is not empty

        scope_of_projects = ''
        for project in inactive_projects:
                summary =  project['pname'] + ' '  + 'Project Archive'
                search_string = "summary ~\"{}\" and statuscategory!=done ".format(summary)
                issues = jira.search_issues(search_string, maxResults=25)
                if issues: #if issue already exist on jira server - count comments, if more than 3 - archive, else - add one more. 
                           # else - create issue
                        comment_text = "Please, provide an update [~{}]".format (project['lead'])
                        print comment_text
                        #jira.add_comment(issues[0].key, comment_text)
                        comments = jira.comments(issues[0])
                        count = 0
                        for comment in comments:
                                if comment_text == comment.body:
                                        count =count + 1
                                        print (count)
                        if count < 3:
                                jira.add_comment(issues[0].key, comment_text)

                        else:
                                project_archive = {"name": "[Archived] - {} ".format(project['pname']),"permissionScheme": 10202}
                                headers={'Content-type':'application/json', 'Accept':'application/json'}
                                jira_url = 'https://jira.com/jira'
                                project_url =jira_url + 'rest/api/2/project/' + project['pkey']
                                auth = (os.environ.get("LOGIN"), os.environ.get("JIRA_PASS"))
                                r = requests.request("PUT",project_url, data=json.dumps(project_archive),auth=auth,headers=headers)
                                #jira.add_comment(issues[0].key, "Issue was closed")
                                transitions = jira.transitions(issues[0].key)
                                #print transitions
                                for t in transitions:
                                        print t
                                        if t['name'] == 'Close Issue':
                                                jira.add_comment(issues[0].key, "Due to the fact that no comments were received, the project will be archived and the task will be closed.")
                                                jira.transition_issue (issues[0].key,'2', fields={'resolution':{'id': '1'}})

                else:
                        issue_dict = HEADERS
                        issue_dict['summary'] = project['pname'] + ' '  + 'Project Archive'
                        issue_dict['description'] = 'Please, approve project archive' + ' '  + project['pname'] + ' '  + 'https://jira.com/jira/browse/' + project['pkey']
                        issue_dict['assignee'] = {'name': project['lead']}
                        new_issue = jira.create_issue(fields=issue_dict)
                        print (new_issue.key)

                        scope_of_projects += project['pname'] + ' - ' +  'https://jira.com/jira/browse/'  + new_issue.key  + '\n' #create slack payload
                        print scope_of_projects
        if scope_of_projects:
                payload = {'text': "Jira Project(s) without activity for 90 days: \n {} ".format(scope_of_projects) }
                r = requests.post("https://hooks.slack.com/services/slack/incoming/webhook", data=json.dumps(payload)) # send notifications to Slack
