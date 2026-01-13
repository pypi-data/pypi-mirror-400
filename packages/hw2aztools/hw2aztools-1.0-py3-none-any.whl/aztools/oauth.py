import requests


class OathGraph:


    def __init__(self, tenant_id: str, client_id: str, client_secret: str):

        # parameters
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        # attributes
        self.graph_auth = f'https://login.windows.net/{self.tenant_id}/oauth2/token'
        self.graph_resource_url = 'https://graph.microsoft.com'
        self.request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.request_body = {
            'resource': self.graph_resource_url,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        self.response_json = requests.request('POST', self.graph_auth,
                                              headers=self.request_header,
                                              data=self.request_body).json()

        self.token_type = self._token_type()
        self.access_token = self._access_token()


    def _token_type(self):
        if 'token_type' in self.response_json:
            output = self.response_json['token_type']
        else:
            output = self.response_json['error']

        return output


    def _access_token(self):
        if 'access_token' in self.response_json:
            output = self.response_json['access_token']
        else:
            output = self.response_json['error']

        return output


class OathMde:


    def __init__(self, tenant_id: str, client_id: str, client_secret: str):

        # parameters
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        # attributes
        self.mde_auth = f'https://login.windows.net/{self.tenant_id}/oauth2/token'
        self.mde_resource_url = 'https://api.securitycenter.windows.com'
        self.request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.request_body = {
            'resource': self.mde_resource_url,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        self.response_json = requests.request('POST', self.mde_auth,
                                              headers=self.request_header,
                                              data=self.request_body).json()

        self.token_type = self._token_type()
        self.access_token = self._access_token()


    def _token_type(self):
        if 'token_type' in self.response_json:
            output = self.response_json['token_type']
        else:
            output = self.response_json['error']

        return output


    def _access_token(self):
        if 'access_token' in self.response_json:
            output = self.response_json['access_token']
        else:
            output = self.response_json['error']

        return output


class OathLogAnalytics:


    def __init__(self, tenant_id: str, client_id: str, client_secret: str):

        # parameters
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        # attributes
        self.la_auth = f'https://login.windows.net/{self.tenant_id}/oauth2/token'
        self.la_resource_url = 'https://api.loganalytics.io'
        self.request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.request_body = {
            'resource': self.la_resource_url,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        self.response_json = requests.request('POST', self.la_auth,
                                              headers=self.request_header,
                                              data=self.request_body).json()

        self.token_type = self._token_type()
        self.access_token = self._access_token()


    def _token_type(self):
        if 'token_type' in self.response_json:
            output = self.response_json['token_type']
        else:
            output = self.response_json['error']

        return output


    def _access_token(self):
        if 'access_token' in self.response_json:
            output = self.response_json['access_token']
        else:
            output = self.response_json['error']

        return output


class OathArm:


    def __init__(self, tenant_id: str, client_id: str, client_secret: str):

        # parameters
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        # attributes
        self.arm_auth = f'https://login.windows.net/{self.tenant_id}/oauth2/token'
        self.arm_resource_url = 'https://management.azure.com'
        self.request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.request_body = {
            'resource': self.arm_resource_url,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        self.response_json = requests.request('POST', self.arm_auth,
                                              headers=self.request_header,
                                              data=self.request_body).json()

        self.token_type = self._token_type()
        self.access_token = self._access_token()


    def _token_type(self):
        if 'token_type' in self.response_json:
            output = self.response_json['token_type']
        else:
            output = self.response_json['error']

        return output


    def _access_token(self):
        if 'access_token' in self.response_json:
            output = self.response_json['access_token']
        else:
            output = self.response_json['error']

        return output


