"""
requires_reboot.py

ansible-rulebook event source plugin that lists all hosts that require a reboot.

Arguments:
  - hostname: SUSE Manager/Uyuni hostname or IP address
  - username: API username
  - password: API password
  - delay: seconds to wait between events
  - hosts: list of hosts to check for reboots

Examples:
  sources:
    - stdevel.uyuni.requires_reboot:
        hostname: uiuiuiuyuni.local.loc
        username: admin
        password: admin
        delay: 10
        hosts:
          - uyuni-client.pinkepank.loc

"""
import asyncio
from typing import Any, Dict
import random
from pyuyuni.management import JSONHTTPClient
from pyuyuni.exceptions import (
    InvalidCredentialsException
)
from pyuyuni.hosts import list_systems_requiring_reboot
import logging


async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    """
    Main function that queries the Uyuni and returns whether hosts require reboots
    """
    delay = args.get("delay", 60)
    hosts = args.get("hosts", [])
    hostname = args.get("hostname")
    username = args.get("username")
    password = args.get("password")
    port = args.get("port", 443)
    verify = args.get("verify", False)

    # access the Uyuni API
    api_client = JSONHTTPClient(
        logging.ERROR,
        hostname,
        username,
        password,
        port,
        verify
    )
    _systems = list_systems_requiring_reboot(api_client)

    while True:
        for host in hosts:
            print(f"checking host {host}")
            _flag = True if host in _systems else False
            await queue.put(
                {
                    "host": host,
                    "requires_reboot": _flag
                }
            )
            await asyncio.sleep(delay)


if __name__ == "__main__":

    class MockQueue:
        """
        Mock queue class
        """

        async def put(self, event):
            """
            Function that simply prints the event
            """
            print(event)

    mock_arguments = {}
    asyncio.run(main(MockQueue(), mock_arguments))
