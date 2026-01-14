"""
This module handles the initialization of connections to the k2-connect
library's services.It defines all functions a k2-connect service class
should have. It is the base services class on top of which k2-connect
services are built.
"""
from k2connect import k2_requests
from k2connect import validation


class Service(k2_requests.Requests):
    """
    The Base service :class: Service  containing all service class
    functionality.
    Used to create custom k2-connect service classes.\
    Example:
        class PayService(Service):
            ...
    """
    def __init__(self,
                 base_url):
        """
        Initializes function arguments and creates protected variables
        accessible to all subclasses of the Service class.

        :param base_url: The domain to use in the library
        :type base_url: str
        """
        super(Service, self).__init__()

        # validate base url
        if validation.validate_url(base_url) is True:
            self._base_url = base_url

    def _build_url(self, url_path):
        """
        Returns complete URL with path for specific services appended to the base URL
        Example:
            Service(client_id, client_secret, 'https://api.kopokopo.com/')
            return: https://api.kopokopo.com/url_path

        :param url_path: path for specific k2-connect services
        :type url_path: str
        :return str
        """
        return self._base_url + url_path
