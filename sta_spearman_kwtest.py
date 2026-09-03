# -*- coding: utf-8 -*-
"""
Created on Mon Nov 10 10:27:34 2025

@author: minay
"""
#帶入套件
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scikit_posthocs as sp
from pathlib import Path
from scipy.stats import spearmanr, kruskal
from itertools import combinations
from statsmodels.stats.multitest import multipletests

#路徑與參數設定
data_path = Path('檔案路徑')
target_gene = ['CDH1', 'PTK2', 'PIK3CA', 'CDH2', 'SNAI1', 'TWIST1', 
               'ZEB1', 'RAB11A', 'RAB5A', 'POU5F1'] 
target_stage = ['Stage I', 'Stage IIA', 'Stage IIB', 'Stage IIC', 
                'Stage IIIA', 'Stage IIIB', 
                'Stage IIIC', 'Stage IV']
#Kruskal-Wallis檢定
kw_target_stage = ['Stage I', 'Stage IIA', 'Stage IIIB', 
                   'Stage IIIC', 'Stage IV']

def significance_stars(fdr):
    if fdr < 0.001: return '***'
    if fdr < 0.01: return '**'
    if fdr < 0.05: return '*'
    return''

    
#相關係數計算&FDR
def compute_analysis(df, genes):
    corr_matrix = df.corr(method='spearman')#計算相關係數
    pairs = list(combinations(genes, 2))#針對每個基因計算p-value
    pvals = []
    pairs_coords = []
    for g1, g2 in pairs:
        if df[g1].std() == 0 or df[g2].std() == 0:
            p = 1.0
        else:
            _, p = spearmanr(df[g1], df[g2])
        pvals.append(p)
        pairs_coords.append((g1, g2))
    _, fdr_pvals, _, _ = multipletests(pvals, alpha=0.05, method='fdr_bh')#FDR

    
   
    #建立標註
    annot_matrix = pd.DataFrame('', index=genes, columns=genes)
    
    #建立計算結果列表
    result_list = []
    
    for (g1, g2), corr, p_val, fdr in zip(pairs_coords, 
                                          [corr_matrix.loc[p] for p in 
                                                pairs_coords], pvals, 
                                          fdr_pvals):
        stars = significance_stars(fdr)
        label = f'{corr:.3f}\n{stars}' if stars else f'{corr:.3f}'
        annot_matrix.loc[g1, g2] = label
        annot_matrix.loc[g2, g1] = label
        
        #數值存入字典
        result_list.append({
            'Gene 1':g1, 
            'Gene 2':g2, 
            'Spearman Rho': round(corr, 4), 
            'P-value': round(p_val, 4), 
            'FDR': round(fdr, 4), 
            'Significance': stars})
    result_df = pd.DataFrame(result_list)
        
    return corr_matrix, annot_matrix, result_df

#Kruskal-Wallis檢定與FDR
def compute_Kruskal_Wallis(data_dict, genes, valid_stages):
    kw_results = []
    pvals = []
    #確保有資料的分期
    stages_to_compare = [s for s in valid_stages if s in data_dict]
    #個分期單獨表現量提取為單獨list
    for gene in genes:
        groups = [data_dict[stage][gene].values for stage in 
                  stages_to_compare if gene in data_dict[stage].columns]
        if len(groups)>= 2:
            stat, p = kruskal(*groups)
            pvals.append(p)
            kw_results.append({
                'Gene':gene, 
                'H-statistic': round(stat, 4), 
                'P-value': p})
        else:
            pvals.append(np.nan)
            kw_results.append({
                'Gene': gene, 
                'H-statistic': np.nan, 
                'P-value': np.nan})
        
            
    #FDR校正
    valid_pvals = [p for p in pvals if not np.isnan(p)]
    if valid_pvals:
        _, fdr_pvals, _, _ = multipletests(valid_pvals, alpha=0.05, 
                                           method='fdr_bh')
        fdr_idx = 0
        for r in kw_results:
            if not np.isnan(r['P-value']):
                r['FDR'] = round(fdr_pvals[fdr_idx], 4)
                r['Significance'] = significance_stars(fdr_pvals[fdr_idx])
                # 把原本的 P-value四捨五入
                r['P-value'] = round(r['P-value'], 4) 
                fdr_idx += 1
            else:
                r['FDR'] = np.nan
                r['Significance'] = ''
                
    return pd.DataFrame(kw_results)
    
        
#heatmap
def plot_heatmap(corr_m, annot_m, stage, n_samples):
    fig_size = max(8, len(corr_m) * 0.9)
    plt.figure(figsize=(fig_size, fig_size * 0.8))
    mask = np.triu(np.ones_like(corr_m, dtype=bool))
    base_size = 11 if len(corr_m) <= 10 else 9
    sns.heatmap(corr_m, mask=mask, annot=annot_m, fmt="", 
                cmap='coolwarm', center=0, vmin=-1, vmax=1, 
                square=True, #強制格子為正方形
                linewidths=1, #格子間距
                cbar_kws={'shrink': .7, 'label': 'Spearman Correlation'}, 
                annot_kws={'size': base_size, 'va': 'center'})#設定字體
    
    plt.title(f'{stage} (n={n_samples})', fontsize=16, pad=20, 
              fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(rotation=0, fontsize=12)
    plt.tight_layout()
    plt.show()
    
    
try:
    crc_df = pd.read_excel(data_path, engine='openpyxl')
except FileNotFoundError:
    print('Cannot Found File')
    exit()
print('Start Analysis')

#新增字典存放清洗後df
processed_data = {}
    
  
for stage in target_stage:
    selec_genes = [g for g in target_gene if g in crc_df.columns]#篩選資料
    #選出該分期資料並移除缺失值
    mask_stage = crc_df['case_stage'] == stage
    
    #提取TPM數據並移除缺失值
    stage_df = crc_df.loc[mask_stage, selec_genes].dropna()
    
    #log2(TPM+1)
    stage_df = np.log2(stage_df + 1)
    
    #檢查樣本數(樣本數小於5不計算)
    if len(stage_df) < 5 :
        print(f"pass {stage}: Insufficient quantity (n={len(stage_df)})")
        continue
    #資料存進字典
    processed_data[stage] = stage_df
    
    print(f"\n{'='*40}")
    print(f"Processing: {stage} (n={len(stage_df)})")
    print(f"{'='*40}")
    
    corr_matrix, annot_matrix, result_df = compute_analysis(stage_df, 
                                                            selec_genes)
    print(result_df.to_string(index=False))
    print("\n")
    
    plot_heatmap(corr_matrix, annot_matrix, stage, len(stage_df))
    
#迴圈結束後執行 Kruskal-Wallis 檢定    
print(f"\n{'='*60}")
print(f"Kruskal-Wallis Test Results (Across Stages: {', '.join(kw_target_stage)})")
print(f"{'='*60}")

kw_results_df = compute_Kruskal_Wallis(processed_data, 
                                       target_gene, kw_target_stage)
print(kw_results_df.to_string(index=False))
    


#Dunn's Post-hoc Test
#KW test FDR<0.05 gene
significant_genes = kw_results_df[kw_results_df['FDR'] < 0.05]['Gene'].tolist()

if not significant_genes:
    print('Cannot Find')
else:
    stages_to_compare = [s for s in kw_target_stage if s in processed_data]
    
    for gene in significant_genes:
        print(f"\n--- Post-hoc Analysis for {gene} ---")
        
        posthoc_data = []
        for stage in stages_to_compare:
            if gene in processed_data[stage].columns:
                values = processed_data[stage][gene].values
                for v in values:
                    posthoc_data.append({'Stage': stage, 'Value': v})
                    
        df_posthoc = pd.DataFrame(posthoc_data)
        
        dunn_matrix = sp.posthoc_dunn(df_posthoc, 
                                      val_col='Value', 
                                      group_col='Stage', 
                                      p_adjust='fdr_bh')
        
        dunn_results = []
        for s1, s2 in combinations(stages_to_compare, 2): 
            if s1 in dunn_matrix.columns and s2 in dunn_matrix.columns:
                p_adj = dunn_matrix.loc[s1, s2]
                stars = significance_stars(p_adj)
                if p_adj < 0.05: 
                    dunn_results.append({
                        'Comparison': f"{s1} vs {s2}",
                        'FDR P-value': round(p_adj, 4),
                        'Significance': stars})
        
        if dunn_results:
            dunn_df = pd.DataFrame(dunn_results)
            print(dunn_df.to_string(index=False))
        else:
            print("經過 FDR 校正後，兩兩分期之間無顯著差異。")
        
        
    
    
    
    
        
        
            
            
    
    
    
    
   

        
        
        
    
