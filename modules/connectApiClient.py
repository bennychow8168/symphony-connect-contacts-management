import requests
import json
import datetime
import logging
import urllib.parse
from jose import jwt
from json.decoder import JSONDecodeError


class ConnectApiClient():

    def __init__(self, config):
        self.config = config
        self.podId = config.data['podId']
        self.jwt = None


    def update_contact(self, externalNetwork, email, firstName, lastName, companyName, phoneNumber, advisorEmailAddress):
        url = f'/api/v1/customer/contacts/{urllib.parse.quote_plus(email)}/update'

        body = {
            "firstName": firstName,
            "lastName": lastName,
            "companyName": companyName,
            "phoneNumber": phoneNumber,
            "externalNetwork": externalNetwork,
            "advisorEmailAddress": advisorEmailAddress,
            }

        status, result = self.execute_rest_call(externalNetwork, "POST", url, json=body)

        return status, result


    def add_contact(self, externalNetwork, firstName, lastName, email, phoneNumber, companyName, advisorEmailList):
        url = '/api/v2/customer/contacts'

        body = {
            "firstName": firstName,
            "lastName": lastName,
            "companyName": companyName,
            "emailAddress": email,
            "phoneNumber": phoneNumber,
            "externalNetwork": externalNetwork,
            "advisorEmailAddresses": advisorEmailList,
            "onboarderEmailAddress": advisorEmailList[0]
            }

        status, result = self.execute_rest_call(externalNetwork, "POST", url, json=body)

        return status, result


    def delete_contact(self, externalNetwork, email, advisorEmailAddress):
        url = f'/api/v1/customer/contacts/advisorEmailAddress/{urllib.parse.quote_plus(advisorEmailAddress)}/contactEmailAddress/{urllib.parse.quote_plus(email)}/externalNetwork/{externalNetwork}'

        status, result = self.execute_rest_call(externalNetwork, "DELETE", url)
        return status, result


    def parse_result(self, apiResult, responseCode):
        if apiResult is not None:
            if responseCode not in (200, 204):
                errorMsg = f'ERROR:'
                if 'status' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["status"]}'
                if 'error' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["error"]}'
                if 'type' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["type"]}'
                if 'title' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["title"]}'
                if 'message' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["message"]}'
                if 'errorMessage' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["errorMessage"]}'
                if 'errorCode' in apiResult:
                    errorMsg = errorMsg + f' - {apiResult["errorCode"]}'
                return errorMsg
            else:
                return 'OK'
        else:
            return 'ERROR: No response found from API call'


    def get_session(self, externalNetwork):
        session = requests.Session()

        if self.jwt is not None:
            jwt = self.jwt
        else:
            jwt = self.create_jwt(externalNetwork)

        session.headers.update({
            'Content-Type': "application/json",
            'Authorization': "Bearer " + jwt}
        )

        session.proxies.update(self.config.data['proxyRequestObject'])
        if self.config.data["truststorePath"]:
            logging.debug("Setting truststorePath to {}".format(
                self.config.data["truststorePath"])
            )
            session.verify = self.config.data["truststorePath"]

        return session


    def execute_rest_call(self, externalNetwork, method, path, **kwargs):
        results = None
        if externalNetwork == "WECHAT":
            apiURL = self.config.data['wechat_apiURL']
        elif externalNetwork == "WHATSAPP":
            apiURL = self.config.data['whatsapp_apiURL']

        url = apiURL + path
        session = self.get_session(externalNetwork)
        try:
            logging.debug(f'Invoke API URL: {url}')
            response = session.request(method, url, **kwargs)
        except requests.exceptions.ConnectionError as err:
            logging.error(err)
            logging.error(type(err))
            raise
        # print(url)
        # print(response.status_code)
        # print(response.text)

        logging.debug(f'Response Status Code: {response.status_code}')
        logging.debug(f'Response Text: {response.text}')

        if response.status_code == 204:
            results = []
        # JWT Expired - Generate new one
        elif response.status_code == 401:
            logging.info("JWT Expired - Reauthenticating...")
            self.jwt = None
            return self.execute_rest_call(externalNetwork, method, path, **kwargs)
        else:
            try:
                results = json.loads(response.text)
            except JSONDecodeError:
                results = response.text

        final_output = self.parse_result(results, response.status_code)
        logging.debug(results)
        logging.debug(final_output)
        logging.debug(f'API Output: {final_output}')
        if response.status_code in (200, 204):
            return 'OK', results
        else:
            return 'ERROR', final_output


    def create_jwt(self, externalNetwork):
        with open(self.config.data['botRSAPath'], 'r') as f:
            content = f.readlines()
            private_key = ''.join(content)
            current_date = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            expiration_date = current_date + (5*58)

            if externalNetwork == 'WHATSAPP':
                payload = {
                    'sub': 'ces:customer:' + self.config.data['whatsapp_publicKeyId'],
                    'exp': expiration_date,
                    'iat': current_date
                }
            elif externalNetwork == 'WECHAT':
                payload = {
                    'sub': 'ces:customer:' + self.config.data['wechat_publicKeyId'],
                    'exp': expiration_date,
                    'iat': current_date
                }

            encoded = jwt.encode(payload, private_key, algorithm='RS512')
            f.close()
            self.jwt = encoded
            return encoded
