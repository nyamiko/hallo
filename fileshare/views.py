from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, Http404

from .models import UploadedFile, FileComment
from .forms import FileUploadForm, CommentForm

@login_required
# ファイル一覧とアップロードを処理するビュー
def file_list_and_upload(request):
    # アップロード処理は変更なし
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.uploaded_by = request.user
            file_instance.save()
            return redirect('file_list')
    else:
        form = FileUploadForm()
    
    # ★ 権限に基づくファイルフィルタリング ★
    if request.user.is_superuser:
        # 管理者（is_superuser=True）はすべてのファイルを見える
        files = UploadedFile.objects.all().order_by('-uploaded_at')
    else:
        # 通常ユーザーは、管理者がアップロードしたファイル または 自分がアップロードしたファイルのみ見える
        files = UploadedFile.objects.filter(
            models.Q(uploaded_by__is_superuser=True) | models.Q(uploaded_by=request.user)
        ).order_by('-uploaded_at')
        
    context = {
        'files': files,
        'form': form,
    }
    return render(request, 'fileshare/file_list.html', context)

@login_required
# ダウンロード処理のビュー
def file_download(request, pk):
    file_obj = get_object_or_404(UploadedFile, pk=pk)
    user = request.user

    # ★ 権限チェックロジック ★
    can_download = False
    if user.is_superuser:
        # 1. 管理者はダウンロード可能
        can_download = True
    elif file_obj.uploaded_by == user:
        # 2. 自分がアップロードしたファイルはダウンロード可能
        can_download = True
    elif file_obj.uploaded_by.is_superuser:
        # 3. 管理者がアップロードしたファイルはダウンロード可能
        can_download = True

    if not can_download:
        # 権限がない場合は404エラー（存在しないファイルとして扱う）
        raise Http404("このファイルにアクセスする権限がありません。")

    # ファイルの配信処理（実際にはファイルシステムから読み込む）
    # DjangoのFileFieldのopenとread機能を利用
    response = HttpResponse(file_obj.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
    return response

@login_required
# ファイル詳細・コメントビューの
def file_detail_and_comment(request, pk):
    file_obj = get_object_or_404(UploadedFile, pk=pk)
    user = request.user

    # ★ 権限チェック（ダウンロードビューと同じロジック）
    can_access = False
    if user.is_superuser or file_obj.uploaded_by == user or file_obj.uploaded_by.is_superuser:
        can_access = True
    
    if not can_access:
        raise Http404("このファイルにアクセスする権限がありません。")

    # コメント投稿処理（POSTリクエスト）
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_instance = comment_form.save(commit=False)
            comment_instance.file = file_obj
            comment_instance.user = request.user
            comment_instance.save()
            return redirect('file_detail', pk=pk)
    else:
        # GETリクエストの場合、空のフォームを作成
        comment_form = CommentForm()

    # コメント一覧を取得 (related_name='comments' を使用)
    comments = file_obj.comments.all().order_by('created_at')

    context = {
        'file': file_obj,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'fileshare/file_detail.html', context)