import uvicorn
import os
import socket
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_ip_address():
    """Get the local IP address of the machine."""
    try:
        # Create a socket connection to an external server
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Doesn't need to be reachable
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        print(f"Error getting IP address: {e}")
        return "127.0.0.1"  # Return localhost if there's an error


if __name__ == "__main__":
    # Create static/images directory if it doesn't exist
    os.makedirs("app/static/images", exist_ok=True)

    # Get the IP address
    ip_address = get_ip_address()

    # Display access information
    print("\n" + "=" * 50)
    print(f"Access from other devices at: http://{ip_address}:8000")
    print("=" * 50 + "\n")

    # Run the application on your IP address
    # Using 0.0.0.0 allows connections from any IP
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)