from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from collaboration.models import Board, Post


class Command(BaseCommand):
    help = '24시간 이상 지난 게스트 계정과 관련 데이터를 삭제합니다.'

    def handle(self, *args, **options):
        # 24시간 전 시간 계산
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        # 'Guest_'로 시작하는 게스트 계정 찾기
        guest_users = User.objects.filter(
            username__startswith='Guest_',
            date_joined__lt=cutoff_time
        )
        
        deleted_count = 0
        for user in guest_users:
            # 관련 데이터 삭제
            # Post 삭제 (CASCADE로 자동 삭제되지만 명시적으로)
            Post.objects.filter(user=user).delete()
            # Board 삭제
            Board.objects.filter(creator=user).delete()
            # User 삭제
            user.delete()
            deleted_count += 1
        
        if deleted_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'성공적으로 {deleted_count}개의 게스트 계정을 삭제했습니다.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('삭제할 게스트 계정이 없습니다.')
            )





