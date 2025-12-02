from django.db import models
from django.conf import settings


class Board(models.Model):
    """협업 보드 모델"""
    title = models.CharField(max_length=100)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_boards'
    )
    is_public = models.BooleanField(default=True, verbose_name='공개 여부')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '보드'
        verbose_name_plural = '보드들'
        ordering = ['-created_at']

    def get_thumbnail_url(self):
        """보드의 썸네일 이미지 URL 반환 (이미지가 있는 가장 최신 포스트)"""
        post_with_image = self.posts.filter(image__isnull=False).exclude(image='').order_by('-created_at').first()
        if post_with_image and post_with_image.image:
            return post_with_image.image.url
        return None
    
    def get_latest_post_text(self):
        """가장 최근 포스트의 텍스트 일부 반환 (이미지가 없을 때 사용)"""
        latest_post = self.posts.filter(content__isnull=False).exclude(content='').order_by('-created_at').first()
        if latest_post and latest_post.content:
            # 최대 100자까지 반환
            return latest_post.content[:100]
        return None
    
    def get_gradient_colors(self):
        """보드의 포스트 색상들을 기반으로 그라디언트 색상 반환"""
        # 포스트 색상 매핑 (색상명 -> CSS 그라디언트)
        color_gradients = {
            'yellow': ('#fef08a', '#fde047'),
            'blue': ('#93c5fd', '#60a5fa'),
            'green': ('#86efac', '#4ade80'),
            'pink': ('#f9a8d4', '#f472b6'),
            'purple': ('#c4b5fd', '#a78bfa'),
            'orange': ('#fdba74', '#fb923c'),
            'cyan': ('#67e8f9', '#22d3ee'),
            'lime': ('#bef264', '#a3e635'),
            'indigo': ('#818cf8', '#6366f1'),
            'teal': ('#5eead4', '#2dd4bf'),
        }
        
        # 보드의 포스트들에서 색상 수집
        post_colors = self.posts.exclude(color='').values_list('color', flat=True).distinct()[:3]
        
        if post_colors:
            # 첫 번째 색상의 그라디언트 사용
            first_color = post_colors[0]
            if first_color in color_gradients:
                return color_gradients[first_color]
        
        # 기본 그라디언트 (보라색)
        return ('#667eea', '#764ba2')
    
    def __str__(self):
        return self.title


class Post(models.Model):
    """보드 내 포스트 모델"""
    COLOR_CHOICES = [
        ('yellow', '노란색'),
        ('blue', '파란색'),
        ('green', '초록색'),
        ('pink', '분홍색'),
        ('purple', '보라색'),
        ('orange', '주황색'),
        ('cyan', '청록색'),
        ('lime', '라임색'),
        ('indigo', '남색'),
        ('teal', '청록색'),
    ]
    
    board = models.ForeignKey(
        Board,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField()
    color = models.CharField(max_length=10, choices=COLOR_CHOICES, default='yellow')
    position_x = models.FloatField(default=0.0, null=True, blank=True)
    position_y = models.FloatField(default=0.0, null=True, blank=True)
    z_index = models.IntegerField(default=1, verbose_name='레이어 순서')
    image = models.ImageField(upload_to='posts/', null=True, blank=True, verbose_name='이미지')
    attached_file = models.FileField(upload_to='files/', null=True, blank=True, verbose_name='첨부 파일')
    likes = models.IntegerField(default=0, verbose_name='좋아요 수')
    dislikes = models.IntegerField(default=0, verbose_name='싫어요 수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '포스트'
        verbose_name_plural = '포스트들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}의 포스트 - {self.content[:50]}"


class Comment(models.Model):
    """포스트 댓글 모델"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField(verbose_name='댓글 내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')

    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username}의 댓글 - {self.content[:30]}"

