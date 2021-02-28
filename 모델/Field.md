# Model Field

```
기술적으로 필드 클래스들은 django.db.models.fields에 정의되어있지만, 사용의 편의성을 위해 django.db.models에 임포트되어있다. 사용 시에는 from django.db import models / models.<FOO>Field로 사용할 것을 권장한다.
```

### Field Option

#### null : Field.null

- True라면 빈 값에 대해 **NULL** 값을 데이터베이스에 저장한다. 기본 값은 False다.
- **CharField**나 **TextField**와 같이 문자열 기반의 필드에는 사용하지 않을 것을 권장한다. 문자열 기반의 필드에서 **null=True**는 두 가지 가능성을 가진다. 첫번째로는 문자열 자체가 비어있다는 뜻일 수도 있고(**NOT NULL**), 두번째로는 값 자체가 없는 경우일 수도 있다.(**NULL**) 예외적인 경우로 **CharField**가 **unique=True**와 **blank=True**인 경우에는 **null=True**를 사용할 수 있다. 이는 유일성 때문에 비어있는 값을 가지는 다수의 객체가 존재하지 않기 때문이다.

#### blank : Field.blank

- True라면 필드는 빈 값을 허용한다. 기본 값은 False다.
- 앞에서 언급한 **null**과 다르다는 점을 명심하자. **null**은 데이터베이스 관점에서, **blank**는 검증 관점에서의 의미다. 즉, **blank=True**는 데이터베이스에 비어있는 값을 넣는게 아니라 검증 과정에서 비어있는 값을 허용한다는 의미다.

#### choices : Field.choices

- 두 개의 아이템으로 이루어진 순열로 첫번째 값은 데이터베이스에 저장되는 값, 두번째 값은 표기되는 값이다. 선택지가 주어지면 모델 검증이 이루어지고 기본 폼 위젯으로 선택 상자로 생성된다.

```python
from django.db import models

class Student(models.Model):
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    GRADUATE = 'GR'
    YEAR_IN_SCHOOL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (GRADUATE, 'Graduate'),
    ]
    year_in_school = models.CharField(
        max_length=2,
        choices=YEAR_IN_SCHOOL_CHOICES,
        default=FRESHMAN,
    )

    def is_upperclass(self):
        return self.year_in_school in {self.JUNIOR, self.SENIOR}
```

`get_FOO_display()` 메서드를 통해 사람이 읽을 수 있는 형태의 값을 반환할 수 있다. **choices**에 들어갈 값은 리스트와 튜플에 상관없이 순열이면 가능하다.

**Enumeration types**

```python
from django.utils.translation import gettext_lazy as _

class Student(models.Model):

    class YearInSchool(models.TextChoices):
        FRESHMAN = 'FR', _('Freshman')
        SOPHOMORE = 'SO', _('Sophomore')
        JUNIOR = 'JR', _('Junior')
        SENIOR = 'SR', _('Senior')
        GRADUATE = 'GR', _('Graduate')

    year_in_school = models.CharField(
        max_length=2,
        choices=YearInSchool.choices,
        default=YearInSchool.FRESHMAN,
    )

    def is_upperclass(self):
        return self.year_in_school in {
            self.YearInSchool.JUNIOR,
            self.YearInSchool.SENIOR,
        }
```

파이썬에서 제공하는 **enum**과 유사하지만 몇가지 수정되었다.

- Enum의 멤버변수는 명확한 데이터 타입으로 이루어진 튜플인자로 구성된다. 장고는 **label**이라는 사람이 읽을 수 있는 문자열을 추가할 수 있는 기능을 지원한다. 대부분의 경우에는 **(value, label)** 형태의 튜플로 사용된다.
- **.label** 프로퍼티가 변수에 더해져, 사람이 읽을 수 있는 값을 반환한다.
- Enumeration 클래스에 몇가지 커스텀 프로퍼티가 추가되었다. - **.choices**, **.labels**, **values**, **.names** - 이는 Enumeration 클래스에 각 부분을 리스트로 접근하기 쉽게 만들기 위해서다.
- **enum.unique()**는 값의 중복을 제한한다. 

**YearInSchool.SENIOR.YearInSchool['SENIOR']**나 **YearInSchool('SR')**로 enum 멤버에 접근하는 것은 **.name**이나 **.value** 프로퍼티로 멤버에 접근하는 것과 같은 방식으로 작동한다.

만약 사람이 읽을 수 있는 값이 필요가 없다면, 멤버의 이름으로 추론하게 된다.

```python
class Vehicle(models.TextChoices):
    CAR = 'C'
    TRUCK = 'T'
    JET_SKI = 'J'
    
Vehicle.JET_SKI.label
# 'Jet Ski'
```

enum의 값으로 숫자를 자주 사용하기 때문에, 장고는 **IntegerChoices** 클래스를 지원한다.

```python
class Card(models.Model):

    class Suit(models.IntegerChoices):
        DIAMOND = 1
        SPADE = 2
        HEART = 3
        CLUB = 4

    suit = models.IntegerField(choices=Suit.choices)
```

Enum 함수형 API를 활용하여 레이블을 자동으로 생성하게 할 수 있다.

```python
MedalType = models.TextChoices('MedalType', 'GOLD SILVER BRONZE')
MedalType.choices # [('GOLD', 'Gold'), ('SILVER', 'Silver'), ('BRONZE', 'Bronze')]
place = models.IntegerChoices('Place', 'FIRST SECOND THiRD')
place # [(1, 'First'), (2, 'Second'), (3, 'Third')]
```

