from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
import random
import string


class AutoGuestMiddleware(MiddlewareMixin):
    """
    인증되지 않은 사용자를 자동으로 게스트로 로그인시키는 미들웨어
    """
    
    # 게스트 로그인을 제외할 경로들
    EXCLUDED_PATHS = [
        '/accounts/login/',
        '/accounts/signup/',
        '/accounts/logout/',
        '/accounts/guest-login/',
        '/admin/',
        '/static/',
        '/media/',
    ]
    
    # 자동 게스트 로그인을 실행할 경로들 (이 경로에 접근할 때만 자동 로그인)
    # 빈 리스트이면 모든 경로에서 자동 로그인 (제외된 경로 제외)
    AUTO_GUEST_PATHS = [
        '/',
        '/collaboration/',
        '/collaboration/gallery/',
        '/collaboration/board/',
        '/forum/',
    ]
    
    def process_request(self, request):
        # 이미 인증된 사용자는 건너뛰기
        if request.user.is_authenticated:
            return None
        
        # 제외된 경로는 건너뛰기 (로그인/회원가입/로그아웃/관리자/정적 파일)
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return None
        
        # 로그인/회원가입 페이지 접근 시 게스트 세션 플래그 초기화
        if any(request.path.startswith(path) for path in ['/accounts/login/', '/accounts/signup/']):
            if 'auto_guest_attempted' in request.session:
                del request.session['auto_guest_attempted']
            if 'logout_flag' in request.session:
                del request.session['logout_flag']
            if 'skip_auto_guest' in request.session:
                del request.session['skip_auto_guest']
            return None
        
        # 로그아웃 페이지 접근 시에는 자동 게스트 로그인 건너뛰기
        if request.path.startswith('/accounts/logout/'):
            return None
        
        # API 요청이나 AJAX 요청은 건너뛰기 (무한 루프 방지)
        if request.path.startswith('/api/') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return None
        
        # 세션에 이미 게스트 로그인 시도가 있었는지 확인 (무한 루프 방지)
        # auto_guest_attempted가 있으면 이미 게스트로 로그인된 상태이므로 건너뛰기
        if request.session.get('auto_guest_attempted'):
            return None
        
        # 자동 게스트 로그인 경로 체크 (AUTO_GUEST_PATHS가 비어있지 않으면 경로 체크)
        if self.AUTO_GUEST_PATHS:
            if not any(request.path.startswith(path) or request.path == path for path in self.AUTO_GUEST_PATHS):
                return None
        
        # 게스트 사용자 생성 및 로그인
        try:
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
            
            # 세션에 게스트 로그인 시도 표시 (무한 루프 방지)
            request.session['auto_guest_attempted'] = True
            
        except Exception as e:
            # 에러 발생 시에도 계속 진행 (로그인 실패해도 사이트는 작동해야 함)
            pass
        
        return None

