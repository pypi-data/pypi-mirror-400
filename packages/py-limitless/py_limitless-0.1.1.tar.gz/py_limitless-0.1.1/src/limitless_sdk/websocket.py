"""
Limitless Exchange WebSocket Client
Real-time market data and position updates via Socket.IO
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Any

import socketio

from .constants import WEBSOCKET_URL
from .auth import authenticate, get_signing_message

logging.basicConfig(level=logging.WARNING, format="%(message)s")
logger = logging.getLogger(__name__)


class LimitlessWebSocket:
    """
    WebSocket client for Limitless Exchange real-time data.
    
    Supports:
    - Market price updates
    - Orderbook updates (CLOB markets)
    - Position updates (requires authentication)
    
    Example:
        ```python
        client = LimitlessWebSocket(auth_private_key="0x...")
        await client.connect()
        await client.subscribe_markets(market_slugs=["market-slug-here"])
        await client.wait()
        ```
    """
    
    def __init__(
        self,
        websocket_url: str = WEBSOCKET_URL,
        auth_private_key: Optional[str] = None,
    ):
        """
        Initialize the WebSocket client.

        Args:
            websocket_url: WebSocket server URL
            auth_private_key: Optional private key for authenticated features
        """
        self.websocket_url = websocket_url
        self.auth_private_key = auth_private_key
        self.session_cookie: Optional[str] = None
        self.user_data: Optional[dict] = None
        self.connected = False
        self.subscribed_markets: set[str] = set()
        self.subscribed_slugs: set[str] = set()
        
        # Custom event handlers
        self._event_handlers: dict[str, list[Callable]] = {}
        
        # Socket.IO client
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup Socket.IO event handlers."""
        
        @self.sio.event(namespace="/markets")
        async def connect():
            self.connected = True
            logger.info("Connected to /markets")
            
            # Send authentication if available
            if self.session_cookie:
                await self.sio.emit(
                    "authenticate",
                    f"Bearer {self.session_cookie}",
                    namespace="/markets"
                )
            
            # Re-subscribe to markets after reconnection
            if self.subscribed_markets or self.subscribed_slugs:
                await asyncio.sleep(1)
                await self._resubscribe()
        
        @self.sio.event(namespace="/markets")
        async def disconnect():
            self.connected = False
            logger.info("Disconnected from /markets")
            await self._emit_event("disconnect", {})
        
        @self.sio.event(namespace="/markets")
        async def authenticated(data):
            logger.debug(f"Authenticated: {data}")
            await self._emit_event("authenticated", data)
        
        @self.sio.event(namespace="/markets")
        async def newPriceData(data):
            """Handle new price data updates."""
            logger.debug(f"Price update: {data}")
            await self._emit_event("price", data)
        
        @self.sio.event(namespace="/markets")
        async def orderbookUpdate(data):
            """Handle CLOB orderbook updates."""
            logger.debug(f"Orderbook update: {data}")
            await self._emit_event("orderbook", data)
        
        @self.sio.event(namespace="/markets")
        async def positions(data):
            """Handle position updates."""
            logger.debug(f"Position update: {data}")
            await self._emit_event("positions", data)
        
        @self.sio.event(namespace="/markets")
        async def system(data):
            """Handle system messages."""
            logger.debug(f"System: {data}")
            await self._emit_event("system", data)
        
        @self.sio.event(namespace="/markets")
        async def exception(data):
            """Handle exception messages."""
            logger.error(f"Exception: {data}")
            await self._emit_event("exception", data)
    
    async def _emit_event(self, event_name: str, data: Any):
        """Emit event to registered handlers."""
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_name}: {e}")
    
    def on(self, event_name: str, handler: Callable):
        """
        Register an event handler.
        
        Args:
            event_name: Event name (price, orderbook, positions, system, exception)
            handler: Callback function (can be sync or async)
            
        Example:
            ```python
            def on_price(data):
                print(f"New price: {data}")
            
            client.on("price", on_price)
            ```
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def off(self, event_name: str, handler: Optional[Callable] = None):
        """
        Remove an event handler.
        
        Args:
            event_name: Event name
            handler: Specific handler to remove, or None to remove all
        """
        if event_name in self._event_handlers:
            if handler is None:
                self._event_handlers[event_name] = []
            else:
                self._event_handlers[event_name] = [
                    h for h in self._event_handlers[event_name] if h != handler
                ]
    
    async def authenticate(self):
        """Authenticate with the server using private key."""
        if not self.auth_private_key:
            logger.info("No private key - running in public mode")
            return
        
        try:
            logger.info("Authenticating with private key...")
            signing_message = get_signing_message()
            self.session_cookie, self.user_data = authenticate(
                self.auth_private_key, signing_message
            )
            logger.info(f"Authenticated as: {self.user_data.get('account')}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def connect(self):
        """
        Connect to the WebSocket server.
        
        Will authenticate first if a private key was provided.
        """
        try:
            # Authenticate first if private key provided
            await self.authenticate()
            
            logger.info(f"Connecting to {self.websocket_url}...")
            
            # Prepare connection options
            connect_options = {"transports": ["websocket"]}
            if self.session_cookie:
                connect_options["headers"] = {
                    "Cookie": f"limitless_session={self.session_cookie}"
                }
                logger.debug("Adding session cookie to connection headers")
            
            await self.sio.connect(
                self.websocket_url,
                namespaces=["/markets"],
                **connect_options
            )
            
            # Wait for connection to establish
            max_retries = 10
            for _ in range(max_retries):
                if self.connected:
                    break
                await asyncio.sleep(0.2)
            
            if not self.connected:
                raise ConnectionError("Failed to establish WebSocket connection")
            
            logger.info("Successfully connected")
            
        except Exception as e:
            logger.error(f"Connection error: {e}")
            raise
    
    async def subscribe_markets(
        self,
        market_addresses: list[str] | None = None,
        market_slugs: list[str] | None = None,
    ):
        """
        Subscribe to market updates.
        
        Args:
            market_addresses: List of market condition IDs
            market_slugs: List of market slugs
        """
        if not self.connected:
            raise ConnectionError("Not connected - call connect() first")
        
        market_addresses = market_addresses or []
        market_slugs = market_slugs or []
        
        # Filter out already subscribed markets to avoid duplicate subscriptions
        new_addresses = [
            addr for addr in market_addresses 
            if addr not in self.subscribed_markets
        ]
        new_slugs = [
            slug for slug in market_slugs 
            if slug not in self.subscribed_slugs
        ]
        
        if not new_addresses and not new_slugs:
            return

        payload = {
            "marketAddresses": new_addresses,
            "marketSlugs": new_slugs,
        }
        
        logger.info(
            f"Subscribing to {len(new_addresses)} addresses "
            f"and {len(new_slugs)} slugs"
        )
        
        # Subscribe to price updates
        await self.sio.emit(
            "subscribe_market_prices",
            payload,
            namespace="/markets"
        )
        
        # Subscribe to positions if authenticated
        if self.session_cookie:
            await self.sio.emit(
                "subscribe_positions",
                payload,
                namespace="/markets"
            )
        
        # Track subscribed markets for reconnection
        self.subscribed_markets.update(new_addresses)
        self.subscribed_slugs.update(new_slugs)
    
    async def _resubscribe(self):
        """Re-subscribe to markets after reconnection."""
        if self.subscribed_markets or self.subscribed_slugs:
            # Copy currently subscribed items
            market_addresses = list(self.subscribed_markets)
            market_slugs = list(self.subscribed_slugs)
            
            # Clear tracking so subscribe_markets will treat them as new
            self.subscribed_markets.clear()
            self.subscribed_slugs.clear()
            
            await self.subscribe_markets(
                market_addresses=market_addresses,
                market_slugs=market_slugs,
            )
    
    async def unsubscribe_markets(
        self,
        market_addresses: list[str] | None = None,
        market_slugs: list[str] | None = None,
    ):
        """
        Unsubscribe from market updates.
        
        Args:
            market_addresses: List of market condition IDs to unsubscribe
            market_slugs: List of market slugs to unsubscribe
        """
        market_addresses = market_addresses or []
        market_slugs = market_slugs or []
        
        # Filter to only those we are tracking
        remove_addresses = [
            addr for addr in market_addresses 
            if addr in self.subscribed_markets
        ]
        remove_slugs = [
            slug for slug in market_slugs 
            if slug in self.subscribed_slugs
        ]
        
        if not remove_addresses and not remove_slugs:
            return
            
        payload = {
            "marketAddresses": remove_addresses,
            "marketSlugs": remove_slugs,
        }
        
        await self.sio.emit(
            "unsubscribe_market_prices",
            payload,
            namespace="/markets"
        )
        
        if self.session_cookie:
            await self.sio.emit(
                "unsubscribe_positions",
                payload,
                namespace="/markets"
            )
        
        # Remove from tracked subscriptions
        self.subscribed_markets.difference_update(remove_addresses)
        self.subscribed_slugs.difference_update(remove_slugs)
    
    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.connected:
            await self.sio.disconnect()
            self.connected = False
            logger.info("Disconnected")
    
    async def wait(self):
        """Keep connection alive and listen for events."""
        await self.sio.wait()

