# Model(basic)

모델은 데이터에 대한 하나의 정보의 소스로 모델은 저장하고 있는 데이터의 필수적인 필드와 동작을 포함하고 있습니다. 각각의 모델은 하나의 데이터베이스 테이블에 매핑됩니다.

- 각각의 모델은 파이썬 클래스로 **django.db.models.Model**에 속합니다.
- 모델의 인자들은 각각이 데이터베이스의 필드를 의미합니다.
- 장고는 자동으로 생성되는 데이터베이스-엑세스 API를 실행해줍니다.

```python
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
```

```sql
CREATE TABLE myapp_person (
    "id" serial NOT NULL PRIMARY KEY,
    "first_name" varchar(30) NOT NULL,
    "last_name" varchar(30) NOT NULL
)
```

- 테이블 이름인 **myapp_person**은 몇 모델의 메타데이터에서 자동으로 도출되며 오버라이딩이 가능합니다.
- **id** 필드는 자동으로 추가되나, 이 역시 오버라이드 될 수 있습니다.
- 이 예제는 PostgreSQL 구문을 이용해 구성됩니다. 하지만 장고는 데이터베이스 백엔드에 맞춘 SQL을 이용한다는 점에 주목할 만한 가치가 있습니다.



### 모델 이용하기

모델을 정의한 후에는 장고에 이 모델을 *이용*할 것이라고 얘기해줘야 합니다. 이는 설정(settings.py) 파일을 수정하면 됩니다. **INSTALLED_APPS**를 바꾸면 되는데, models.py를 포함하고 있는 모듈(앱)의 이름을 추가하면 설정됩니다.

```python
INSTALLED_APPS = [
    #...,
    'myapp',
    #...
]
```

새로운 앱을 **INSTALLED_APPS**에 추가했다면 `python manage.py makemigrations my_app`, `python manage.py migrate`을 통해 마이그레이션 작업을 해야합니다.



### 필드

모델에서 가장 중요한 부분으로 데이터베이스 필드에 정의된 리스트를 꼽을 수 있습니다. 필드는 클래스 인자로 정의됩니다. 필드명을 지정할 때는 **model API**에서 지정한 이름과 충돌이 나지 않도록 조심해야합니다.(ex. **clean**, **save**, **delete**...)

```python
from django.db import models

class Musician(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    instrument = models.CharField(max_length=100)
    
class Album(models.Model):
    artist = models.ForeignKey(Musician, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    release_data = models.DateField()
    num_stars = models.IntegerField()
```



### 필드 타입

모델에 있는 각각의 필드는 적절한 **Field** 클래스의 인스턴스가 되어야합니다. 장고는 몇가지 필드 클래스 타입을 사용하고 있습니다.

- 컬럼 타입은 데이터베이스에 저장될 데이터의 종류를 의미합니다.(ex. **INTEGER**, **VARCHAR**, **TEXT**)
- 폼 필드를 렌더링할 때는 기본값으로 HTML 위젯을 사용합니다.(ex. \<input type="text">, \<select>)
- 자동으로 생성되는 폼들과 장고 어드민에서 사용될 최소한의 인증이 요구됩니다.

적절한 필드 클래스에 대해서는 다음 문서를 참고합니다. [모델 필드 문서](https://docs.djangoproject.com/ko/3.1/ref/models/fields/#model-field-types)

필요에 따라서는 직접 맞춤형 필드를 작성할 수도 있습니다. [모델 맞춤 필드 작성](https://docs.djangoproject.com/ko/3.1/howto/custom-model-fields/)



### 필드 일반 옵션

각각의 필드는 필드에 특정한 인자들을 받습니다.

- **null** : True라면 **NULL** 값을 데이터베이스에 저장할 수 있습니다. 기본값은 False입니다.

- **blank** : True라면 필드는 빈 값을 허용합니다. 기본값은 False입니다.

  null은 순수 데이터베이스와 관련된 개념이라면 blank는 검증에 관련된 개념입니다. blank=True라면 폼 검증단계에서 빈 값을 입력해도 허용됩니다.

- **choices** : 2개의 값으로 이루어진 튜플 시퀀스를 받습니다. 해당 필드는 기본적으로 select box로 렌더링되며, 선택지를 제한할 수 있습니다.

  튜플의 첫번째 인자는 데이터베이스에 저장될 값을 의미하며, 두번째 인자는 폼 필드 위젯에서 보여줄 값을 의미합니다.

  주어진 모델 인스턴스에서 `get_FOO_display()`를 통해 두번째 인자 값을 가져올 수 있습니다.

  ```python
  from django.db import models
  
  class Person(models.Model):
      SHIRT_SIZES = (
          ('S', 'Small'),
          ('M', 'Medium'),
          ('L', 'Large')
      )
      name = models.CharField(max_length=60)
      shirt_size = models.CharField(max_length=1, choices=SHIRT_SIZES)
  ```

  ```python
  p = Person(name="Winters", shirt_size="L")
  p.save()
  p.shirt_size # "L"
  p.get_shirt_size_display() # "Large"
  ```

  열거형 클래스에 대해서도 choices를 사용할 수 있습니다.

  ```python
  from django.db import models
  
  class Runner(models.Model):
      MedalType = models.TextChoices('Medal Type', 'GOLD SILVER BRONZE')
      name = models.CharField(max_length=60)
      medal = models.CharField(blank=True, choices=MedalType.choices, max_length=10)
  ```

- **default** : 필드의 기본 값을 지정하며, 값 또는 호출가능한 객체가 될 수 있다. 새로운 객체가 생성될 때마다 호출된다.

- **help_text** : 폼 위젯에 도움이 될 수 있는 정보를 표시한다. 폼을 사용하지 않는 필드더라도 문서 작업에 유용하다.

- **primary_key** : 참이라면 필드는 모델의 primary key가 된다.

  primary_key=True를 모델의 어떤 필드에서도 정의하지 않았다면 장고는 자동으로 `id = models.AutoField(primary_key=True)`를 생성하여 사용한다. 따라서, 굳이 primary key를 지정하여 오버라이드하지 않고도 primary key를 사용할 수 있다.

  primary key는 읽기 전용이며, 이미 생성된 객체의 primary key를 변경할 경우에는 새로운 객체가 생성된다.

- **unique** : 참이라면 필드는 테이블 내에서 유일한 값을 갖는다.



### 자동으로 증가하는 primary key 필드

앞서 언급했듯이 장고는 모델마다 다음 필드를 기본적으로 생성한다.

```python
id = models.AutoField(primary_key=True)
```

만약에 필드에 명시적으로 `primary_key=True` 옵션을 가지고 있는 필드가 존재할 경우, 장고는 id 컬럼을 생성하지 않는다. 각각의 모델에는 반드시 한 개의 `primary_key=True` 옵션을 가지고 있는 필드가 존재해야한다.



### 필드명

**ForeignKey**, **ManyToManyField**, 그리고 **OneToOneField**를 제외한 필드들은 첫번째 위치인자로 필드명을 설정할 수 있습니다. 다중 필드명이 주어지지 않았을 경우, 장고는 자동으로 필드의 변수명에서 언더스코어(\_)를 스페이스로 바꿔 사용합니다.

```python
# verbose name is 'person's first name'
first_name = models.CharField("person's first name", max_length=30)

# verbose name is 'first name'
first_name = models.CharField(max_length=30)
```

**ForeignKey**, **ManyToManyField**, 그리고 **OneToOneField**는 첫 번째 위치인자로 모델 클래스를 받으므로 별도로 **verbose_name** 키워드 인자를 설정해야합니다.

```python
poll = models.ForeignKey(
    Poll,
    on_delete=models.CASCADE,
    verbose_name="the related poll",
)
sites = models.ManyToManyField(Site, verbose_name="list of sites")
place = models.OneToOneField(
    Place,
    on_delete=models.CASCADE,
    verbose_name="related place",
)
```

**verbose_name**은 소문자로 작성하는 것이 원칙입니다. 장고가 알아서 첫번째 문자를 대문자로 변경하기 때문입니다.



### 관계

관계형 필드는 관계형 데이터베이스의 강점인 테이블 상호간의 관계에서 기인합니다. 장고는 주요한 3가지 데이터베이스 관계 : 다대일, 다대다, 일대일을 제공합니다.

- **다대일 관계** : 다대일 관계를 정의하기 위해 **django.db.model.ForeignKey**를 사용합니다. 다른 **Field** 타입을 사용하듯이 모델에 클래스 속성을 포함시킴으로써 사용합니다.

  **django.db.model.ForeignKey**는 위치 기반 인자로 해당 모델과 관련있는 클래스를 필요로 합니다.

  ```python
  from django.db import models
  
  class Manufacturer(models.Model):
      # ...
      pass
  
  class Car(models.Model):
      manufacturer = models.ForeignKey(Manufacturer, on_delete=models.CASCADE)
      # ...
  ```

  또한 [재귀 관계](https://docs.djangoproject.com/ko/3.1/ref/models/fields/#recursive-relationships)(자신을 참조하는 다대일 관계를 갖는 객체)와 [아직 정의되지 않은 모델과의 관계](https://docs.djangoproject.com/ko/3.1/ref/models/fields/#lazy-relationships)도 생성할 수 있습니다. 자세한 내용은 [모델 필드 레퍼런스](https://docs.djangoproject.com/ko/3.1/ref/models/fields/#ref-foreignkey)를 참조하세요.

  **ForeignKey** 필드로 사용되는 변수명은 자유롭게 변경이 가능합니다.

  ```python
  class Car(models.Model):
      company_that_makes_it = models.ForeignKey(
          Manufacturer,
          on_delete=models.CASCADE,
      )
  ```

- **다대다 관계** : 다대다 관계를 정의하기 위해서는 **ManyToManyField**를 다른 **Field** 타입에 사용하듯이 모델의 클래스 속성처럼 포함시켜 사용하면 됩니다.

  **ManyToManyField**는 위치인자로 모델과 관련있는 클래스를 받습니다.

  ```python
  from django.db import models
  
  class Topping(models.Model):
      # ...
      pass
  
  class Pizza(models.Model):
      # ...
      toppings = models.ManyToManyField(Topping)
  ```

  **ManyToManyField**에서 모델 오브젝트들의 관계를 복수 명사로 표기하는 것을 권장합니다. 어떤 모델을 기준으로 정의할지는 상관 없지만 둘 다가 아닌, 하나의 모델에서만 정의해야합니다.

  일반적으로 **ManyToManyField** 인스턴스는 폼에서 수정되어질 오브젝트 안에 위치해야합니다. 위 예에서 상식적으로 Pizza는 여러개의 Topping을 가질 수 있지만, Topping은 여러 개의 Pizza를 가지는 것이 맞지 않기 때문입니다.

- **다대다 관계**에서의 여분의 필드들

  두 모델 간의 관계에 대한 필드를 추가적으로 다룰 필요가 있을때, 다음과 같이 중간단계의 임시모델을 추가하여 관리할 수 있습니다. **ManyToManyField**의 **through** 키워드 인자를 세팅하면 됩니다.

  ```python
  from django.db import models
  
  class Person(models.Model):
      name = models.CharField(max_length=128)
  
      def __str__(self):
          return self.name
  
  class Group(models.Model):
      name = models.CharField(max_length=128)
      members = models.ManyToManyField(Person, through='Membership')
  
      def __str__(self):
          return self.name
  
  class Membership(models.Model):
      person = models.ForeignKey(Person, on_delete=models.CASCADE)
      group = models.ForeignKey(Group, on_delete=models.CASCADE)
      date_joined = models.DateField()
      invite_reason = models.CharField(max_length=64)
  ```

  임시모델을 설정했을 경우에는 두 모델 모두 명시적으로 **Foreign Key**로 정의하여 다대다 관계임을 보여주어야 합니다. 이러한 명시적인 선언은 두 모델이 어떤 관계에 있는지를 알려줍니다.

  - 중간 모델은 반드시 하나의 **Foreign Key**를 가져야 합니다. 또는 장고가 모델간의 관계를 **ManyToManyField.through_fields**로 사용하기 위해 **Foreign Key**들을 명시적으로 정의해야합니다. 만약 두개 이상의 **Foreign Key**가 정의되어 있고 **through_fields**가 정의되어있지 않다면 검증에러가 반환됩니다.
  - 자체적으로 임시 모델을 통한 다대다 관계를 가지는 모델에 대해서는 동일한 모델에 대해서 두 개의 **Foreign Key**를 가지는 것이 허용된다. 하지만 이들은 서로 다른 다대다 관계로 다루어진다. 두개보다 더 많은 **Foreign Key**를 사용한다면 반드시 **through_fields**를 정의해야 한다. 

  ```shell
  >>> ringo = Person.objects.create(name="Ringo Starr")
  >>> paul = Person.objects.create(name="Paul McCartney")
  >>> beatles = Group.objects.create(name="The Beatles")
  >>> m1 = Membership(person=ringo, group=beatles,
  ...     date_joined=date(1962, 8, 16),
  ...     invite_reason="Needed a new drummer.")
  >>> m1.save()
  >>> beatles.members.all()
  <QuerySet [<Person: Ringo Starr>]>
  >>> ringo.group_set.all()
  <QuerySet [<Group: The Beatles>]>
  >>> m2 = Membership.objects.create(person=paul, group=beatles,
  ...     date_joined=date(1960, 8, 1),
  ...     invite_reason="Wanted to form a band.")
  >>> beatles.members.all()
  <QuerySet [<Person: Ringo Starr>, <Person: Paul McCartney>]>
  ```

  **through_defaults** 키워드 인자를 정의하여 **add()**, **create()**, **set()** 작업을 수행할 수 있습니다.

  ```shell
  >>> beatles.members.add(john, through_defaults={'date_joined': date(1960, 8, 1)})
  >>> beatles.members.create(name="George Harrison", through_defaults={'date_joined': date(1960, 8, 1)})
  >>> beatles.members.set([john, paul, ringo, george], through_defaults={'date_joined': date(1960, 8, 1)})
  ```

  임시 모델을 통해 인스턴스를 바로 생성하고 싶을 때도 있을 것이다. 만약 임시 모델이 두 모델 쌍에 대하여 다중 값을 허용하여 유일할 필요가 없다면 **remove()** 메서드는 모든 임시 모델의 인스턴스를 제거할 것이다. 

  ```shell
  >>> Membership.objects.create(person=ringo, group=beatles,
  ...     date_joined=date(1968, 9, 4),
  ...     invite_reason="You've been gone for a month and we miss you.")
  >>> beatles.members.all()
  <QuerySet [<Person: Ringo Starr>, <Person: Paul McCartney>, <Person: Ringo Starr>]>
  >>> # This deletes both of the intermediate model instances for Ringo Starr
  >>> beatles.members.remove(ringo)
  >>> beatles.members.all()
  <QuerySet [<Person: Paul McCartney>]>
  ```

  **clear()** 메서드는 인스턴스의 다대다 관계를 모두 제거한다.

  다대다 관계의 모델 및 임시 모델 또한 일반 모델처럼 쿼리를 사용할 수 있다.

- **일대일 관계** : 객체의 primary key를 다른 객체로 확장시킬 때 유용하다. **OneToOneField**는 위치 인자로 관련된 모델의 클래스를 받는다. 또한, **OneToOneField**는 **parent_link** 인자를 가진다. **OneToOneField** 클래스들은 해당 모델에서 자동으로 primary key로 사용된적도 있었지만, 지금은 그렇지 않다. 따라서 단일 모델에서 여러 개의 **OneToOneField**를 만들 수 있게 되었다.



### 다른 앱의 모델

다른 앱에 있는 모델과도 대응 관계를 만들 수 있다. 그러기 위해서는 해당 앱에 있는 모델을 임포트해와야 한다.

```python
from django.db import models
from geography.models import ZipCode

class Restaurant(models.Model):
    # ...
    zip_code = models.ForeignKey(
        ZipCode,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
```



### 필드 이름 제약

1. 필드 이름은 파이썬 예약어로 만들 수 없습니다.
2. Django의 쿼리 조회 문법과 구분짓기 위해 언더스코어는 두 개 이상 사용해서는 안됩니다.
3. 위와 같은 이유로 필드 이름은 언더스코어로 끝낼 수 없습니다.

SQL 예약어들은 모델 필드의 변수명으로 사용 가능한데, 이는 장고가 자동적으로 SQL 쿼리 예약어들을 피해가기 때문입니다. 이는 데이터베이스 엔진에 따라 다릅니다.



### 임의 필드 타입

[모델 맞춤 필드 작성](https://docs.djangoproject.com/ko/3.1/howto/custom-model-fields/)



### Meta 옵션

다음과 같이 모델에 메타데이터를 넣기 위해서 **Meta** 클래스를 추가하면 된다.

```python
from django.db import models

class Ox(models.Model):
    horn_length = models.IntegerField()

    class Meta:
        ordering = ["horn_length"]
        verbose_name_plural = "oxen"
```

모델의 메타데이터는 필드를 제외한 나머지로 순서 옵션(**ordering**), 데이터베이스 테이블 이름(**db_table**), 또는 사람이 읽기 쉬운 필드명(**verbose_name**, **verbose_name_plural**) 등이 있다. 모든 값은 필수가 아니므로 **Meta** 클래스를 추가하는 것은 선택이다.



### 모델 속성

- **objects** : 모델에서 가장 중요한 인자인 **Manager**다. 데이터베이스에 쿼리 작업을 수행하여 인스턴스들을 데이터베이스로부터 반환시킨다. **Manager**가 정의되어 있지 않다면 기본 이름인 **objects**가 사용된다. **Manager** 인자는 인스턴스로 접근할 수 없으며, 클래스로만 접근이 가능하다.



### 모델 메서드

모델에 임의 메서드를 정의하거나 추가할 수 있다. 이는 row-level에서의 기능이며, **Manager** 메서드는 table-wide한 것으로 일부 모델 인스턴스에서도 작동해야한다.

```python
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()

    def baby_boomer_status(self):
        "Returns the person's baby-boomer status."
        import datetime
        if self.birth_date < datetime.date(1945, 8, 1):
            return "Pre-boomer"
        elif self.birth_date < datetime.date(1965, 1, 1):
            return "Baby boomer"
        else:
            return "Post-boomer"

    @property
    def full_name(self):
        "Returns the person's full name."
        return '%s %s' % (self.first_name, self.last_name)
```

마지막 메서드는 프로퍼티 데코레이터의 예다.

[모델 인스턴스 문서](https://docs.djangoproject.com/ko/3.1/ref/models/instances/)를 보면 대부분의 메서드가 자동으로 주어지며, 주로 그 메서드들을 오버라이드하여 사용하게 된다.

- `__str__()` : 콘솔이나 관리자 창에서 객체를 표시하는 문자열을 반환한다. 기본값은 유용하지 않으므로 이 메서드를 정의할 것을 권장한다.
- `get_absolute_url()` : 객체를 위한 URL을 연산한다. 유일하게 구분되는 URL을 갖는 어떤 객체든 이 메서드가 정의되어야한다.



### 모델 메서드 오버라이딩

모델의 메서드 중에 은닉화 되어있지만 변경하고 싶은 메서드가 있을 수 있다. 업무중에 변경이 필요한 메서드는 대부분 **save()**와 **delete()**다.

장고는 이러한 메서드들을 오버라이딩하는데 제약이 없다.

```python
from django.db import models

class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def save(self, *args, **kwargs):
        do_something()
        super().save(*args, **kwargs)  # 미리 정의된 save()를 상속받아 실행시킨다.
        do_something_else()
```

```python
from django.db import models

class Blog(models.Model):
    name = models.CharField(max_length=100)
    tagline = models.TextField()

    def save(self, *args, **kwargs):
        if self.name == "Yoko Ono's blog":
            return # 이미 존재하는 객체의 생성을 막는다.
        else:
            super().save(*args, **kwargs)  # 미리 정의한 save()를 상속받아 실행시킨다.
```

항상 **super().save(\*args, \*\*kwargs)**를 호출하는 것을 잊어서는 안된다. 만약 이 슈퍼클래스 메서드를 호출하는 것을 잊었다면 데이터베이스에 데이터가 저장되지 않을 것이다.

또한, 슈퍼클래스 메서드를 호출할 때 인자(**\*args, \*\*kwargs**)를 반드시 포함해야한다. 이는 당신이 인자들을 추가하더라도 코드가 자동적으로 기능을 지원할 수 있게 해준다.

오버라이딩된 모델 메서드는 벌크 작업을 호출하지 않는다.



### 모델 상속

장고에서 모델 상속은 파이썬의 일반 클래스 상속과 거의 동일하다. 단, 여기서 기본 클래스는 **django.db.models.Model**의 서브클래스를 의미한다.

당신이 정해야할 것은 부모 모델을 모델 자체로 사용할 것인가, 아니면 자식 모델들의 공통적인 요소를 가지는 모델로 사용할 것인가이다.

장고에서 가능한 상속에는 3가지 스타일이 있다.

1. 자식 클래스들이 개별적으로 가지기를 원하지 않는 정보들을 부모 클래스에 저장하는 경우로 이는 자주 사용되는 스타일이다. 이 클래스는 단일로 사용되지 않으며, 이에 관해서는 [추상 기반 클래스](https://docs.djangoproject.com/ko/3.1/topics/db/models/#abstract-base-classes)을 참고하자.
2. 이미 존재하는 모델(대부분 다른 앱에 존재하는 모델)의 서브클래스를 만들고 각각의 모델이 각자의 데이터베이스 테이블을 가지기를 원한다면 [다중 테이블 상속](https://docs.djangoproject.com/ko/3.1/topics/db/models/#multi-table-inheritance)을 참고하자.
3. 마지막으로, 파이썬 단계에서 조정이 가능한 모델을 원한다면, 즉, 어떤 방법으로든 모델 필드를 변경하고 싶지 않다면 [대리 모델 (Proxy Model )](https://docs.djangoproject.com/ko/3.1/topics/db/models/#proxy-models)을 참고하자.



### 추상 기반 클래스

추상 기반 클래스는 다른 모델들이 공유하는 공통 데이터를 하나로 묶는데 유용하다. 추상 기반 클래스를 사용하기 위해서는 메타 클래스에 **abstract=True**라고 정의해주면 된다. 추상 기반 클래스로 정의된 모델은 데이터베이스 테이블을 추가적으로 생성하지 않는다. 대신, 다른 모델들의 기본 클래스로서 사용되면 자식 클래스의 필드에 추가되어 사용한다.

```python
class CommonInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True

class Student(CommonInfo):
    home_group = models.CharField(max_length=5)
```

**Student** 모델은 **home_group** 필드 외에도 **CommonInfo**로부터 상속받은 **name**, **age** 필드를 가진다. 또한, **CommonInfo** 모델은 추상 기반 클래스이므로 장고 모델로서 사용할 수 없다. 데이터베이스 테이블을 생성하지 않으며, 매니저를 가지지 않고 직접적으로 저장되거나 인스턴스화 될 수 없다. 대부분의 경우에 당신이 원하는 모델 상속은 추상 기반 클래스를 의미할 것이다.



### Meta 상속

추상 기반 클래스가 생성되면 장고는 내부에 선언된 **Meta** 클래스를 인자로서 사용 가능하게 한다. 만약 자식 클래스에 별도로 **Meta** 클래스가 선언되지 않았다면, 부모 클래스의 **Meta** 클래스를 상속받는다. 만약 자식 클래스에서 부모 클래스의 **Meta** 클래스를 확장하여 사용하고 싶다면 다음과 같이 사용하면 된다.

```python
from django.db import models

class CommonInfo(models.Model):
    # ...
    class Meta:
        abstract = True
        ordering = ['name']
        
class Student(CommonInfo):
    # ...
    class Meta(CommonInfo.Meta):
        db_table = 'student_info'
```

장고는 추상 기반 클래스의 **Meta** 클래스에 한가지 조건을 추가하는데, **Meta** 클래스 인자를 적용하기 전에 **abstract=False**를 세팅한다. 이는 추상 기반 클래스를 상속받은 자식 클래스가 추상 기반 클래스가 되는 것을 막아준다. 만약 추상 기반 클래스를 상속받은 자식 클래스를 추상 기반 클래스로 사용할 경우에는 **abstract=True**라고 명시적으로 자식의 **Meta** 클래스에 정의해야한다.

추상 기반 클래스의 **Meta** 클래스에 포함되는 몇몇 인자들은 상식적이지 않다. 예를 들어 **Meta** 클래스에 **db_table** 인자가 정의되어 있다고 가정하자. 추상 기반 클래스를 상속받은 모든 자식 클래스들은 데이터베이스 테이블에 동일한 이름을 사용할 것이며, 이는 우리가 원하는 방향이 아니다.

파이썬의 상속 방식 때문에 만약 자식 클래스가 여러 개의 추상 기반 클래스들을 상속받을 경우, 첫번째 추상 기반 클래스의 **Meta** 클래스만을 상속받는 것이 기본값이다. 여러 개의 추상 기반 클래스들로부터 **Meta** 클래스를 상속받고 싶다면 명시적으로 **Meta** 클래스 상속을 표기해야한다.

```python
from django.db import models

class CommonInfo(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    class Meta:
        abstract = True
        ordering = ['name']

class Unmanaged(models.Model):
    class Meta:
        abstract = True
        managed = False

class Student(CommonInfo, Unmanaged):
    home_group = models.CharField(max_length=5)

    class Meta(CommonInfo.Meta, Unmanaged.Meta):
        pass
```

**related_name과 related_query_name 사용에 주의**

만약 **ForeignKey**나 **ManyToManyField**에서 **related_name** 또는 **related_query_name**을 사용 중일 경우, 항상 유일한 역 필드명 또는 역 쿼리명 지정해주어야한다. 이 문제는 대체로 추상 기반 클래스에서 일어나는 문제로 자식 클래스들을 포함한 필드이 인자들에 대해 동일한 값을 가지기 때문에 일어나는 문제다.

이 문제를 다루기 위해서는 추상 기반 클래스에서 **related_name** 또는 **related_query_name**을 사용할 경우, 이 변수는 **%(app_label)s** 그리고 **%(class)s**를 포함해야한다.

- **%(class)s** : 필드를 사용하는 자식 클래스의 이름을 소문자로 대체한다.
- **%(app_label)s** : 자식 클래스를 포함하는 앱의 이름을 소문자로 대체한다. 각각의 앱은 프로젝트 폴더 내에서 유일한 이름을 가지기 때문이다.

```python
# common/models.py
from django.db import models

class Base(models.Model):
    m2m = models.ManyToManyField(
        OtherModel,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    class Meta:
        abstract = True

class ChildA(Base):
    pass

class ChildB(Base):
    pass
```

```python
# rare/models.py
from common.models import Base

class ChildB(Base):
    pass
```

**common.ChildA.m2m** 필드의 역 필드명은 **common_childa_related**이고 역 쿼리명은 **common_childa**가 된다. 같은 방법으로 **common.ChildB.m2m** 필드의 역 필드명은 **common_childb_related**이고 역 쿼리명은 **common_childb**가 된다. 마지막으로 **rare.ChildB.m2m** 필드의 역 필드명은 **rare_childb_related**이고 역 쿼리명은 **rare_childbs**가 된다. **%(class)s**와 **%(app_label)s**를 활용한다면 명명법은 사용자의 자유에 맞길 수 있다. 만약 이 방법을 사용하는 것을 잊어버려도 **migrate** 과정에서 발생하는 에러가 그 사실을 알려줄 것이다.

만약 추상 기반 클래스의 인자로 **related_name**을 지정하지 않았다면 기본 역 필드명은 자식 클래스의 이름 뒤에 **_set**을 붙인 값이다.



### 다중 테이블 상속

장고에서 제공하는 두번째 상속 모델 타입은 **다중 테이블 상속**입니다. 각각의 모델은 각자의 데이터베이스 테이블에 상응하며, 그렇기에 개별적으로 데이터가 생성되고 쿼리 작업이 이루어집니다. 상속 관계는 각각의 부모 모델의 자식 모델 간의 연결(**OneToOneField**가 자동적으로 생성됨으로써)로 이루어집니다.

```python
from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=80)

class Restaurant(Place):
    serves_hot_dogs = models.BooleanField(default=False)
    serves_pizza = models.BooleanField(default=False)
```

**Place**의 모든 필드는 **Restaurant**에서 사용이 가능합니다. 여기서 두 가지 가능성이 존재합니다.

```python
Place.objects.filter(name="Bob's Cafe")
Restaurant.objects.filter(name="Bob's Cafe")
```

 만약 **Restaurant**인 **Place**가 존재한다면 다음과 같이 **Place** 객체를 통해 **Restaurant** 객체에 접근할 수 있습니다.

```shell
>>> p = Place.objects.get(id=12)
# 만약 p가 Restaurant 객체라면, 이 값은 자식 클래스를 줄 것이다.
>>> p.restaurant
<Restaurant: ...>
```

하지만 위의 예제에서 **p** 변수는 **Restaurant**가 아닙니다.(이는 직접 **Place** 객체로서 생성되었거나 혹은 다른 클래스의 부모 클래스로서 만들어진 것입니다.) 그러므로 **p.restaurant**는 **Restaurant.DoesNotExist** 예외를 발생시킬 것입니다.

**Restaurant**에 자동적으로 생성된 **OneToOneField**로 **Place**에 연결된 코드는 다음과 같습니다.

```python
place_ptr = models.OneToOneField(
    place, on_delete=models.CASCADE,
    parent_link=True,
    primary_key=True
)
```

**Restaurant**에  **parent_link=True** 인자 값을 가지는 **OneToOneField**를 선언함으로써 오버라이딩이 가능합니다.



### Meta 그리고 다중 테이블 상속

**다중 테이블 상속**의 상황에서 자식 클래스가 부모 클래스의 **Meta** 클래스를 상속받는다는 것은 상식적이지 않습니다. 이미 정의되어 부모 클래스에 적용중인 **Meta** 클래스 옵션들을 자식 클래스에 다시 적용시킨다는 것은 모순적인 행동입니다.(이는 추상 기반 클래스의 경우와 반대의 경우입니다.)

따라서, **다중 테이블 상속**에서 자식 클래스는 부모 클래스의 **Meta** 클래스에 접근할 수 없습니다. 하지만, 몇가지 제한된 경우로 부모 클래스의 **Meta** 클래스를 상속받을 수 있습니다. 예시로 자식이 **ordering** 프로퍼티나 **get_last_by** 프로퍼티를 가지고 있지 않다면 부모 클래스로부터 상속받을 것입니다.

만약 부모 클래스의 프로퍼티를 상속받아 사용하기를 거부한다면 다음과 같이 명시적으로 사용하지 않는다는 것을 알려줘야합니다.

```python
class ChildModel(ParentModel):
    # ...
    class Meta:
        # 부모의 ordering 프로퍼티를 제거한다.
        ordering = []
```



### 상속과 역관계

**다중 상속 관계**에서는 부모 클래스와 자식 클래스가 암묵적으로 **OneToOneField**를 통해 연결되므로 부모 클래스에서 자식 클래스를 참조하는 것이 가능하다. 하지만, 이는 **Foreign Key**와 **ManyToManyField**의 **related_name**이 기본으로 값을 부여할 때만 사용이 가능하다. 앞에서 언급한 관계로 부모 모델의 서브클래스로 사용하려면 **related_name**을 반드시 정의해야 합니다.



### 부모 클래스와 연결할 필드 정의

앞에서 언급했듯이 부모 클래스와 자식 클래스는 자동적으로 **OneToOneField**가 생성되어 연결됩니다. 만약, **OneToOneField**를 임의의 이름으로 지정해주고 싶다면 인자에 **parent_link=True**를 세팅하여 **OneToOneField**를 생성하면 됩니다.



### 대리(Proxy) 모델

**다중 상속 관계**를 사용하면 모델 각각의 서브클래스에대한 새로운 데이터베이스 테이블이 생성됩니다. 이는 일반적으로 상속받은 모델에 정의되지 않은 필드를 서브클래스에 저장할 수 있도록 추가적인 필드를 생성할 수 있다는 점에서 바람직합니다. 하지만, 때로는 파이썬 단계에서의 작업으로 기본 매니저를 변경하거나 새로운 메서드를 추가하는 작업만을 원할 때가 있습니다.

이 경우가 기존 모델의 대리(proxy) 모델을 생성하기 위한 **대리 모델** 상속이 필요한 것입니다. 대리 모델의 인스턴스를 통해 이루어진 생성, 수정, 삭제 작업 등은 원래 모델에서 이루어진 것과 같이 작업이 수행됩니다. 단지 차이점이라면 원래 모델을 보존한 상태에서 모델에 새로운 기능을 추가하거나 변경할 수 있다는 점입니다.

대리 모델은 일반 모델과 마찬가지로 생성되며, **Meta** 클래스에 **proxy=True** 인자를 세팅하여 생성합니다.

```python
from django.db import models

class Person(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

class MyPerson(Person):
    class Meta:
        proxy = True

    def do_something(self):
        # ...
        pass
```

**MyPerson** 클래스는 동일한 데이터베이스 테이블에서 **Person** 클래스와 동일하게 작동합니다. **Person** 클래스의 어떤 인스턴스도 **MyPerson** 클래스에 접근이 가능하며, 그 역도 가능합니다.

또한, 대리 모델을 통해 동일한 모델에 다른 **Meta** 클래스를 적용하는 것도 가능합니다. 다음과 같이, 기본의 모델을 새롭게 정렬하는 것이 가능합니다.

```python
class OrderedPerson(Person):
    class Meta:
        ordering = ["last_name"]
        proxy = True
```

또한, 대리 모델은 기본 모델과 마찬가지로 **Meta** 클래스 인자를 상속받습니다.



### 쿼리셋은 아직 요청받은 모델을 반환한다.

장고에는 **Person** 객체를 쿼리한다고 해서 **MyPerson**이 반환되는 경우는 없습니다. 특정 객체를 위한 쿼리의 반환값은 항상 그 특정 객체가 됩니다. 대리 모델의 역할은 기존에 존재하는 모델을 확장시키기 위해 사용하는 것이지 기존의 모델을 대체하기 위해 만들어진 것이 아니기 때문입니다.



### 기본 클래스 제한

대리 모델은 반드시 추상 기반 모델 클래스가 아닌 단 하나의 모델 클래스를 상속받아야 합니다. 대리 모델을 생성할 때 다수의 일반 모델 클래스로부터 상속 받을 수 없습니다. 이는 대리 모델이 여러 테이블의 열에 동시에 연결하는 기능을 제공하지 않기 때문입니다. 대신 대리 모델은 다수의 추상 기반 모델을 상속받을 수 있는데, 이는 추상 기반 모델은 데이터베이스에 테이블을 생성하지 않기 때문입니다. 또한, 대리 모델은 여러 개의 대리 모델을 상속받을 수 있습니다. 이를 통해 대리 모델들 간에는 일반 부모 클래스를 공유할 수 있습니다.



### 대리 모델 매니저

대리 모델에 특정한 매니저를 정의하지 않을 경우, 대리 모델은 부모 모델로부터 매니저를 받습니다. 만약 대리 모델의 매니저를 정의한다면 부모 모델이 매니저를 가지고 있다고 해도 정의된 매니저가 기본값이됩니다.

```python
from django.db import models

class NewManager(models.Manager):
    # ...
    pass

class MyPerson(Person):
    objects = NewManager()

    class Meta:
        proxy = True
```

대리 모델에 새 매니저를 추가하고 싶다면, 다음과 같이 새로운 매니저를 가지고 있는 기본 클래스를 생성하여 상속받게 하면 됩니다.

```python
# 새로운 매니저를 위한 추상 클래스 생성
class ExtraManagers(models.Model):
    secondary = NewManager()

    class Meta:
        abstract = True

class MyPerson(Person, ExtraManagers):
    class Meta:
        proxy = True
```

자주 사용되는 팁은 아니지만 필요할 때는 도움이 될 것입니다.



### 대리 모델 상속과 언매니지드 모델의 차이점

대리 모델 상속은 언매니지드 모델을 만드는 과정과 유사해보이지만, 모델의 **Meta** 클래스가 매니지드 인자를 사용합니다.

**Meta.db_table**을 세팅하여 기존의 모델을 숨기는 언매니지드 모델을 만들고 파이썬 매서드가 매니저의 역할을 대신하게 할 수 있습니다. 하지만, 이같은 방식은 반복적이고 변화가 일어났을 때 양쪽이 동기화되어야 한다는 점에서 오류가 일어나기 쉽습니다.

반면, 대리 모델은 모델과 똑같이 작동하도록 의도되었습니다. 부모 모델의 필드와 매니저를 상속받았다면 대리 모델은 항상 부모 모델과 동기화가 일어납니다.

1. 만약 기존의 데이터베이스 테이블 열을 가져오지 않고, 이미 존재하는 데이터베이스 테이블이나 모델을 미러랑하기를 원한다면, **Meta.managed=False**로 설정하면 된다. 이 옵션은 장고에 의해 관리되지 않는 데이터베이스 테이블이나 뷰의 모델링에 유용하다.
2. 만약 모델의 파이썬 관련된 작업만을 변경하고자 하면서 기본 모델의 필드를 동일하게 계속 유지하고 싶다면 **Meta.proxy=True**로 설정하면 된다. 이 옵션은 데이터가 저장될 때 원본 모델의 저장구조를 정확히 똑같이 복사하여 대리 모델이 사용할 수 있게 해줍니다.

### 다중 상속

파이썬의 서브클래스화처럼 장고의 모델도 여러 부모 모델들로부터 다중 상속을 지원합니다. 일반적으로 파이썬의 명명법을 따라간다는 사실을 명심해야합니다. 첫번째 기본 클래스에 보여지는 이름이 사용될 이름입니다. 예를 들어, 각각의 부모 클래스들이 각자 **Meta** 클래스를 가지고 있다해도 첫번째 부모의 **Meta** 클래스만을 상속받고 다른 부모들의 **Meta** 클래스는 무시됩니다.

일반적으로, 다중 상속을 사용할 필요는 없습니다. 다중 상속의 장점은 여러 "mixin" 클래스를 조합할 때 유용하다는 점입니다. 클래스 간의 상속과 위계관계는 가능한한 명확하고 단순할수록 좋습니다.

다중 상속에 사용되는 모델들이 공통적으로 **id** primary key 필드를 공유하고 있다면 예외가 발생하게 됩니다. 다중 상속을 사용할 때는 다음과 같이 명시적으로 **AutoField**를 기본 모델에 정의해야합니다.

```python
class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    ...

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    ...

class BookReview(Book, Article):
    pass
```

또는, **AutoField**를 가지는 공통 조상을 사용하는 것도 방법입니다. 이 경우에는 각각의 부모 모델에 **OneToOneField**를 명시적으로 설정하여 자식 모델에 상속되는 자동 생성 필드 간의 충돌을 방지해야합니다.

```python
class Piece(models.Model):
    pass

class Article(Piece):
    article_piece = models.OneToOneField(Piece, on_delete=models.CASCADE, parent_link=True)
    ...

class Book(Piece):
    book_piece = models.OneToOneField(Piece, on_delete=models.CASCADE, parent_link=True)
    ...

class BookReview(Book, Article):
    pass
```



### 필드 이름으로 "hiding"은 허용되지 않습니다.

일반 파이썬 클래스의 상속에서 자식 클래스는 어떤 부모 클래스든 간에 인자에 대한 오버라이딩을 허용합니다. 장고에서는 일반적으로 모델 필드에 대한 오버라이딩을 허용하지 않습니다.

이 제한은 추상 기반 모델을 상속받을 때 적용되지 않습니다. 그러한 필드는 다른 필드 혹은 값에 의해 오버라이딩 되거나 **field_name=None**으로 제거할 수 있습니다.

부모 모델에 속한 필드에 대한 오버라이딩은 새로운 인스턴스를 초기화(**Model.\_\_init\_\_**)나 직렬화에 어려울 수 있습니다. 이러한 특징들은 일반 파이썬 클래스의 상속으로는 다룰 수 없습니다. 그래서 장고 모델 간의 상속이 파이썬의 상속과 갖는 차이는 일관됩니다.

이러한 제한은 오직 **Field** 인스턴스인 속성에 대해서만 적용됩니다. 보통의 파이썬 인자라면 필요할 때 오버라이딩을 할 수 있습니다. 또한 이 제한은 파이썬이 그것을 알아차렸을 때 그 속성의 이름에 적용됩니다. 만일 수동으로 데이터베이스의 컬럼에 이름을 명시적으로 사용했다면 자식 모델과 조상 모델이 동일한 이름을 갖는 컬럼을 가지게 됩니다.

만약 조상 모델의 모델 필드를 오버라이딩할 경우에는 장고에서 **FieldError** 예외를 발생시킵니다.



### 패키지 안의 모델 조직화

**manage.py startapp** 명령은 **models.py** 파일을 포함하는 애플리케이션 구조를 생성합니다. 만약 모델의 수가 많다면 그들을 각각의 파일로 분리해서 관리하는 것이 유용합니다.

모델에 대한 패키지를 만들기 위해서는 **models.py** 파일을 제거하고 **myapp/models/** 디렉토리를 생성하여 **\_\_init\_\_.py** 파일에서 사용되는 모델들을 임포트해야합니다.

**from .models import \*** 보다는 **from .modles import Person**과 같이 필요한 모델만을 임포트하는 것이 모델 관리에 더 유용합니다.