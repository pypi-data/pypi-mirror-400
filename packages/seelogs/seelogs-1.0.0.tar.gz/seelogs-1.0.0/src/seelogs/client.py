import time
import threading
import signal
import atexit
from typing import Dict, Any, Optional, List
import requests

from .types import LogLevel, LogEvent, SeeLogsConfig
from .utils.utils import decode_base64

from .utils.system_info import get_system_info, get_full_system_info

class SeeLogs:
    """SeeLogs Python Client"""
    
    def __init__(self, config: SeeLogsConfig, enable_debug: bool = False):
        self.api_key = config['token']
        self.service = config.get('service', 'develop')
        self.endpoint = config.get('endpoint') or decode_base64("aHR0cHM6Ly9hcGkuc2VlbG9ncy5jb20=")
        
        self.batch_size = config.get('batch_size', 200)
        self.flush_interval = config.get('flush_interval', 1.0)
        self._enable_debug = enable_debug  # Renomeado para evitar conflito
        
        # Internal state
        self._buffer: List[LogEvent] = []
        self._buffer_lock = threading.RLock()
        self._is_server_online = True  # Assume online initially
        self._retry_count = 0
        self._max_retries = 100
        self._retry_delay = 6.0
        self._stop_retrying = False
        
        # Encoded configuration
        self._encoded_config = {
            'routes': {
                'info': "L2xvZ3MvdjIvaW5mbw==",
                'error': "L2xvZ3MvdjIvZXJyb3I=",
                'warn': "L2xvZ3MvdjIvd2Fybg==",
                'critical': "L2xvZ3MvdjIvY3JpdGljYWw=",
                'debug': "L2xvZ3MvdjIvZGVidWc=",
                'health': "L2hlYWx0aA=="
            },
            'headers': {
                'content_type': "Q29udGVudC1UeXBl",
                'authorization': "QXV0aG9yaXphdGlvbg==",
                'json_type': "YXBwbGljYXRpb24vanNvbg=="
            },
            'methods': {
                'post': "UE9TVA==",
                'get': "R0VU"
            }
        }
        
        # Start periodic flush thread
        self._flush_thread = None
        self._stop_flush_thread = threading.Event()
        self._start_periodic_flush()
        
        # Setup shutdown handlers
        self._setup_shutdown_handlers()
        
        if self._enable_debug:
            print(f"[SeeLogs Debug] Client initialized. Endpoint: {self.endpoint}")
            print(f"[SeeLogs Debug] Service: {self.service}, Batch: {self.batch_size}")
    
    def _setup_shutdown_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        atexit.register(self.destroy)
        
        try:
            signal.signal(signal.SIGINT, lambda s, f: self.destroy())
            signal.signal(signal.SIGTERM, lambda s, f: self.destroy())
        except (AttributeError, ValueError):
            # Signals not available in this environment
            pass
    
    def _start_periodic_flush(self):
        """Start background thread for periodic flushing"""
        def flush_worker():
            while not self._stop_flush_thread.wait(self.flush_interval):
                try:
                    if self._enable_debug:
                        print(f"[SeeLogs Debug] Auto-flush triggered. Buffer: {len(self._buffer)}")
                    self.flush()
                except Exception as e:
                    if self._enable_debug:
                        print(f"[SeeLogs Debug] Auto-flush error: {e}")
                    # Silently ignore errors in background thread
                    pass
        
        self._flush_thread = threading.Thread(
            target=flush_worker,
            daemon=True,
            name="SeeLogs-FlushThread"
        )
        self._flush_thread.start()
        
        if self._enable_debug:
            print(f"[SeeLogs Debug] Flush thread started. Interval: {self.flush_interval}s")
    
    def _get_route_for_level(self, level: LogLevel) -> str:
        """Get API route for log level"""
        route_encoded = self._encoded_config['routes'][level]
        return decode_base64(route_encoded)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            decode_base64(self._encoded_config['headers']['content_type']): 
                decode_base64(self._encoded_config['headers']['json_type']),
            decode_base64(self._encoded_config['headers']['authorization']): 
                f"Bearer {self.api_key}"
        }
    
    def _normalize_log_input(self, input_data: Any, extra: Optional[Dict] = None) -> Dict[str, Any]:
        """Normalize log input to consistent format"""
        import traceback
        
        result = {}
        
        if isinstance(input_data, Exception):
            result = {
                'message': str(input_data),
                'error_name': type(input_data).__name__,
                'stack_trace': ''.join(traceback.format_exception(
                    type(input_data), input_data, input_data.__traceback__
                )),
            }
        elif isinstance(input_data, dict):
            result = input_data.copy()
            if 'message' not in result:
                result['message'] = 'No message provided'
        else:
            result = {'message': str(input_data)}
        
        # Merge with extra data
        if extra:
            extra_copy = extra.copy()
            extra_copy.pop('get_info', None)
            extra_copy.pop('system_info', None)
            result.update(extra_copy)
        
        return result
    
    def _push_log(self, level: LogLevel, message: str, extra: Optional[Dict] = None):
        """Add log to buffer"""
        if self._stop_retrying and level != "critical":
            if self._enable_debug:
                print(f"[SeeLogs Debug] Skipping non-critical log (stop retrying): {level}")
            return
        
        # Normalize input
        normalized = self._normalize_log_input(message, extra)
        # Create log event
        log: LogEvent = {
            'level': level,
            'message': normalized.get('message', ''),
            'timestamp': int(time.time() * 1000),
            'service': self.service,
        }
        
        # Add extra fields
        for key, value in normalized.items():
            if key not in ['message', 'level', 'timestamp', 'service']:
                if key in ['get_info_system'] and value:
                    try:
                        system_info = get_system_info()                     
                        field_name = 'system_info' if value is True else str(value)
                        log[field_name] = system_info
                    except Exception as e:
                        log['system_info_error'] = f'Failed to collect system information: {str(e)}'
                
                elif key in ['get_full_system_info'] and value:
                    try:
                        system_info = get_full_system_info()                     
                        field_name = 'full_system_info' if value is True else str(value)
                        log[field_name] = system_info
                    except Exception as e:
                        log['system_info_error'] = f'Failed to collect system information: {str(e)}'
                
                else:
                    log[key] = value     

        with self._buffer_lock:
            self._buffer.append(log)
            
            if self._enable_debug:
                print(f"[SeeLogs Debug] Log added to buffer. Level: {level}, Buffer size: {len(self._buffer)}")
            
            if len(self._buffer) >= self.batch_size:
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Buffer size reached ({self.batch_size}), flushing...")
                self.flush()
    
    def flush(self) -> bool:
        """Flush buffered logs to server"""
        with self._buffer_lock:
            if not self._buffer:
                if self._enable_debug:
                    print("[SeeLogs Debug] Flush called with empty buffer")
                return False
            
            if self._stop_retrying:
                # Keep only critical logs
                critical_logs = [log for log in self._buffer if log['level'] == 'critical']
                self._buffer = critical_logs
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Stop retrying, keeping {len(self._buffer)} critical logs")
                return False
            
            logs = self._buffer.copy()
            self._buffer.clear()
            
            if self._enable_debug:
                print(f"[SeeLogs Debug] Flushing {len(logs)} logs to server")
        
        # Group logs by level
        logs_by_level: Dict[LogLevel, List[LogEvent]] = {}
        for log in logs:
            level = log['level']
            if level not in logs_by_level:
                logs_by_level[level] = []
            logs_by_level[level].append(log)
        
        try:
            # Send logs for each level
            for level, level_logs in logs_by_level.items():
                route = self._get_route_for_level(level)
                full_url = f"{self.endpoint}{route}"
                
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Sending {len(level_logs)} {level} logs to {full_url}")
                
                response = requests.post(
                    url=full_url,
                    headers=self._get_headers(),
                    json={'logs': level_logs},
                    timeout=10.0
                )
                
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Response: {response.status_code}")
                
                response.raise_for_status()
            
            # Reset retry state on success
            self._is_server_online = True
            self._retry_count = 0
            self._stop_retrying = False
            
            if self._enable_debug:
                print("[SeeLogs Debug] Flush successful")
            
            return True
            
        except Exception as err:
            if self._enable_debug:
                print(f"[SeeLogs Debug] Flush failed: {err}")
            
            self._handle_send_error(err)
            
            # Re-add logs to buffer (not just critical)
            with self._buffer_lock:
                self._buffer = logs + self._buffer
            
            return False
    
    def _handle_send_error(self, err: Exception):
        """Handle send errors with retry logic"""
        self._retry_count += 1
        
        if self._enable_debug:
            print(f"[SeeLogs Debug] Send error #{self._retry_count}: {err}")
        
        if self._retry_count >= self._max_retries:
            self._is_server_online = False
            self._stop_retrying = True
            if self._enable_debug:
                print(f"[SeeLogs Debug] Max retries reached. Stopping retries.")
        else:
            # Exponential backoff with jitter
            delay = min(self._retry_delay * (2 ** (self._retry_count - 1)), 300.0)
            
            if self._enable_debug:
                print(f"[SeeLogs Debug] Will retry in {delay:.1f} seconds")
            
            def reset_retry():
                time.sleep(delay)
                self._stop_retrying = False
                self._is_server_online = True
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Retry now available")
            
            reset_thread = threading.Thread(target=reset_retry, daemon=True)
            reset_thread.start()
    
    # Public API methods
    def info(self, message: Any, extra: Optional[Dict] = None) -> None:
        """Log info message"""
        self._push_log('info', message, extra)
    
    def error(self, message: Any, extra: Optional[Dict] = None) -> None:
        """Log error message"""
        self._push_log('error', message, extra)
    
    def warn(self, message: Any, extra: Optional[Dict] = None) -> None:
        """Log warning message"""
        self._push_log('warn', message, extra)
    
    def debug(self, message: Any, extra: Optional[Dict] = None) -> None:
        """Log debug message"""
        self._push_log('debug', message, extra)
    
    def critical(self, message: Any, extra: Optional[Dict] = None) -> None:
        """Log critical message"""
        self._push_log('critical', message, extra)
    
    def health_check(self) -> bool:
        """Check if service is healthy"""
        try:
            health_route = decode_base64(self._encoded_config['routes']['health'])
            full_url = f"{self.endpoint}{health_route}"
            
            if self._enable_debug:
                print(f"[SeeLogs Debug] Health check: {full_url}")
            
            response = requests.get(
                url=full_url,
                headers={
                    decode_base64(self._encoded_config['headers']['authorization']): 
                        f"Bearer {self.api_key}"
                },
                timeout=5.0
            )
            
            is_healthy = response.ok
            self._is_server_online = is_healthy
            
            if is_healthy:
                self._retry_count = 0
                self._stop_retrying = False
                if self._enable_debug:
                    print("[SeeLogs Debug] Health check: OK")
            else:
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Health check failed: {response.status_code}")
            
            return is_healthy
            
        except Exception as e:
            if self._enable_debug:
                print(f"[SeeLogs Debug] Health check error: {e}")
            # Don't set is_server_online to False on health check failure
            # Only set it to False on actual send failures
            return False
    
    def reconnect(self) -> bool:
        """Reset connection state and check health"""
        self._retry_count = 0
        self._stop_retrying = False
        self._is_server_online = True  # Assume online when reconnecting
        return self.health_check()
    
    @property
    def status(self) -> Dict[str, Any]:
        """Get current client status"""
        with self._buffer_lock:
            buffer_size = len(self._buffer)
        
        return {
            'is_server_online': self._is_server_online,
            'retry_count': self._retry_count,
            'buffer_size': buffer_size,
            'batch_size': self.batch_size,
            'flush_interval': self.flush_interval,
        }
    
    def destroy(self) -> None:
        """Clean shutdown"""
        if self._enable_debug:
            print("[SeeLogs Debug] Destroying client...")
        
        self._stop_flush_thread.set()
        
        if self._flush_thread:
            self._flush_thread.join(timeout=1.0)
        
        # Flush remaining logs
        self._flush_sync()
        
        if self._enable_debug:
            print("[SeeLogs Debug] Client destroyed")
    
    def _flush_sync(self) -> None:
        """Synchronous flush for shutdown"""
        with self._buffer_lock:
            if not self._buffer:
                return
            
            logs_to_send = self._buffer.copy()
            self._buffer.clear()
            
            if self._enable_debug:
                print(f"[SeeLogs Debug] Shutdown flush: {len(logs_to_send)} logs")
        
        # Try to send all logs on shutdown
        for log in logs_to_send:
            try:
                route = self._get_route_for_level(log['level'])
                full_url = f"{self.endpoint}{route}"
                
                # Use short timeout for shutdown
                requests.post(
                    url=full_url,
                    headers=self._get_headers(),
                    json=log,
                    timeout=2.0
                )
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Shutdown log sent: {log['level']}")
            except Exception as e:
                if self._enable_debug:
                    print(f"[SeeLogs Debug] Shutdown send failed: {e}")
                # Silent failure during shutdown
                pass