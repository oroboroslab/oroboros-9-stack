#!/usr/bin/env python3
"""
9S Public Tier Client Example
Connect to a public node and send commands
"""
import asyncio
import json
import websockets
from typing import Dict

class PublicTierClient:
    """Client for connecting to 9S public nodes"""
    
    def __init__(self, node_url: str = "ws://localhost:9001"):
        self.node_url = node_url
    
    async def send_command(self, command: Dict) -> Dict:
        """Send a command to the public node"""
        
        try:
            async with websockets.connect(self.node_url) as websocket:
                await websocket.send(json.dumps(command))
                response = await websocket.recv()
                return json.loads(response)
                
        except Exception as e:
            return {"error": str(e)}
    
    async def process_text(self, text: str) -> Dict:
        """Process text using LOGOS-9.5 model"""
        
        command = {
            "action": "process",
            "model": "logos9.5",
            "prompt": text,
            "tier": "PUBLIC"
        }
        
        return await self.send_command(command)
    
    async def get_status(self) -> Dict:
        """Get node status"""
        
        command = {
            "action": "status",
            "tier": "PUBLIC"
        }
        
        return await self.send_command(command)

async def main():
    """Example usage"""
    
    client = PublicTierClient("ws://localhost:9001")
    
    # Get status
    status = await client.get_status()
    print("Node Status:", status)
    
    # Process some text
    result = await client.process_text("Hello, 9S Public Tier!")
    print("Processing Result:", result)

if __name__ == "__main__":
    asyncio.run(main())