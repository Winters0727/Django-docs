# Django API

### 기본 설정

##### 모델(models.py)

```python
from django.db import models
from django.contrib.auth.models import User


class Poll(models.Model):
    question = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question


class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)

    def __str__(self):
        return self.choice_text


class Vote(models.Model):
    choice = models.ForeignKey(Choice, related_name='votes', on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    voted_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("poll", "voted_by")
```



##### URL(urls.py)

```python
from django.urls import include, re_path

urlpatterns = [
    re_path(r'^', include('polls.urls')),
]
Now you
```



##### Admin(admin.py)

```python
from django.contrib import admin

from .models import Poll, Choice

admin.site.register(Poll)
admin.site.register(Choice)
```



### Django Rest Framework

##### 직렬화와 역직렬화

DRF는 웹 API를 간단하고 유연하게 생성할 수 있는 프로세스를 가진다.

API 생성에 가장 먼저 해야할 일은  모델 인스턴스의 데이터를 표현식으로 직렬화하는 것이다. 직렬화란 네트워크를 통해 전송 될 전송 가능한 데이터의 표현식을 생성하는 과정이다. 역과정은 역직렬화라고 한다.



##### 직렬화 클래스 생성(serializers.py)

모델의 인스턴스를 JSON 표현식으로 직렬화 및 역직렬화할 직렬화 클래스를 생성해보자. 여기서는 `ModelSerializer`를 사용하여 코드의 반복을 줄이고, 필드 및 생성 메서드(`create`, `update`)를 자동으로 생성하겠다.

```python
from rest_framework import serializers

from .models import Poll, Choice, Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class ChoiceSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, required=False)

    class Meta:
        model = Choice
        fields = '__all__'


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Poll
        fields = '__all__'
```

예시로 `PollSerializer` 클래스가 가지는 몇가지 메서드를 확인해보자.

- `is_valid(self, ...)`는 모델의 create/update 작업을 수행하기 위한 충분한 데이터가 제공되었는지 검증하는 메서드다.
- `save(self, ...)`는 모델의 create 또는 update 작업을 수행하는 메서드다.
- `create(self, validated_data, ...)`는 모델의 인스턴스를 생성하는 메서드다. 이 메서드는 오버라이딩이 가능하다.
- `update(self, instance, validated_data, ...)`는 모델의 인스턴스를 수정하는 메서드다. 이 메서드는 오버라이딩이 가능하다.



### 뷰(View)와 제네릭 뷰(Generic View)

**`APIView`를 활용한 뷰 생성**

```python
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Poll, Choice
from  .serializers import PollSerializer

class PollList(APIView):
    def get(self, request):
        polls = Poll.objects.all()[:20]
        data = PollSerializer(polls, many=True).data
        return Response(data)


class PollDetail(APIView):
    def get(self, request, pk):
        poll = get_object_or_404(Poll, pk=pk)
        data = PollSerializer(poll).data
        return Response(data)
```

```python
# urls.py
from django.urls import path

from .apiviews import PollList, PollDetail

urlpatterns = [
    path("polls/", PollList.as_view(), name="polls_list"),
    path("polls/<int:pk>/", PollDetail.as_view(), name="polls_detail")
]
```



**제네릭 뷰 생성**

DRF의 제네릭 뷰는 코드의 재사용성을 높여준다. 응답 포맷을 추론하고, 기반 클래스와 시리얼라이저 클래스로부터 메서드를 허용한다.

```python
# views.py
from rest_framework import generics

from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer,\
    VoteSerializer


class PollList(generics.ListCreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer


class PollDetail(generics.RetrieveDestroyAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
```



**더 많은 제네릭 뷰**

```python
# views.py
from rest_framework import generics

from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer

...

class ChoiceList(generics.ListCreateAPIView):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class CreateVote(generics.CreateAPIView):
    serializer_class = VoteSerializer
```

```python
# urls.py
from .apiviews import ChoiceList, CreateVote, # ...

urlpatterns = [
    # ...
    path("choices/", ChoiceList.as_view(), name="choice_list"),
    path("vote/", CreateVote.as_view(), name="create_vote"),

]
```

- `queryset` : 초기 쿼리셋을 결정한다. 쿼리셋은 뷰에 의해 정렬, 필터링, 슬라이싱 될 수 있다.
- `serializer_class` : 결과값을 직렬화 하거나 입력값을 역직렬화 및 검증하는 시리얼라이저 클래스



### 뷰와 뷰셋

**더 나은 URL 구조**

현재 API는 3개의 엔드포인트를 가진다.

- `/polls/` 와 `/polls/<pk>`
- `/chocies/`
- `/votes/`

URL 좀 더 직관적으로 바꾸기 위해 내장형 URL로 재디자인 하겠다.

- `/polls/` 와 `/polls/<pk>`
- `/polls/<pk>/choices/`
- `/polls/<pk>/chocies/<choice_pk>/vote/`



**뷰 변경**

```python
# views.py
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer

# ...
# PollList and PollDetail views

class ChoiceList(generics.ListCreateAPIView):
    def get_queryset(self):
        queryset = Choice.objects.filter(poll_id=self.kwargs["pk"])
        return queryset
    serializer_class = ChoiceSerializer


class CreateVote(APIView):
    serializer_class = VoteSerializer

    def post(self, request, pk, choice_pk):
        voted_by = request.data.get("voted_by")
        data = {'choice': choice_pk, 'poll': pk, 'voted_by': voted_by}
        serializer = VoteSerializer(data=data)
        if serializer.is_valid():
            vote = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

```python
# urls.py

#...
urlpatterns = [
    path("polls/<int:pk>/choices/", ChoiceList.as_view(), name="choice_list"),
    path("polls/<int:pk>/choices/<int:choice_pk>/vote/", CreateVote.as_view(), name="create_vote"),

]
```



**뷰셋과 라우터**

`/polls/`와 `/polls/<pk>/`는 동일한 쿼리셋과 시리얼라이저를 가지는 두개의 뷰 클래스다. 뷰셋과 라우터를 이용하여 이를 하나로 병합하자.

```python
# urls.py
# ...
from rest_framework.routers import DefaultRouter
from .apiviews import PollViewSet


router = DefaultRouter()
router.register('polls', PollViewSet, basename='polls')


urlpatterns = [
    # ...
]

urlpatterns += router.urls

# views.py
# ...
from rest_framework import viewsets

from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
```



### 접근권한

유저 생성 및 인증에 관한 API다.

- 유저 생성의 엔드포인트는 `/users/`다.
- 유저를 인증하고 토큰을 검증하는 엔드포인트는 `/login/`다.



**유저 생성**

```python
# ...
from django.contrib.auth.models import User

# ...
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
```

`ModelSerializer`의 `create()` 메서드를 오버라이드하여 `User` 인스턴스를 저장했다. Hash로 직접 비밀번호를 설정하기 보다는 `user.set_password`를 사용하여 비밀번호를 설정하자. 응답에 비밀번호를 포함시키지 않기 위해 `extra_kwargs = {'password': {'write_only': True}}`를 추가한다.

```python
# in views.py
# ...
from .serializers import PollSerializer, ChoiceSerializer, VoteSerializer, UserSerializer

# ...
class UserCreate(generics.CreateAPIView):
    serializer_class = UserSerializer

# in urls.py
# ...
from .apiviews import PollViewSet, ChoiceList, CreateVote, UserCreate


urlpatterns = [
    # ...
    path("users/", UserCreate.as_view(), name="user_create"),
]
```



**인증 스키마 설정**

```python
# settings.py
INSTALLED_APPS = (
    # ...
    'rest_framework.authtoken'
)

# ...

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}
```

인증 관련 데이터를 데이터베이스에 반영시키기위해 `python manage.py migrate`를 실행한다.

`UserCreate` 뷰의 인증관련 전역 설정을 오버라이딩하자.

```python
class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer
```

`UserCreate` 과정에서 토큰이 생성되어야 하므로 `UserSerializer`를 다음과 같이 수정한다.

```python
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        Token.objects.create(user=user) # 토큰 생성
        return user
```



**로그인 API**

`settings.py`에 `rest_framework.authentication.TokenAuthentication`로 토큰 인증을 반영하였으니 앞으로 요청 헤더에 `Authorization: Token c2a84953f47288ac1943a3f389a6034e395ad940`와 같이 토큰 값을 보내야 한다.

```python
# in views.py
# ...
from django.contrib.auth import authenticate

class LoginView(APIView):
    permission_classes = ()

    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)


# in urls.py
# ...

from .apiviews import PollViewSet, ChoiceList, CreateVote, UserCreate, LoginView



urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    # ...
]
```

로그인 엔드포인트는 DRF에서 제공하는 `obtain_auth_token` 메서드를 사용할 수도 있다.

```python
from rest_framework.authtoken import views

urlpatterns = [
    path("login/", views.obtain_auth_token, name="login"),
    # ...
]
```



**권한 설정**

```python
# ...
from rest_framework.exceptions import PermissionDenied


class PollViewSet(viewsets.ModelViewSet):
    # ...

    def destroy(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == poll.created_by:
            raise PermissionDenied("You can not delete this poll.")
        return super().destroy(request, *args, **kwargs)


class ChoiceList(generics.ListCreateAPIView):
    # ...

    def post(self, request, *args, **kwargs):
        poll = Poll.objects.get(pk=self.kwargs["pk"])
        if not request.user == poll.created_by:
            raise PermissionDenied("You can not create choice for this poll.")
        return super().post(request, *args, **kwargs)
```

