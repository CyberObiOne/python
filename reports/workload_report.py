import requests
from requests.auth import HTTPBasicAuth
import json
from jira import JIRA
import csv
jira = JIRA(basic_auth=("email", "API Token"), options={'server': 'Jira_URL', 'verify': True})  # Jira Cloud: a username/token tuple
for issue in jira.search_issues('project = MAG AND sprint in (7345) ', maxResults=400):
    issues = jira.issue(issue.key)
    if issues.fields.worklog.worklogs !=0:
        data_comment = []
        data_empty_comment = []
        for worklog in issues.fields.worklog.worklogs:
            if hasattr(worklog, 'comment'):
                #print(issue.key)
                data_comment.append([issue.key, issue.fields.summary, worklog.author.displayName,  worklog.timeSpent ,worklog.comment.replace("\n", "").replace("\t", "").replace("\r", "")])

            else:
                #print('No comment ' + issue.key)
                data_empty_comment.append([issue.key, issue.fields.summary, worklog.author.displayName,  worklog.timeSpent] )
            print (data_comment,data_empty_comment)
        with open('report.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            header = ['key', 'summary', 'author', 'timeSpent', 'comment']
            writer.writerow(header)
            writer.writerows(data_comment)
            writer.writerows(data_empty_comment)
