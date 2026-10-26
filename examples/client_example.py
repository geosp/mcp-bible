#!/usr/bin/env python3
"""
Example client for Bible MCP Server.

Connects to a running server over HTTP, lists its tools and fetches a
passage. This is a live smoke test: it calls BibleGateway.com.

Requirements:
    - Server running in HTTP mode: mcp-bible --mode http --port 3000 --no-auth

Usage:
    python examples/client_example.py [--url URL] [PASSAGE]

    # Examples:
    python examples/client_example.py "John 3:16"
    python examples/client_example.py --url http://localhost:4000/mcp "Romans 8:28"
"""

import sys
import asyncio
import json
import argparse
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport

DEFAULT_URL = "http://localhost:3000/mcp"


async def run_example(url: str = DEFAULT_URL, passage: str = None):
    """
    Test the Bible MCP Server

    Args:
        url: MCP endpoint URL
        passage: Optional Bible passage to test (default: "John 3:16")
    """

    if not passage:
        passage = "John 3:16"

    print("🧪 Testing Bible MCP Server")
    print("=" * 70)
    print(f"🔗 URL: {url}")
    print()

    try:
        # Create transport (no auth needed since it's disabled)
        transport = StreamableHttpTransport(url=url)

        print("🔌 Attempting to connect to MCP server...")
        async with Client(transport=transport) as client:
            print('✅ Connected successfully')

            # Test 1: List Tools
            print("\n" + "=" * 70)
            print("📋 Available Tools")
            print("-" * 70)

            tools_response = await asyncio.wait_for(client.list_tools(), timeout=10.0)
            tools = tools_response.tools if hasattr(tools_response, 'tools') else tools_response

            for tool in tools:
                print(f"🔧 {tool.name}")
                if hasattr(tool, 'description') and tool.description:
                    desc = tool.description.split('\n')[0]
                    print(f"   {desc[:100]}")

            # Test 2: Call Bible Tool
            print("\n" + "=" * 70)
            print("📖 Testing Bible Passage Tool")
            print("-" * 70)

            print(f"📍 Passage: {passage}")

            result = await asyncio.wait_for(
                client.call_tool('get_passage', {'passage': passage, 'version': 'NIV'}),
                timeout=15.0
            )

            # Parse response
            if hasattr(result, 'content') and result.content:
                content = result.content[0]
                if hasattr(content, 'text'):
                    passage_data = json.loads(content.text)

                    # Display results
                    print(f"\n📊 Bible Passage Result")
                    print(f"{'─' * 70}")
                    print(f"📖 {passage_data.get('passage', passage)}")
                    print(f"📚 Version: {passage_data.get('version', 'NIV')}")

                    if passage_data.get('text'):
                        print(f"\n{passage_data['text'][:200]}...")
                    else:
                        print("❌ No text returned")

                    print(f"\n✅ Test completed!")
                    return True
                else:
                    print(f"❌ Unexpected content format: {content}")
                    return False
            else:
                print("❌ No content returned")
                return False

    except asyncio.TimeoutError:
        print('\n❌ Timeout - server not responding')
        return False
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test Bible MCP Server")
    parser.add_argument("passage", nargs="?", help="Bible passage to test")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"MCP endpoint URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    # Run the test
    success = asyncio.run(run_example(args.url, args.passage))
    sys.exit(0 if success else 1)