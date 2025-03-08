import asyncio
import websockets
import json
import random
import threading
import tkinter as tk
import time
import AI_TTS
import os
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

url = "wss://pubsub-edge.twitch.tv"

# Get sensitive data from environment variables with fallbacks
client_id = os.environ.get('TWITCH_CLIENT_ID')
channel_id = os.environ.get('TWITCH_CHANNEL_ID')
access_token = os.environ.get('TWITCH_ACCESS_TOKEN')

# Validate that required environment variables are set
if not all([client_id, channel_id, access_token]):
    print("ERROR: Missing required environment variables. Please check your .env file.")
    print(f"TWITCH_CLIENT_ID: {'Set' if client_id else 'Missing'}")
    print(f"TWITCH_CHANNEL_ID: {'Set' if channel_id else 'Missing'}")
    print(f"TWITCH_ACCESS_TOKEN: {'Set' if access_token else 'Missing'}")
    # You can choose to exit or continue with defaults for development
    # import sys; sys.exit(1)

# Global variables to track enabled/disabled state
tts_enabled = False
sound_player_enabled = False
reconnect_delay = 5  # Seconds to wait before reconnecting
max_reconnect_attempts = 10
settings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
MAX_TTS_CHARACTERS = 200  # Maximum characters allowed for TTS input

# Function to save settings to a file
def save_settings():
    settings = {
        "tts_enabled": tts_enabled,
        "sound_player_enabled": sound_player_enabled
    }
    try:
        with open(settings_file, "w") as f:
            json.dump(settings, f)
        print("Settings saved")
    except Exception as e:
        print(f"Error saving settings: {e}")

# Function to load settings from a file
def load_settings():
    global tts_enabled, sound_player_enabled
    try:
        if os.path.exists(settings_file):
            with open(settings_file, "r") as f:
                settings = json.load(f)
                tts_enabled = settings.get("tts_enabled", False)
                sound_player_enabled = settings.get("sound_player_enabled", False)
            print(f"Settings loaded: TTS={tts_enabled}, Sound Player={sound_player_enabled}")
        else:
            print("No settings file found, using defaults")
    except Exception as e:
        print(f"Error loading settings: {e}")

# Load settings at startup
load_settings()

def ChannelPointsTTS(reward_title, user_input, username):
    if tts_enabled and reward_title == "TTS":
        # Truncate user input if it exceeds maximum character limit
        original_input = user_input
        if len(user_input) > MAX_TTS_CHARACTERS:
            user_input = user_input[:MAX_TTS_CHARACTERS] + "... (message truncated)"
            print(f"Input exceeded {MAX_TTS_CHARACTERS} characters. Truncated from {len(original_input)} characters.")
            
        print(f"TTS ACTIVATED: Reading message from {username}: {user_input}")
        AI_TTS.play_voice(user_input)
        AI_TTS.play_audio(AI_TTS.speech_file_path)

def ChannelPointsSoundPlayer(reward_title, user_input, username):
    if sound_player_enabled:
        print(f"Sound Player enabled: Would play sound for {reward_title}")
        # Implement sound player functionality here when needed

async def stay():
    attempts = 0
    while attempts < max_reconnect_attempts:
        try:
            # Create a dedicated connection for the ping task with a timeout
            async with websockets.connect(url, ping_interval=100, close_timeout=10) as socket:
                attempts = 0  # Reset attempts on successful connection
                print("Ping connection established successfully")
                while True:
                    try:
                        ping = json.dumps({"type": "PING"})
                        await asyncio.wait_for(socket.send(ping), timeout=10)
                        res = await asyncio.wait_for(socket.recv(), timeout=10)
                        print(f"Ping response: {res}")
                        await asyncio.sleep(100 + random.randrange(1, 50))
                    except asyncio.TimeoutError:
                        print("Ping timed out, reconnecting...")
                        break
        except (ConnectionRefusedError, ConnectionClosedError, ConnectionClosedOK) as e:
            attempts += 1
            print(f"Ping connection error: {e}. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
        except asyncio.TimeoutError as e:
            attempts += 1
            print(f"Ping connection timeout: Connection took too long to establish or respond. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
        except Exception as e:
            attempts += 1
            print(f"Unexpected error in ping task: {type(e).__name__}: {e}. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
    
    print("Max ping reconnection attempts reached. Exiting ping task.")

def extract_redemption_data(message_data):
    """Extract relevant information from a redemption message"""
    try:
        # Parse the message string to a JSON object
        message = json.loads(message_data['message'])
        
        if message['type'] == 'reward-redeemed':
            redemption = message['data']['redemption']
            
            # Extract the reward title
            reward_title = redemption['reward']['title']
            
            # Extract user input (if present)
            user_input = redemption.get('user_input', '')
            
            # Extract user info
            username = redemption['user']['display_name']
            
            # Call the functions with the extracted data
            ChannelPointsTTS(reward_title, user_input, username)
            ChannelPointsSoundPlayer(reward_title, user_input, username)
            
            return {
                'reward_title': reward_title,
                'user_input': user_input,
                'username': username,
                'timestamp': redemption['redeemed_at'],
                'status': redemption['status']
            }
        return None
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing redemption: {e}")
        return None

async def listen():
    attempts = 0
    while attempts < max_reconnect_attempts:
        try:
            # Create a dedicated connection for the listener with a timeout
            async with websockets.connect(url, ping_interval=100, close_timeout=10) as socket:
                data = json.dumps({
                    "type": "LISTEN",
                    "data": {
                        "topics": [f"channel-points-channel-v1.{channel_id}"],
                        "auth_token": access_token,
                    }
                })
                
                await asyncio.wait_for(socket.send(data), timeout=10)
                resp = await asyncio.wait_for(socket.recv(), timeout=10)
                dec_resp = json.loads(resp)
                print(f"Listen response: {dec_resp}")
                
                # Reset attempts on successful connection
                attempts = 0
                print("Listen connection established successfully")
                
                # Keep the connection alive and listen for messages
                while True:
                    try:
                        msg = await asyncio.wait_for(socket.recv(), timeout=120)  # 2 minute timeout
                        msg_data = json.loads(msg)
                        
                        if msg_data['type'] == 'MESSAGE':
                            redemption_data = extract_redemption_data(msg_data['data'])
                            if (redemption_data):
                                print(f"Channel point redeemed: {redemption_data['reward_title']} with user data: {redemption_data['user_input']}")
                            else:
                                print(f"Non-redemption message received")
                        else:
                            print(f"Received: {msg_data['type']}")
                    except asyncio.TimeoutError:
                        print("Listen connection timed out, sending a ping to check connection")
                        try:
                            ping = json.dumps({"type": "PING"})
                            await asyncio.wait_for(socket.send(ping), timeout=5)
                            # If ping succeeds, continue with the connection
                            continue
                        except Exception as e:
                            print(f"Ping failed: {type(e).__name__}: {e}. Reconnecting listener...")
                            break
        except (ConnectionRefusedError, ConnectionClosedError, ConnectionClosedOK) as e:
            attempts += 1
            print(f"Listen connection error: {e}. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
        except asyncio.TimeoutError as e:
            attempts += 1
            print(f"Listen connection timeout: Connection took too long to establish or respond. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
        except Exception as e:
            attempts += 1
            print(f"Unexpected error in listen task: {type(e).__name__}: {e}. Attempt {attempts}/{max_reconnect_attempts}")
            await asyncio.sleep(reconnect_delay)
    
    print("Max listen reconnection attempts reached. Exiting listen task.")

async def main():
    # Run both tasks concurrently
    ping_task = asyncio.create_task(stay())
    listen_task = asyncio.create_task(listen())
    
    try:
        # Wait for both tasks to complete (they shouldn't under normal circumstances)
        await asyncio.gather(ping_task, listen_task)
    except asyncio.CancelledError:
        print("Tasks were cancelled")
    except Exception as e:
        print(f"Error occurred in main: {e}")

# UI functions
def toggle_tts():
    global tts_enabled
    tts_enabled = not tts_enabled
    tts_button.config(text=f"TTS: {'Enabled' if tts_enabled else 'Disabled'}", 
                     bg='green' if tts_enabled else 'red')
    print(f"TTS function is now {'enabled' if tts_enabled else 'disabled'}")
    save_settings()  # Save settings when changed

def toggle_sound_player():
    global sound_player_enabled
    sound_player_enabled = not sound_player_enabled
    sound_button.config(text=f"Sound Player: {'Enabled' if sound_player_enabled else 'Disabled'}", 
                       bg='green' if sound_player_enabled else 'red')
    print(f"Sound Player function is now {'enabled' if sound_player_enabled else 'disabled'}")
    save_settings()  # Save settings when changed

def create_ui():
    global tts_button, sound_button
    
    # Create the main window
    root = tk.Tk()
    root.title("Channel Point Functions Control")
    root.geometry("300x200")
    root.configure(bg='#333333')

    # Add a label
    title_label = tk.Label(root, text="Toggle Channel Point Functions", 
                          font=("Arial", 14), 
                          bg='#333333', fg='white')
    title_label.pack(pady=15)

    # Create a button to toggle TTS - set initial state from loaded settings
    tts_button = tk.Button(root, 
                         text=f"TTS: {'Enabled' if tts_enabled else 'Disabled'}", 
                         command=toggle_tts,
                         width=20, height=2, 
                         bg='green' if tts_enabled else 'red', fg='white',
                         font=("Arial", 10, "bold"))
    tts_button.pack(pady=10)

    # Create a button to toggle Sound Player - set initial state from loaded settings
    sound_button = tk.Button(root, 
                           text=f"Sound Player: {'Enabled' if sound_player_enabled else 'Disabled'}", 
                           command=toggle_sound_player,
                           width=20, height=2,
                           bg='green' if sound_player_enabled else 'red', fg='white',
                           font=("Arial", 10, "bold"))
    sound_button.pack(pady=10)
    
    return root

def run_async_main():
    """Run the async main function in a separate thread"""
    asyncio.run(main())

# Run both the UI and the async code
if __name__ == "__main__":
    # Start the async functions in a separate thread
    async_thread = threading.Thread(target=run_async_main, daemon=True)
    async_thread.start()
    
    # Create and start the UI in the main thread
    root = create_ui()
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("Program interrupted")
    finally:
        print("Program exiting")
