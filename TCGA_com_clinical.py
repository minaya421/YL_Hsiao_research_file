# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 13:13:34 2024

@author: minay
"""
import os
import pandas as pd


file_input_path = '輸入資料夾路徑'
file_output_path = '輸出資料夾路徑'
if not os.path.exists(file_input_path):
    raise FileNotFoundError(f'Input file not found:{file_input_path}')

df = pd.read_excel(file_input_path)

sel_columns = ['bcr_patient_barcode', 
               'ajcc_tumor_pathologic_pt', 
               'ajcc_nodes_pathologic_pn', 
               'ajcc_metastasis_pathologic_pm',
               'ajcc_pathologic_tumor_stage', 
               'ajcc_staging_edition', 
               'ajcc_7th_final_stage_v3']#自行加入需要的欄位

mis_columns = [col for col in sel_columns if col not in df.columns]
if mis_columns:
    raise ValueError('Missing columns:\n{}'.format('\n'.join(mis_columns)))
       
sel_df = df[sel_columns]

   
sel_df.to_excel(file_output_path, index=False)

print('Finish')                     
    
    

    
    
