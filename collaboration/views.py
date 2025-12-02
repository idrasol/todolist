from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from math import isnan
from .models import Board, Post, Comment
from .forms import BoardForm, PostForm


def index(request):
    """메인 페이지 (랜딩 페이지)"""
    return render(request, 'collaboration/landing.html')


def board_list(request):
    """보드 목록 조회 - 로그인한 사용자는 자신의 보드와 공개 보드, 비로그인 사용자는 공개 보드만"""
    if request.user.is_authenticated:
        # 로그인한 사용자: 공개 보드 또는 자신이 만든 보드
        boards = Board.objects.filter(
            Q(is_public=True) | Q(creator=request.user)
        ).order_by('-created_at')
    else:
        # 비로그인 사용자: 공개 보드만
        boards = Board.objects.filter(is_public=True).order_by('-created_at')
    
    context = {
        'boards': boards
    }
    return render(request, 'collaboration/board_list.html', context)


def gallery(request):
    """갤러리 - 공개 보드만 최신순으로 표시 (작성자는 자신의 비공개 보드도 볼 수 있음)"""
    if request.user.is_authenticated:
        # 로그인한 사용자: 공개 보드 또는 자신이 만든 보드
        boards = Board.objects.filter(
            Q(is_public=True) | Q(creator=request.user)
        ).order_by('-created_at')
    else:
        # 비로그인 사용자: 공개 보드만
        boards = Board.objects.filter(is_public=True).order_by('-created_at')
    
    # 각 보드의 모든 포스트를 가져와서 컨텍스트에 포함
    posts = Post.objects.filter(board__in=boards).select_related('user', 'board').prefetch_related('comments')
    
    context = {
        'boards': boards,
        'posts': posts
    }
    return render(request, 'collaboration/gallery.html', context)


def board_detail(request, board_id):
    """보드 상세 페이지"""
    board = get_object_or_404(Board, id=board_id)
    
    # 비공개 보드는 작성자만 접근 가능
    if not board.is_public:
        if not request.user.is_authenticated or board.creator != request.user:
            return HttpResponseForbidden("이 보드에 접근할 권한이 없습니다.")
    
    posts = Post.objects.filter(board=board)
    post_form = PostForm()
    
    context = {
        'board': board,
        'posts': posts,
        'post_form': post_form,
        'color_choices': Post.COLOR_CHOICES
    }
    return render(request, 'collaboration/board_detail.html', context)


@login_required
def board_create(request):
    """새 보드 생성"""
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.creator = request.user
            board.save()
            return redirect('collaboration:board_list')
    else:
        form = BoardForm()
    
    context = {
        'form': form
    }
    return render(request, 'collaboration/board_form.html', context)


@require_POST
def post_create(request):
    """포스트 생성 - 무조건 작동하는 강력한 버전"""
    # 로그인 체크 (내부에서 직접 확인)
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'login_required',
            'login_url': '/accounts/login/'
        }, status=401)
    
    try:
        # 폼 데이터 바인딩 (POST와 FILES 모두 포함)
        form = PostForm(request.POST, request.FILES)
        
        # 폼이 유효하지 않아도 처리 (이미지만 업로드하는 경우 등)
        # Post 객체를 직접 생성
        post = Post()
        
        # 1. 작성자 및 보드 연결
        post.user = request.user
        board_id = request.POST.get('board_id')
        if not board_id:
            return JsonResponse({'success': False, 'message': 'Board ID가 누락되었습니다.'}, status=400)
        post.board = get_object_or_404(Board, id=board_id)
        
        # 2. 좌표 데이터 처리 (핵심 수정: 무조건 0.0으로 초기화 후 값이 있으면 덮어쓰기)
        # 먼저 무조건 0.0으로 초기화 (NOT NULL 에러 방지)
        post.position_x = 0.0
        post.position_y = 0.0
        
        # 프론트엔드에서 'position_x' 또는 'x'로 보낼 수 있으므로 둘 다 확인
        raw_x = request.POST.get('position_x') or request.POST.get('x')
        raw_y = request.POST.get('position_y') or request.POST.get('y')
        
        # 받은 값이 있으면 float로 변환하여 덮어쓰기 (NaN 체크 포함)
        if raw_x:
            try:
                raw_x_str = str(raw_x).strip()
                if raw_x_str and raw_x_str != 'NaN' and raw_x_str != 'undefined':
                    parsed_x = float(raw_x_str)
                    if not isnan(parsed_x):
                        post.position_x = parsed_x
            except (ValueError, TypeError, AttributeError):
                pass  # 이미 0.0으로 설정되어 있으므로 그대로 유지
        
        if raw_y:
            try:
                raw_y_str = str(raw_y).strip()
                if raw_y_str and raw_y_str != 'NaN' and raw_y_str != 'undefined':
                    parsed_y = float(raw_y_str)
                    if not isnan(parsed_y):
                        post.position_y = parsed_y
            except (ValueError, TypeError, AttributeError):
                pass  # 이미 0.0으로 설정되어 있으므로 그대로 유지
        
        # save() 직전에 최종 확인 (NOT NULL 및 NaN 에러 방지) - 무조건 float 값 보장
        if post.position_x is None or (isinstance(post.position_x, float) and isnan(post.position_x)):
            post.position_x = 0.0
        if post.position_y is None or (isinstance(post.position_y, float) and isnan(post.position_y)):
            post.position_y = 0.0
        
        # 타입 확인 및 변환 (NaN 체크 포함)
        if not isinstance(post.position_x, (int, float)) or (isinstance(post.position_x, float) and isnan(post.position_x)):
            post.position_x = 0.0
        if not isinstance(post.position_y, (int, float)) or (isinstance(post.position_y, float) and isnan(post.position_y)):
            post.position_y = 0.0
        
        # 3. 이미지 파일 처리 (이미지가 있으면 이미지 전용 Post 생성)
        if 'image' in request.FILES:
            post.image = request.FILES['image']
            # 이미지 전용 Post는 content를 빈 문자열로 초기화
            post.content = ''
        else:
            # 4. content 필드 처리 (빈 문자열 허용)
            content = request.POST.get('content', '').strip()
            post.content = content  # 빈 문자열도 허용
        
        # 5. 색상 데이터 처리 (기본값: yellow, 이미지 전용 Post는 색상 불필요)
        if 'image' not in request.FILES:
            color = request.POST.get('color', 'yellow')
            if color:
                post.color = color
                
        # 6. 저장
        post.save()
        
        # 응답 데이터 준비
        response_data = {
            'success': True,
            'post': {
                'id': post.id,
                'content': post.content,
                'user': post.user.username,
                'color': post.color,
                'position_x': post.position_x,
                'position_y': post.position_y,
                'z_index': post.z_index,
                'image_url': post.image.url if post.image else None
            }
        }
        
        # 캔버스 이미지인 경우 추가 정보 포함
        if post.image:
            response_data['image_url'] = post.image.url
            response_data['post_id'] = post.id
        
        return JsonResponse(response_data, status=200)
            
    except Exception as e:
        # 서버 내부 에러 발생 시에도 JSON으로 응답
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def post_update(request, post_id):
    """포스트 수정 (위치 업데이트 및 내용 수정) - 작성자 또는 관리자만 가능"""
    post = get_object_or_404(Post, id=post_id)
    
    # 작성자 또는 관리자만 수정 가능
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '로그인이 필요합니다.'}, status=403)
    
    if post.user != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '수정 권한이 없습니다.'}, status=403)
    
    if request.method == 'POST':
        # AJAX 요청인 경우
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 이미지 업로드 (파일 업로드는 먼저 체크)
            if 'image' in request.FILES:
                try:
                    post.image = request.FILES['image']
                    post.save(update_fields=['image'])  # 명시적으로 image 필드만 업데이트
                    
                    # 이미지 URL이 제대로 생성되는지 확인
                    image_url = post.image.url if post.image else None
                    if not image_url:
                        return JsonResponse({
                            'success': False,
                            'message': '이미지 URL을 생성할 수 없습니다.'
                        }, status=400)
                    
                    return JsonResponse({
                        'success': True,
                        'image_url': image_url
                    })
                except Exception as e:
                    import traceback
                    return JsonResponse({
                        'success': False,
                        'message': f'이미지 업로드 실패: {str(e)}',
                        'error_detail': traceback.format_exc() if settings.DEBUG else None
                    }, status=400)
            
            # 파일 업로드
            if 'attached_file' in request.FILES:
                try:
                    post.attached_file = request.FILES['attached_file']
                    post.save(update_fields=['attached_file'])
                    return JsonResponse({
                        'success': True,
                        'file_url': post.attached_file.url if post.attached_file else None,
                        'file_name': post.attached_file.name.split('/')[-1] if post.attached_file else None
                    })
                except Exception as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'파일 업로드 실패: {str(e)}'
                    }, status=400)
            
            # 위치 업데이트
            if 'position_x' in request.POST and 'position_y' in request.POST:
                try:
                    position_x = float(request.POST.get('position_x', post.position_x))
                    position_y = float(request.POST.get('position_y', post.position_y))
                    
                    post.position_x = position_x
                    post.position_y = position_y
                    post.save(update_fields=['position_x', 'position_y'])
                    
                    return JsonResponse({
                        'success': True
                    })
                except (ValueError, TypeError) as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'위치 업데이트 실패: {str(e)}'
                    }, status=400)
            
            # 이미지 크기 업데이트 (width, height)
            if 'width' in request.POST and 'height' in request.POST:
                try:
                    width = float(request.POST.get('width'))
                    height = float(request.POST.get('height'))
                    # width와 height를 content에 JSON 형태로 저장 (임시 방법)
                    # 나중에 모델 필드를 추가할 수 있음
                    import json
                    metadata = {}
                    try:
                        if post.content and post.content.startswith('{') and 'metadata' in post.content:
                            metadata = json.loads(post.content).get('metadata', {})
                    except:
                        pass
                    metadata['width'] = width
                    metadata['height'] = height
                    # content가 비어있으면 metadata만 저장, 아니면 기존 content 유지
                    if not post.content or post.content.strip() == '':
                        post.content = json.dumps({'metadata': metadata})
                        post.save(update_fields=['content'])
                    else:
                        # content가 있으면 metadata를 저장하지 않음 (포스트잇의 텍스트 보호)
                        pass
                    return JsonResponse({
                        'success': True
                    })
                except (ValueError, TypeError) as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'이미지 크기 업데이트 실패: {str(e)}'
                    }, status=400)
            
            # z_index 업데이트
            if 'z_index' in request.POST:
                try:
                    z_index = int(request.POST.get('z_index', post.z_index))
                    post.z_index = z_index
                    post.save()
                    return JsonResponse({
                        'success': True
                    })
                except (ValueError, TypeError) as e:
                    return JsonResponse({
                        'success': False,
                        'message': f'z_index 업데이트 실패: {str(e)}'
                    }, status=400)
            
            # 내용 수정
            if 'content' in request.POST:
                post.content = request.POST.get('content', post.content)
                post.save()
                
                return JsonResponse({
                    'success': True,
                    'post': {
                        'id': post.id,
                        'content': post.content,
                        'user': post.user.username,
                        'color': post.color,
                        'position_x': post.position_x,
                        'position_y': post.position_y,
                        'z_index': post.z_index,
                        'image_url': post.image.url if post.image else None,
                        'file_url': post.attached_file.url if post.attached_file else None,
                        'file_name': post.attached_file.name.split('/')[-1] if post.attached_file else None
                    }
                })
    
    return JsonResponse({'success': False}, status=400)


@login_required
def board_delete(request, board_id):
    """보드 삭제 (작성자 또는 관리자만 가능)"""
    board = get_object_or_404(Board, id=board_id)
    
    # 작성자 또는 관리자만 삭제 가능
    if board.creator != request.user and not request.user.is_superuser:
        return redirect('collaboration:board_list')
    
    if request.method == 'POST':
        board.delete()
        return redirect('collaboration:board_list')
    
    return redirect('collaboration:board_list')


def post_delete(request, post_id):
    """포스트 삭제 - 작성자 또는 관리자만 가능"""
    post = get_object_or_404(Post, id=post_id)
    
    # 작성자 또는 관리자만 삭제 가능
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': '로그인이 필요합니다.'}, status=403)
    
    if post.user != request.user and not request.user.is_superuser:
        return JsonResponse({'success': False, 'message': '삭제 권한이 없습니다.'}, status=403)
    
    if request.method == 'POST':
        # AJAX 요청인 경우
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            post.delete()
            return JsonResponse({
                'success': True
            })
        
        # 일반 요청인 경우
        post.delete()
        return redirect('collaboration:board_detail', board_id=post.board.id)
    
    return JsonResponse({'success': False}, status=400)


@require_POST
def post_feedback(request, post_id):
    """포스트 피드백 처리 (좋아요) - AJAX POST 허용"""
    post = get_object_or_404(Post, id=post_id)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '로그인이 필요합니다.',
            'login_url': '/accounts/login/'
        }, status=401)
    
    feedback_type = request.POST.get('type')  # 'like' only
    
    # 싫어요 기능 제거 - like만 허용
    if feedback_type != 'like':
        return JsonResponse({
            'success': False,
            'message': '잘못된 피드백 타입입니다.'
        }, status=400)
    
    # 세션을 사용하여 중복 클릭 방지
    session_key = 'liked_posts'
    liked_posts = request.session.get(session_key, [])
    
    # post_id를 문자열로 변환하여 비교
    post_id_str = str(post_id)
    if post_id_str in liked_posts:
        return JsonResponse({
            'success': False,
            'message': '이미 좋아요를 누르셨습니다.',
            'likes': post.likes,
            'dislikes': post.dislikes
        }, status=400)
    
    # 좋아요 증가
    post.likes += 1
    post.save(update_fields=['likes'])
    
    # 세션에 추가 (문자열로 저장)
    liked_posts.append(post_id_str)
    request.session[session_key] = liked_posts
    
    return JsonResponse({
        'success': True,
        'likes': post.likes,
        'dislikes': post.dislikes
    })


@require_POST
def comment_create(request, post_id):
    """댓글 작성 - AJAX POST 허용"""
    post = get_object_or_404(Post, id=post_id)
    
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': '로그인이 필요합니다.',
            'login_url': '/accounts/login/'
        }, status=401)
    
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({
            'success': False,
            'message': '댓글 내용을 입력해주세요.'
        }, status=400)
    
    comment = Comment.objects.create(
        post=post,
        author=request.user,
        content=content
    )
    
    return JsonResponse({
        'success': True,
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'author': comment.author.username,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M')
        }
    })

