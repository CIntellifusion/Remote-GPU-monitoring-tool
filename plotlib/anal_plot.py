
import re
import matplotlib.pyplot as plt
import os
import  pandas as pd
from time import time
from scipy.ndimage.filters import gaussian_filter1d
import numpy as np
import cv2
# 2023-12-24 16:00:09.118 | INFO     | __main__:main:131 - step: [30/160001] tex_loss:0.147909 lmk_loss:0.234621 all_loss:0.382530

def parse_line(log_message= "2023-12-24 16:00:09.118 | INFO | __main__:main:131 - step: [30/160001] tex_loss:0.147909 lmk_loss:0.234621 all_loss:0.382530"):
    log_message = log_message.replace("\n","")
    step_pattern = r"step: \[(\d+)/(\d+)\]"
    # Use re.search to find the pattern in the log message
    match  = re.search(step_pattern, log_message)
    if match is None:
        return None
    else:
        crt_step,tt_step = match.groups()
    # Define a regular expression pattern to capture any loss name and its value
    loss_pattern = r"(\w+_loss):([\d.]+)"
    # Use re.findall to find all occurrences of the pattern in the log message
    losses = re.findall(loss_pattern, log_message)
    lossdict = {k:float(v) for k,v in losses}
    return  crt_step,tt_step,lossdict


def plot_losses(log_file_path, train_name,save_folder):
    df = pd.DataFrame()
    steps = []
    # 逐行读取 log 文件并解析
    t0 =time()
    with open(log_file_path, 'r') as file:
        for line in file:
            # 解析每一行的信息
            parsed_info = parse_line(line)
            if parsed_info:
                step, total_steps, losses = parsed_info
                # file into df , index set to step
                df = df._append(losses, ignore_index=True)
                steps.append(step)
    t1 = time()
    print(f"take {t1-t0} to process {len(steps)} line")
    # 设置图表的整体样式
    plt.rcParams['figure.figsize'] = [10, 6]
    df['step'] = steps
    # 绘制并保存图表
    os.makedirs(save_folder,exist_ok=True)

    for loss_type in losses.keys():

        loss = np.array(df[loss_type])
        sm_loss = gaussian_filter1d(loss,sigma=4)
        subset_df = df[['step', loss_type]]
        subset_df['sm_loss'] = sm_loss
        # Plot using ggplot style
        plt.style.use('ggplot')

        # Create a line plot
        # subset_df.plot(x='step', y=loss_type, label=loss_type.capitalize(),color='red')#color
        # subset_df.plot(x='step', y='sm_loss', label='sm_loss'.capitalize(),color='blue')
        fig, ax = plt.subplots(figsize=(8, 6))

        # Plot 'tex_loss' with red color
        subset_df.plot(x='step', y=loss_type, label=loss_type, color='#F3401A', marker='o', ax=ax)
        # Plot 'sm_loss' with blue color
        subset_df.plot(x='step', y='sm_loss', label=f'sm_{loss_type}', color='#3A2CBA', marker='o', ax=ax)

        # Set labels and title
        plt.xlabel('Step')
        plt.ylabel(loss_type.capitalize())
        plt.title(f'{train_name} {loss_type.capitalize()} over Steps')

        # Display legend
        plt.legend()
        # 保存图表到指定路径
        save_filename = f'{train_name}_{loss_type.lower()}_plot.png'
        save_path = os.path.join(save_folder, save_filename)
        plt.savefig(save_path)
        plt.close()
    all_plot = []
    for loss_type in losses.keys():
        save_filename = f'{train_name}_{loss_type.lower()}_plot.png'
        save_path = os.path.join(save_folder, save_filename)
        sub = cv2.imread(save_path)
        all_plot.append(sub)
    cv2.imwrite(os.path.join(save_folder,f'{train_name}_summary_plot.png'),np.concatenate(all_plot,axis=1))
import argparse
if __name__ == "__main__":
    if False:
        print(parse_line())
        exit()
    parser = argparse.ArgumentParser(description="Plot training losses from a log file.")
    parser.add_argument("--log_file",'-f', type=str, help="Path to the log file.")
    parser.add_argument("--save_folder",'-s', type=str, default="./plots", help="Folder to save the plots.")


    args = parser.parse_args()
    log_file_path = args.log_file
    save_folder = args.save_folder
    train_name = log_file_path.split("/")[-2]
    plot_losses(log_file_path,train_name ,save_folder)