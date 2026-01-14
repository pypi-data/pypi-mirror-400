#!/usr/bin/env python3
"""
UDPBus - Simple UDP Message Bus
CBOR Array Protocol: [increment, topic, meta, field1, field2, ...]

Clean API:
    from udpbus import UDPBus
    
    bus = UDPBus("node_name")
    
    # Publish with field list - meta optional
    bus.publish("sensor/temperature", [23.5, "°C", "cpu"])
    bus.publish("actuator/led", [True, 255], meta={"priority": "high"})
    
    # Subscribe with header/payload separation
    def handle_temperature(header, msg):
        # header = [increment, topic, meta]
        # msg = [field1, field2, ...] starting at index 0
        increment, topic, meta = header[0], header[1], header[2]
        temp, unit, sensor = msg[0], msg[1], msg[2]
        print(f"Temperature: {temp}{unit} from {sensor} (inc: {increment})")
    
    bus.subscribe("sensor/temperature", handle_temperature)
    bus.run()
"""

import socket
import struct
import time
import threading
from typing import Dict, Callable, Any, Optional, Union, List
import json
import logging

import cbor2

# Configure logging for production
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# UDPBus Configuration - Protocol defaults (consistent across Python/C++/Arduino)
DISCOVERY_MULTICAST = "239.255.42.99"  # Protocol standard multicast group
DISCOVERY_PORT = 4299                   # Protocol standard discovery port  
MESSAGE_PORT_BASE = 4300                # Protocol standard message port
ANNOUNCE_INTERVAL_1 = 1.0
ANNOUNCE_INTERVAL_2 = 2.0
ANNOUNCE_INTERVAL_3 = 5.0
ANNOUNCE_INTERVAL_4 = 10.0
NODE_TIMEOUT = 30.0  # Increased from 10.0s - more stable peer tracking

# Phase 4.2: Precise packet structure constants
MAX_PACKET_SIZE = 512           # Internet-safe UDP frame size
MAX_TOPIC_LENGTH = 42           # Protocol topic limit
MAX_CHUNK_SIZE = 463            # 512 - 49 bytes CBOR overhead  
CHUNK_TIMEOUT_SECONDS = 5
MAX_REASSEMBLED_SIZE = 2048 * 2048  # 4MB limit for reassembled messages

class UDPBus:
    """Simple UDP message bus with CBOR array protocol"""
    
    def __init__(self, node_name: str, debug: bool = False, uniquify: bool = False, 
                 enable_discovery: bool = True, manual_peers: List[Dict] = None):
        # Apply uniquify if requested
        if uniquify:
            postfix = str(int(time.time() * 1000))[-3:]  # Last 3 digits of millisecond timestamp
            node_name = f"{node_name}_{postfix}"

        self.node_name = node_name
        self.debug = debug
        self.running = False
        self.enable_discovery = enable_discovery
        
        # Networking
        self.discovery_socket = None
        self.message_socket = None
        self.message_port = None
        
        # Message tracking - SIMPLIFIED: No duplicate checking
        self.increment_counter = 0  # CBOR array increment counter
        
        # Subscription storage - separate exact and wildcard
        self.exact_subscribers: Dict[str, list] = {}  # "topic" -> [callbacks]
        self.wildcard_subscribers: List[tuple] = []   # [(pattern, callback), ...]
        self.published_topics = set()
        
        # SIMPLIFIED Node management  
        self.peers: Dict[str, Dict] = {}  # node_name -> {ip, port, subscribed_topics, last_seen, is_manual}
        
        # Phase 4.2: Chunk reassembly tracking
        self.active_chunks: Dict[str, Dict] = {}  # "sender_ip:topic" -> {topic, expected_seq, chunks, start_time}
        self.last_chunk_cleanup = time.time()
        
        # Threading
        self.threads = []
        # Separate locks to prevent discovery from blocking message operations
        self.message_lock = threading.RLock()    # For message sequence generation and sending
        self.discovery_lock = threading.RLock()  # For peer management and discovery
        
        # Production optimizations
        self._last_discovery_send = 0
        
        # Phase 4.3: Initialize manual peers if provided
        if manual_peers:
            for peer_config in manual_peers:
                self.add_peer(peer_config['ip'], peer_config['port'], peer_config['subscribed_topics'])
        
    def begin(self) -> bool:
        """Initialize the UDP bus (Arduino-compatible API)"""
        success = self._setup_sockets()
        if success:
            self.running = True  # Mark bus as running after successful setup
        return success
        
    def _setup_sockets(self) -> bool:
        """Setup UDP sockets for discovery and messaging"""
        try:
            # Phase 4.3: Only setup discovery socket if discovery is enabled
            if self.enable_discovery:
                # Discovery socket (multicast)
                self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Enable multicast sharing on macOS/BSD
                try:
                    self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
                except (AttributeError, OSError):
                    pass  # Not available on all platforms
                
                self.discovery_socket.bind(('', DISCOVERY_PORT))
                
                # Join multicast group
                mreq = struct.pack("4sl", socket.inet_aton(DISCOVERY_MULTICAST), socket.INADDR_ANY)
                self.discovery_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
                self.discovery_socket.settimeout(1.0)
            
            # Message socket (unicast) - prefer protocol port, auto-select if unavailable
            self.message_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                # Try protocol-preferred port first
                self.message_socket.bind(('', MESSAGE_PORT_BASE))
                self.message_port = MESSAGE_PORT_BASE
                if self.debug:
                    logger.info(f"📍 Bound to preferred protocol port {MESSAGE_PORT_BASE}")
            except OSError:
                # Protocol-preferred port unavailable, let OS choose available port
                self.message_socket.bind(('', 0))  # OS chooses available port
                self.message_port = self.message_socket.getsockname()[1]
                if self.debug:
                    logger.info(f"📍 Protocol port {MESSAGE_PORT_BASE} unavailable, using port {self.message_port}")
                # This is normal for multi-node scenarios - discovery will announce actual port
            self.message_socket.settimeout(1.0)
            
            if self.debug:
                logger.info(f"🚀 UDPBus '{self.node_name}' started on port {self.message_port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to setup sockets: {e}")
            return False
    
    def publish(self, topic: str, fields: List[Any], meta: Any = None) -> bool:
        """Publish with Phase 4.2 type field and chunking support"""
        if not self.running:
            if self.debug:
                logger.warning(f"Cannot publish '{topic}' - bus not running")
            return False
        
        # Validate topic length (protocol requirement)
        if len(topic) > MAX_TOPIC_LENGTH:
            logger.error(f"Topic '{topic}' too long: {len(topic)} > {MAX_TOPIC_LENGTH} chars")
            return False
        
        # Track published topics
        self.published_topics.add(topic)
        
        # Create message and increment counter
        with self.message_lock:
            self.increment_counter = (self.increment_counter + 1) % 65536  # Simple rollover
            sequence_id = self.increment_counter
        
        # Phase 4.2: Create message with type field: [sequence_id, topic, type, fields]
        # For backward compatibility, if meta is provided, embed it in fields
        if meta is not None:
            # Legacy mode: convert to new format with meta as first field
            message_fields = [meta] + fields
        else:
            message_fields = fields
            
        message_array = [sequence_id, topic, 0, message_fields]  # type 0 = normal message
        
        try:
            # Encode array as CBOR to check size
            cbor_array = cbor2.dumps(message_array)
            
            # Phase 4.2: Check if message needs chunking
            if len(cbor_array) <= MAX_PACKET_SIZE:
                # Small message - send normally
                return self._send_packet(cbor_array, topic, sequence_id)
            else:
                # Large message - use chunking
                return self._send_chunked_message(topic, message_fields)
                
        except Exception as e:
            if self.debug:
                logger.debug(f"Failed to publish '{topic}': {e}")
            return False
    
    def _send_packet(self, packet: bytes, topic: str, sequence_id: int) -> bool:
        """Send a packet to interested peers"""
        if self.debug:
            print(f"→ {topic}: (seq={sequence_id}, {len(packet)} bytes)")
        
        # Send to interested peers - use discovery_lock for peer access
        sent_count = 0
        with self.discovery_lock:
            # Quick snapshot of interested peers to minimize lock time
            interested_peers = []
            for i, (peer_name, peer_info) in enumerate(self.peers.items()):
                if self._topic_matches_subscription(topic, peer_info.get('subscribed_topics', [])):
                    interested_peers.append((peer_info['ip'], peer_info['port'], peer_name))
                
                # Yield GIL periodically during long peer lists
                if i % 5 == 0 and i > 0:
                    time.sleep(0)  # Explicit GIL release
        
        # Send to peers without holding any locks (I/O operations release GIL naturally)
        for ip, port, peer_name in interested_peers:
            try:
                self.message_socket.sendto(packet, (ip, port))
                sent_count += 1
            except Exception as e:
                if self.debug:
                    logger.debug(f"Failed to send to {peer_name}: {e}")
        
        if self.debug and sent_count == 0:
            logger.debug(f"📤 Published '{topic}' but no interested peers found")
        return True
    
    def _send_chunked_message(self, topic: str, fields: List[Any]) -> bool:
        """Phase 4.2: Send large message as chunks"""
        try:
            # Serialize the payload to get raw data for chunking
            payload_cbor = cbor2.dumps(fields)
            
            # Calculate number of chunks needed
            total_chunks = (len(payload_cbor) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE
            
            if self.debug:
                print(f"🔗 Chunking large message: {len(payload_cbor)} bytes into {total_chunks} chunks")
            
            all_sent = True
            
            # Send each chunk with consecutive sequence numbers
            for i in range(total_chunks):
                with self.message_lock:
                    self.increment_counter = (self.increment_counter + 1) % 65536
                    seq = self.increment_counter
                
                # Calculate chunk boundaries
                start = i * MAX_CHUNK_SIZE
                end = min(start + MAX_CHUNK_SIZE, len(payload_cbor))
                chunk_data = payload_cbor[start:end]
                
                # Create chunk message: [seq, topic, type, chunk_data]
                msg_type = 2 if i == total_chunks - 1 else 1  # type 2 for final, type 1 for more
                chunk_message = [seq, topic, msg_type, chunk_data]
                
                # Send chunk
                cbor_chunk = cbor2.dumps(chunk_message)
                sent = self._send_packet(cbor_chunk, topic, seq)
                
                if not sent:
                    all_sent = False
                
                if self.debug:
                    print(f"🔗 Sent chunk {i + 1}/{total_chunks} (seq={seq}, type={msg_type}, {len(chunk_data)} bytes)", file=sys.stderr)
            
            return all_sent
            
        except Exception as e:
            if self.debug:
                logger.debug(f"Failed to send chunked message: {e}")
            return False
    
    def subscribe(self, topic_pattern: str, callback: Callable[[List[Any], List[Any]], None]) -> bool:
        """Subscribe with clean API: callback(header, msg) where header=[inc,topic,meta], msg=[field1,field2,...]"""
        if self._is_wildcard(topic_pattern):
            # Store as wildcard subscription
            self.wildcard_subscribers.append((topic_pattern, callback))
            if self.debug:
                logger.info(f"📥 Subscribed to wildcard: '{topic_pattern}'")
        else:
            # Store as exact subscription
            if topic_pattern not in self.exact_subscribers:
                self.exact_subscribers[topic_pattern] = []
            self.exact_subscribers[topic_pattern].append(callback)
            if self.debug:
                logger.info(f"📥 Subscribed to exact: '{topic_pattern}'")
        return True
    
    def _is_wildcard(self, pattern: str) -> bool:
        """Check if pattern contains wildcard characters"""
        return '*' in pattern
    
    def _topic_matches_subscription(self, topic: str, subscriptions: list) -> bool:
        """Check if topic matches any subscription pattern"""
        for sub in subscriptions:
            if sub == topic:
                return True
            # Simple * wildcard matching
            if '*' in sub:
                if self._simple_wildcard_match(topic, sub):
                    return True
        return False
    
    def _simple_wildcard_match(self, topic: str, pattern: str) -> bool:
        """Simple * wildcard matching - efficient for ESP32"""
        if pattern == "*":
            return "/" not in topic  # Match single-level topics only
        
        # Split by / and match each level
        topic_parts = topic.split('/')
        pattern_parts = pattern.split('/')
        
        if len(topic_parts) != len(pattern_parts):
            return False
        
        for topic_part, pattern_part in zip(topic_parts, pattern_parts):
            if pattern_part == "*":
                continue  # * matches anything
            if pattern_part != topic_part:
                return False
        
        return True
    
    
    def _announce_loop(self):
        """Announce this node periodically with adaptive timing"""
        sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sender_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        while self.running:
            try:
                current_time = time.time()
                
                # Adaptive discovery: faster when no peers, slower when stable
                if len(self.peers) == 0:
                    interval = ANNOUNCE_INTERVAL_1  # Fast discovery when isolated
                elif len(self.peers) < 3:
                    interval = ANNOUNCE_INTERVAL_2  # Medium when few peers
                elif len(self.peers) < 10:
                    interval = ANNOUNCE_INTERVAL_3  # Medium when few peers
                else:
                    interval = ANNOUNCE_INTERVAL_4  # Slow when many peers
                
                if current_time - self._last_discovery_send >= interval:
                    # Create announcement - include both exact and wildcard subscriptions
                    all_subscriptions = list(self.exact_subscribers.keys())
                    for pattern, _ in self.wildcard_subscribers:
                        all_subscriptions.append(pattern)
                    
                    # OPTIMIZED: New efficient array format [node_name, port, subscribed_topics, published_topics]
                    # 50% smaller than object format, 3x faster to parse
                    announcement = [
                        self.node_name,
                        self.message_port, 
                        all_subscriptions,
                        list(self.published_topics)
                    ]
                    
                    # Encode as CBOR
                    announcement_bytes = cbor2.dumps(announcement)
                    
                    # Send to multicast group
                    sender_socket.sendto(announcement_bytes, (DISCOVERY_MULTICAST, DISCOVERY_PORT))
                    
                    # Also send to localhost for same-machine discovery
                    sender_socket.sendto(announcement_bytes, ("127.0.0.1", DISCOVERY_PORT))
                    
                    self._last_discovery_send = current_time
                    
                    if self.debug:
                        logger.info(f"📢 Discovery sent (interval: {interval}s)")
                
                # Clean up old peers
                self._cleanup_old_peers()
                
                time.sleep(1.0)  # Check every second, but send based on interval
                
            except Exception as e:
                if self.running and self.debug:
                    logger.info(f"Announce error: {e}")
                    
                # FALLBACK: If multicast fails, try broadcast for local network
                if "No route to host" in str(e) or "Network is unreachable" in str(e):
                    try:
                        # Create announcement for fallback
                        all_subscriptions = list(self.exact_subscribers.keys())
                        for pattern, _ in self.wildcard_subscribers:
                            all_subscriptions.append(pattern)
                        
                        # OPTIMIZED: New efficient array format [node_name, port, subscribed_topics, published_topics]
                        announcement = [
                            self.node_name,
                            self.message_port,
                            all_subscriptions,
                            list(self.published_topics)
                        ]
                        
                        announcement_bytes = cbor2.dumps(announcement)
                        
                        # Try broadcast as fallback
                        fallback_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        fallback_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                        fallback_socket.sendto(announcement_bytes, ("255.255.255.255", DISCOVERY_PORT))
                        fallback_socket.close()
                        
                        self._last_discovery_send = time.time()
                        
                        if self.debug:
                            logger.info(f"📢 Discovery sent via broadcast fallback")
                    except Exception as fallback_e:
                        if self.debug:
                            logger.info(f"Broadcast fallback also failed: {fallback_e}")
        
        sender_socket.close()
    
    def _discovery_loop(self):
        """Listen for peer announcements"""
        while self.running:
            try:
                data, addr = self.discovery_socket.recvfrom(1024)
                
                try:
                    # Decode CBOR announcement
                    announcement = cbor2.loads(data)
                    
                    # New optimized array format: [node_name, port, subscribed_topics, published_topics]
                    if isinstance(announcement, list) and len(announcement) >= 4:
                        sender_node = announcement[0]
                        
                        # Ignore our own announcements
                        if sender_node != self.node_name:
                            self._process_peer_announcement(announcement, addr[0])
                    else:
                        if self.debug:
                            logger.info(f"Invalid announcement format from {addr[0]} - expected 4-element array")
                        
                except Exception as e:
                    if self.debug:
                        logger.info(f"Failed to parse announcement from {addr[0]}: {e}")
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running and self.debug:
                    logger.info(f"Discovery error: {e}")
    
    def _process_peer_announcement(self, announcement, ip: str):
        """GIL-optimized: Process peer announcement with minimal lock duration"""
        # Parse data outside locks (minimal GIL time)
        node_name = announcement[0]
        port = announcement[1] 
        subscribed_topics = announcement[2]
        published_topics = announcement[3]
        
        if not node_name or not port:
            return
        
        # Pre-compute expensive operations outside lock
        current_time = time.time()  # System call outside lock
        
        with self.discovery_lock:
            # Remove old peer by name (O(1), minimal GIL time)
            if node_name in self.peers:
                del self.peers[node_name]
            
            # Single-pass removal by IP+port with GIL yields
            peers_to_remove = []
            for i, (peer_name, peer_info) in enumerate(self.peers.items()):
                if peer_info.get('ip') == ip and peer_info.get('port') == port:
                    peers_to_remove.append(peer_name)
                
                # Yield GIL every few iterations to allow message thread to run
                if i % 3 == 0 and i > 0:
                    time.sleep(0)  # Explicit GIL release
            
            # Remove conflicts (minimal GIL time per deletion)
            for peer_name in peers_to_remove:
                if peer_name in self.peers:  # Double-check for thread safety
                    del self.peers[peer_name]
            
            # Add new peer entry (pre-computed data)
            self.peers[node_name] = {
                'ip': ip,
                'port': port,
                'subscribed_topics': subscribed_topics,
                'published_topics': published_topics,
                'last_seen': current_time,  # Pre-computed
                'is_manual': False
            }
        
        # Debug logging outside lock (I/O naturally releases GIL)
        if self.debug:
            logger.info(f"🔄 Rebuilt peer: {node_name} at {ip}:{port} with {len(subscribed_topics)} subscriptions, {len(published_topics)} publications")
    
    
    def _message_loop(self):
        """SIMPLIFIED: Listen for incoming messages - no duplicate checking"""
        while self.running:
            try:
                packet, addr = self.message_socket.recvfrom(MAX_PACKET_SIZE)
                
                if len(packet) < 1:
                    continue
                
                try:
                    # Phase 4.2: Parse message with type field support
                    message_array = cbor2.loads(packet)
                    
                    # Validate array structure: minimum [sequence_id, topic, type]
                    if not isinstance(message_array, list) or len(message_array) < 3:
                        if self.debug:
                            logger.debug(f"Invalid array from {addr}: expected list with >=3 elements")
                        continue
                    
                    # Extract protocol fields
                    sequence_id = message_array[0]
                    topic = message_array[1]
                    msg_type = message_array[2]
                    
                    if msg_type == 0:
                        # Normal message - deliver immediately
                        payload = message_array[3] if len(message_array) > 3 else []
                        
                        # Create header: [sequence_id, topic, type] 
                        header = [sequence_id, topic, msg_type]
                        
                        if self.debug:
                            print(f"🔥 {topic}: {payload}", file=sys.stderr)
                        
                        # Dispatch to matching subscribers
                        self._dispatch_message(topic, header, payload)
                        
                    elif msg_type == 1 or msg_type == 2:
                        # Phase 4.2: Chunked message (type 1 = more chunks, type 2 = final chunk)
                        if len(message_array) > 3:
                            chunk_data = message_array[3]
                            self._handle_chunk_packet(sequence_id, topic, msg_type, chunk_data, addr[0])
                            
                    # Cleanup stale chunks periodically
                    current_time = time.time()
                    if current_time - self.last_chunk_cleanup > 10:  # Every 10 seconds
                        self._cleanup_stale_chunks()
                        self.last_chunk_cleanup = current_time
                                
                except Exception as e:
                    if self.debug:
                        logger.debug(f"Failed to parse CBOR array from {addr}: {e}")
                    
            except socket.timeout:
                continue
            except Exception as e:
                if self.running and self.debug:
                    logger.debug(f"Message receive error: {e}")
    
    def _cleanup_old_peers(self):
        """GIL-optimized: Remove stale peers with minimal lock duration"""
        current_time = time.time()
        with self.discovery_lock:
            stale_peers = []
            for i, (name, peer) in enumerate(self.peers.items()):
                # Only timeout discovered peers, not manual peers
                if not peer.get('is_manual', False) and current_time - peer['last_seen'] > NODE_TIMEOUT:
                    stale_peers.append(name)
                
                # Yield GIL periodically during long peer lists
                if i % 5 == 0 and i > 0:
                    time.sleep(0)  # Explicit GIL release
                    
            for name in stale_peers:
                if name in self.peers:  # Double-check for thread safety
                    del self.peers[name]
        
        # Debug logging outside lock (I/O releases GIL naturally)
        if self.debug and stale_peers:
            for name in stale_peers:
                logger.info(f"🗑️ Removed stale peer: {name}")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def run(self, blocking: bool = True):
        """Start the UDP bus"""
        if not self.begin():
            return False
            
        self.running = True
        
        # Start background threads - Phase 4.3: Only start discovery threads if enabled
        self.threads = [threading.Thread(target=self._message_loop, daemon=True)]
        
        if self.enable_discovery:
            self.threads.extend([
                threading.Thread(target=self._announce_loop, daemon=True),
                threading.Thread(target=self._discovery_loop, daemon=True)
            ])
        
        for t in self.threads:
            t.start()
        
        # Brief startup delay
        time.sleep(0.5)
        
        if self.debug:
            logger.info(f"🔥 UDPBus '{self.node_name}' running")
        
        if blocking:
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
        
        return True
    
    def loop(self):
        """Non-blocking loop for Arduino-style usage"""
        if not self.running:
            self.run(blocking=False)
            time.sleep(0.1)
    
    def stop(self):
        """Stop the UDP bus"""
        if self.debug:
            logger.info(f"🛑 Stopping UDPBus '{self.node_name}'...")
        self.running = False
        
        # Close sockets
        if self.discovery_socket:
            self.discovery_socket.close()
        if self.message_socket:
            self.message_socket.close()
            
        if self.debug:
            logger.info("✅ UDPBus stopped")
    
    def get_peers(self) -> Dict[str, Dict]:
        """Get discovered peers (for debugging)"""
        with self.discovery_lock:
            return self.peers.copy()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bus statistics"""
        # Use both locks to get consistent snapshot
        with self.message_lock:
            increment = self.increment_counter
            topics_published = len(self.published_topics)
            topics_subscribed = len(self.exact_subscribers)
        
        with self.discovery_lock:
            peers_discovered = len(self.peers)
        
        return {
            "node_name": self.node_name,
            "peers_discovered": peers_discovered,
            "topics_published": topics_published,
            "topics_subscribed": topics_subscribed,
            "increment": increment,
            "running": self.running
        }
    
    # Phase 4.3: Manual peer management methods
    
    def add_peer(self, ip: str, port: int, subscribed_topics: List[str]):
        """Add a manual peer with specified subscribed topics"""
        # Pre-compute outside lock
        current_time = time.time()
        peer_name = f"manual_{ip}_{port}"
        
        with self.discovery_lock:
            self.peers[peer_name] = {
                'ip': ip,
                'port': port,
                'subscribed_topics': subscribed_topics,
                'last_seen': current_time,  # Pre-computed
                'is_manual': True
            }
        
        # Debug logging outside lock
        if self.debug:
            logger.info(f"📌 Added manual peer: {ip}:{port} - {subscribed_topics}")
    
    def remove_peer(self, ip: str):
        """Remove a manual peer by IP address"""
        with self.discovery_lock:
            peers_to_remove = []
            for i, (peer_name, peer_info) in enumerate(self.peers.items()):
                if peer_info['ip'] == ip and peer_info.get('is_manual', False):
                    peers_to_remove.append(peer_name)
                
                # Yield GIL periodically
                if i % 5 == 0 and i > 0:
                    time.sleep(0)
            
            for peer_name in peers_to_remove:
                if peer_name in self.peers:  # Double-check for thread safety
                    del self.peers[peer_name]
        
        # Debug logging outside lock
        if self.debug and peers_to_remove:
            logger.info(f"🗑️ Removed manual peer: {ip}")
    
    def set_discovery_mode(self, enabled: bool):
        """Enable or disable discovery mode"""
        self.enable_discovery = enabled
        
        if not enabled:
            # Clean up discovered peers when switching to manual mode
            with self.discovery_lock:
                discovered_peers = []
                for i, (peer_name, peer_info) in enumerate(self.peers.items()):
                    if not peer_info.get('is_manual', False):
                        discovered_peers.append(peer_name)
                    
                    # Yield GIL periodically
                    if i % 5 == 0 and i > 0:
                        time.sleep(0)
                
                for peer_name in discovered_peers:
                    if peer_name in self.peers:  # Double-check for thread safety
                        del self.peers[peer_name]
            
            # Debug logging outside lock
            if self.debug and discovered_peers:
                logger.info(f"🔄 Discovery disabled, removed {len(discovered_peers)} discovered peers")
        else:
            if self.debug:
                logger.info("🔄 Discovery enabled")
    
    @staticmethod
    def from_config(config_path: str) -> 'UDPBus':
        """Load UDPBus configuration from JSON file"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Extract configuration parameters
        node_name = config['node_name']
        debug = config.get('debug', False)
        enable_discovery = config.get('discovery_mode', True)
        manual_peers = config.get('manual_peers', [])
        
        # Create UDPBus instance with configuration
        return UDPBus(node_name, debug=debug, enable_discovery=enable_discovery, manual_peers=manual_peers)

    def _dispatch_message(self, topic: str, header: List[Any], payload: List[Any]):
        """Dispatch message to matching subscribers (exact and wildcard)"""
        # Fast path: exact matches O(1)
        if topic in self.exact_subscribers:
            for callback in self.exact_subscribers[topic]:
                try:
                    callback(header, payload)
                except Exception as e:
                    logger.error(f"Callback error for exact topic '{topic}': {e}")
        
        # Wildcard matches O(n) - only check if wildcards exist
        for pattern, callback in self.wildcard_subscribers:
            try:
                if self._simple_wildcard_match(topic, pattern):
                    callback(header, payload)
            except Exception as e:
                logger.error(f"Callback error for wildcard '{pattern}': {e}")

    def _handle_chunk_packet(self, seq: int, topic: str, msg_type: int, chunk_data: bytes, sender_ip: str):
        """Phase 4.2: Handle chunked message packet"""
        # Use sender_ip:topic as key to avoid topic interference
        collection_key = f"{sender_ip}:{topic}"
        
        # Get or create chunk collection for this sender+topic
        if collection_key not in self.active_chunks:
            self.active_chunks[collection_key] = {
                'topic': topic,
                'expected_seq': seq,
                'chunks': [],
                'start_time': time.time()
            }
        
        collection = self.active_chunks[collection_key]
        
        # Check if this is a new chunk sequence (sequence gap indicates new message)
        if not collection['chunks'] or seq != collection['expected_seq']:
            # Start new chunk collection, drop any previous incomplete collection
            if collection['chunks'] and self.debug:
                print(f"🔗 Dropping incomplete chunked message from {sender_ip} topic {topic} "
                      f"(expected seq {collection['expected_seq']}, got {seq})", file=sys.stderr)
            
            collection.update({
                'topic': topic,
                'expected_seq': seq,
                'chunks': [],
                'start_time': time.time()
            })
        
        # Basic duplicate detection
        if seq < collection['expected_seq']:
            if self.debug:
                print(f"🔗 Ignoring duplicate/out-of-order chunk from {sender_ip} topic {topic} "
                      f"(seq={seq}, expected={collection['expected_seq']})", file=sys.stderr)
            return
        
        # Add this chunk
        collection['chunks'].append(chunk_data)
        collection['expected_seq'] = seq + 1
        
        if self.debug:
            print(f"🔗 Received chunk {len(collection['chunks'])} from {sender_ip} "
                  f"(seq={seq}, type={msg_type})", file=sys.stderr)
        
        # If this is the final chunk (type 2), reassemble and deliver
        if msg_type == 2:
            try:
                # Calculate total size before reassembling
                total_size = sum(len(chunk) for chunk in collection['chunks'])
                
                # Check size limit to prevent memory exhaustion
                if total_size > MAX_REASSEMBLED_SIZE:
                    if self.debug:
                        print(f"🔗 Reassembled message too large: {total_size} bytes "
                              f"(limit: {MAX_REASSEMBLED_SIZE})", file=sys.stderr)
                    del self.active_chunks[collection_key]
                    return
                
                # Reassemble all chunks
                complete_payload = b''.join(collection['chunks'])
                
                # Parse the reassembled payload
                payload = cbor2.loads(complete_payload)
                
                # Create header for the complete message (use first sequence number, type 0)
                first_seq = seq - (len(collection['chunks']) - 1)
                header = [first_seq, topic, 0]
                
                # Clear the chunk collection
                del self.active_chunks[collection_key]
                
                if self.debug:
                    print(f"🔗 Reassembled and delivering chunked message: {topic} "
                          f"({len(complete_payload)} bytes, {len(collection['chunks'])} chunks)", file=sys.stderr)
                
                # Dispatch the complete message
                self._dispatch_message(topic, header, payload)
                
            except Exception as e:
                if self.debug:
                    logger.debug(f"Failed to reassemble chunked message: {e}")
                if collection_key in self.active_chunks:
                    del self.active_chunks[collection_key]

    def _cleanup_stale_chunks(self):
        """Phase 4.2: Remove incomplete chunk collections that have timed out"""
        current_time = time.time()
        stale_senders = []
        
        for collection_key, collection in self.active_chunks.items():
            age = current_time - collection['start_time']
            if age > CHUNK_TIMEOUT_SECONDS:
                stale_senders.append(collection_key)
        
        for collection_key in stale_senders:
            if self.debug:
                print(f"🔗 Cleaning up stale chunk collection: {collection_key} "
                      f"(age={current_time - self.active_chunks[collection_key]['start_time']:.1f}s)", file=sys.stderr)
            del self.active_chunks[collection_key]

# Convenience factory function
def create(node_name: str) -> UDPBus:
    """Create a UDPBus instance"""
    return UDPBus(node_name) 