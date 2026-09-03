# -*- coding: utf-8 -*-
"""
Created on Thu May 28 20:25:30 2026

@author: minay
"""
#載入套件
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.stats import spearmanr, mannwhitneyu
from statsmodels.stats.multitest import multipletests

#設定路徑
normal_data = Path(r'c:\TCGA_NEW\gene_data_normal_newversion.xlsx')
tumor_data = Path(r'c:\TCGA_NEW\gene_data_tumor_newversion.xlsx')


normal_df = pd.read_excel(normal_data)
tumor_df = pd.read_excel(tumor_data)

#定義目標基因
target_gene = ['CDH1', 'PTK2', 'PIK3CA', 'CDH2', 'SNAI1', 'TWIST1', 
               'ZEB1', 'RAB11A', 'RAB5A', 'POU5F1'] 

#正常樣本的Spearman
corr_matrix = pd.DataFrame(index=target_gene, columns=target_gene, 
                            dtype=float)
pval_matrix = pd.DataFrame(index=target_gene, columns=target_gene, 
                            dtype=float)
annot_matrix = pd.DataFrame(index=target_gene, columns=target_gene, 
                            dtype=str)

for i in target_gene:
    for j in target_gene:
        corr, pval = spearmanr(normal_df[i].dropna(), 
                               normal_df[j].dropna())
        corr_matrix.loc[i, j] = corr
        pval_matrix.loc[i, j] = pval
        
        
        stars = ""
        if pval < 0.001: stars = '***'
        elif pval < 0.01: stars = '**'
        elif pval < 0.05: stars = '*'
       
        if i == j:
            annot_matrix.loc[i, j] = ""
        else:
            annot_matrix.loc[i, j] = f"{corr:.2f}\n{stars}" if stars else f"{corr:.2f}"
            
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

#熱圖製作
plt.figure(figsize=(10, 8), dpi=300)

sns.heatmap(corr_matrix, mask=mask, annot=annot_matrix, 
           fmt="", 
           cmap='coolwarm', center=0, vmin=-1, vmax=1, 
           square=True, 
           linewidths=1,
           cbar_kws={'shrink': .7, 'label': 'Spearman Correlation'}) 

plt.title(f'Spearman Correlation Network in Normal Tissues (n={len(normal_df)})', 
          fontsize=16, pad=20)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(rotation=0, fontsize=12)
plt.tight_layout()
plt.show()


#正常樣本與腫瘤樣本的Mann-Whitney U 檢定
mwu_result = []
for gene in target_gene:
    normal_expr = normal_df[gene].dropna()
    tumor_expr = tumor_df[gene].dropna()
    stat, pval = mannwhitneyu(tumor_expr, normal_expr, alternative='two-sided')
    mwu_result.append({'Gene': gene, 
                       'Median_Normal': normal_expr.median(),
                       'Median_Tumor': tumor_expr.median(),
                       'U_Statistic': stat,
                       'P_value': pval})
    
mwu_df = pd.DataFrame(mwu_result)
#FDR校正
mwu_df['FDR'] = multipletests(mwu_df['P_value'], method='fdr_bh')[1]
mwu_df = mwu_df.sort_values(by='FDR').reset_index(drop=True)  

#數據輸出
def get_stars(fdr):
    if fdr < 0.001: return '***'
    elif fdr < 0.01: return '**'
    elif fdr < 0.05: return '*'
    else:
        return 'ns'
    
mwu_df['Significance'] = mwu_df['FDR'].apply(get_stars)

def format_pvalue(val):
    if val < 0.001:
        return '<0.001'
    else:
        return f'{val:.3f}'
    
mwu_df['P_value'] = mwu_df['P_value'].apply(format_pvalue)
mwu_df['FDR'] = mwu_df['FDR'].apply(format_pvalue)

mwu_df['Median_Normal'] = mwu_df['Median_Normal'].round(3)
mwu_df['Median_Tumor'] = mwu_df['Median_Tumor'].round(3)


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
print("\n--- Mann-Whitney U ---")
print(mwu_df.to_string(index=False))
    
    

          

            
        
                               