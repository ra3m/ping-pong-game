import requests
import logging
import threading
import time
from constants import SERVER1_URL, SERVER2_PORT
from flask import Flask, request, jsonify

logging.basicConfig(
    level=logging.INFO,
    format='%(name)s - %(message)s'
)
logger = logging.getLogger('server2')

app = Flask(__name__)

game_state = {
    "running": False,
    "ended": False,
    "pong_time_ms": 4000
}

@app.route('/ping', methods=['POST'])
def receive_ping():
    """Handle ping request from Server 1"""
    data = request.json
    logger.info(f"Received ping from Server 1: {data}")

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
    
    if command == 'start':
        game_state["running"] = True
        game_state["ended"] = False
        game_state["pong_time_ms"] = data.get('pong_time_ms', 4000)
        logger.info(f"Game started with {game_state['pong_time_ms']}ms wait time")
        return jsonify({"message": "Game started"}), 200
    
    elif command == 'pause':
        if game_state["ended"]:
            return jsonify({"message": "Please start the game again"}), 200
        game_state["running"] = False
        logger.info("Game paused")
        return jsonify({"message": "Game paused"}), 200
    
    elif command == 'resume':
        if game_state["ended"]:
            return jsonify({"message": "Please start the game again"}), 200
        game_state["running"] = True
        logger.info("Game resumed")
        return jsonify({"message": "Game resumed"}), 200
    
    elif command == 'stop':
        game_state["running"] = False
        game_state["ended"] = True
        logger.info("Game stopped")
        return jsonify({"message": "Game stopped"}), 200
    
    return jsonify({"message": "Invalid command"}), 400

def send_delayed_ping():
    """Send a ping to Server 1 after the specified wait time"""
    time.sleep(game_state["pong_time_ms"] / 1000)
    
    if game_state["running"]:
        try:
            logger.info(f"Sending ping to Server 1 after {game_state['pong_time_ms']}ms wait time")
            response = requests.post(
                f"{SERVER1_URL}/ping", 
                json={"message": "ping"}
            )
            logger.info(f"Response from Server 1: {response.status_code} - {response.json()}")
        except requests.RequestException as connection_exception:
            logger.error(f"Error connecting to Server 1: {connection_exception}")

if __name__ == '__main__':
    logger.info("Server 2 starting on port %s", SERVER2_PORT)
    app.run(port=SERVER2_PORT, debug=True, use_reloader=True)