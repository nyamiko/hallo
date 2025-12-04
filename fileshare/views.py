from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, Http404, FileResponse

from .models import UploadedFile, FileComment
from .forms import FileUploadForm, CommentForm
from django.contrib import messages
import os
from urllib.parse import quote # URLエンコードのために import します

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
    # ... (権限チェック終わり) ...

    original_filename = os.path.basename(file_obj.file.name)
    encoded_filename = quote(original_filename)

    response = FileResponse(file_obj.file, as_attachment=True)
    response['Content-Disposition'] = (
        f"attachment; filename=\"download\"; filename*=UTF-8''{encoded_filename}"
    )
    return response

    
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

@login_required # ログインしているユーザーのみが削除できるようにする
def file_delete(request, pk):
    # pkに基づいてファイルを検索。見つからなければ404エラー
    file_to_delete = get_object_or_404(UploadedFile, pk=pk)

    # セキュリティ考慮事項: アップロードしたユーザーのみが削除できるかチェックする
    if file_to_delete.uploaded_by != request.user:
        messages.error(request, "他のユーザーがアップロードしたファイルを削除することはできません。")
        return redirect('file_list') # ファイル一覧画面のURL名に置き換えてください

    if request.method == 'POST':
        # データベースからレコードと関連するストレージ上のファイルの両方を削除
        file_to_delete.delete()
        messages.success(request, f'ファイル "{file_to_delete.file.name}" は正常に削除されました。')
        
        # 削除後にファイル一覧画面（または適切な画面）にリダイレクト
        return redirect('file_list') # ファイル一覧画面のURL名に置き換えてください
    
    # POSTリクエストでない場合は、通常は削除確認画面を表示しますが、
    # シンプルなアプリでは直接一覧へリダイレクトする場合もあります。
    # 削除確認を挟む場合は、ここを修正し、対応するテンプレートを作成してください。
    
    # 今回は一覧画面の削除ボタンから直接POST送信することを想定し、
    # 確認画面をスキップして、ファイル一覧に戻します。
    return redirect('file_list')