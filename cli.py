import argparse
import requests
import logging
from constants import SERVER1_URL,SERVER2_URL 

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(message)s'
)
logger = logging.getLogger('cli')

def send_control_command(command, pong_time_ms=None):
    """Send control command to both servers"""
    payload = {"command": command}
    
    if pong_time_ms is not None:
        payload["pong_time_ms"] = pong_time_ms
    
    try:
        response1 = requests.post(f"{SERVER1_URL}/controls", json=payload)
        response2 = requests.post(f"{SERVER2_URL}/controls", json=payload)
        
        logger.info(f"Server 1 response: {response1.status_code} - {response1.json()}")
        logger.info(f"Server 2 response: {response2.status_code} - {response2.json()}")
        
        return True
    except requests.RequestException as connection_exception:
        logger.error(f"Error communicating with servers: {connection_exception}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Control the ping-pong game servers')
    parser.add_argument('command', choices=['start', 'pause', 'resume', 'stop'],
                        help='Command to execute')
    parser.add_argument('pong_time_ms', nargs='?', type=int, default=4000,
                        help='Delay in milliseconds between ping-pongs (only used with start)')
    
    args = parser.parse_args()
    
    if args.command == 'start':
        logger.info(f"Starting game with {args.pong_time_ms}ms wait time")
        send_control_command(args.command, args.pong_time_ms)
    else:
        logger.info(f"Sending {args.command} command to servers")
        send_control_command(args.command)

if __name__ == '__main__':
    main()