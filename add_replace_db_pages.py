

import requests
import os, sys
sys.path.insert(1, "/".join(os.path.realpath(__file__).split("/")[0:-2]))
from main import settings_local as authentication
from lxml import etree


qbUsername = authentication.QB_USERNAME
qbPassword = authentication.QB_PASSWORD
qbAppToken = authentication.QB_TOKEN
qbRealmHost = authentication.QB_REALM_HOST
qbHours = authentication.QB_HOURS
qbBaseURL = authentication.QB_BASE_URL
qbApplicationDBID = authentication.QB_APPLICATION_DBID

pyFolderName = sys.argv[1]
pyFileName = sys.argv[2]

class DatabaseClient:
    def __init__(self):
        self.qb_dbid = getattr(self, 'qb_dbid', None) 
        self.field_values = {}
        self.username = qbUsername
        self.password = qbPassword
        self.apptoken = qbAppToken
        self.realmhost = qbRealmHost
        self.hours = qbHours
        self.base_url = qbBaseURL
        self.application_dbid = qbApplicationDBID
        self.session = requests.Session()

    def authenticate(self):
        temp_auth = f"{qbBaseURL}/db/main?a=API_Authenticate"
        temp_auth += f"&username={qbUsername}&password={qbPassword}&hours={qbHours}"
        response = requests.post(temp_auth)
        ticket = etree.fromstring(response.content).findtext('ticket')
        return ticket

    def add_replace_db_pages(self):
        authentication_ticket = self.authenticate()
        
        # Request URL Handler
        url = self.base_url + '/db/' + qbApplicationDBID

        # Generate Headers For Request
        headers = {
            'Content-Type': 'application/xml',
            'QUICKBASE-ACTION': 'API_AddReplaceDBPage',
        }

        # Specify The File Path And Get Contents
        file_path = f'./{pyFolderName}/{pyFileName}'
        with open(file_path, 'r', encoding='utf-8') as file:
            contents = file.read()
        
        # Create A Request Dictionary
        request_dict = {
            'encoding': 'UTF-8',
            'msInUTC': 1,
            'pagename': pyFileName,
            'ticket': authentication_ticket,
            'apptoken': qbAppToken,
            'pagebody': contents,
        }

        # Convert to XML 
        xml_data = self._build_request(**request_dict)

        # Submit Request
        request = requests.post(url, xml_data, headers=headers)
        response = request.content

        # Get Request Response
        parsed = etree.fromstring(response)
        error_code = int(parsed.findtext('errcode'))
        if error_code == 0:
            print("Success! Code Page Has Been Updated And Completed")
        else:
            print("Error Code", error_code)

    def _build_request(self, **kwargs):
        # Convert the dictionary to an XML string with CDATA around pagebody
        request_xml = "<?xml version='1.0' encoding='utf-8'?>\n<qdbapi>"
        for key, value in kwargs.items():
            if key == 'pagebody':
                request_xml += f"<{key}><![CDATA[{value}]]></{key}>"
            else:
                request_xml += f"<{key}>{value}</{key}>"
        request_xml += "</qdbapi>"
        return request_xml

# Example usage
client = DatabaseClient()
client.add_replace_db_pages()
