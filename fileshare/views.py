from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UploadedFile
from .forms import FileUploadForm

# ファイル一覧とアップロードを処理するビュー
# @login_required により、ログインしていないユーザーはアクセスできなくなります
@login_required
def file_list_and_upload(request):
    # ファイルアップロード処理（POSTリクエスト）
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # フォームを保存するが、commit=Falseで一旦データベースへの保存を保留
            file_instance = form.save(commit=False)
            # アップロードユーザーを現在のログインユーザーに設定
            file_instance.uploaded_by = request.user
            # データベースに保存
            file_instance.save()
            return redirect('file_list')
    
    # ファイル一覧表示処理（GETリクエスト）
    else:
        form = FileUploadForm()
    
    # すべてのファイルを取得
    files = UploadedFile.objects.all().order_by('-uploaded_at')
    
    context = {
        'files': files,
        'form': form,
    }
    return render(request, 'fileshare/file_list.html', context)