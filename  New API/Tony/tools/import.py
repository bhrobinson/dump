import json
import urllib.request
import requests
import subprocess
from datetime import datetime
import base64

def jira_story(confi):
    field = {}
    field['labels'] = ['Axway']
    field['summary'] = (confi['f3'].replace('Change to an existing API.', 'CHANGE ')
                        .replace('This is a new API.', 'New')
                        + ' ' + confi['CallType'].replace('External call.', 'Ext-to-Int')
                        .replace('Internal to external call.', 'Int-to-Ext')
                        .replace('Internal call.', 'Int-to-Int')
                        + ': ' + confi['projectName'])
    field['description'] = confi['description']
    field['components'] = [{'id': '17133'}] # Components Axway
    field['reporter'] = {'key': confi['leadName'], 'name': confi['leadName']}
    field['project'] = {'id': '11750'} # Axway Project
    field['issuetype'] = {'id': '14'} # issue type Story
    field['customfield_13603'] = {'value': 'Unknown'} # Portfolio
    field['customfield_13605'] = [{'value': 'All Markets-Enterprise'}] # Market
    field['customfield_13604'] = [{'value': 'Commercial'}] # Line of Business
    field['customfield_13800'] = {'id': '15150'} # Business Capabilities
    field['customfield_10803'] = 'AXWY-712'
    field['priority'] = {'id': '10'} # Trivial
    jira = {'fields': field}
    return json.dumps(jira, indent=4)

def submit_jira_ticket(jira_url,data):
    print(data)
    # Set the authentication credentials
    credentials = ('USERNAME', 'PWD')
    
    # Encode the credentials in base64
    encoded_credentials = base64.b64encode(f"{credentials[0]}:{credentials[1]}".encode()).decode('utf-8')
    
    # Define the request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Basic ' + encoded_credentials
    }
    # print(json.dumps(data))
    # print(headers)
    # Make the request
    response = requests.post(jira_url, auth=credentials, headers=headers, data=json.dumps(data))
    
    # Print the response content
    print(response.content)
    
    # Return the response JSON
    return response.json()


def jira_initial_comment(confi):
    # Convert Time from epoch to usable.
    dev_date = datetime.fromtimestamp(int(str(confi['developmentDate'])[:10])).strftime('%m-%d-%Y')
    test_date = datetime.fromtimestamp(int(str(confi['f17'])[:10])).strftime('%m-%d-%Y')
    prod_date = datetime.fromtimestamp(int(str(confi['f18'])[:10])).strftime('%m-%d-%Y')
    RESTCallTypesArray = json.loads(confi['RESTCallTypes'])
    RESTCallTypes = ""
    print(RESTCallTypes)
    for REST in RESTCallTypesArray:
        print(REST)
        RESTCallTypes = RESTCallTypes + REST['label'] + "\n"
    leadName = subprocess.check_output(['ldapsearch', '-LLL', '-B', '-o', 'ldif-wrap=no', '-b', 'dc=centene,dc=com', '-h', 'ofldc2', 'samaccountname=' + confi['leadName'], 'name']).decode('utf-8').split('\n')[0].split('-')[0].replace('name: ', '')
    secondaryName = subprocess.check_output(['ldapsearch', '-LLL', '-B', '-o', 'ldif-wrap=no', '-b', 'dc=centene,dc=com', '-h', 'ofldc2', 'samaccountname=' + confi['secondaryName'], 'name']).decode('utf-8').split('\n')[0].split('-')[0].replace('name: ', '')
    managerName = subprocess.check_output(['ldapsearch', '-LLL', '-B', '-o', 'ldif-wrap=no', '-b', 'dc=centene,dc=com', '-h', 'ofldc2', 'samaccountname=' + confi['managerName'], 'name']).decode('utf-8').split('\n')[0].split('-')[0].replace('name: ', '')
    supportName = subprocess.check_output(['ldapsearch', '-LLL', '-B', '-o', 'ldif-wrap=no', '-b', 'dc=centene,dc=com', '-h', 'ofldc2', 'samaccountname=' + confi['supportName'], 'name']).decode('utf-8').split('\n')[0].split('-')[0].replace('name: ', '')
    comment = f"""
    *Dates*
    ----------------------------------
    Requested Development Date: {dev_date}
    Requested Test Date:        {test_date}
    Requested Prod Date:        {prod_date}



    *Contacts*
    -----------------------------------
    Project Lead:               {leadName}
    Secondary:                  {secondaryName}
    Manager:                    {managerName}

    Ongoing Support:            *{supportName}*



    *PHI/PII Data*
    -----------------------------------
    Responses contain private data:               *{confi['f19']}*



    *API Methods*
    -----------------------------------
    {RESTCallTypes}



    *Endpoints*
    -----------------------------------
    Requested URI:              *{confi['requestedURI']}*

    Dev Endpoint:               {confi['devEndpoint']}
    Test Endpoint:              {confi['testEndpoint']}
    Production Endpoint:        {confi['prodEndpoint']}



    *Auth Methods*
    ------------------------------------
    Axway:                      {confi['f28']}
    Endpoint:                   {confi['Security']}



    *Testing*
    -------------------------------------
    Test Path:
        {confi['Path']}
    Test Case (CURL statement preferred): 
        {confi['testCaseDev']}
"""
    return comment

def submit_comment(jiraUrl, ticket, comment):
    comment_array = {"body": comment}
    json_comment = json.dumps(comment_array, indent=4)
    # print(json_comment)
    print(jiraUrl + '/' + ticket + '/comment')
    commentticket = submit_jira_ticket(jiraUrl + '/' + ticket + '/comment', auth_header, json_comment)
    return commentticket
    # print(ticket)

# set unassigned info
url = 'https://confluence.centene.com/ajax/confiforms/rest/filter.action?pageId=746324912&f=APIRequest&q=!JIRA:*-*'
#(recordId:106%20AND%20!JIRA:AXWY*)';
jira_url = 'https://jira.centene.com/rest/api/2/issue'
confluence_url = 'https://confluence.centene.com/ajax/confiforms/rest/update.action?pageId=746324912&f=APIRequest'
# provide your username and password here
auth = base64.b64encode(f"USERNAME:PWD".encode("utf-8")).decode("ascii")

# call api
req = urllib.request.Request(url)
req.add_header("Authorization", "Basic " + auth)
response = urllib.request.urlopen(req)
json_str = response.read().decode()
json_data = json.loads(json_str)
if len(json_data['list']['entry']) > 0:
    for record in json_data['list']['entry']:
        jira = jira_story(record['fields'])
        auth_header = "Authorization: Basic " + auth
        jiraticket = submit_jira_ticket(jira_url, jira)
        comment = jira_initial_comment(record['fields'])
        commentcommit = submit_comment(jira_url, jiraticket["id"], comment, auth_header)
        closeconfigurl = confluence_url + '&q=recordId:' + str(record['recordId']) + '&fv=JIRA:' + jiraticket["key"]
        # send the axway number to confiforms
        req2 = urllib.request.Request(closeconfigurl)
        req2.add_header("Authorization", "Basic " + auth)
        response2 = urllib.request.urlopen(req2)
