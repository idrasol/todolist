from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    """게시글 작성/수정 폼"""
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'is_notice', 'image', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '제목을 입력하세요'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': '내용을 입력하세요'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_notice': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'title': '제목',
            'content': '내용',
            'category': '카테고리',
            'is_notice': '공지사항',
            'image': '이미지',
            'file': '첨부 파일'
        }


class CommentForm(forms.ModelForm):
    """댓글 작성 폼"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': '댓글을 입력하세요'
            })
        }
        labels = {
            'content': '댓글'
        }



