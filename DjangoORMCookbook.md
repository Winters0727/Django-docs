# Django Cookbook 정리

### 쿼리셋 간 연산

**OR 연산**

- `queryset_1 | queryset_2`
- `filter(Q(<condition_1>) | Q(<condition_2>))`



**AND 연산**

- `queryset_1 & queryset_2`
- `filter(Q(<condition_1>), Q(<condition_2>))`
- `filter(Q(<condition_1>) & Q(<condition_2>))`



**NOT 연산**

- `exclude(<condition>)`
- `filter(~Q(<condition>))`



**UNION 연산**

- 전체 필드가 동일한 경우

  ```python
  queryset_1 = User.objects.filter(id__gte=5)
  queryset_2 = User.objects.filter(id__lte=9)
  
  queryset_1.union(queryset_2)
  queryset_2.union(queryset_1)
  ```

- 일부 필드만 동일할 경우

  ```python
  User.objects.all().value_list(
    'name', 'gender'
  ).union(
  anotherUser.objects.all().value_list(
    'name', 'gender'
  ))
  ```



**JOIN 연산**

```python
a1 = Article.objects.select_related('reporter') # select_related 사용
a2 = Article.objects.filter(reporter__username='John')
```



### 쿼리셋 다루기

**필요한 열만 조회**

- `queryset.values()` OR `queryset.values_list()`
- `queryset.only()`



**필드의 값을 통한 비교**

`F` 객체를 사용, `__gt`, `__le`와 같은 룩업 적용 가능

```python
User.objects.filter(last_name = F('first_name')) # first_name과 last_name이 같은 경우
```



**항목 연산**

- 첫번째 항목 : `.first()`
- 마지막 항목 : `.last()`
- N번째 항목 : `Model.objects.order_by('-기준')[N-1]`

쿼리셋의 인덱스 연산은 전체 데이터를 가져오는 것이 아니라 `LIMIT ... OFFSET` SQL 구문을 사용한다.



**집계 연산**

`.aggregate()` 메서드의 인자로 집계 연산을 넘겨준다.

```python
from django.db.models import Avg, Max, Min, Sum, Count

User.objects.all().aggregate(Avg('id'))
User.objects.all().aggregate(Max('id'))
User.objects.all().aggregate(Min('id'))
User.objects.all().aggregate(Sum('id'))
```



**무작위 항목 추출**

```python
import random

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name
    
def get_random(): # 첫번째 방법 : 전체 표를 무작위로 정렬
    # 단, 사용하는 데이터베이스에 따라 order_by('?')의 실행 비용이 비싸고 성능이 느릴 수 있다.
    return Category.objects.order_by("?").first()

def get_random2(): # 두번째 방법 : 저장된 항목의 마지막 id까지 random 모듈로 난수를 생성
     max_id = Category.objects.all().aggregate(max_id=Max("id"))['max_id']
     pk = random.randint(1, max_id)
     return Category.objects.get(pk=pk)
    
def get_random3(): # 세번째 방법 : 두번째 방법에서 유효한 id가 나올 때까지 반복
     max_id = Category.objects.all().aggregate(max_id=Max("id"))['max_id']
     while True:
         pk = random.randint(1, max_id)
         category = Category.objects.filter(pk=pk).first()
         if category:
             return category
```



**여러 개의 행 동시 생성**

`.bluk_create()` 메서드를 사용한다.

```python
Category.objects.bulk_create(
    [Category(name="God"),
     Category(name="Demi God"),
     Category(name="Mortal")]
)
```



**기존 데이터 복사하기**

장고 ORM에 모델 인스턴스를 복사하는 내장 메서드는 없다. 하지만, 새 인스턴스를 생성한 뒤, pk를 제거하면 데이터베이스에 새 행으로 저장된다.

```python
user = User.objects.first()
user.pk = None
user.save()
```



**특정 모델의 항목이 하나만 생성되도록 강제**

프로그램의 환경 설정 기록, 공유 자원에 대한 잠금 제어 등을 예로 들 수 있다. 이런 경우에는 모델을 싱글턴(단일개체)로 만들면 된다.

```python
class Origin(models.Model):
    name = models.CharField(max_length=100)
    
    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)
```

위 코드는 `save` 메서드를 재정의하여 `pk` 필드를 이미 존재하는 값으로 지정하도록 강제한다. 이로써 객체가 이미 존재할 때 `create` 메서드를 호출하면 `IntegrityError`가 발생한다.



**모델 인스턴스를 저장할 때, 다른 모델에 반정규화된 필드를 함께 갱신**

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    hero_count = models.PositiveIntegerField()
    villain_count = models.PositiveIntegerField()

    class Meta:
        verbose_name_plural = "Categories"


class Hero(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ...


class Villain(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ...
```

Hero 모델과 Villian 모델의 항목을 새로 저장할 때, Category 모델의 `hero_count` 필드와 `vilian_count` 필드를 갱신해야한다. 다음과 같이 각각의 모델의 `save` 메서드를 재정의한다.

```python
class Hero(models.Model):
    # ...

    def save(self, *args, **kwargs):
        if not self.pk:
            Category.objects.filter(pk=self.category_id).update(hero_count=F('hero_count')+1)
        super().save(*args, **kwargs)


class Villain(models.Model):
    # ...

    def save(self, *args, **kwargs):
        if not self.pk:
            Category.objects.filter(pk=self.category_id).update(villain_count=F('villain_count')+1)
        super().save(*args, **kwargs)
```

위 코드에서 `self.category.hero_count += 1`과 같이 인스턴스의 값을 수정하는 것이 아니라, `update` 메서드로 데이터베이스의 갱신을 수행하도록 한 것을 확인할 수 있다.

또 다른 방법으로 '시그널(신호)'이라는 기능을 이용하는 방법이 있다.

```python
from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Hero, dispatch_uid="update_hero_count")
def update_hero_count(sender, **kwargs):
    hero = kwargs['instance']
    if hero.pk:
        Category.objects.filter(pk=hero.category_id).update(hero_count=F('hero_count')+1)

@receiver(pre_save, sender=Villain, dispatch_uid="update_villain_count")
def update_villain_count(sender, **kwargs):
    villain = kwargs['instance']
    if villain.pk:
        Category.objects.filter(pk=villain.category_id).update(villain_count=F('villain_count')+1)
```

`save` 메서드를 재정의하는 방법과 시그널을 이용하는 방법 두가지 모두 사용이 가능하다. 어느 것을 사용할지는 다음 규칙을 권장한다.

- 반정규화 필드에 영향을 끼치는 모델을 통제할 수 있다면 `save` 메서드를 재정의한다.
- 반정규화 필드에 영향을 끼치는 모델을 통제할 수 없다면(그 영향이 라이브러리 등에서 이루어진다면) 시그널을 이용한다.



**Truncate문 수행**

장고는 TRUNCATE 문을 실행하는 명령을 제공하지 않는다. 하지만 `delete` 메서드를 이용해 비슷한 결과를 얻을 수 있다.

```python
Category.objects.all().delete()
```

위 코드는 잘 동작하지만, TRUNCATE 문이 아니라 `DELETE FROM ...`과 같이 SQL 질의를 수행한다. 삭제해야 하는 항목의 수가 많은 경우에 처리 속도가 느릴 수 밖에 없다. `truncate` 명령이 필요하다면 다음과 같이 `Category` 모델에 `classmethod`로 추가하면 된다.

```python
class Category(models.Model):
    # ...

    @classmethod
    def truncate(cls):
        with connection.cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(cls._meta.db_table))
```

이렇게 메서드를 정의해두면 `Cateogry.truncate()`를 실행하여 정말로 데이터베이스 시스템에 TRUNCATE 문을 질의할 수 있다.



**분류·댓글처럼 아무 모델이나 가리킬 수 있는 범용 모델 생성**

```python
class Category(models.Model):
    name = models.CharField(max_length=100)
    # ...

    class Meta:
        verbose_name_plural = "Categories"


class Hero(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ...


class Villain(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # ...
```

여기서 `Category` 모델은 범용 모델로 고쳐 정의할 수 있다. 다음과 같이 수정하면 된다.

```python
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# ...

class FlexCategory(models.Model):
    name = models.SlugField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Hero(models.Model):
    name = models.CharField(max_length=100)
    flex_category = GenericRelation(FlexCategory, related_query_name='flex_category')
    # ...


class Villain(models.Model):
    name = models.CharField(max_length=100)
    flex_category = GenericRelation(FlexCategory, related_query_name='flex_category')
    # ...
```

수정한 코드에서는 `FlexCategory` 모델에 외래 키 필드(`ForeignKey`) 하나와 양의 정수 필드(`PositiveIntegerField`) 하나를 정의하여 범용 외래 키 필드(`GenericForeignKey`)를 사용할 수 있도록 만들었다. 그리고 분류를 이용할 모델에 범용 관계 필드(`GenericRelation`)를 추가했다.



### 서브쿼리 다루기

```python
class Category(models.Model):
    name = models.CharField(max_length=100)


class Hero(models.Model):
    # ...
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE) # 1대다 관계

    benevolence_factor = models.PositiveSmallIntegerField(
        help_text="How benevolent this hero is?",
        default=50
    )
```

```python
from django.db.models import Subquery

# 가장 선한 영웅을 구해보자
hero_qs = Hero.objects.filter(
  category=OuterRef('pk')
).order_by('-benevolence_factor')
Category.objects.all().annotate(
  most_benevolent_hero = Subquery(
    hero_qs.values('name')[:1]
  )
)
```



### 정렬

**쿼리셋을 오름차순/내림차순으로 정렬**

```python
User.objects.all().order_by('standard') # 오름차순
User.objects.all().order_by('-standard') # 내림차순

User.objects.all().order_by('standard1', 'standard2', 'standard3') # 기준 필드를 여러 개로 잡을 수 있다.
```



**대문자·소문자 구별 없이 정렬**

`order_by` 메서드로 쿼리셋을 정렬할 때는 대문자가 소문자보다 높은 우선순위를 가진다.

텍스트 필드에서 대문자·소문자를 구별하지 않고 정렬하려면  `Lower`을 사용한다.

```python
from django.db.models.functions import Lower
User.objects.all().order_by(Lower('username')).values_list('username', flat=True)
```

`annotate` 메서드로 `Lower`를 적용한 열을 준비하고, 그 열을 기준으로 정렬할 수도 있다.

```python
User.objects.annotate(
    lower_name=Lower('username')
).order_by('lower_name').values_list('username', flat=True)
```



**외래 키로 연결된 다른 표의 열을 기준으로 정렬**

`Category` 모델과 `Hero` 모델이 다음과 같이 외래 키로 연결되어 있다.

```python
class Category(models.Model):
    name = models.CharField(max_length=100)


class Hero(models.Model):
    # ...
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
```

아래 코드는 `Hero` 모델의 쿼리셋을 category 필드 순으로 정렬하되, category가 같은 항목은 `Hero`의 name 필드 순으로 정렬한다.

```python
Hero.objects.all().order_by(
  'category__name', 'name'
)
```

`category__name`의 이중 밑줄 기호(\_\_)로 모델의 필드를 가리킬 수 있다.



**계산된 필드를 기준으로 정렬**

위의 `Category` 모델과 `Hero` 모델에서 `Category` 항목들을 각 `Category` 항목에 속한 `Hero` 항목의 개수에 따라 정렬하고 싶다면, 다음과 같이 `annotate` 메서드로 계산 필드를 준비하여 기준으로 삼을 수 있다.

```python
Category.objects.annotate(
    hero_count=Count("hero")
).order_by(
    "-hero_count"
)
```



### 모델 간의 관계

**일대일 관계**

일대일 관계란 두 표에서 각 항목이 서로 다른 표의 항목 단 하나와 연결되는 관계다. 예를 들어, 우리들 각자는 생부와 생모를 각각 하나씩만 가질 수 있다.

```python
from django.contrib.auth.models import User

class UserParent(models.Model):
    user = models.OneToOneField(
      User,
      on_delete=models.CASCADE,
      primary_key=True,
    )
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
```

`on_delete` 메서드는 그 필드에 연결된 항목이 삭제될 때, 그 항목을 가리키는 항목들을 어떻게 처리해야 할지 결정한다.



**일대다 관계**

일대다 관계는 한 표의 상위 항목이 다른 표의 여러 하위 항목에서 참조되는 관계다. 일대다 관계에서 상위 항목이 반드시 하위 항목을 가진다는 보장은 없다.

장고 모델에서 일대다 관계를 정의할 때는 `ForeignKey` 필드를 사용한다.

```python
class Article(models.Model):
    headline = models.CharField(max_length=100)
    pub_date = models.DateField()
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reporter')

    def __str__(self):
        return self.headline

    class Meta:
        ordering = ('headline',)
```

상위 객체를 데이터베이스에 저장하지 않은 채로 하위 객체에 할당하려 하면 `ValueError`가 발생한다.



**다대다 관계**

다대다 관계란 한 표의 항목이 다른 표의 항목 여러 개를 가리킬 수 있고, 반대로 다른 표의 항목이 그 표의 항목을 여러 개 가리킬 수 있는 관계다.

장고 모델에서 다대다 관계를 정의할 때는 `ManyToMany` 필드를 사용한다.

```python
class User(AbstractUser):
    tweet = models.ManyToManyField(Tweet, blank=True)
    follower = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    pass

class Tweet(models.Model):
    tweet = models.TextField()
    favorite = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='user_favorite')

    def __unicode__(self):
        return self.tweet
```



**모델에 자기 참조 외래 키를 정의**

자기 참조 외래 키를 이용하여 중첩 관계·재귀 관계를 표현할 수 있다. 일대다 관계와 유사하지만, 모델이 자기 자신을 참조한다는 특징을 가진다.

```python
class Employee(models.Model):
    manager = models.ForeignKey('self', on_delete=models.CASCADE)

# 또는

class Employee(models.Model):
    manager = models.ForeignKey("app.Employee", on_delete=models.CASCADE)
```



### 데이터베이스

**기존 데이터베이스를 장고 모델로 옮기기**

장고에는 기존 데이터베이스를 분석하여 그에 맞는 모델을 생성해주는 `inspectdb` 명령어가 있다.

```shell
$ python manage.py inspectdb
```

이 명령을 실행하려면 먼저 `settings.py` 파일에 분석하려는 데이터베이스의 접속 정보를 설정해둬야한다. 출력결과로 생성되는 파일은 모델의 파이썬 코드다.

```shell
$ python manage.py inspectdb > models.py
```



**데이터베이스 뷰에 대응하는 모델 정의**

데이터베이스 뷰는 데이터베이스 내에서 조회할 수 있도록 질의문으로 정의된 객체다. 뷰가 데이터를 물리적으로 저장하는 것은 아니지만, 실제 표와 같이 조회할 수 있기 때문에 ‘가상 표’라고 불리기도 한다. 뷰는 여러 표를 결합(JOIN)한 정보를 보여줄 수도 있고, 한 표의 부분 집합만을 보여줄 수도 있다. 이를 활용하면 복잡한 질의문을 감추고 필요한 정보를 쉽게 조회하는 인터페이스를 만들 수 있다.

장고 앱에서는 모델을 정의할 때 메타(`Meta`) 클래스에 `managed = False`, `db_table="temp_user"` 와 같이 옵션을 설정하여 뷰를 가리키는 모델로 사용할 수 있다.

```python
class TempUser(models.Model):
    first_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "temp_user"
```

생성된 모델은 실제 표와 마찬가지로 뷰를 조회할 수 있다. 하지만, 뷰에 기록은 하지 못한다.



**모델에 연결된 표의 이름을 지정**

모델에 연결된 데이터베이스 표의 이름을 직접 지정하지 않으면 장고가 자동으로 표의 이름을 지어준다. 자동으로 붙는 데이터베이스 표의 이름은 '앱의 레이블(manage.py startapp 명령어에서 지은 이름)'과 모델 클래스의 이름을 밑줄 기호로 연결한 것이다.

이름을 직접 붙이려면 `Meta` 클래스에  `db_table` 값을 설정하면 된다.

```python
class TempUser(models.Model):
    first_name = models.CharField(max_length=100)
    . . .
    class Meta:
        db_table = "temp_user"
```



**모델 필드의 데이터베이스 열 이름 지정**

필드 인스턴스 초기화 매개변수 `db_column`에 원하는 이름을 전달하면 된다.

```python
class ColumnName(models.Model):
    a = models.CharField(max_length=40,db_column='column1')
    column2 = models.CharField(max_length=50)

    def __str__(self):
        return self.a
```



**하나의 장고 프로젝트에서 여러 개의 데이터베이스 사용**

데이터베이스의 접속에 관련된 설정은 대부분 `settings.py` 파일에서 이루어진다. 장고 프로젝트에 여러 개의 데이터베이스를 추가하려면 해당 파일의 `DATABASES` 사전에 등록하면 된다.

```python
DATABASE_ROUTERS = ['path.to.DemoRouter']
DATABASE_APPS_MAPPING = {'user_data': 'users_db',
                        'customer_data':'customers_db'}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'users_db': {
        'NAME': 'user_data',
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'postgres_user',
        'PASSWORD': 'password'
    },
    'customers_db': {
        'NAME': 'customer_data',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'mysql_cust',
        'PASSWORD': 'root'
    }
}
```

여러 개의 데이터베이스를 함께 사용하려면 데이터베이스 중계기(database router)에 대해 알아야 한다. 장고의 기본 중계 설정은 데이터베이스를 특정하지 않은 경우 기본(default) 데이터베이스로 중계하는 것이다. `DATABASE_ROUTERS` 설정의 기본값은 `[]` 입니다. 중계기는 다음과 같이 정의할 수 있다.

```python
class DemoRouter:
    """
    user_data 앱의 모델에서 수행되는 모든 데이터베이스 연산을 제어하는 중계기
    """
    def db_for_read(self, model, **hints):
        """
        user_data 앱의 모델을 조회하는 경우 users_db로 중계한다.
        """
        if model._meta.app_label == 'user_data':
            return 'users_db'
        return None

    def db_for_write(self, model, **hints):
        """
        user_data 앱의 모델을 기록하는 경우 users_db로 중계한다.
        """
        if model._meta.app_label == 'user_data':
            return 'users_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        user_data 앱의 모델과 관련된 관계 접근을 허용한다.
        """
        if obj1._meta.app_label == 'user_data' or \
           obj2._meta.app_label == 'user_data':
           return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        user_data 앱의 모델에 대응하는 표가 users_db 데이터베이스에만 생성되도록 한다.
        """
        if app_label == 'user_data':
            return db == 'users_db'
        return None
```



### 그 외

**장고 ORM의 실제 SQL 질의문** : `queryset.query`



**FileField에 파일이 들어있지 않은 행 검색** : 장고의 `FileField`와 `ImageField`는 파일과 이미지 경로를 저장한다. 이는 응용 수준에서의 구별이고 데이터베이스 수준에서는 모두 `CharField`와 동일한 방식으로 저장된다.

```python
no_files_objects = MyModel.objects.filter(
  Q(file='')|Q(file=None)
)
```



**특정 열의 값이 같은 항목을 검색**

```python
duplicates = User.objects.values(
  'first_name' # 'first_name'을 가져온다
)
.annotate(name__count=Count('first_name')) # first_name를 세는데
.filter(name_count__gt=1) # 개수가 1 이상일 때
```

```python
records = User.objects.filter(first_name__in=[item['first_name'] for item in duplicates])
```



**고유한 필드 값을 가지는 항목 검색**

```python
distinct = User.objects.values(
    'first_name'
).annotate(
    name_count=Count('first_name')
).filter(name_count=1)
records = User.objects.filter(first_name__in=[item['first_name'] for item in distinct])
```

`User.objects.distinct("first_name").all()`는 고유한 `first_name`을 가진 사용자 별로 첫번째 사용자를 구하는 코드다.



**장고가 지원하지 않는 데이터베이스의 함수 사용**

장고의 `Func` 객체를 사용하면 된다.

```python
from django.db.models import Func, F
Hero.objects.annotate(like_zeus=Func(F('name'), function='levenshtein', template="%(function)s(%(expressions)s, 'Zeus')"))
```

다음과 같이 클래스를 확장하여 정의하면 사용하기 편리하다.

```python
class LevenshteinLikeZeus(Func):
    function='levenshtein'
    template="%(function)s(%(expressions)s, 'Zeus')"
```

이제 `Hero.objects.annotate(like_zeus=LevenshteinLikeZeus(F("name")))`와 같이 클래스로 사용이 가능하다.



**모델 인스턴스 생성 시의 시그널**

장고의 시그널을 이용하면 모델 인스턴스의 생명주기에 따라 특정 코드가 실행되도록 예약해 둘 수 있다. 장고에서 제공하는 시그널의 종류는 다음과 같다.

- `pre_init`
- `post_init`
- `pre_save`
- `post_save`
- `pre_delete`
- `post_delete`

이 가운데 `pre_save`와 `post_save`가 가장 많이 사용된다.

시그널을 이용하면 `save` 메서드를 재정의하는 것과 비슷한 효과를 누릴 수 있다. 어느 것을 사용할지는 다음 규칙을 권장한다.

- 다른 사람(외부 라이브러리)이 앱의 `save` 메서드를 재정의·커스터마이즈하도록 허용하려면 직접 시그널을 발생시킨다.
- 통제할 수 없는 앱의 `save` 메서드가 호출될 때 원하는 코드가 실행되도록 하려면 `post_save` 시그널 또는 `pre_save` 시그널을 사용한다.
- 통제할 수 있는 앱의 저장 방식을 손 볼 때는 `save` 메서드를 재정의한다.



**시간 정보를 다른 양식으로 변환하여 데이터베이스에 저장**

장고의 dateparser 모듈이나 파이썬 표준 라이브러리를 이용하여 날짜 양식을 변환할 수 있다.

```python
user = User.objects.get(id=1)
date_str = "2018-03-11"
from django.utils.dateparse import parse_date // Way 1
temp_date = parse_date(date_str)
a1 = Article(headline="String converted to date", pub_date=temp_date, reporter=user)
a1.save()
a1.pub_date

from datetime import datetime // Way 2
temp_date = datetime.strptime(date_str, "%Y-%m-%d").date()
a2 = Article(headline="String converted to date way 2", pub_date=temp_date, reporter=user)
a2.save()
a2.pub_date
```



**`null=True`와 `blank=True`의 차이점**

`null`과 `blank`는 둘 다 기본값이 `False`다. 이 두 설정 모두 필드(열) 수준에서 동작한다.

`null=True`는 필드의 값이 NULL(정보 없음)로 저장되는 것을 허용한다. 데이터베이스 열에 관한 설정이다.

```python
date = models.DateTimeField(null=True)
```

`blank=True`는 필드가 폼(입력 양식)에서 빈 채로 저장되는 것을 허용한다. 장고 관리자(admin) 및 직접 정의한 폼에도 반영된다.

```python
title = models.CharField(blank=True)  # 폼에서 비워둘 수 있다. 데이터베이스에는 ''으로 저장.
```

`null=True`와 `blank=True`을 모두 지정하면 어떤 조건으로든 값을 비워둘 수 있다는 의미가 된다.

```python
epic = models.ForeignKey(null=True, blank=True)
# 단, CharFields()와 TextFields()에서는 예외다.
# 장고는 이 경우 NULL을 저장하지 않으며, 빈 값을 빈 문자열('')로 저장한다.
```

또 하나 예외적인 경우가 있는데, 불리언 필드(`BooleanField`)은 `null=True` 대신에 널 불리언 필드(`NullBooleanField`)를 사용해야 한다.



**기본 키(PK)로 ID 대신 UUID 사용**

장고에서 모델을 생성하면 ID 필드가 기본 키로 생성된다. 양의 정수가 아닌 UUID를 기본 키로 사용하고 싶다면 장고 1.8에서 추가된 `UUIDField`를 사용하면 된다.

```python
import uuid
from django.db import models

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    details = models.TextField()
    years_ago = models.PositiveIntegerField()
```



**슬러그 필드**

슬러그(slug)는 URL의 구성요소로 웹사이트의 특정 페이지를 가리키는 사람이 읽기 쉬운 형식의 식별자다. 장고에서는 슬러그 필드(`SlugField`)로 슬러그를 지원한다. 앞서 살펴보았던 `Article` 모델에 슬러그 필드를 추가해 가독성을 높일 수 있다.

```python
from django.utils.text import slugify
class Article(models.Model):
    headline = models.CharField(max_length=100)
    . . .
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.headline)
        super(Article, self).save(*args, **kwargs)
    . . .
```

```shell
>>> u1 = User.objects.get(id=1)
>>> from datetime import date
>>> a1 = Article.objects.create(headline="todays market report", pub_date=date(2018, 3, 6), reporter=u1)
>>> a1.save()
# 슬러그는 자동으로 생성된다. create 메서드를 따로 정의한 것이 아니다.
>>> a1.slug
'todays-market-report'
```

슬러그의 장점은 사람이 이해하기 좋고, 제목과 URL을 동일하게 맞춰 검색엔진 최적화(SEO)에 도움이 된다.