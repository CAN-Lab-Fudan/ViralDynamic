import networkx as nx
import time
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import matplotlib.pyplot as plt
import scienceplots

from parameters import parameter_parser
from trainer import Trainer
from utils import threshold, threshold_SQS, UCM_SF_network, ER_Random_Graph
from dataset import Just_Test
from SQS_simulation import DynamicsSIS


# 比较各种不同的平均方式，每次进行重复实验的同时生成图。
def main():
    args = parameter_parser()
    avg_k = 4
    gamma = 2.25
    group_name = f'Erdos_Renyi_Graph_N={args.N}'
    model_path=os.path.join(args.file_path, group_name, args.model_path)
    threshold_prime = []
    threshold_sqs = []
    lambda_HMF = []
    lambda_QMF = []
    avg_prime = []
    avg_sqs = []
    avg_HMF = []
    avg_QMF = []
    times = 101
    for i in tqdm(range(times)):
        # G = ER_Random_Graph(N=args.N, avg_k=avg_k)
        G = UCM_SF_network(N=args.N, gama=gamma)
        threshold_QMF, threshold_HMF = threshold(G=G)
        lambda_HMF.append(threshold_HMF)
        lambda_QMF.append(threshold_QMF)
        cur_group_name = f'ER_Graph_N={args.N}_gamma={gamma}'
        trainer = Trainer(args=args, group_name=cur_group_name)
        SQS = DynamicsSIS(
            Graph=G,
            beta=(max(0.01, threshold_HMF-0.1), min(threshold_HMF+0.1, 1)),
            file_path=args.file_path,
            group_name=cur_group_name,
            numbers_every_miu=30,
        )
        SQS.multiprocess_simulation()
        just = Just_Test(
            file_path=args.file_path,
            dataset_path=cur_group_name,
        )
        lambda_c_pre, df_out, df_var = trainer.test_and_get_threshold(
            model_path=model_path,
            group_name=cur_group_name,
        )
        lambda_sqs = threshold_SQS(file_path=args.file_path, group_name=cur_group_name)
        threshold_prime.append(lambda_c_pre)
        threshold_sqs.append(lambda_sqs)
        
        if i % 5 == 0:
            avg_prime.append(np.mean(threshold_prime))
            avg_sqs.append(np.mean(threshold_sqs))
            avg_HMF.append(np.mean(lambda_HMF))
            avg_QMF.append(np.mean(lambda_QMF))

    
    x = np.arange(len(avg_prime)) * 5
    with plt.style.context(['science', 'ieee']):
        figure = plt.figure()
        # plt.title(r'The Fluctuation on UCM\_SF Graph (N={},$\gamma$={})'.format(args.N, gamma))
        plt.plot(x , avg_prime, ls=':', marker='o', ms=5, color='blue', label=r'$\lambda_c^\prime$')
        # plt.plot(x, avg_sqs, ls=':', color='green', label=r'$\lambda_c^{SQS}$')
        plt.plot(x, avg_HMF, ls='--', color='red', label=r'$\lambda_c^{HMF}$')
        plt.plot(x, avg_QMF, ls='-.', color='green', label=r'$\lambda_c^{QMF}$')

        plt.xlabel(r'$\eta$')
        plt.ylabel(r'$\lambda$')

        plt.ylim((0.05, 0.15))
        # plt.text(0.05, 0.95, '(b)', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
        # plt.text(0.05, 0.95, '(a)', horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)

        plt.legend()
        try:
            plt.savefig(os.path.join('Validation_Average', 'diff_network.png'))
        except OSError:
            os.mkdir('Validation_Average')
            plt.savefig(os.path.join('Validation_Average', 'diff_network.png'))

        plt.close()


if __name__ == '__main__':
    main()
