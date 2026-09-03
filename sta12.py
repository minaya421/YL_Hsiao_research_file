# -*- coding: utf-8 -*-
"""
Created on Fri May 29 19:21:46 2026

@author: minay
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

tumor_data = Path(r'檔案路徑')
tumor_df = pd.read_excel(tumor_data)

target_gene = ['CDH1', 'PTK2', 'PIK3CA', 'CDH2', 'SNAI1', 'TWIST1', 
               'ZEB1', 'RAB11A', 'RAB5A', 'POU5F1'] 
 
#log2轉換
stage_col = 'case_stage'
plot_df = tumor_df.copy()
plot_df = plot_df[plot_df[stage_col] != 'Stage 0'].copy()
plot_df = plot_df.dropna(subset=target_gene + [stage_col])
for gene in target_gene:
    plot_df[gene] = np.log2(plot_df[gene] + 1)
    
#PCA
X = plot_df[target_gene]

#標準化(Z-score)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

#建立PCA模型(降二維)
pca = PCA(n_components=2)
principal_components = pca.fit_transform(X_scaled)

#主成分存入DataFrame
plot_df['PC1'] = principal_components[:, 0]
plot_df['PC2'] = principal_components[:, 1]
explained_variance = pca.explained_variance_ratio_* 100

#製作10個gene的Biplot
stage_col = 'case_stage'
stage_order = sorted(plot_df[stage_col].dropna().unique())
fig, ax = plt.subplots(figsize=(12, 9), dpi=300)

sns.scatterplot(data=plot_df, x='PC1', y='PC2', hue=stage_col, 
                hue_order=stage_order, palette='viridis', alpha=0.6, 
                edgecolor='w', ax=ax)

#10個gene的Loadings
loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
arrow_scale = 3.5

for i, feature in enumerate(target_gene):
    ax.arrow(0, 0, loadings[i, 0] * arrow_scale, 
             loadings[i, 1] * arrow_scale, 
             color='red', alpha=0.8, width=0.015, head_width=0.08)
    
    ax.text(loadings[i, 0] * arrow_scale * 1.15, 
            loadings[i, 1] * arrow_scale * 1.15, 
            feature, color='black', ha='center', va='center', 
            fontsize=12, fontweight='bold', 
            bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))
    
plt.axhline(0, color='gray', linestyle='--', alpha=0.3)
plt.axvline(0, color='gray', linestyle='--', alpha=0.3)
plt.title('PCA Biplot of 10 Core Genes in CRC', fontsize=16, pad=20)
plt.xlabel(f'Principal Component 1 ({explained_variance[0]:.1f}% Variance)', 
           fontsize=12)
plt.ylabel(f'Principal Component 2 ({explained_variance[1]:.1f}% Variance)', 
           fontsize=12)
    
plt.legend(title='Tumor Stage', bbox_to_anchor=(1.05, 1), 
           loc='upper left')
plt.tight_layout()
plt.show()


print("\n--- PC1 與 PC2 的基因權重貢獻 ---")
loadings_df = pd.DataFrame(
    pca.components_.T, 
    columns=['PC1', 'PC2'], 
    index=target_gene)
print(loadings_df.round(4))






      
 
  
    
    
    
    