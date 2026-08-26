# -*- coding: utf-8 -*-
"""
Created on Mon Apr  8 09:53:17 2024

@author: minay
"""

import pandas as pd
import os

#指定的輸入文件夾路徑
input_path = '你的檔案路徑'
#指定的輸出文件夾路徑
output_path = '你要輸出的檔案路徑'

#讀取所有tsv檔案
for root, dirs, files in os.walk(input_path):
    for filename in files:
        if filename.endswith('.tsv'):
           filepath = os.path.join(root, filename)
           df = pd.read_csv(filepath, sep='\t')
        #改變檔名並存入指定路徑
        output_filename = os.path.splitext(filename)[0] + '.xlsx'
        output_filepath = os.path.join(output_path, output_filename)
        
        with pd.ExcelWriter(output_filepath, engine='openpyxl') as writer:
            df.to_excel(writer, index=True)#保留索引列
            worksheet = writer.sheets['Sheet1']#設定欄寬
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                worksheet.column_dimensions[column].width = adjusted_width
                            
print("complete.")