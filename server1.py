import requests
import logging
import threading
import time
from constants import SERVER2_URL, SERVER1_PORT
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(message)s'
)
logger = logging.getLogger('server1')

app = Flask(__name__)

game_state = {
    "running": False,
    "ended": False,
    "pong_time_ms": 4000
}

@app.route('/ping', methods=['POST'])
def receive_ping():
    """Handle ping request recieved from Server 2"""
    data = request.json
    logger.info(f"Received ping from Server 2: {data}")
    
    if not game_state["running"]:
        return jsonify({"message": "Game paused"}), 200
    
    response = jsonify({"message": "pong"}), 200
    
    if game_state["running"]:
        threading.Thread(target=send_delayed_ping).start()

    return response

@app.route('/controls', methods=['POST'])
def control_game():
    """Control the game (start, pause, resume, stop)"""
    data = request.json
    command = data.get('command')
    
    if command is None:
        logger.error("No command found in the request")
        return jsonify({"message": "Missing required 'command' parameter"}), 400
    
    if command == 'start':
        game_state["running"] = True
        game_state["ended"] = False
        game_state["pong_time_ms"] = data.get('pong_time_ms', 4000)
        # Start the game by sending the first ping
        threading.Thread(target=start_game).start()
        logger.info(f"Game started with {game_state['pong_time_ms']}m wait time")
        return jsonify({"message": "Game started"}), 200
    
    elif command in ['pause', 'resume']:
        if game_state["ended"]:
            return jsonify({"message": "Please start the game again"}), 200

        game_state["running"] = (command == 'resume')
        logger.info(f"Game {command}d")
        return jsonify({"message": f"Game {command}d"}), 200
    
    elif command == 'stop':
        game_state["running"] = False
        game_state["ended"] = True
        logger.info("Game stopped")
        return jsonify({"message": "Game stopped"}), 200
    
    return jsonify({"message": "Invalid command"}), 400

def start_game():
    """Initiate the ping-pong game by sending the first ping"""
    if game_state["running"]:
        try:
            logger.info("Sending initial ping to Server 2")
            response = requests.post(
                f"{SERVER2_URL}/ping",
                json={"message": "ping"}
            )
            logger.info(f"Response from Server 2: {response.status_code} - {response.json()}")
        except requests.RequestException as connection_exception:
            logger.error(f"Error connecting to Server 2: {connection_exception}")

def send_delayed_ping():
    """Send a ping to Server 1 after the specified wait time"""
    time.sleep(game_state["pong_time_ms"] / 1000)
    
    if game_state["running"]:
        try:
            logger.info(f"Sending ping to Server 2 after {game_state['pong_time_ms']}ms wait time")
            response = requests.post(
                f"{SERVER2_URL}/ping", 
                json={"message": "ping"}
            )
            logger.info(f"Response from Server 2: {response.status_code} - {response.json()}")
        except requests.RequestException as connection_exception:
            logger.error(f"Error connecting to Server 2: {connection_exception}")

if __name__ == '__main__':
    logger.info("Server 1 starting on port %s", SERVER1_PORT)
    app.run(port=SERVER1_PORT, debug=True, use_reloader=True)