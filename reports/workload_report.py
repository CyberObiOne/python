import requests
from requests.auth import HTTPBasicAuth
import json
from jira import JIRA
import csv
jira = JIRA(basic_auth=("email", "token"), options={'server': 'Jira_URL', 'verify': True})  # Jira Cloud: a username/token tuple
for issue in jira.search_issues('project = Test AND sprint in (1, 2, 3, 4)', maxResults=400):
    issues = jira.issue(issue.key)
    if issues.fields.worklog.worklogs !=0:
        data = []
        for worklog in issues.fields.worklog.worklogs:
            data.append([issue.key, issue.fields.summary,worklog.author.displayName,worklog.comment.replace("\n","").replace("\t","").replace("\r",""),worklog.timeSpent])
            #print (data)
        with open('report.csv', 'a', encoding='UTF8', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            header = ['key', 'summary', 'author', 'comment', 'timeSpent']
            writer.writerow(header)
            writer.writerows(data)
