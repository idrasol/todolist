from django.db import models
from django.conf import settings
from django.urls import reverse


class Post(models.Model):
    """게시판 포스트 모델"""
    CATEGORY_CHOICES = [
        ('general', '자유'),
        ('question', '질문'),
        ('tip', '팁/노하우'),
        ('showcase', '작품 자랑'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_posts',
        verbose_name='작성자'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    views = models.PositiveIntegerField(default=0, verbose_name='조회수')
    is_notice = models.BooleanField(default=False, verbose_name='공지사항')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name='카테고리'
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='liked_posts',
        blank=True,
        verbose_name='좋아요'
    )
    
    class Meta:
        verbose_name = '게시글'
        verbose_name_plural = '게시글들'
        ordering = ['-is_notice', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forum:post_detail', kwargs={'pk': self.pk})
    
    def increase_views(self):
        """조회수 증가"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def total_likes(self):
        """좋아요 수 반환"""
        return self.likes.count()


class Comment(models.Model):
    """댓글 모델"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='게시글'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='forum_comments',
        verbose_name='작성자'
    )
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        verbose_name = '댓글'
        verbose_name_plural = '댓글들'
        ordering = ['created_at']
    
    def __str__(self):
        return f'{self.author.username}의 댓글 - {self.content[:30]}'
