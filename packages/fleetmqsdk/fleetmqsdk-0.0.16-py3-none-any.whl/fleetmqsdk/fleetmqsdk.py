from . import Message_pb2
from .utils import _getAddress
from .logger import Logger
import threading
import time
import zmq
from google.protobuf.json_format import MessageToJson

MAX_PUBLISHER_RATE_HZ = 200 # Maximum publisher rate in hz
MIN_RATE_HZ = 20 # Minimum publisher rate in hz
SUBSCRIBER_BLOCK_TIME = 50 # Subscriber wait block time in ms
SUBSCRIBER_LINGER = 1000 # time in ms to try to send pending messages after closer
DEFAULT_LOGGING_PORT = "5550"
LOGGING_RATE_LIMIT_INTERVAL = 100 # Rate limit interval in ms
LOGGING_FLUSH_INTERVAL = 3.0 # Flush interval in seconds

class FleetMQMetric:
    def __init__(self, type, value, peer, timestamp):
        self.type = type
        self.value = value
        self.peer = peer
        self.timestamp = timestamp

class FleetMQ:
    def __init__(self, sendToDatastreamer=True, flushInterval=LOGGING_FLUSH_INTERVAL, rateLimitInterval=LOGGING_RATE_LIMIT_INTERVAL, port=DEFAULT_LOGGING_PORT, publisherRateHz=MAX_PUBLISHER_RATE_HZ):
        self._context = zmq.Context()
        self._logger = Logger(self._context, sendToDatastreamer, flushInterval, rateLimitInterval, port)
        self._logger.writeLine("FleetMQ SDK")
        self._rpcSocket = self._initRpcReq()
        self._pullSocket = self._initPull()
        self._publishers = {}
        self._subscribers = {}
        self._publisherRateHz = publisherRateHz

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._rpcSocket.close()
        self._pullSocket.close()
        for publisher in self._publishers.values():
            publisher.close()
        for subscriber in self._subscribers.values():
            subscriber.close()
        self._logger.close()

    def _initRpcReq(self, rpcReqPort="5558"):
        address = 'tcp://localhost:' + rpcReqPort
        try:
            rpcReqInterface = self._context.socket(zmq.REQ)
            rpcReqInterface.connect(address)
            self._logger.writeLine("Connected to RPC request address: {}", address)
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to open RPC request socket on port {}: {}", [rpcReqPort, e])
            exit(1)
        return rpcReqInterface  

    def _initPull(self, pullPort="5557"):
        address = 'tcp://*:' + pullPort
        try:
            pullInterface = self._context.socket(zmq.PULL)
            pullInterface.bind(address)
            self._logger.writeLine("Connected to pull socket on address: {}", address)
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to open pull socket on port {}: {}", [pullPort, e])
            exit(1)
        return pullInterface
    
    def _createPublisherFromConfig(self, port, topic, source_type, ipc=False):       
        if topic in self._publishers:
            self._logger.writeLine("Publisher for topic {} already exists", topic)
            return
        self._publishers[topic] = _Publisher(self._context, self._logger, port, topic, ipc, self._publisherRateHz)    
    
    def _createSubscriberFromConfig(self, port, topic, sink_type, ipc=False):
        if topic in self._subscribers:
            self._logger.writeLine("Subscriber for topic {} already exists", topic)
            return
        self._subscribers[topic] = _Subscriber(self._context, self._logger, port, topic, ipc)
    
    def _createConfigState(self, config, ports):
        for topic in config.send_topics:
            if topic not in ports:
                self._logger.writeLine("Error: send topic {} not found in ports, won't create publisher", topic)
                continue
            self._createPublisherFromConfig(ports[topic], topic, config.send_topics[topic].source.source)
        for topic in config.receive_topics:
            if topic not in ports:
                self._logger.writeLine("Error: receive topic {} not found in ports, won't create subscriber", topic)
                continue
            self._createSubscriberFromConfig(ports[topic], topic, config.receive_topics[topic].sink.sink)

    def _receiveConfig(self):
        try:
            configBytes = self._rpcSocket.recv_multipart()
            if len(configBytes) != 2:
                self._logger.writeLine("Error getting config from datastreamer, expected 2 frames, got {}", str(len(configBytes)))
                return None, None
            
            # Parse received config data into ABConnectMessage.
            msg = Message_pb2.ABConnectMessage()
            msg.ParseFromString(configBytes[0])

            # Evaluate the message type.
            if msg.HasField("device_config"):
                self._logger.writeLine("Received config response from datastreamer")
            elif msg.HasField("error"):            
                self._logger.writeLine("Received Error from datastreamer: {}", msg.error.error_message)
                return None, None
            else:
                self._logger.writeLine("Unexpected message type received from datastreamer: {}", msg)
                exit(1)

        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to receive config: {}", e)
            exit(1)

        
        portsString = configBytes[1].decode()
        self._logger.writeLine("Ports: {}", portsString)
        
        self._logger.writeLine("Device config: {}", [MessageToJson(msg.device_config, indent=None)])     

        return msg.device_config, eval(portsString)        

    def getConfig(self, createConfigState=False):
        req = Message_pb2.ABConnectMessage()
        req.config_request.SetInParent()
        self._logger.writeLine("Sending config request to datastreamer...")
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to receive config: {}", e)
            exit(1)

        # Wait for response
        config, addresses = self._receiveConfig()
        if config is None or addresses is None:
            self._logger.writeLine("Failed to get config from datastreamer")
            exit(1)

        if createConfigState:
            self._createConfigState(config, addresses)

        return config, addresses
    
    def pullMetric(self):
        try:
            metricBytes = self._pullSocket.recv_multipart()
            msg = Message_pb2.ABConnectMessage()
            msg.ParseFromString(metricBytes[0])

            if msg.HasField("metrics"):
                metrics = []
                for metric in msg.metrics.metrics:
                    value = metric.double_value if metric.double_value != 0 else metric.string_value
                    metrics.append(FleetMQMetric(Message_pb2.Metric.MetricType.Name(metric.type), value, msg.to, metric.timestamp))
                return metrics
            else:
                return None
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to receive metric: {}", e)
            return None
        except KeyboardInterrupt:
            return None

    # CreatePublisher creates a publisher for the given topic, executing an rpc to the datastreamer
    # to provision a zmq port.    
    def createPublisher(self, topic, source_type):    
        if topic in self._publishers:
            self._logger.writeLine("Publisher for topic {} already exists", topic)
            return        
             
        req = Message_pb2.ABConnectMessage()
        req.create_publisher.topic = topic
        req.create_publisher.source.source = source_type
        self._logger.writeLine("Sending create publisher request to datastreamer...")
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to send CreatePublisher request to datastreamer: {}", e)
            exit(1)

        config, ports = self._receiveConfig()
        if config is None or ports is None:
            self._logger.writeLine("Failed to create publisher")
            exit(1)
        self._createConfigState(config, ports)

        if topic not in self._publishers:
            self._logger.writeLine("Internal error, publisher for topic {} not created", topic)
            exit(1)
    
    # CreateSubscriber creates a subscriber for the given topic, executing an rpc to the
    # datastreamer to provision a zmq port.    
    def createSubscriber(self, topic, sink_type):
        if topic in self._subscribers:
            self._logger.writeLine("Subscriber for topic {} already exists", topic)
            return
        
        req = Message_pb2.ABConnectMessage()
        req.create_subscription.topic = topic
        req.create_subscription.sink.sink = sink_type
        self._logger.writeLine("Sending create subscriber request to datastreamer...")
        try:
            self._rpcSocket.send(req.SerializeToString())
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to send CreateSubscriber request to datastreamer: {}", e)
            exit(1)
        
        config, ports = self._receiveConfig()
        if config is None or ports is None:
            self._logger.writeLine("Failed to create subscriber")
            exit(1)
        self._createConfigState(config, ports)

        if topic not in self._subscribers:
            self._logger.writeLine("Internal error, subscriber for topic {} not created", topic)
            exit(1)    

    def publish(self, topic, data):
        if topic not in self._publishers:
            self._logger.writeLine("Publisher for topic {} does not exist", topic)
            return
        
        self._publishers[topic].publish(data)

    def publishBytes(self, topic, data):
        if topic not in self._publishers:
            self._logger.writeLine("Publisher for topic {} does not exist", topic)
            return
        
        self._publishers[topic].publishBytes(data)

    def receive(self, topic):
        if topic not in self._subscribers:
            self._logger.writeLine("Subscriber for topic {} does not exist", topic)
            return
        return self._subscribers[topic].receive()
    
    def receiveBytes(self, topic):
        if topic not in self._subscribers:
            self._logger.writeLine("Subscriber for topic {} does not exist", topic)
            return 
        return self._subscribers[topic].receiveBytes()

class _Publisher:
    def __init__(self, context, logger, port, topic, ipc=False, rate_hz=MAX_PUBLISHER_RATE_HZ):        
        self._topic = topic
        self._topicBytes = topic.encode()
        self._context = context
        self._publisherSocket = None
        self._logger = logger

        # Latest data and version tracking for rate limiting
        self._rate_hz = self._normalize_rate(rate_hz)
        self._latest_data = None
        self._latest_lock = threading.Lock()
        self._latest_version = 0
        self._last_sent_version = -1
        self._stop_event = threading.Event()
        self._startup_event = threading.Event()
        self._sender_error = None
        self._sender_thread = threading.Thread(target=self._send_loop, name=f"FleetMQPublisher-{topic}", daemon=True)
        self._address = _getAddress(port, ipc)
        self._sender_thread.start()
        self._startup_event.wait(timeout=1.0)
        if self._sender_error is not None:
            raise RuntimeError(self._sender_error)

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._stop_event.set()
        if self._sender_thread.is_alive():
            self._sender_thread.join(timeout=1.0)
    
    def publish(self, msg):
        self.publishBytes(msg.encode())
    
    def publishBytes(self, data):
        if self._sender_error is not None:
            raise RuntimeError(self._sender_error)
        with self._latest_lock:
            self._latest_data = data
            self._latest_version += 1

    def _send_loop(self):
        try:
            self._publisherSocket = self._context.socket(zmq.PUB)
            self._publisherSocket.setsockopt(zmq.SNDHWM, 1)
            self._publisherSocket.setsockopt(zmq.LINGER, 0)
            self._publisherSocket.bind(self._address)
            self._logger.writeLine("Bound to publish socket on address {} for topic {}", [self._address, self._topic])
            self._startup_event.set()
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to open publish socket on address {} error: {}", [self._address, e])
            self._sender_error = f"Publisher failed to bind on {self._address}: {e}"
            self._startup_event.set()
            return
        tick_interval = 1.0 / self._rate_hz
        next_tick = time.monotonic()
        last_sent_version = -1
        try:
            while not self._stop_event.is_set():
                now = time.monotonic()
                if now < next_tick:
                    time.sleep(next_tick - now)
                next_tick += tick_interval

                with self._latest_lock:
                    data = self._latest_data
                    ver = self._latest_version
                if data is None or ver == last_sent_version:
                    continue # Nothing new to send

                try:
                    self._publisherSocket.send_multipart([self._topicBytes, data], flags=zmq.NOBLOCK)
                    self._logger.writeRateLimited("Publishing bytes of length: {}", len(data))
                    last_sent_version = ver
                except zmq.Again:
                    self._logger.writeRateLimited("Dropping publish for topic {} due to backpressure", self._topic)
                except Exception as e:
                    self._logger.writeLine("Failed to publish bytes to topic {}: error: {}", [self._topic, e])
        finally:
            if self._publisherSocket is not None:
                self._publisherSocket.close()

    def _normalize_rate(self, rate_hz):
        try:
            rate_value = float(rate_hz)
        except (TypeError, ValueError):
            self._logger.writeLine("Invalid publisher rate {}, defaulting to {}Hz", rate_hz, MAX_PUBLISHER_RATE_HZ)
            rate_value = MAX_PUBLISHER_RATE_HZ
        if rate_value < MIN_RATE_HZ:
            self._logger.writeLine("Publisher rate {}Hz too low, clamping to {}Hz", rate_value, MIN_RATE_HZ)
            rate_value = MIN_RATE_HZ
        if rate_value > MAX_PUBLISHER_RATE_HZ:
            self._logger.writeLine("Publisher rate {}Hz too high, clamping to {}Hz", rate_value, MAX_PUBLISHER_RATE_HZ)
            rate_value = MAX_PUBLISHER_RATE_HZ
        return rate_value

class _Subscriber:
    def __init__(self, context, logger, port, topic, ipc=False):            
        self._topic = topic
        self._subscriberSocket = context.socket(zmq.SUB)
        self._subscriberSocket.RCVTIMEO = SUBSCRIBER_BLOCK_TIME
        self._subscriberSocket.LINGER = SUBSCRIBER_LINGER
        self._logger = logger
        address = _getAddress(port, ipc)
        try:
            self._subscriberSocket.connect(address)
            self._subscriberSocket.setsockopt(zmq.SUBSCRIBE, topic.encode())
            self._logger.writeLine("Bound to subscribe socket on address {} for topic {}", [address, topic])
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to open subscribe socket on address {} error: {}",[address, e])
            exit(1)    
        
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def close(self):
        self._subscriberSocket.close()

    def receive(self):
        msg = self.receiveBytes()
        return msg.decode() if msg is not None else None
            
    def receiveBytes(self):
        try:
            message = self._subscriberSocket.recv_multipart()
            if len(message) == 2:
                self._logger.writeRateLimited("Received message of length: {}", len(message[1]))
                return message[1]
            else:
                self._logger.writeLine("Received message of unexpected length: {}", len(message))
                return None
        except zmq.Again:
            return None
        except zmq.ZMQError as e:
            self._logger.writeLine("Failed to receive message: {}", e)
            return None
