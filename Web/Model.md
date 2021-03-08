# Model

### 모델 정의

테이블을 클래스로 처리하는 ORM 기법의 특징에 따라 테이블을 정의하는 클래스를 모델이라 하며, 모델은 속성과 메소드를 갖습니다. 테이블의 컬럼은 모델 클래스의 속성으로 정의하고, 테이블에는 메소드가 없지만 모델(테이블) 클래스에는 메소드를 정의할 수 있습니다.

```python
from django.db import models

class Album(models.Model): # models.Model을 상속받는 모델 클래스 정의
    name = models.CharField(max_length=50) # 속성 = 테이블 컬럼
    # ...
    
    class Meta: # Meta 내부 클래스
        ordering = ['name'] # Meta 내부 클래스 속성
        def __str__(self): # 모델 메소드 1
            return self.name
        
        def get_absolute_url(self): # 모델 메소드 2
            return reverse('photo:album_detail', args=(self.id))
```



**모델 속성**

ORM 기법의 특징에 따라 테이블의 컬럼은 모델 클래스의 속성으로 정의합니다. 장고에서는 테이블의 컬럼을 테이블의 필드 또는 모델의 필드라고 합니다. 각 필드는 용도에 따라 적절한 타입을 지정해야 하는데, 필드 타입의 역할은 다음과 같습니다.

- 테이블의 컬럼 타입을 지정합니다.
- 폼으로 렌더링되는 경우, HTML 위젯을 지정합니다.
- 필드 또는 폼에 대한 유효성 검사 시 최소 기준이 됩니다.

또한, 각 필드는 필드 타입에 따른 부가적인 옵션을 지정할 수 있습니다.



**모델 메소드**

모델 클래스에는 메소드를 정의할 수 있습니다. 여기서 주의할 점은 클래스 메소드와 객체 메소드를 구분하는 것입니다. 클래스 메소드는 테이블 레벨에서 동작하는 메소드이고, 객체 메소드는 레코드 레벨에서 동작하는 메소드입니다. 장고에서는 클래스 메소드를 사용하지 않고 객체 메소드만 사용합니다. 그리고 테이블 레벨의 동작은 클래스 메소드 대신, 별도의 Manager 클래스를 정의하고 Manager 클래스의 메소드를 통해서 테이블에 대한 CRUD 동작을 수행합니다.



**Meta 내부 클래스 속성**

Meta 내부 클래스를 정의해 모델에 대한 메타데이터를 정의할 수 있습니다. 장고에서는 모델 클래스의 필드는 아니지만 모델 클래스에 필요한 항목을 Meta 내부 클래스에 정의합니다.

- `ordering` : 모델 객체의 리스트 출력 시 정렬하기 위해 사용하는 속성(필드)명을 지정합니다. 오름차순이 기본값이고, 내림차순은 `-`를 붙입니다.
- `db_table` : 데이터베이스에 저장되는 테이블 이름을 지정합니다. 기본값으로 `AppName_ClassName`(소문자)입니다.
- `verbose_name` : 사용자가 이해하기 쉬운 모델 객체의 별칭입니다. 이 항목을 지정하지 않으면 장고는 모델 클래스명을 변형해서 기본 verbose_name으로 사용합니다.
- `verbose_name_plural` : verbose_name에 대한 복수 명칭을 지정합니다. 지정하지 않으면 기본값으로 verbose_name + 's'가 사용됩니다.



**Manager 속성**

모델 속성 중에서 예외적으로 필드에 매핑되지 않는 속성입니다. 모든 모델은 반드시 Manager 속성을 가져야 합니다. 만일 모델을 정의할 때 명시적으로 지정하지 않으면, Manager 속성의 기본값은 objects가 됩니다. 또한 Manager 속성은 모델 클래스를 통해서만 접근할 수 있고 모델 객체를 통해서는 접근할 수 없습니다.

Manager 속성은 models.Manager 타입으로 정의되므로, 장고의 Manager 클래스를 이해하는 것이 중요합니다. Manager 클래스를 통해 데이터베이스 쿼리가 이뤄지기 때문입니다.

```python
'''
Album : 모델 클래스
objects : Manager 속성명
all : Manager 클래스의 메소드 / all(), filter(), get(), count()...
'''
Album.objects.all() # QuerySet을 반환
```

모델 클래스에서 Manager 속성을 여러 개 정의할 수 있으며, 첫 번째로 정의된 Manager 속성을 기본 Manager라고 합니다.

```python
from django.db import models

class SecondAlbumManager(models.Manager):
    def get_queryset(self): # 메소드 오버라이딩
        return super().get_queryset().filter(owner_username='winters')
    
class Album(models.Manager):
    name = models.CharField(max_length=50)
    # ...
    
    objects = models.Manager() # 기본 매니저
    second_objects = SecondAlbumManager() # 추가 매니저
```



### 모델 간 관계

테이블 간에는 관계를 맺을 수 있으며, 장고는 테이블 간의 관계를 3가지로 분류해서 제공하고 있습니다. 1:N(one-to-many), N:N(many-to-many), 1:1(one-to-one) 관계입니다.

- 관계라는 것은 양방향 개념이므로 양쪽 모델에서 정의가 필요한 것이 원칙이지만, 장고에서는 한쪽 클래스에서만 관계를 정의하면 이를 바탕으로 상대편 정의는 자동으로 정의해줍니다.
- 한쪽 방향으로 관계를 생성하거나 변경하면 반대 방향으로의 관계도 그에 따라 변합니다.



**1:N(one-to-many) 관계**

테이블 간에 1:N 관계를 맺기 위해서는 모델의 필드를 정의할 때 ForeignKey 필드 타입을 사용하면 됩니다. ForeignKey 필드 타입은 필수 인자로 관계를 맺고자 하는 모델 클래스를 지정해야 합니다. 이는 N 모델에서 ForeignKey 필드를 정의하면서 필수 인자로 1 모델을 지정하는 방식입니다.

```python
from django.db import models
from django.contrib.auth.models import User

class Album(models.Model):
    # ...
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name='OWNER', blank=True, null=True)
```



**N:N(many-to-many) 관계**

테이블 간에 N:N 관계를 맺기 위해서는 모델의 필드를 정의할 때 ManyToManyField 필드 타입을 사용하면 됩니다. ManyToMany 필드 타입도 ForeignKey 필드와 마찬가지로 관계를 맺고자 하는 모델 클래스를 필수 인자로 지정합니다. ManyToManyField 필드 정의는 두 모델 중 어느 쪽이라도 가능하지만, 한쪽에만 정의해야 하며 양쪽에 정의하면 안 됩니다.

```python
from django.db import models
from django.contrib.auth.models import User

class Album(models.Model):
    # ...
    
class Publication(models.Model):
    title = models.CharField(max_length=30)
    albums = models.ManyToManyField(Album)
```



**1:1(one-to-one) 관계**

테이블 간에 1:1 관계를 맺기 위해서는 모델의 필드를 정의할 때 OneToOneField 필드 타입을 사용하면 됩니다. OneToOneField 필드 타입도 ForeignKey 필드와 마찬가지로 관계를 맺고자 하는 모델 클래스를 필수 인자로 지정합니다. 개념적으로는 OneToOneField 필드 타입은 ForeignKey 필드 타입에 `unique=True` 옵션을 준 것과 유사합니다. 다만 반대 방향의 동작은 다릅니다. ForeignKey 관계에서 반대 방향의 객체는 복수 개의 객체를 반환하지만, OneToOneField 관계에서 반대 방향의 객체는 하나의 객체만 반환하는 점이 다릅니다.

```python
from django.db import models

class Place(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    
    def __str__(self):
        return f'Place-{self.name}'
    
class Restaurant(models.Model):
    place = models.OneToOneField(Place, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    serves_pizza = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Restaurant-{self.name}'
```



### 관계 매니저(RelatedManager)

앞에서 설명한 매니저 중에서 모델 간 관계에 대한 기능 및 데이터베이스 쿼리를 담당하는 클래스를 관계 매니저<sup>Related Manager</sup>라고 합니다.



**관계 매니저 클래스를 사용하는 경우**

장고에서 모델 간 관계는 세 가지가 있는데, 그 중 1:N 및 N:N 관계에서만 관계 매니저가 사용되고, 1:1 관계에서는 관계 매니저를 사용하지 않습니다. 관계 매니저 클래스는 객체의 집합을 다루기 위한 클래스이지만 1:1 관계에서는 상대 객체가 하나뿐이기 때문입니다.

```python
# 1:N 관계
user.album_set # user → album
album.owner # album → user

# N:N 관계
album.publication_set # album → publication
publication.albums # publication → albums
```



**관계 매니저 메소드**

설명의 편의를 위해 관계 매니저 클래스에 대한 객체를 관계 객체라고 부르겠습니다. 또한, 이번 절에서 사용하는 예제는 Blog와 Entry 모델 간의 1:N 관계가 성립한다고 가정한 코드들입니다.

- `add(*objs, bulk=True)` : 인자로 주어진 모델 객체들을 관계 객체의 집합에 추가합니다.

  ```shell
  b = Blog.objects.get(id=1)
  e = Entry.objects.get(id=234)
  b.entry_set.add(e)
  ```

  ForeignKey 관계에서 관계 매니저는 자동으로 `QuerySet.update()` 메소드를 호출해 데이터베이스 업데이트를 수행합니다. 만약 `bule=False`인 경우 `e.save()` 메소드를 호출해 데이터베이스 업데이트를 수행합니다.

  반면 N:N 관계에서 add() 메소드를 사용하는 경우, update() 또는 save() 메소드를 사용하지 않고 `QuerySet.bulk_create()` 메소드를 호출해 관계를 생성합니다. bulk_create() 메소드는 한 번의 쿼리로 여러 개의 객체를 데이터베이스에 삽입합니다.

- `create(**kwargs)` : 새로운 객체를 생성해서 이를 데이터베이스에 저장하고 관계 객체 집합에 넣습니다. 새로 생성된 객체를 반환합니다.

  ```shell
  b = Blog.objects.get(id=1)
  e = b.entry_set.create(
    # ...
  )
  ```

  create() 메소드를 사용하면 `e.save()` 메소드를 호출하지 않아도 자동으로 데이터베이스에 저장됩니다. 또한, create() 메소드는 blog 인자를 사용하지 않습니다.

- `remove(*objs, bulk=True)` : 인자로 지정된 모델 객체들을 관계 객체 집합에서 삭제합니다.

  ```shell
  b = Blog.objects.get(id=1)
  e = Entry.objects.get(id=234)
  b.entry_set.remove(e)
  ```

  위 예제에서 `b.entry_set`에서 e 객체를 삭제하는 것은 `e.blog=None` 문장을 실행하는 것과 같습니다. 따라서 ForeignKey 관계에서 `null=True`인 경우만 이 메소드를 사용할 수 있습니다. 또한, 이 메소드는 1:N 관계에서 bulk 인자를 가질 수 있는데, bulk 인자에 따라 실행 방법이 달라집니다. `bulk=True`이면 `QuerySet.update()` 메소드가 사용되고, `bulk=False`이면 모델 객체마다 save() 메소드를 호출합니다. 반면 N:N 관계에서 remove() 메소드를 사용하면 bulk 인자를 사용할 수 없으며 `QuerySet.delete()` 메소드를 호출해 관계를 삭제합니다.

- `clear(bulk=True)` : 관계 객체 집합에 있는 모든 객체를 삭제합니다.

  ```shell
  b = Blog.objects.get(id=1)
  b.entry_set.clear()
  ```

  remove() 메소드처럼 clear() 메소드도 ForeignKey에 사용될 때는 `null=True`일 경우만 사용 가능하고 또한 bulk 인자에 따라 내부 실행 방법이 달라집니다.

- `set(objs, bulk=True, clear=False)` : 관계 객체 집합의 내용을 변경합니다.

  ```shell
  new_lisst = [obj1, obj2, obj3]
  e.related_set.set(new_list)
  ```

  set() 메소드는 내부적으로 add(), remove(), clear() 메소드가 적절히 조합되어 실행됩니다. 그래서 bulk 인자는 remove() 내용과 동일합니다. 만일 `clear=False`인 경우 기존 항목들을 체크하여, 지울 항목은 remove()로 추가할 항목은 add() 메소드로 실행합니다. 그리고 `clear=True`인 경우 clear() 메소드로 기존 항목을 한꺼번에 모두 지운 후 add() 메소드로 new_list 내용을 새로 한꺼번에 추가합니다.

관계 매니저 메소드들은 실행 즉시 데이터베이스에 반영되므로 save() 메소드를 호출할 필요가 없습니다.