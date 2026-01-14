import os
from fastmcp import FastMCP

# Get keys from environment variables
access_key = os.environ.get("X_ACCESS_KEY")
secret_key = os.environ.get("X_SECRET_KEY")
url = os.environ.get("X_URL")

if not access_key or not secret_key or not url:
    raise ValueError("X_ACCESS_KEY and X_SECRET_KEY and X_URL environment variables must be set")
# Create a proxy directly from a config dictionary
config = {
    "mcpServers": {
        "auto-insights": {
          "type": "http",
          "url": url,
          "headers": {
            "x-access-key": access_key,
            "x-secret": secret_key
          }
        }
    }
}

import os
from fastmcp import FastMCP

# Get keys from environment variables
access_key = os.environ.get("X_ACCESS_KEY")
secret_key = os.environ.get("X_SECRET_KEY")
url = os.environ.get("X_URL")

if not access_key or not secret_key or not url:
    raise ValueError("X_ACCESS_KEY and X_SECRET_KEY and X_URL environment variables must be set")
# Create a proxy directly from a config dictionary
config = {
    "mcpServers": {
        "auto-insights": {
          "type": "http",
          "url": url,
          "headers": {
            "x-access-key": access_key,
            "x-secret": secret_key
          }
        }
    }
}

# Create a proxy to the configured server (auto-creates ProxyClient)
proxy = FastMCP.as_proxy(config, name="Config-Based Proxy")

def main():
    # Run the proxy with stdio transport for local access
    proxy.run()

if __name__ == "__main__":
    main()