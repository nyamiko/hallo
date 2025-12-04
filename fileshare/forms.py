from django import forms
from .models import UploadedFile, FileComment

class FileUploadForm(forms.ModelForm):
    """ファイルアップロード用のフォーム"""
    class Meta:
        model = UploadedFile
        # ユーザーが入力するフィールドを指定（fileとdescription）
        fields = ('file', 'description',)

        labels = {
                    'file': '',
                    'description': 'ファイルの説明',
                }

class CommentForm(forms.ModelForm):
    """コメント投稿用のフォーム"""
    class Meta:
        model = FileComment
        # userとfileはビューで自動設定するため、ユーザーはtextのみ入力
        fields = ('text',)
        
        labels = {
            'text': '',
        }

        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }