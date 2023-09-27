"""
requires_reboot.py

ansible-rulebook event source plugin that lists all hosts that require a reboot.

Arguments:
  - delay: seconds to wait between events

Examples:
  sources:
    - stdevel.uyuni.requires_reboot:
        delay: 10

"""
import asyncio
from typing import Any, Dict
import random


async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    """
    Main function that queries the Uyuni and returns whether hosts require reboots
    """
    delay = args.get("delay", 60)

    while True:
        await queue.put(
            {
                "requires_reboot": bool(random.randrange(0, 2))
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

    # mock_arguments = dict()
    mock_arguments = {}
    asyncio.run(main(MockQueue(), mock_arguments))
