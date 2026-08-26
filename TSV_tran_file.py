# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:21:55 2026

@author: minay
"""

import os
import pandas as pd

#直接指定該特定檔案的完整絕對路徑
input_filepath = r'你下載的gdc_sample_sheet'

#指定輸出的資料夾路徑
output_path = r'c:\TCGA_NEW'

#確保輸出資料夾存在，如不存在則自動建立
if not os.path.exists(output_path):
    os.makedirs(output_path)

#從完整路徑中提取檔案名稱 
filename = os.path.basename(input_filepath)

#改變檔名並組合出最終的輸出路徑
output_filename = os.path.splitext(filename)[0] + '.xlsx'
output_filepath = os.path.join(output_path, output_filename)

#直接讀取該檔案(不需要迴圈)
df = pd.read_csv(input_filepath, sep='\t')

# 寫入Excel並調整欄寬
with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
    df.to_excel(writer, index=True) # 保留索引列
    worksheet = writer.sheets['Sheet1']
    
    # 設定欄寬
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = (max_length + 2) * 1.2
        worksheet.column_dimensions[column].width = adjusted_width
                    
print('Finish')