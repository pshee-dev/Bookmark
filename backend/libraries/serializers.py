from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from accounts.accounts_serializers.serializers import UserProfileSerializer
from books.serializers import BookSimpleSerializer, BookWithReviewAndGalfiesSerializerInLibrary
from .models import Library
from books.models import Book, Category
from datetime import date
from django.utils import timezone

# 서재에서 사용할 책 정보 기본 시리얼라이저
class BookBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author', 'publisher', 'thumbnail')


# 독서 상태 등록/수정 시 유효성 검증 및 자동화 로직을 위한 기본 시리얼라이저
class LibraryBookBaseSerializer(serializers.ModelSerializer):

    # rating 범위(0~5) 설정
    rating = serializers.IntegerField(
        min_value=0, # 최소값
        max_value=5,  # 최대값
        required=False, # 필수 입력 필드가 아님
        allow_null=True, # null 값 입력 허용
    )

    class Meta:
        model = Library
        fields = ('id', 'status', 'start_date', 'finish_date', 'current_page', 'rating')

    # 유효성 검증 로직
    def validate(self, data):
        start_date = data.get('start_date') or getattr(self.instance, 'start_date', None)
        finish_date = data.get('finish_date') or getattr(self.instance, 'finish_date', None)
        book = data.get('book') or getattr(self.instance, 'book', None) # book 데이터는 CreateSerializer에서만 존재
        
        '''
        [ current_page ]
        사용자가 의도적으로 보낸 0 값이 falsy로 인식되어 기존 값으로 덮어씌워지는 것을 방지하기 위해 data에 존재하는지 확인 후 할당
        잘못된 사용 법 -> current_page = data.get('current_page') or getattr(self.instance, 'current_page', None)
        '''
        if 'current_page' in data:
            current_page = data.get('current_page')
        else:
            current_page = getattr(self.instance, 'current_page', None)

        # start_date 범위 설정
        if start_date is not None:
            if start_date < date(1900, 1, 1):
                raise serializers.ValidationError({"start_date": "독서 시작 날짜는 1900년 1월 1일 이후로 설정할 수 있습니다."})
            if start_date > timezone.now().date():
                raise serializers.ValidationError({"start_date": "독서 시작 날짜는 오늘보다 미래일 수 없습니다."})

        # start_date 없이 finish_date 설정 불가
        if finish_date and not start_date:
            raise serializers.ValidationError({"finish_date": "독서 시작 날짜를 먼저 설정해주세요."})
        
        # start_date보다 빠른 finish_date 설정 불가
        if start_date and finish_date:
            if finish_date < start_date:
                raise serializers.ValidationError({"finish_date": "독서 완료 날짜는 독서 시작 날짜보다 빠를 수 없습니다."})

        # finish_date 범위 설정
        if finish_date is not None:
            if finish_date < date(1900, 1, 1):
                raise serializers.ValidationError({"finish_date": "독서 완료 날짜는 1900년 1월 1일 이후로 설정할 수 있습니다."})
            if finish_date > timezone.now().date():
                raise serializers.ValidationError({"finish_date": "독서 완료 날짜는 오늘보다 미래일 수 없습니다."})
        
        # current_page 유효 범위 설정
        if current_page is not None:
            # 음수 설정 불가
            if current_page < 0:
                raise serializers.ValidationError(
                    {"current_page": "읽고 있는 페이지는 0 이상이어야 합니다."}
                )
            # book.page 보다 큰 수로 설정 불가
            if hasattr(book, 'page') and book.page:
                if current_page > book.page:
                    raise serializers.ValidationError(
                        {"current_page": f"읽고 있는 페이지는 최대 {book.page}페이지까지 가능합니다."}
                    )
        
        return data

    # 자동화 로직
    def save(self, **kwargs):
        instance = super().save(**kwargs)

        # '다 읽은 책'일 때 current_page = book.page로 설정
        if instance.status == Library.StatusEnum.finished:
            book_page = getattr(instance.book, 'page', None)
            if book_page:
                instance.current_page = book_page
                instance.save(update_fields=['current_page'])
        
        return instance


# [GET] 내 서재에 있는 도서 목록 조회 - /library/
class LibraryBookListSerializer(serializers.ModelSerializer):
    book = BookBaseSerializer(read_only=True)
    class Meta:
        model = Library
        fields = ('id', 'status', 'start_date', 'finish_date', 'rating', 'book')
    
    # Todo: 페이지네이션


# [POST] 내 서재에 독서 상태 등록 - /library/
class LibraryBookCreateSerializer(LibraryBookBaseSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    book = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all())

    class Meta(LibraryBookBaseSerializer.Meta):
        model = Library
        fields = LibraryBookBaseSerializer.Meta.fields + ('book', 'user')
        
        # 유니크제약조건 유효성 검사
        validators = [
            UniqueTogetherValidator(
                queryset=Library.objects.all(),
                fields=['user', 'book'],
                message="이미 내 서재에 등록된 책입니다."
            )
        ]

# [GET] 내 서재에 있는 도서 상세 조회 - /library/{library_id}
class LibraryBookDetailSerializer(serializers.ModelSerializer):
    book = BookWithReviewAndGalfiesSerializerInLibrary()
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Library
        fields = ('id', 'user', 'book', 'status', 'start_date', 'finish_date', 'rating', 'current_page' )

# [PATCH] 내 서재에 독서 상태 수정 - /library/{library_id}
class LibraryBookUpdateSerializer(LibraryBookBaseSerializer):
    pass # 상속받은 serializer에서 추가 필드 없음 (용도에 따른 serializer 네이밍 통일성을 위해 상속 구조 활용)
