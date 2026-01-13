"""
GraphQL availability test

This module implements a test that checks if the provided URL is hosting GraphQL or not

Contains:
- IsGraphQL to perform the availability test
- run() function as an entry point for running the test
"""
from http import HTTPStatus
from ptlibs.ptjsonlib import PtJsonLib
from ptlibs.http.http_client import HttpClient
from argparse import Namespace
from ptlibs.ptprinthelper import ptprint
from urllib.parse import urlparse
from requests.exceptions import JSONDecodeError
from requests import Response

__TESTLABEL__ = "GraphQL availability test"


class IsGraphQL:
    """Class for executing the GraphQL availability test"""
    def __init__(self, args: Namespace, ptjsonlib: PtJsonLib, helpers: object, http_client: HttpClient) -> None:
        self.args = args
        self.ptjsonlib = ptjsonlib
        self.helpers = helpers
        self.http_client = http_client

        self.helpers.print_header(__TESTLABEL__)


    def _check_response(self, response: Response) -> bool:
        """
        This method checks whether the provided HTTP response has the status code of 200 HTTP OK and if the received JSON
        equals {"data":{"__typename:":"Query"}}

        :param response: HTTP response from the suspected GraphQL endpoint we want to probe
        :return: True if the HTTP response is 200 HTTP OK and the JSON matches. False otherwise
        """
        if response.status_code == HTTPStatus.NOT_FOUND:
            return False

        expected = {"data":{"__typename":"Query"}}

        try:
            json_response = response.json()
        except JSONDecodeError as e:
            ptprint(f"Error decoding JSON from response: {e}", "ERROR", not self.args.json, indent=4)
            ptprint(f"Full response: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            return False

        return response.status_code == HTTPStatus.OK and json_response == expected


    def _brute_force(self) -> str:
        """
        This method probes suspected GraphQL endpoints from a wordlist specified with the -w/--wordlist argument (default data/wordlists/endpoints.txt).
        If the response is verified with the _check_response() method to be a GraphQL response. We return a URL of the host and verified endpoint.

        :return: URL of the verified GraphQL endpoint. Empty string if none is found
        """
        payload = '{"query": "query{__typename}"}'
        parsed = urlparse(self.args.url)
        url = parsed.scheme + "://" + parsed.netloc

        with open(self.args.wordlist, "r") as wordlist:
            endpoints = set(wordlist.read().split('\n'))

        for endpoint in endpoints:
            ptprint(f"Trying endpoint {endpoint}...", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            response = self.http_client.send_request(method="POST", url=url+endpoint, data=payload, allow_redirects=False)

            ptprint(f"Received response: {response.text}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)

            if self._check_response(response):
                return url+endpoint

        return ""


    def run(self) -> None:
        """
        Executes the GraphQL availability test

        Sends the following query to test if GraphQL is present on the provided URL: {'query': 'query{__typename}'}.
        If GraphQL is not detected on the provided URL, we try to bruteforce common GraphQL endpoints with a wordlist.
        Ends with an error if GraphQL is not detected.
        """

        response = self.http_client.send_request(method="POST", data='{"query": "query{__typename}"}', url=self.args.url, allow_redirects=False)

        if self._check_response(response):
            ptprint(f"{response.json()}", "ADDITIONS", self.args.verbose, indent=4, colortext=True)
            ptprint(f"The provided URL {self.args.url} is hosting GraphQL", "VULN", not self.args.json, indent=4)
            return
        else:
            ptprint(f"The provided URL {self.args.url} is not hosting GraphQL. Attempting bruteforce with the {self.args.wordlist} wordlist",
                    "OK", not self.args.json, indent=4)
            if new_url := self._brute_force():
                ptprint(f"The provided URL {new_url} is hosting GraphQL", "VULN", not self.args.json, indent=4)
                self.args.url = new_url
            else:
                self.ptjsonlib.end_error("GraphQL is not present on the provided URL.", self.args.json)


def run(args, ptjsonlib, helpers, http_client):
    """Entry point for running the IsGraphQL test"""
    IsGraphQL(args, ptjsonlib, helpers, http_client).run()
