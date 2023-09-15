import argparse
import paramiko
import os 
from time import sleep 
from torch.utils.tensorboard import SummaryWriter
class Monitor():
    def __init__(self,path,server_ip ,username ,password,verbose = 0 ) -> None:
        self.verbose = verbose
        self.path = path 
        self.writer = SummaryWriter(log_dir=path)
        self.server_ip = server_ip
        self.username = username
        self.password = password
        self.global_step = 0 
        self.max_step = 100000
        self.interval = 1
    def parse_info(self,gpu_info,query_id):
        infos = gpu_info.split("\n")[:-1]
        infos = [i.replace(' ','').split(',') for i in infos]
        infos = [[float(i) for i in j] for j in infos]
        for id,info in zip(query_id,infos):
            self.writer.add_scalar(f"GPU{id}/Mem %",info[0]/info[1],global_step=self.global_step)
            self.writer.add_scalar(f"GPU{id}/Util %",info[2]/1024,global_step=self.global_step)
        string = [f"GPU {id} Mem [{(round(info[0]/1024,2))}/{int(info[1])//1024}] GB , Uitl {info[2]}%\n" for id,info in zip(query_id,infos)]
        return "".join(string)
    def ssh_gpu_monitoring(self,gpu_id = "0,1,2,3"):
        try:
            # 建立SSH连接
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_client.connect(self.server_ip, username=self.username, password=self.password)

            # 执行nvidia-smi命令来获取GPU信息
            while True:
                #nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits --query-compute-apps
                _, stdout, _ = ssh_client.exec_command(f"nvidia-smi -i {gpu_id} --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits --query-compute-apps")
                gpu_info = stdout.read().decode()

                # print("GPU 使用情况:")
                new_info = self.parse_info(gpu_info,gpu_id)
                if self.verbose:
                    print(new_info)
                self.global_step+=1
                if self.global_step>self.max_step:
                    break
                sleep(self.interval)

            # 关闭SSH连接
            ssh_client.close()
            return gpu_info
        except Exception as e:
            print(f"连接到服务器时发生错误: {e}")


def main():
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="My GPU Utilization Script")

    # 添加需要的参数
    parser.add_argument("--server_ip", type=str, default="xxxxx", help="Server IP address")
    parser.add_argument("--username", type=str, default="xxxxx", help="Username")
    parser.add_argument("--password", type=str, default="Newxxx", help="Password")
    parser.add_argument("--verbose", type=int, default=0, help="Verbose level (0, 1, 2, ...)")
    parser.add_argument("--logdir", type=str, default="./logs", help="Log directory")
    parser.add_argument("--gpu_id", type=str, default="0", help="target gpus (0,1,2)")

    # 解析命令行参数
    args = parser.parse_args()

    # 输出解析后的参数
    monitor = Monitor(args.logdir,args.server_ip,args.username, args.password,args.verbose)
    monitor.ssh_gpu_monitoring(args.gpu_id)
if __name__ == "__main__":
    main()


# python script.py --server_ip "your_server_ip" --username "your_username" --password "your_password" --verbose 1 --logdir "./your_logs_directory" --gpu_id 0,1

