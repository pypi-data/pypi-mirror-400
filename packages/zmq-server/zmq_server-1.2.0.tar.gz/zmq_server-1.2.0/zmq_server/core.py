import zmq
import json
from loguru import logger
import time
import threading
from typing import Dict, Any, Optional, Callable, Set, List
from collections import defaultdict
from datetime import datetime

logger.add("logs/zmq_{time:YYYY-MM-DD}.log", rotation="00:00", retention="7 days")

class TopicManager:
    def __init__(self):
        self._topics: Dict[str, Set[bytes]] = defaultdict(set)
        self._client_topics: Dict[bytes, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()

    def subscribe(self, client_id: bytes, topic: str) -> bool:
        with self._lock:
            self._topics[topic].add(client_id)
            self._client_topics[client_id].add(topic)
            logger.info(f"客户端订阅主题: {topic}")
            return True

    def unsubscribe(self, client_id: bytes, topic: str) -> bool:
        with self._lock:
            if topic in self._topics:
                self._topics[topic].discard(client_id)
                if not self._topics[topic]:
                    del self._topics[topic]
            if client_id in self._client_topics:
                self._client_topics[client_id].discard(topic)
                if not self._client_topics[client_id]:
                    del self._client_topics[client_id]
            logger.info(f"客户端取消订阅主题: {topic}")
            return True

    def publish(self, topic: str, message: Any) -> List[bytes]:
        with self._lock:
            subscribers = self._topics.get(topic, set())
            logger.debug(f"主题 {topic} 有 {len(subscribers)} 个订阅者")
            return list(subscribers)

    def get_client_topics(self, client_id: bytes) -> Set[str]:
        with self._lock:
            return self._client_topics.get(client_id, set()).copy()

    def get_topic_subscribers(self, topic: str) -> Set[bytes]:
        with self._lock:
            return self._topics.get(topic, set()).copy()

    def remove_client(self, client_id: bytes):
        with self._lock:
            topics = self.get_client_topics(client_id)
            for topic in topics:
                self._topics[topic].discard(client_id)
                if not self._topics[topic]:
                    del self._topics[topic]
            if client_id in self._client_topics:
                del self._client_topics[client_id]
            logger.info("客户端已从Topic管理器中移除")

class ZMQServer:
    def __init__(self, host: str = "*", port: int = 5555, users: Dict[str, str] = None, heartbeat_interval: int = 30,
                 client_timeout: int = 60):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.host = host
        self.port = port

        self.users: Dict[str, str] = users.copy() if users else {}
        self.connected_clients: Dict[bytes, str] = {}
        self.client_last_active: Dict[bytes, float] = {}
        self.client_ids: Dict[str, bytes] = {}  # 客户端ID到身份的映射

        self.topic_manager = TopicManager()

        self.heartbeat_interval = heartbeat_interval
        self.client_timeout = client_timeout
        self.running = False
        self.heartbeat_thread: Optional[threading.Thread] = None

        self.custom_handlers: Dict[str, Callable] = {}

        self._setup_default_handlers()

    def add_user(self, username: str, password: str):
        self.users[username] = password

    def _setup_default_handlers(self):
        self.custom_handlers = {
            "auth": self._handle_auth,
            "subscribe": self._handle_subscribe,
            "unsubscribe": self._handle_unsubscribe,
            "publish": self._handle_publish,
            "heartbeat_response": self._handle_heartbeat_response,
        }

    def register_handler(self, message_type: str, handler: Callable):
        self.custom_handlers[message_type] = handler

    def authenticate(self, username: str, password: str) -> bool:
        return username in self.users and self.users[username] == password

    def _update_client_active_time(self, identity: bytes):
        self.client_last_active[identity] = time.time()

    def _check_timeout_clients(self):
        current_time = time.time()
        timeout_clients = []

        for client_id, last_active in self.client_last_active.items():
            if current_time - last_active > self.client_timeout:
                timeout_clients.append(client_id)

        for client_id in timeout_clients:
            username = self.connected_clients.get(client_id, "未知")
            del self.connected_clients[client_id]
            del self.client_last_active[client_id]
            self.topic_manager.remove_client(client_id)
            
            # 从 client_ids 中移除
            client_id_str = None
            for cid, ident in list(self.client_ids.items()):
                if ident == client_id:
                    client_id_str = cid
                    del self.client_ids[cid]
                    break
            
            if client_id_str:
                logger.warning(f"客户端 {username} (ID: {client_id_str}) 超时断开连接")
            else:
                logger.warning(f"客户端 {username} 超时断开连接")

    def _send_heartbeat(self):
        current_time = time.time()
        heartbeat_msg = {
            "type": "heartbeat",
            "timestamp": current_time
        }

        for client_id in list(self.connected_clients.keys()):
            try:
                self.socket.send(client_id, zmq.SNDMORE)
                self.socket.send(b"", zmq.SNDMORE)
                self.socket.send_json(heartbeat_msg)
                logger.debug(f"发送心跳给客户端")
            except Exception as e:
                logger.error(f"发送心跳时出错: {str(e)}")

    def _heartbeat_worker(self):
        while self.running:
            time.sleep(self.heartbeat_interval)
            if self.running:
                self._check_timeout_clients()
                self._send_heartbeat()

    def _get_client_id_str(self, identity: bytes) -> str:
        try:
            # 尝试解码为UTF-8字符串
            client_id = identity.decode('utf-8')
            # 移除可能的控制字符和无效字符
            client_id = ''.join(c for c in client_id if c.isprintable())
            if client_id:
                return client_id
            return f"client-{hash(identity) % 10000}"
        except UnicodeDecodeError:
            # 对于无法解码的二进制数据，使用哈希值作为客户端ID
            return f"client-{hash(identity) % 10000}"

    def _handle_auth(self, identity: bytes, message: Dict[str, Any]) -> Dict[str, Any]:
        username = message.get("username", "")
        password = message.get("password", "")
        
        client_id_str = self._get_client_id_str(identity)
        logger.info(f"收到认证请求 - 客户端ID: {client_id_str}, 用户名: {username}")
        
        # 检查客户端ID是否已在线
        if client_id_str in self.client_ids:
            logger.warning(f"客户端ID {client_id_str} 已在线")
            return {
                "type": "auth_response",
                "status": "failed",
                "message": f"认证失败：客户端ID {client_id_str} 已在线"
            }
        
        if self.authenticate(username, password):
            self.connected_clients[identity] = username
            self._update_client_active_time(identity)
            self.client_ids[client_id_str] = identity
            
            # 获取在线客户端列表
            online_clients = []
            for client_id, ident in self.client_ids.items():
                online_clients.append({
                    "client_id": client_id,
                    "username": self.connected_clients.get(ident, "未知")
                })
            
            logger.success(f"客户端 {username} 认证成功 - 客户端ID: {client_id_str}")
            logger.info(f"当前在线客户端: {len(online_clients)}")
            
            return {
                "type": "auth_response",
                "status": "success",
                "message": "认证成功",
                "online_clients": online_clients
            }
        else:
            logger.warning(f"客户端认证失败 - 客户端ID: {client_id_str}, 用户名: {username}")
            return {
                "type": "auth_response",
                "status": "failed",
                "message": "认证失败：用户名或密码错误"
            }

    def _handle_subscribe(self, identity: bytes, message: Dict[str, Any]) -> Dict[str, Any]:
        if identity not in self.connected_clients:
            return {
                "type": "error",
                "message": "未认证，请先进行认证"
            }
        
        self._update_client_active_time(identity)
        topic = message.get("topic", "")
        
        if not topic:
            return {
                "type": "subscribe_response",
                "status": "failed",
                "message": "主题不能为空"
            }
        
        self.topic_manager.subscribe(identity, topic)
        username = self.connected_clients[identity]
        logger.info(f"客户端 {username} 订阅主题: {topic}")
        
        return {
            "type": "subscribe_response",
            "status": "success",
            "message": f"订阅主题 {topic} 成功",
            "topic": topic
        }

    def _handle_unsubscribe(self, identity: bytes, message: Dict[str, Any]) -> Dict[str, Any]:
        if identity not in self.connected_clients:
            return {
                "type": "error",
                "message": "未认证，请先进行认证"
            }
        
        self._update_client_active_time(identity)
        topic = message.get("topic", "")
        
        if not topic:
            return {
                "type": "unsubscribe_response",
                "status": "failed",
                "message": "主题不能为空"
            }
        
        self.topic_manager.unsubscribe(identity, topic)
        username = self.connected_clients[identity]
        logger.info(f"客户端 {username} 取消订阅主题: {topic}")
        
        return {
            "type": "unsubscribe_response",
            "status": "success",
            "message": f"取消订阅主题 {topic} 成功",
            "topic": topic
        }

    def _handle_publish(self, identity: bytes, message: Dict[str, Any]) -> Dict[str, Any]:
        if identity not in self.connected_clients:
            return {
                "type": "error",
                "message": "未认证，请先进行认证"
            }
        
        self._update_client_active_time(identity)
        topic = message.get("topic", "")
        content = message.get("content", "")
        username = self.connected_clients[identity]
        
        if not topic:
            return {
                "type": "publish_response",
                "status": "failed",
                "message": "主题不能为空"
            }
        
        subscribers = self.topic_manager.get_topic_subscribers(topic)
        
        if not subscribers:
            return {
                "type": "publish_response",
                "status": "success",
                "message": f"消息已发布到主题 {topic}，无订阅者",
                "topic": topic,
                "subscriber_count": 0
            }
        
        broadcast_msg = {
            "type": "message",
            "topic": topic,
            "from": username,
            "content": content,
            "timestamp": time.time()
        }
        
        sent_count = 0
        for subscriber_id in subscribers:
            try:
                self.socket.send(subscriber_id, zmq.SNDMORE)
                self.socket.send(b"", zmq.SNDMORE)
                self.socket.send_json(broadcast_msg)
                sent_count += 1
            except Exception as e:
                logger.error(f"发送消息给订阅者时出错: {str(e)}")
        
        return {
            "type": "publish_response",
            "status": "success",
            "message": f"消息已发布到主题 {topic}",
            "topic": topic,
            "subscriber_count": len(subscribers),
            "sent_count": sent_count
        }

    def _handle_heartbeat_response(self, identity: bytes, message: Dict[str, Any]):
        if identity in self.connected_clients:
            self._update_client_active_time(identity)
            logger.debug(f"收到心跳响应")

    def _handle_message(self, identity: bytes, message: Dict[str, Any]):
        message_type = message.get("type", "")
        
        handler = self.custom_handlers.get(message_type)
        if handler:
            response = handler(identity, message)
            
            if response:
                try:
                    self.socket.send(identity, zmq.SNDMORE)
                    self.socket.send(b"", zmq.SNDMORE)
                    self.socket.send_json(response)
                except Exception as e:
                    logger.error(f"发送响应时出错: {str(e)}")
        else:
            logger.warning(f"未知消息类型: {message_type}")

    def start(self):
        self.socket.bind(f"tcp://{self.host}:{self.port}")
        logger.success(f"服务端已启动，监听地址: tcp://{self.host}:{self.port}")

        if self.users:
            logger.info(f"已配置 {len(self.users)} 个用户")

        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)

        logger.info("等待客户端连接...")
        logger.info(f"心跳间隔: {self.heartbeat_interval}秒, 超时时间: {self.client_timeout}秒")

        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()

        while self.running:
            try:
                socks = dict(poller.poll(1000))
                
                if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                    try:
                        identity = self.socket.recv()
                        raw_message = self.socket.recv()
                        message = json.loads(raw_message.decode('utf-8'))
                        
                        self._handle_message(identity, message)
                        
                    except json.JSONDecodeError:
                        logger.error("收到无效的JSON消息")
                    except Exception as e:
                        logger.error(f"处理消息时发生错误: {str(e)}")
                        
            except KeyboardInterrupt:
                logger.info("正在关闭服务端...")
                self.running = False
                break
            except Exception as e:
                logger.error(f"服务端发生错误: {str(e)}")
        
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
        
        self.socket.close()
        self.context.term()
        logger.success("服务端已关闭")

    def stop(self):
        logger.info("正在停止服务端...")
        self.running = False

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "connected_clients": len(self.connected_clients),
            "topic_statistics": {"total_topics": len(self.topic_manager._topics)}
        }

class ZMQClient:
    def __init__(self, client_id: str, server_host: str = "localhost", server_port: int = 5555):
        # 检查客户端id不能超过8位
        if len(client_id) > 8:
            raise ValueError("客户端ID不能超过8位")
        logger.info(f"正在初始化客户端 {client_id}...")
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.DEALER)
        self.server_host = server_host
        self.server_port = server_port
        self.client_id = client_id

        if client_id:
            self.socket.setsockopt_string(zmq.IDENTITY, client_id)
            logger.info(f"客户端ID已设置: {client_id}")

        self.authenticated = False
        self.username = ""

        self.subscribed_topics: List[str] = []

        self.running = False
        self.receive_thread: Optional[threading.Thread] = None

        self.message_handlers: Dict[str, Callable] = {}
        self.default_handler: Optional[Callable] = None

        self._setup_default_handlers()

    def _setup_default_handlers(self):
        self.message_handlers = {
            "message": self._handle_message,
            "heartbeat": self._handle_heartbeat,
            "auth_response": self._handle_auth_response,
            "subscribe_response": self._handle_subscribe_response,
            "unsubscribe_response": self._handle_unsubscribe_response,
            "publish_response": self._handle_publish_response,
            "error": self._handle_error,
        }

    def register_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], None]):
        self.message_handlers[message_type] = handler

    def set_default_handler(self, handler: Callable[[Dict[str, Any]], None]):
        self.default_handler = handler

    def connect(self):
        self.socket.connect(f"tcp://{self.server_host}:{self.server_port}")
        logger.info(f"正在连接到服务器: tcp://{self.server_host}:{self.server_port}")

    def authenticate(self, username: str, password: str) -> bool:
        auth_message = {
            "type": "auth",
            "username": username,
            "password": password
        }
        
        logger.info(f"发送认证请求 - 用户名: {username}")
        self.socket.send_json(auth_message)
        
        try:
            frames = self.socket.recv_multipart()
            response = json.loads(frames[-1].decode('utf-8'))
            
            if response.get("type") == "auth_response":
                if response.get("status") == "success":
                    self.authenticated = True
                    self.username = username
                    logger.success(f"认证成功: {response.get('message')}")
                    return True
                else:
                    logger.error(f"认证失败: {response.get('message')}")
                    return False
        except Exception as e:
            logger.error(f"认证过程中发生错误: {str(e)}")
            return False

    def subscribe(self, topic: str) -> bool:
        if not self.authenticated:
            logger.error("未认证，无法订阅主题")
            return False
        
        subscribe_message = {
            "type": "subscribe",
            "topic": topic
        }
        
        logger.info(f"订阅主题: {topic}")
        self.socket.send_json(subscribe_message)
        
        try:
            frames = self.socket.recv_multipart()
            response = json.loads(frames[-1].decode('utf-8'))
            
            if response.get("type") == "subscribe_response":
                if response.get("status") == "success":
                    if topic not in self.subscribed_topics:
                        self.subscribed_topics.append(topic)
                    logger.success(f"订阅主题 {topic} 成功")
                    return True
                else:
                    logger.error(f"订阅主题失败: {response.get('message')}")
                    return False
        except Exception as e:
            logger.error(f"订阅主题时发生错误: {str(e)}")
            return False

    def unsubscribe(self, topic: str) -> bool:
        if not self.authenticated:
            logger.error("未认证，无法取消订阅主题")
            return False
        
        unsubscribe_message = {
            "type": "unsubscribe",
            "topic": topic
        }
        
        logger.info(f"取消订阅主题: {topic}")
        self.socket.send_json(unsubscribe_message)
        
        try:
            frames = self.socket.recv_multipart()
            response = json.loads(frames[-1].decode('utf-8'))
            
            if response.get("type") == "unsubscribe_response":
                if response.get("status") == "success":
                    if topic in self.subscribed_topics:
                        self.subscribed_topics.remove(topic)
                    logger.success(f"取消订阅主题 {topic} 成功")
                    return True
                else:
                    logger.error(f"取消订阅主题失败: {response.get('message')}")
                    return False
        except Exception as e:
            logger.error(f"取消订阅主题时发生错误: {str(e)}")
            return False

    def publish(self, topic: str, content: Any) -> bool:
        if not self.authenticated:
            logger.error("未认证，无法发布消息")
            return False
        
        publish_message = {
            "type": "publish",
            "topic": topic,
            "content": content
        }

        self.socket.send_json(publish_message)
        
        try:
            frames = self.socket.recv_multipart()
            response = json.loads(frames[-1].decode('utf-8'))
            
            if response.get("type") == "publish_response":
                if response.get("status") == "success":
                    return True
                else:
                    logger.error(f"发布消息失败: {response.get('message')}")
                    return False
        except Exception as e:
            logger.error(f"发布消息时发生错误: {str(e)}")
            return False

    def _handle_message(self, message: Dict[str, Any]):
        topic = message.get("topic", "未知")
        from_user = message.get("from", "未知")
        content = message.get("content", "")
        timestamp = message.get("timestamp", 0)
        
        time_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

    def _handle_heartbeat(self, message: Dict[str, Any]):
        heartbeat_response = {
            "type": "heartbeat_response",
            "timestamp": time.time()
        }
        self.socket.send_json(heartbeat_response)

    def _handle_auth_response(self, message: Dict[str, Any]):
        logger.info(f"认证响应: {message.get('message')}")

    def _handle_subscribe_response(self, message: Dict[str, Any]):
        logger.info(f"订阅响应: {message.get('message')}")

    def _handle_unsubscribe_response(self, message: Dict[str, Any]):
        logger.info(f"取消订阅响应: {message.get('message')}")

    def _handle_publish_response(self, message: Dict[str, Any]):
        logger.info(f"发布响应: {message.get('message')}")

    def _handle_error(self, message: Dict[str, Any]):
        logger.error(f"错误: {message.get('message')}")

    def _process_message(self, frames: List[bytes]):
        if len(frames) < 1:
            logger.warning("收到的消息帧数不足")
            return
        
        try:
            message = json.loads(frames[-1].decode('utf-8'))
            message_type = message.get("type", "")
            
            handler = self.message_handlers.get(message_type)
            if handler:
                handler(message)
            elif self.default_handler:
                self.default_handler(message)
            else:
                logger.debug(f"收到未处理的消息类型: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("收到无效的JSON消息")
        except Exception as e:
            logger.error(f"处理消息时发生错误: {str(e)}")

    def start_receiving(self):
        if not self.authenticated:
            logger.error("未认证，无法接收消息")
            return
        
        if self.running:
            logger.warning("已经在接收消息")
            return
        
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        logger.info("开始接收消息...")

    def _receive_loop(self):
        poller = zmq.Poller()
        poller.register(self.socket, zmq.POLLIN)
        
        try:
            while self.running:
                socks = dict(poller.poll(1000))
                
                if self.socket in socks and socks[self.socket] == zmq.POLLIN:
                    try:
                        frames = self.socket.recv_multipart()
                        self._process_message(frames)
                    except Exception as e:
                        logger.error(f"接收消息时发生错误: {str(e)}")
                        
        except Exception as e:
            logger.error(f"接收循环出错: {str(e)}")

    def stop_receiving(self):
        logger.info("停止接收消息...")
        self.running = False

    def get_subscribed_topics(self) -> List[str]:
        return self.subscribed_topics.copy()

    def is_authenticated(self) -> bool:
        return self.authenticated

    def close(self):
        logger.info("正在关闭客户端...")
        self.running = False
        
        if self.receive_thread:
            self.receive_thread.join(timeout=2)
        
        self.socket.close()
        self.context.term()
        logger.success("客户端已关闭")
