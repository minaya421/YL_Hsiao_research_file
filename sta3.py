# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 15:56:10 2024

@author: minay
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import spearmanr
from pathlib import Path

#路徑設定
tumor_data_path = Path('輸入檔案路徑')
normal_data_path = Path('輸入檔案路徑')

#目標基因
target_gene = ['CDH1', 'PTK2', 'PIK3CA', 'CDH2', 'SNAI1', 'TWIST1', 
               'ZEB1', 'RAB11A', 'RAB5A', 'POU5F1']

tumor_df = pd.read_excel(tumor_data_path)
normal_df = pd.read_excel(normal_data_path)

#數據清理
tumor_df = tumor_df.dropna(subset = ['case_stage']).copy()
normal_df['case_stage'] = 'Normal'

#垂直合併數據
combined_df = pd.concat([tumor_df, normal_df], ignore_index=True)


#定義分期順序
order_stage = ['Normal', 'Stage I', 'Stage IIA', 'Stage IIB', 'Stage IIC', 
               'Stage IIIA', 'Stage IIIB', 
               'Stage IIIC', 'Stage IV']

combined_df['case_stage'] = pd.Categorical(
    combined_df['case_stage'], categories=order_stage, 
    ordered=True)

#篩除異常值
combined_df = combined_df.dropna(subset=['case_stage'])


#計算個分期樣本數及生成x軸標籤
stage_counts = combined_df['case_stage'].value_counts()

#建立新欄位
combined_df['stage_with_n'] = combined_df['case_stage'].apply(
    lambda x: f'{x}\n(n={stage_counts[x]})')

#樣本數大於0才會呈現
order_stage_with_n = [f'{stage}\n(n={stage_counts[stage]})'
                      for stage in order_stage if stage_counts[stage] > 0]

#繪製箱型圖
for gene in target_gene:
    if gene not in combined_df.columns:
        print('CANNOT FIND')
        continue

    #log2轉換
    combined_df['log2_tpm'] = np.log2(combined_df[gene] + 1)


    plt.figure(figsize=(10, 6))
    sns.boxplot(data=combined_df, 
                x='stage_with_n', 
                y='log2_tpm', 
                order=order_stage_with_n, 
                palette='Set2')
    
    plt.xlabel('TNM stage', fontsize=12)
    plt.ylabel(f'{gene} Expression ($log_2$(TPM + 1))', fontsize=12)
    plt.title(f'Distribution of {gene} Expression Across TNM Stages', 
              fontsize=14)
    plt.tight_layout()
    plt.show()

