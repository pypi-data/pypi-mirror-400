"""
Enhanced Error Messages for LatencyZero
User-friendly error handling and debugging
"""

class LatencyZeroError(Exception):
    """Base exception for LatencyZero errors"""
    def __init__(self, message: str, help_text: str = None):
        self.message = message
        self.help_text = help_text
        super().__init__(self.format_error())
    
    def format_error(self) -> str:
        error = f"\n{'='*70}\n"
        error += f"❌ LatencyZero Error\n"
        error += f"{'='*70}\n\n"
        error += f"{self.message}\n"
        
        if self.help_text:
            error += f"\n💡 How to fix:\n{self.help_text}\n"
        
        error += f"\n{'='*70}\n"
        return error


class GatewayNotRunningError(LatencyZeroError):
    """Gateway is not accessible"""
    def __init__(self, gateway_url: str):
        super().__init__(
            message=f"Cannot connect to LatencyZero gateway at {gateway_url}",
            help_text=f"""
   1. Start the gateway:
      cd gateway
      python server.py
   
   2. Verify it's running:
      curl {gateway_url}
   
   3. Check firewall settings
   
   4. If using custom URL, configure it:
      from latencyzero import configure
      configure(gateway_url="http://your-server:8080")
            """
        )


class GatewayTimeoutError(LatencyZeroError):
    """Gateway took too long to respond"""
    def __init__(self, timeout: float):
        super().__init__(
            message=f"Gateway timeout after {timeout}s",
            help_text=f"""
   The gateway is running but responding slowly.
   
   1. Check gateway logs for errors
   
   2. Increase timeout:
      from latencyzero import configure
      configure(timeout=1.0)  # Increase from {timeout}s
   
   3. Check gateway server resources (CPU, memory)
            """
        )


class StorageError(LatencyZeroError):
    """Error storing or retrieving from cache"""
    def __init__(self, operation: str, details: str):
        super().__init__(
            message=f"Storage {operation} failed: {details}",
            help_text="""
   1. Check gateway logs for details
   
   2. Verify Redis is running (if using Redis):
      redis-cli ping
   
   3. Check disk space (if using file storage)
   
   4. Restart gateway:
      cd gateway && python server.py
            """
        )


class InvalidToleranceError(LatencyZeroError):
    """Invalid tolerance value"""
    def __init__(self, tolerance: float):
        super().__init__(
            message=f"Invalid tolerance: {tolerance}",
            help_text="""
   Tolerance must be between 0.0 and 1.0:
   
   - tolerance=0.01  (1% error, very strict)
   - tolerance=0.10  (10% error, recommended)
   - tolerance=0.20  (20% error, aggressive)
   
   Example:
   @a3(tolerance=0.15)  # 15% tolerance
   def my_function():
       ...
            """
        )


class SerializationError(LatencyZeroError):
    """Cannot serialize function result"""
    def __init__(self, result_type: str):
        super().__init__(
            message=f"Cannot serialize result of type {result_type}",
            help_text="""
   LatencyZero can only cache pickle-able objects.
   
   ✅ Works with: dict, list, str, int, float, bool
   ❌ Doesn't work with: file handles, database connections, threads
   
   Solution: Return only simple data types from cached functions.
   
   Example:
   @a3(tolerance=0.15)
   def query_db(user_id):
       conn = get_db_connection()  # Don't return this
       result = conn.query(...)
       conn.close()
       return result  # Return dict/list instead ✓
            """
        )


# Error messages for common issues
ERROR_MESSAGES = {
    "connection_refused": """
❌ Connection Refused

The gateway is not running.

💡 Fix:
   Terminal 1:
   cd gateway
   python server.py
   
   Terminal 2:
   cd examples
   python your_script.py
    """,
    
    "no_module_latencyzero": """
❌ ModuleNotFoundError: No module named 'latencyzero'

You haven't installed the LatencyZero package.

💡 Fix:
   cd latencyzero-mvp
   pip install -e .
    """,
    
    "api_key_missing": """
❌ API Key Not Configured

💡 Fix:
   export OPENAI_API_KEY='sk-...'
   
   Or in Python:
   import os
   os.environ['OPENAI_API_KEY'] = 'sk-...'
    """,
    
    "redis_not_running": """
❌ Redis Connection Failed

Redis is not running (optional for development).

💡 Options:
   1. Use in-memory store (automatic fallback) ✓
   
   2. Or install Redis:
      # macOS
      brew install redis
      brew services start redis
      
      # Ubuntu
      sudo apt-get install redis
      sudo service redis-server start
      
      # Docker
      docker run -d -p 6379:6379 redis
    """,
    
    "function_not_cached": """
❌ No Cache Hits Yet

This is normal for first calls!

💡 How caching works:
   1st call:  Slow (computes + stores)
   2nd call:  Fast (uses cache) ⚡
   3rd call:  Fast (uses cache) ⚡
   
   Be patient - caching happens after the first call.
    """,
    
    "confidence_too_low": """
⚠️  Cache Available But Confidence Too Low

The cached result exists but isn't fresh/accurate enough.

💡 Fix:
   Increase tolerance to use cached results more:
   
   @a3(tolerance=0.20)  # Was 0.02, now 0.20
   def my_function():
       ...
   
   Higher tolerance = more aggressive caching
    """,
}


def print_startup_banner():
    """Print helpful banner when app starts"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║   LatencyZero - Adaptive Anticipatory Approximation (A³)          ║
║                                                                    ║
║   Status: ✓ SDK Loaded                                            ║
║           ? Gateway: Checking...                                   ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)


def print_gateway_status(connected: bool, url: str):
    """Print gateway connection status"""
    if connected:
        print(f"""
✅ Gateway Connected
   URL: {url}
   Status: Operational
   
   Your functions will be cached automatically!
        """)
    else:
        print(f"""
⚠️  Gateway Not Connected
   URL: {url}
   Status: Not reachable
   
   Functions will run normally (no caching).
   
   To enable caching:
   1. Open a new terminal
   2. cd gateway
   3. python server.py
        """)


def print_first_cache_hint():
    """Print hint about first cache behavior"""
    print("""
💡 First-Time Caching Behavior:

   Call 1: ████████████████ 2000ms (building cache)
   Call 2: ██ 10ms ⚡ (using cache)
   Call 3: ██ 8ms ⚡ (using cache)
   
   This is expected! The first call is always slow.
    """)


def print_cost_savings(cache_hits: int, api_cost_per_call: float = 0.03):
    """Print cost savings from caching"""
    savings = cache_hits * api_cost_per_call
    
    if savings > 0:
        print(f"""
💰 Cost Savings:
   Cache hits: {cache_hits}
   Cost per API call: ${api_cost_per_call}
   Total saved: ${savings:.2f}
   
   At this rate:
   - Daily: ${savings * 3:.2f}
   - Monthly: ${savings * 90:.2f}
   - Yearly: ${savings * 1095:.2f}
        """)


def print_troubleshooting_guide():
    """Print troubleshooting guide"""
    print("""
🔧 Troubleshooting Guide:

   Problem: No speedup on 2nd call
   → Check gateway is running
   → Verify tolerance is reasonable (0.10-0.20)
   → Look for errors in gateway logs
   
   Problem: "Connection refused"
   → Start gateway: cd gateway && python server.py
   
   Problem: "Module not found"
   → Install SDK: pip install -e .
   
   Problem: Functions running slow
   → First call is always slow (builds cache)
   → 2nd+ calls should be fast
   
   Problem: Cache not working
   → Check gateway logs for errors
   → Verify function inputs are identical
   → Increase tolerance: @a3(tolerance=0.20)
   
   Still stuck? Check logs:
   - Gateway: Look at terminal running server.py
   - Client: Add enable_metrics=True to see stats
    """)


if __name__ == "__main__":
    # Demo the error messages
    print("LatencyZero Error Message Examples:\n")
    
    try:
        raise GatewayNotRunningError("http://localhost:8080")
    except Exception as e:
        print(e)
    
    print("\n" + "="*70 + "\n")
    
    try:
        raise InvalidToleranceError(1.5)
    except Exception as e:
        print(e)