# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 17:38:04 2026

@author: minay
"""

import os
import pikepdf


file_path = r"你的資料夾路徑"
temp_path = r"站存檔路徑" 


with pikepdf.Pdf.open(file_path) as pdf:
    
    #設定權限：禁止複製 (extract)、禁止一般修改 (modify_other)、禁止增刪頁面 (modify_assembly)
    permissions = pikepdf.Permissions(
        extract=False, 
        modify_other=False, 
        modify_assembly=False
    )
    
    #將結果儲存成暫存檔案
    pdf.save(temp_path, encryption=pikepdf.Encryption(
        user="",              
        owner="random_pass",  
        allow=permissions))

#原檔案已解除鎖定，暫存檔覆蓋原始檔案
os.replace(temp_path, file_path)

print(f"change_finishi：{file_path}")
print(f"change_finishi_clear：{file_path}")