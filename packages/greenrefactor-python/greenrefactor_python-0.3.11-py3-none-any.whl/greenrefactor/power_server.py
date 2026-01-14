import asyncio
import json
import logging
import time
import websockets
from .core import choose_provider

# Configuration
PORT = 8126

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("PowerServer")

class PowerServer:
    def __init__(self):
        self.provider = None
        self.connected_clients = set()
    
    def initialize_provider(self):
        logger.info("Initializing Power Provider...")
        self.provider = choose_provider()
        logger.info(f"Using provider: {self.provider.name}")

    async def register(self, websocket):
        self.connected_clients.add(websocket)
        logger.info(f"Client connected. Total: {len(self.connected_clients)}")

    async def unregister(self, websocket):
        self.connected_clients.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.connected_clients)}")

    async def handler(self, websocket):
        await self.register(websocket)
        try:
            # Keep connection open and handle incoming messages if any (mostly ignored)
            async for message in websocket:
                pass 
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            await self.unregister(websocket)

    async def broadcast_loop(self):
        logger.info("Starting broadcast loop...")
        while True:
            try:
                # Always read power (even if no clients yet)
                watts = float(self.provider.read_watts())
                logger.info(f"Read power: {watts}W")
                
                provider_name = getattr(self.provider, 'name', self.provider.__class__.__name__.replace("Provider", ""))
                
                data = {
                    "event": "tick",
                    "power_w": watts,
                    "timestamp": time.time(),
                    "provider": provider_name
                }
                
                # Add extra metrics if available
                if hasattr(self.provider, "get_metrics"):
                     metrics = self.provider.get_metrics() or {}
                     data.update(metrics)
                
                message = json.dumps(data)
                
                # Only broadcast if clients connected
                if self.connected_clients:
                    websockets.broadcast(self.connected_clients, message)
                    logger.info(f"Broadcast to {len(self.connected_clients)} clients")
                    
            except Exception as e:
                logger.error(f"Error reading/broadcasting power: {e}", exc_info=True)
            
            await asyncio.sleep(1.0) # 1Hz update rate

    async def start(self):
        self.initialize_provider()
        async with websockets.serve(self.handler, "0.0.0.0", PORT):
            logger.info(f"WebSocket Power Server listening on ws://0.0.0.0:{PORT}")
            await self.broadcast_loop()

def run(port=PORT):
    # Wrapper to run async server
    try:
        server = PowerServer()
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server stopping...")

if __name__ == "__main__":
    run()
