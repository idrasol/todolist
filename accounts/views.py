from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
import random
import string

from collaboration.models import Board


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True


def logout_view(request):
    """로그아웃 뷰 - GET 요청도 허용"""
    logout(request)
    return redirect('/')


def signup(request):
    """회원가입"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('collaboration:board_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


@require_http_methods(["POST"])
def guest_login(request):
    """게스트 로그인 - 임시 아이디 생성 및 자동 로그인"""
    # 'Guest_' + 6자리 난수 생성
    random_suffix = ''.join(random.choices(string.digits, k=6))
    guest_username = f'Guest_{random_suffix}'
    
    # 이미 존재하는 사용자인지 확인
    while User.objects.filter(username=guest_username).exists():
        random_suffix = ''.join(random.choices(string.digits, k=6))
        guest_username = f'Guest_{random_suffix}'
    
    # 임시 비밀번호 생성
    temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # 게스트 사용자 생성
    user = User.objects.create_user(
        username=guest_username,
        password=temp_password
    )
    
    # 자동 로그인
    login(request, user)
    
    return redirect('collaboration:board_list')


def profile(request):
    """사용자 프로필 페이지 - 작성한 보드 목록"""
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    
    boards = Board.objects.filter(creator=request.user).order_by('-created_at')
    
    context = {
        'user': request.user,
        'boards': boards,
    }
    
    return render(request, 'accounts/profile.html', context)

