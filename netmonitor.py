import psutil
import time
import psutil
import time


def bytes_to_mb(bytes_value):
    mb_value = bytes_value / (1024.0 ** 2)
    return mb_value


def get_network_usage(interface='eth0'):
    while True:
        try:
            net_stats = psutil.net_io_counters(pernic=True)[interface]
            print(f"Interface: {interface}")
            print(f"   sent: {bytes_to_mb(net_stats.bytes_sent):05f} MB")
            print(f"   received: {bytes_to_mb(net_stats.bytes_recv):05f} MB")
            print("=" * 30)
            time.sleep(1)
        except KeyError:
            print(f"Error: Interface '{interface}' not found.")
            break

def get_network_interfaces():
    interfaces = psutil.net_if_stats().keys()
    return interfaces

def get_process_network_usage(pid, interval=1):
    try:
        process = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"Error: Process with PID {pid} not found.")
        return

    while True:
        try:
            io_counters = process.io_counters()
            print(f"Process: {process.name()} (PID: {pid})")
            print(f"   sent: {bytes_to_mb(io_counters.bytes_sent):05f} MB")
            print(f"   received: {bytes_to_mb(io_counters.bytes_recv):05f} MB")
            print("=" * 30)
            time.sleep(interval)
        except (psutil.AccessDenied, psutil.ZombieProcess):
            print(f"Error: Unable to access process with PID {pid}.")
            break

if __name__ == "__main__":
    # 用法示例
    interfaces_list = get_network_interfaces()
    print("Available network interfaces:", interfaces_list)
    interface_to_monitor = input("choosse interface:")
    get_network_usage(interface_to_monitor)
    pid = int(input("enter pid"))
    get_process_network_usage(pid)