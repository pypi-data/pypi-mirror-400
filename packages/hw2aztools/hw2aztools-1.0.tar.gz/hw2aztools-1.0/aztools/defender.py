import requests
import pandas as pd
import datetime


class DefenderPortalAhtQueryRun:

    def __init__(self, **kwargs):

        # parameters
        self.oath_token = kwargs.get('graph_oauth_token', 'Variable Input Error')
        self.query_text = kwargs.get('query_text', 'Variable Input Error')

        # attributes
        self.query_json = {"query": self.query_text}
        self.request_url = 'https://graph.microsoft.com/v1.0/security/runHuntingQuery'
        self.request_headers = {
            'Authorization': f'Bearer {self.oath_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.response_json = requests.request('POST',
                                              self.request_url,
                                              headers=self.request_headers,
                                              json=self.query_json).json()
        self.pull_date = datetime.datetime.now()
        self.response_df = self._to_df()


    def _to_df(self):
        if 'results' in self.response_json:
            aht_df = pd.DataFrame.from_dict(self.response_json['results'])
            aht_df['QueryRunDate'] = self.pull_date

        else:
            aht_df = pd.DataFrame.from_dict(self.response_json['error'])

        return aht_df


class DefenderPortalListCustomRules:

    def __init__(self, **kwargs):

        # parameters
        self.oath_token = kwargs.get('graph_oauth_token', 'Variable Input Error')

        # attributes
        self.request_url = 'https://graph.microsoft.com/beta/security/rules/detectionRules'
        self.request_headers = {
            'Authorization': f'Bearer {self.oath_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.response_json = requests.request('GET',
                                              self.request_url,
                                              headers=self.request_headers).json()
        self.pull_date = datetime.datetime.now()
        self.response_df = self._to_df()
        self.response_df_flat = self._flat_df()


    def _to_df(self):
        df1 = pd.DataFrame(self.response_json)

        return df1

    def _flat_df(self):
        df2 = pd.DataFrame(self.response_json)
        df2 = pd.concat([df2, df2['value'].apply(pd.Series)], axis=1)
        df2 = df2.drop('value', axis=1)
        df2 = pd.concat([df2, df2['queryCondition'].apply(pd.Series)], axis=1)
        df2 = df2.drop('queryCondition', axis=1)
        df2 = pd.concat([df2, df2['schedule'].apply(pd.Series)], axis=1)
        df2 = df2.drop('schedule', axis=1)
        df2 = pd.concat([df2, df2['lastRunDetails'].apply(pd.Series)], axis=1)
        df2 = df2.drop('lastRunDetails', axis=1)
        df2 = pd.concat([df2, df2['detectionAction'].apply(pd.Series)], axis=1)
        df2 = df2.drop('detectionAction', axis=1)
        df2 = pd.concat([df2, df2['alertTemplate'].apply(pd.Series)], axis=1)
        df2 = df2.drop('alertTemplate', axis=1)

        return df2
