from loguru import logger
import psutil
import time
import argparse
def convert_bytes_to_unit(bytes_value, unit='MB'):
    bytes_value*=8
    units = {'B': 1, 'KB': 1024, 'MB': 1024 ** 2, 'GB': 1024 ** 3}
    return bytes_value / units[unit]

def get_network_speed(interface='eth0', interval=1, unit='MB', duration=600):
    log_file = "network_speed.log"
    logger.add(log_file, rotation="1 day")

    start_time = time.time()
    end_time = start_time + duration

    while time.time() < end_time:
        # 获取初始时间点的字节数
        initial_stats = psutil.net_io_counters(pernic=True)[interface]
        start_time_interval = time.time()

        # 等待一段时间
        time.sleep(interval)

        # 获取结束时间点的字节数
        final_stats = psutil.net_io_counters(pernic=True)[interface]
        end_time_interval = time.time()

        # 计算字节数的差异和时间的差异
        bytes_sent_diff = final_stats.bytes_sent - initial_stats.bytes_sent
        bytes_recv_diff = final_stats.bytes_recv - initial_stats.bytes_recv
        time_diff = end_time_interval - start_time_interval

        # 计算瞬时速度
        send_speed = convert_bytes_to_unit(bytes_sent_diff / time_diff, unit)
        recv_speed = convert_bytes_to_unit(bytes_recv_diff / time_diff, unit)

        logger.info(f"Send Speed: {send_speed:.2f} {unit}/second, Receive Speed: {recv_speed:.2f} {unit}/second")

def get_network_interfaces():
    interfaces = psutil.net_if_stats().keys()
    return interfaces

def get_interface_to_monitor():
    interfaces_list = get_network_interfaces()
    print("Available network interfaces:", interfaces_list)

    parser = argparse.ArgumentParser(description="Monitor network speed on a specific interface.")
    parser.add_argument("--interface", type=str, help="Specify the network interface to monitor.")

    args = parser.parse_args()

    if args.interface is None:
        interface_to_monitor = input("Choose interface: ")
    else:
        interface_to_monitor = args.interface
    return interface_to_monitor

if __name__ == "__main__":
    interface_to_monitor = get_interface_to_monitor()
    get_network_speed(interface_to_monitor)