#If Priority was changed from High, than update custom field with it's value
import json
from jira import JIRA

jira = JIRA(basic_auth=('username', 'pass'), options={'server': 'https://jira.url', 'verify': False})

issues = jira.search_issues('jql', maxResults=100, expand='changelog') #insert your jql
for issue in issues:
    for history in issue.changelog.histories:
        for item in history.items:
            if item.field == 'priority': #issue field
                if item.fromString == "High": #value changed from
                    print (issue.key)
                    issue.update(notify=False, fields={'customfield_14704': {'value':'High'}})# customfieldid and it's value
