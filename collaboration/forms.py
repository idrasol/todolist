from django import forms
from .models import Board, Post


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '보드 제목을 입력하세요'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': '보드 제목',
            'is_public': '공개 보드'
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'color']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'rows': 4,
                'style': 'height: 100px;'
            }),
            'color': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'content': '포스트 내용',
            'color': '색상'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # content 필드를 선택적으로 만들기 (빈 문자열 허용)
        self.fields['content'].required = False

