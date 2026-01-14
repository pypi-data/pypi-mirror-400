class ServiceAccount(object):
    def __init__(self, username: str = None, secret: str = None):
        """
        Constructs a new mixpanel service account instance.

        :param username: Service account username
        :param secret: Service account secret
        """
        self.username = username
        self.secret = secret

    def get_credentials(self):
        """
        Returns preserved credentials as basic auth parameters for this service account.

        :return: Tuple of service account credentials
        """
        creds = (self.username, self.secret)
        return creds


class Connection(object):
    def __init__(
        self,
        service_account_name: str = None,
        service_account_secret: str = None,
        access_token: str = None,
    ):
        """
        Constructs a new mixpanel connection instance.
        Supports both service account and token based authentications for various api call needs.

        :param service_account_name: Service account username
        :param service_account_secret: Service account secret
        :param access_token: Access token
        """
        self.service_account = ServiceAccount(
            username=service_account_name, secret=service_account_secret
        )
        self.access_token = access_token

    def get_service_account_credentials(self):
        """
        Should be used for basic auth based on service account credentials.

        :return: Tuple of service account credentials
        """
        return self.service_account.get_credentials()

    def get_access_token(self):
        """
        Should be used for token based auth

        :return: Access token
        """
        return self.access_token
