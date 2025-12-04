import os
import datetime
from django.db import models
from django.contrib.auth import get_user_model

# ユーザー認証モデルを取得
User = get_user_model() 

# ファイル名生成のための関数を定義
def file_upload_path(instance, filename):
    """
    アップロードパスとファイル名を生成する。
    例: 'uploads/2025/12/04/20251204_143059_original.pdf'
    """
    
    # 1. 現在の日時を取得
    now = datetime.datetime.now()
    timestamp_str = now.strftime('%Y%m%d_%H%M%S')
    
    # 2. ファイル名から拡張子とファイル名本体を分離
    name, ext = os.path.splitext(filename)
    
    # 3. 新しいファイル名を生成 (日時 + 元の名前)
    new_filename = f"{timestamp_str}_{name}{ext}"
    
    # 4. 年/月/日 のディレクトリ構造を作成
    date_path = now.strftime('%Y/%m/%d')
    
    # 5. 最終的なパスを結合
    # 'uploads' は FileField の upload_to の '戻り値' のルートとなります。
    return os.path.join('uploads', date_path, new_filename)

class UploadedFile(models.Model):
    """アップロードされたファイルの情報とメタデータを保持するモデル"""
    
    # ファイル本体を格納するフィールド。後でAzure Storageに設定を切り替えます。
    file = models.FileField(upload_to=file_upload_path)
    
    # ユーザー認証が必要なため、誰がアップロードしたか記録
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # ファイルの説明
    description = models.CharField(max_length=255, blank=True)
    
    # アップロードされた日時
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # 管理画面などで表示されるときの名前
        return self.file.name

class FileComment(models.Model):
    """アップロードファイルに対するコメントを保持するモデル"""
    
    # どのファイルに対するコメントか
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='comments')
    
    # 誰がコメントしたか
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # コメント内容
    text = models.TextField()
    
    # コメントされた日時
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} on {self.file.name}'