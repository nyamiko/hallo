from django import forms
from .models import UploadedFile

class FileUploadForm(forms.ModelForm):
    """ファイルアップロード用のフォーム"""
    class Meta:
        model = UploadedFile
        # ユーザーが入力するフィールドを指定（fileとdescription）
        fields = ('file', 'description',)