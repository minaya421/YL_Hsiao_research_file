# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 15:14:39 2024

@author: minay
"""

import os
import glob
import pandas as pd

TARGET_GENE = ['你的基因標的']
folder_path = '輸入資料夾路徑'
output_file_path = '輸出資料夾路徑'
sample_sheet_path = 'gdc_sample_sheet路徑'

df_sheet = pd.read_excel(sample_sheet_path)
file_to_case = dict(zip(df_sheet['File Name'], df_sheet['Case ID']))

file_list = glob.glob(os.path.join(folder_path, '**', '*.tsv'), 
                      recursive=True)

data = []
idx = ['case_id', 'gene_name', 'tpm_unstranded']

for count, file_path in enumerate(file_list, 1):
    try:
        file_name = os.path.basename(file_path)
        
        df1 = pd.read_csv(
            file_path, 
            sep='\t', 
            skiprows=1,
            usecols=['gene_name', 'tpm_unstranded'],
            low_memory=False)
        
        target_gene_row = df1[df1['gene_name'].isin(TARGET_GENE)]
        
        if target_gene_row.empty:
            print('Error')
            
        else:
            case_id = file_to_case.get(file_name, file_name.split('.')[0])
            
            
            for _, row in target_gene_row.iterrows():
                gene_name = row['gene_name']
                tpm_val = row['tpm_unstranded']
            
                individual_list = [case_id, gene_name, tpm_val]
                data.append(individual_list)
                
         
    except Exception as e:
            print('Not found')
        
            
df2 = pd.DataFrame(data, columns=idx )

df_matrix = df2.pivot(index='case_id', 
                      columns='gene_name', values='tpm_unstranded')

df_matrix = df_matrix.reset_index()

df_matrix.columns.name = None

df_matrix.to_excel(output_file_path, index=False)

print('Finish')
        
    

