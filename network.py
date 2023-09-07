import network
from network_manager import NetworkManager

def get_manager():
    return NetworkManager("AU", status_handler=None, error_handler=None)

def scan_aps():
    wlan = get_manager()._sta_if
    return [x[0].decode('utf-8') for x in wlan.scan()]

if __name__ == "__main__":
    print(scan_aps())