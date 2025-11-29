from django.urls import path
from . import views

urlpatterns = [
    # トップページ（ファイル一覧とアップロードフォームを表示）
    path('', views.file_list_and_upload, name='file_list'),
    
    # ここにダウンロード、コメント機能のURLを今後追加します
]