#!/usr/bin/env python3
"""
9S PUBLIC NODE SERVICE
Individual public node service with tier enforcement

Usage:
    python 9s_public_node.py <node_id>

Example:
    python 9s_public_node.py PUBLIC-001
"""
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("9s_public_node")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("[WARNING] websockets not installed. Run: pip install websockets")

class PublicNodeConfig:
    """Public node configuration with enforced limits"""
    
    def __init__(self):
        self.max_slots = 400
        self.max_context = 8192
        self.allowed_models = ["logos9.5"]
        self.max_mirrors = 3

class PublicNodeService:
    """Public tier node service"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.config = PublicNodeConfig()
        self.active_slots = 0
        self.mirror_count = 0
        self.connections = []
        self.message_log = []
        
        # Generate unique port based on node ID
        self.ws_port = 9000 + abs(hash(node_id)) % 1000
    
    def log_message(self, msg_type: str, content: Dict):
        """Log messages for debugging"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg_type,
            "content": content,
            "node": self.node_id
        }
        self.message_log.append(entry)
        
        # Keep log size manageable
        if len(self.message_log) > 1000:
            self.message_log = self.message_log[-500:]
    
    def can_process(self, command: Dict) -> bool:
        """Check if command can be processed within public tier limits"""
        
        # Check model restriction
        if command.get("model") not in self.config.allowed_models:
            logger.warning(f"Model {command.get('model')} not allowed in public tier")
            return False
        
        # Check slot availability
        if self.active_slots >= self.config.max_slots:
            logger.warning("Public tier slots exhausted")
            return False
        
        # Check mirroring limit
        if command.get("action") == "mirror":
            if self.mirror_count >= self.config.max_mirrors:
                logger.warning("Mirroring limit reached")
                return False
        
        return True
    
    async def process_command(self, command: Dict) -> Dict:
        """Process command with public tier enforcement"""
        
        if not self.can_process(command):
            return {
                "error": "Public tier limit exceeded",
                "node": self.node_id,
                "tier": "PUBLIC"
            }
        
        self.active_slots += 1
        
        try:
            # Simulate processing
            await asyncio.sleep(0.1)
            
            result = {
                "node": self.node_id,
                "tier": "PUBLIC",
                "result": f"Processed: {command.get('action')}",
                "timestamp": datetime.now().isoformat(),
                "slots_used": self.active_slots,
                "max_slots": self.config.max_slots
            }
            
            self.log_message("PROCESSED", result)
            return result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "node": self.node_id,
                "tier": "PUBLIC"
            }
            self.log_message("ERROR", error_result)
            return error_result
            
        finally:
            self.active_slots -= 1
    
    async def handle_connection(self, websocket, path):
        """Handle WebSocket connections"""
        
        self.connections.append(websocket)
        logger.info(f"Connection established from {websocket.remote_address}")
        
        try:
            async for message in websocket:
                try:
                    command = json.loads(message)
                    self.log_message("RECEIVED", command)
                    
                    # Process command
                    result = await self.process_command(command)
                    self.log_message("RESPONSE", result)
                    
                    # Send response
                    await websocket.send(json.dumps(result))
                    
                except json.JSONDecodeError as e:
                    error_response = {
                        "error": f"Invalid JSON: {str(e)}",
                        "node": self.node_id
                    }
                    await websocket.send(json.dumps(error_response))
                    
                except Exception as e:
                    error_response = {
                        "error": str(e),
                        "node": self.node_id
                    }
                    await websocket.send(json.dumps(error_response))
                    
        finally:
            self.connections.remove(websocket)
            logger.info("Connection closed")
    
    async def start_server(self):
        """Start the WebSocket server"""
        
        if not WEBSOCKETS_AVAILABLE:
            print("ERROR: websockets package not installed")
            print("Run: pip install websockets")
            return
        
        print(f"\n{'='*60}")
        print(f"9S PUBLIC NODE SERVICE")
        print(f"{'='*60}")
        print(f"Node ID: {self.node_id}")
        print(f"Port: {self.ws_port}")
        print(f"Max Slots: {self.config.max_slots}")
        print(f"Allowed Models: {', '.join(self.config.allowed_models)}")
        print(f"Max Mirrors: {self.config.max_mirrors}")
        print(f"{'='*60}")
        
        try:
            server = await websockets.serve(
                self.handle_connection, 
                "localhost", 
                self.ws_port
            )
            
            print(f"Public node service started on ws://localhost:{self.ws_port}")
            print("Press Ctrl+C to stop")
            
            await server.wait_closed()
            
        except Exception as e:
            print(f"Failed to start server: {e}")
    
    def get_status(self) -> Dict:
        """Get current node status"""
        
        return {
            "node_id": self.node_id,
            "tier": "PUBLIC",
            "active_slots": self.active_slots,
            "max_slots": self.config.max_slots,
            "mirror_count": self.mirror_count,
            "max_mirrors": self.config.max_mirrors,
            "connections": len(self.connections),
            "allowed_models": self.config.allowed_models
        }

async def main():
    """Main function"""
    
    if len(sys.argv) != 2:
        print("Usage: python 9s_public_node.py <node_id>")
        print("Example: python 9s_public_node.py PUBLIC-001")
        return
    
    node_id = sys.argv[1]
    
    # Validate node ID format
    if not node_id.startswith("PUBLIC-"):
        print("Public node IDs must start with 'PUBLIC-'")
        return
    
    node_service = PublicNodeService(node_id)
    await node_service.start_server()

if __name__ == "__main__":
    asyncio.run(main())