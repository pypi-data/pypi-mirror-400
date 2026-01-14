import requests
from urllib.parse import quote_plus


def get_token(url: str, account: str, username: str, api_key: str):
    """
    Further documentation: https://docs.cyberark.com/Product-Doc/OnlineHelp/AAM-DAP/Latest/en/Content/Developer/Conjur_API_Authenticate.htm
    :param url:      Conjur API endpoint: https://conjur-prod-follower.cisco.com for prod
    :param account:  Always use "cisco"
    :param username: The full host identifier you can copy from the portal prefixed by "host/" (e.g.
    :param api_key:  API key you generated in the portal
    :return: return base64-encoded token
    """
    # 'account' and 'username' need to be url-encoded, whereas special characters get encoded safely
    account = quote_plus(account)
    username = quote_plus(username)
    r = requests.post(
        url=f"{url}/authn/{account}/{username}/authenticate",
        data=api_key,
        headers={"Accept-Encoding": "base64"},
    )
    # status code is 200 when the auth request has gone thru successfully
    if r.status_code == 200:
        return r.text  # return base64-encoded token
    else:
        print(f"Authentication error, response code: {r.status_code}")
        return None


def get_bulk_secrets(url: str, account: str, token: str, identifiers: list):
    """
    Further docs: https://docs.cyberark.com/Product-Doc/OnlineHelp/AAM-DAP/Latest/en/Content/Developer/Conjur_API_Batch_Retrieve.htm
    :param url:           Conjur API endpoint: https://conjur-prod-follower.cisco.com for prod
    :param account:       Always use "cisco"
    :param token:         token generated at the previous step
    :param identifiers:   list of full identifiers copied from the portal
    :return: list of secrets values
    """

    full_identifiers = ",".join(
        [f"{account}:variable:{quote_plus(var_id)}" for var_id in identifiers]
    )
    r = requests.get(
        url=f"{url}/secrets?variable_ids={full_identifiers}",
        headers={"Authorization": f'Token token="{token}"'},
    )

    # status code is 200 when the request is successful
    if r.status_code == 200:
        return r.text
    else:
        print(
            f"Bulk secret retrieval error, response code: {r.status_code} - check docs above"
        )
        return None


def set_secret_value(
    url: str, account: str, token: str, secret_path: str, secret_value: str
):
    """
    Set a secret value in Conjur using the /secrets API.

    :param url:           Conjur API endpoint (write endpoint)
    :param account:       Always use "cisco"
    :param token:         token generated from authentication
    :param secret_path:   full path to the secret variable
    :param secret_value:  value to set for the secret
    :return: True if successful, False otherwise
    """
    encoded_secret_path = quote_plus(secret_path)

    r = requests.post(
        url=f"{url}/secrets/{account}/variable/{encoded_secret_path}",
        data=secret_value,
        headers={"Authorization": f'Token token="{token}"'},
    )

    if r.status_code in [200, 201]:
        return True
    else:
        print(f"Secret setting error, response code: {r.status_code}")
        return False


def load_policy(
    url: str, account: str, token: str, policy_path: str, policy_content: str
):
    """
    Load policy to Conjur using the /policies API.

    :param url:             Conjur API endpoint (write endpoint)
    :param account:         Always use "cisco"
    :param token:           token generated from authentication
    :param policy_path:     path where to load the policy
    :param policy_content:  YAML policy content to load
    :return: True if successful, False otherwise
    """
    encoded_policy_path = quote_plus(policy_path)

    r = requests.post(
        url=f"{url}/policies/{account}/policy/{encoded_policy_path}",
        data=policy_content,
        headers={"Authorization": f'Token token="{token}"'},
    )

    if r.status_code == 201:
        return True
    else:
        print(
            f"Policy loading error, response code: {r.status_code}, response: {r.text}"
        )
        return False
