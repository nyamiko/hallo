from django.db import models
from django.contrib.auth import get_user_model

# ユーザー認証モデルを取得
User = get_user_model() 

class UploadedFile(models.Model):
    """アップロードされたファイルの情報とメタデータを保持するモデル"""
    
    # ファイル本体を格納するフィールド。後でAzure Storageに設定を切り替えます。
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    
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