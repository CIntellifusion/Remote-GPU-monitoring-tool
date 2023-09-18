import argparse
import paramiko
import os 
from time import sleep 
from torch.utils.tensorboard import SummaryWriter
class Monitor():
    def __init__(self,conf ) -> None:
        # Access configuration values
        self.server_ip = conf.server_ip
        self.username = conf.username
        self.password = conf.password
        self.verbose = conf.verbose
        self.logdir = conf.logdir
        self.gpu_id = conf.gpu_id
        self.stop_mode = conf.stop_mode 
        self.global_step = 0
        self.max_step = conf.max_step 
        self.interval = conf.interval
        self.writer = SummaryWriter(log_dir=conf.logdir)
    def parse_info(self,gpu_info,query_id):
        infos = gpu_info.split("\n")[:-1]
        infos = [i.replace(' ','').split(',') for i in infos]
        infos = [[float(i) for i in j] for j in infos]
        for id,info in zip(query_id.split(","),infos):
            self.writer.add_scalar(f"GPU{id}/Mem %",info[0]/info[1],global_step=self.global_step)
            self.writer.add_scalar(f"GPU{id}/Util %",info[2]/1024,global_step=self.global_step)
        string = [f"GPU {id} Mem [{(round(info[0]/1024,2))}/{int(info[1])//1024}] GB , Uitl {info[2]}%\n" for id,info in zip(query_id,infos)]
        return "".join(string)
    def ssh_gpu_monitoring(self):
        try:
            gpu_id = self.gpu_id
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
                if self.global_step>self.max_step and self.stop_mode=="max_step":
                    break
                sleep(self.interval)

            # 关闭SSH连接
            ssh_client.close()
            return gpu_info
        except Exception as e:
            print(f"连接到服务器时发生错误: {e}")


def main():
    import omegaconf as omega
    # Load the YAML configuration file
    conf = omega.OmegaConf.load("config.yaml")
    monitor = Monitor(conf)
    monitor.ssh_gpu_monitoring()
if __name__ == "__main__":
    main()


# python script.py --server_ip "your_server_ip" --username "your_username" --password "your_password" --verbose 1 --logdir "./your_logs_directory" --gpu_id 0,1

