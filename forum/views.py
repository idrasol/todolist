from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Post, Comment
from .forms import PostForm, CommentForm


def post_list(request):
    """게시글 목록"""
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    posts = Post.objects.all()
    
    # 카테고리 필터링
    if category_filter:
        posts = posts.filter(category=category_filter)
    
    # 검색 기능
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # 페이지네이션
    paginator = Paginator(posts, 5)  # 페이지당 5개
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'category_filter': category_filter,
        'category_choices': Post.CATEGORY_CHOICES,
    }
    return render(request, 'forum/post_list.html', context)


def post_detail(request, pk):
    """게시글 상세보기"""
    post = get_object_or_404(Post, pk=pk)
    
    # 조회수 증가 (작성자는 제외)
    if request.user != post.author:
        post.increase_views()
    
    # 댓글 목록
    comments = post.comments.all()
    
    # 좋아요 여부 확인
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(pk=request.user.pk).exists()
    
    # 댓글 작성
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, '댓글이 작성되었습니다.')
            return redirect('forum:post_detail', pk=post.pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
        'is_liked': is_liked,
    }
    return render(request, 'forum/post_detail.html', context)


@login_required
def post_create(request):
    """게시글 작성"""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            # 일반 사용자는 공지사항 작성 불가
            if not request.user.is_superuser:
                post.is_notice = False
            post.save()
            messages.success(request, '게시글이 작성되었습니다.')
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = PostForm()
    
    context = {
        'form': form,
    }
    return render(request, 'forum/post_form.html', context)


@login_required
def post_update(request, pk):
    """게시글 수정"""
    post = get_object_or_404(Post, pk=pk)
    
    # 작성자 또는 관리자만 수정 가능
    if post.author != request.user and not request.user.is_superuser:
        messages.error(request, '수정 권한이 없습니다.')
        return redirect('forum:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            # 일반 사용자는 공지사항 작성 불가
            if not request.user.is_superuser:
                post.is_notice = False
            post.save()
            messages.success(request, '게시글이 수정되었습니다.')
            return redirect('forum:post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    
    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'forum/post_form.html', context)


@login_required
def post_delete(request, pk):
    """게시글 삭제"""
    post = get_object_or_404(Post, pk=pk)
    
    # 작성자 또는 관리자만 삭제 가능
    if post.author != request.user and not request.user.is_superuser:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('forum:post_detail', pk=post.pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다.')
        return redirect('forum:post_list')
    
    context = {
        'post': post,
    }
    return render(request, 'forum/post_confirm_delete.html', context)


@login_required
def comment_delete(request, pk):
    """댓글 삭제"""
    comment = get_object_or_404(Comment, pk=pk)
    
    # 작성자 또는 관리자만 삭제 가능
    if comment.author != request.user and not request.user.is_superuser:
        messages.error(request, '삭제 권한이 없습니다.')
        return redirect('forum:post_detail', pk=comment.post.pk)
    
    post_pk = comment.post.pk
    comment.delete()
    messages.success(request, '댓글이 삭제되었습니다.')
    return redirect('forum:post_detail', pk=post_pk)


@login_required
@require_POST
def post_like(request, pk):
    """게시글 좋아요/좋아요 취소"""
    post = get_object_or_404(Post, pk=pk)
    
    if post.likes.filter(pk=request.user.pk).exists():
        # 이미 좋아요를 눌렀으면 취소
        post.likes.remove(request.user)
        is_liked = False
    else:
        # 좋아요 추가
        post.likes.add(request.user)
        is_liked = True
    
    return JsonResponse({
        'success': True,
        'is_liked': is_liked,
        'total_likes': post.total_likes()
    })
