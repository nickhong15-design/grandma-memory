import os
import shutil
import json
from PIL import Image

# ================= 參數設定區 =================
# 請將這兩個路徑修改為你電腦上的實際路徑 (可以使用相對路徑)
INPUT_DIR = 'D:\整理\Original_Photos'  # 你放那 120 個資料夾的地方
OUTPUT_DIR = 'D:\整理'      # 程式處理完後，要輸出的新資料夾
JSON_OUTPUT = 'timeline_data.json' # 輸出的資料庫檔名

MAX_IMAGE_SIZE = 1920  # 限制圖片最長邊為 1920 像素 (適合網頁且畫質不錯)
# ==============================================

def process_media():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timeline_data = []

    # 排序資料夾，確保時間軸是由舊到新 (或由新到舊)
    folders = sorted([f for f in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, f))])

    for folder_name in folders:
        # 解析資料夾名稱 (例如: "20230121 過年圍爐")
        parts = folder_name.split(' ', 1)
        date_str = parts[0]
        # 如果資料夾只有日期沒有標題 (例如圖中的 20220124)，就給個預設名稱
        title_str = parts[1] if len(parts) > 1 else "美好回憶" 

        input_folder_path = os.path.join(INPUT_DIR, folder_name)
        output_folder_path = os.path.join(OUTPUT_DIR, folder_name)
        
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        folder_media_list = []
        files = os.listdir(input_folder_path)
        
        print(f"正在處理: {folder_name} (共 {len(files)} 個檔案)...")

        for file_name in files:
            file_ext = file_name.split('.')[-1].lower()
            input_file_path = os.path.join(input_folder_path, file_name)
            output_file_path = os.path.join(output_folder_path, file_name)
            
            # 網頁圖片相對路徑 (給未來網站讀取用的)
            web_path = f"./Web_Photos/{folder_name}/{file_name}"

            if file_ext in ['jpg', 'jpeg', 'png']:
                # 壓縮並調整圖片大小
                try:
                    with Image.open(input_file_path) as img:
                        # 修正圖片方向 (處理手機拍攝常遇到的旋轉問題)
                        try:
                            from PIL import ImageOps
                            img = ImageOps.exif_transpose(img)
                        except:
                            pass
                        
                        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE), Image.Resampling.LANCZOS)
                        
                        # 如果是 PNG，轉存為 JPEG 會有黑底問題，所以統一存為 RGB
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                            
                        # 替換副檔名為 jpg 以統一格式並減少大小
                        output_file_path = os.path.splitext(output_file_path)[0] + '.jpg'
                        web_path = f"./Web_Photos/{folder_name}/{os.path.splitext(file_name)[0]}.jpg"
                        
                        img.save(output_file_path, "JPEG", quality=80)
                        folder_media_list.append({"type": "image", "src": web_path})
                except Exception as e:
                    print(f"  [錯誤] 圖片 {file_name} 處理失敗: {e}")

            elif file_ext in ['mp4', 'mov', 'webm']:
                # 影片直接複製
                try:
                    shutil.copy2(input_file_path, output_file_path)
                    folder_media_list.append({"type": "video", "src": web_path})
                except Exception as e:
                    print(f"  [錯誤] 影片 {file_name} 複製失敗: {e}")

        # 如果這個資料夾裡有成功處理的檔案，才加入時間軸資料中
        if folder_media_list:
            timeline_data.append({
                "date": date_str,
                "title": title_str,
                "folder": folder_name,
                "media": folder_media_list
            })

    # 將結果寫入 JSON 檔案
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(timeline_data, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ 處理完成！已成功輸出至 {OUTPUT_DIR}")
    print(f"✅ 資料庫檔案已生成：{JSON_OUTPUT}")

if __name__ == "__main__":
    process_media()