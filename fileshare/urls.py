from django.urls import path
from . import views

urlpatterns = [
    path('', views.file_list_and_upload, name='file_list'),
    
    # ★ 詳細ページURLを追加
    path('file/<int:pk>/', views.file_detail_and_comment, name='file_detail'),

    # ★ ダウンロードURLを追加
    # pk（Primary Key）でファイルオブジェクトを一意に特定
    path('download/<int:pk>/', views.file_download, name='file_download'),
]