# Form

장고의 폼 동작은 Form 클래스로 폼을 정의하고 정의된 폼을 뷰에서 사용하며, 최종적으로 템플릿 엔진에 의해 HTML 텍스트로 렌더링되는 절차를 거쳐 사용자에게 보여집니다.

장고에서 폼은 기본적으로 Form 클래스를 상속받아 정의합니다. 그 외에도 다음과 같은 폼 종류를 구분하고 만드는 방법을 알아야 합니다.

- **일반 폼** : Form 클래스를 상속받아 정의합니다.
- **모델 폼** : ModelForm 클래스를 상속받아 정의합니다. 폼 필드의 구성을 데이터베이스 모델 정의 기반으로 폼을 정의하는 경우에 사용합니다. modelform_factory() 함수를 사용해 모델 폼을 정의할 수도 있습니다.
- **폼셋** : 일반 폼을 여러 개 묶어서 한 번에 보여주는 폼입니다. formset_factory() 함수를 사용해 폼셋을 정의합니다.
- **모델 폼셋** : 데이터베이스 모델에 기초해서 만든 모델 폼을 여러 개 묶은 폼셋입니다. modelformset_factory() 함수를 사용해 모델 폼셋을 정의합니다.
- **인라인 폼셋** : 두 모델 간의 관계가 1:N인 경우, N 모델에 기초해서 만든 모델 폼을 여러 개 묶은 폼셋입니다. inlineformset_factory() 함수를 사용해 인라인 폼셋을 정의합니다.



### 장고 Form 클래스 이해

장고의 폼 기능을 이해하기 위해서는 폼에서 사용하는 바운드/언바운드, 유효성 검사 등의 용어와 HTML 텍스트로 렌더링하는 과정을 알아야 합니다.

```python
# forms.py
from django import forms

class PostSearchForm(forms.Form):
    search_word = forms.charField(label='Search Word')
```

```python
# views.py
from blog.models import Post
from blog.forms import PostSearchForm

from django.db.models import Q
from django.shortcuts import render
from django.views.generic import FormView

class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/post_search.html'
    
    def form_valid(self, form):
        searchWord = form.cleaned_data['search_word']
        post_list = Post.objects.filter(Q(title__icontains=searchWord) | Q(description__icontains=searchWord) | Q(content__icontains=searchWord)).distinct()
        
        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['object_list'] = post_list
        
        return render(self,request, self.template_name, context)
```



### 16.2 일반 폼 정의

```python
# models.py
from django.db import models

class Album(models.Model):
    name = models.CharField('NAME', max_length=30)
    description = models.CharField('One Line Discription', max_length=100, blank=True)

class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    title = models.CharField('TITLE', max_length=30)
    description = models.TextField('Photo Description', blank=True)
    image = ThumbnailImageField('IMAGE', upload_to='photo/%Y/%m')
    upload_dt = models.DateTimeField('UPLOAD DATE', auto_now_add=True)
```

```python
# forms.py
from .models import Album, Photo

from django import forms

class PhotoForm(forms.Form):
    album = fomrs.ModelChoiceField(queryset=Album.objects.all())
    title = forms.CharField(label='TITLE', max_length=30)
    description = forms.CharField(label='Photo Description', widget=forms.Textarea, required=False)
    image = ImageField(label='IMAGE')
    upload_dt = forms.DateTimeField(label='UPLOAD DATE')
```

일반 폼을 작성하기 위해서는 직접 폼 필드를 지정해야 하므로, 모델의 필드와 폼의 필드 간 매핑 룰을 알아야 합니다.

- 모델의 ForeignKey 필드는 폼의 ModelChoiceField 필드로 매핑됩니다. 선택 항목들은 queryset 속성으로 지정합니다.
- 모델의 CharField 필드는 폼의 CharField 필드로 매핑됩니다. 모델의 verbose_name 속성은 폼의 label 속성으로 매핑됩니다. max_length 속성도 그대로 매핑됩니다.
- 모델의 TextField 필드는 폼의 CharField 필드로 매핑되면서 widget 속성을 forms.Textarea로 지정합니다. 또한 모델 정의에서 `blank=True`면 폼 필드는 `required=False`가 됩니다.
- 모델의 ImageField 필드는 폼의 ImageField 필드로 매핑됩니다.
- 모델의 upload_dt 필드는 자동으로 채워지는 속성(auto_now_add)이므로, 폼에는 정의하지 않아도 됩니다.



### 모델 폼 정의

모든 폼이 모델과 관련되는 것은 아닙니다. 단순하게 이름을 입력하는 폼이나 모델과 무관한 폼이 있을 수도 있습니다. 이런 경우는 모델 폼을 만듭니다. 모델 정의를 기초해서 만드는 폼을 모델 폼이라 하고, 모델 폼을 정의할 때는 폼 필드를 정의하지 않아도 장고가 알아서 정의해줍니다. 이런 모델 폼을 만드는 방법을 세 가지로 나누어 설명하겠습니다. 방법은 다르지만 모델을 기초로 해서 폼을 만든다는 원리는 동일합니다.



**ModelForm 클래스 방식**

장고에서 기본으로 제공하는 ModelForm 클래스는 모델에 정의한 필드를 참조해서 모델 폼을 만드는 역할을 합니다. 개발자는 ModelForm 클래스를 상속받아 모델 폼을 정의하면 되므로 작업이 매우 간단해집니다.

```python
from django import forms

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'description']
        # fields = '__all__'
        # exclude = ['description']
```

모델 폼을 만들 때는 위와 같이 기초가 되는 모델과 폼에 표시될 필드를 Meta 클래스에 정의하면 됩니다. 다만, 다음처럼 약간 변형된 방법으로도 정의할 수 있습니다.

- fields 속성에 '\_\_all\_\_'이라고 하면 모델에 정의된 모든 필드를 폼에 포함합니다.
- fields 속성 대신 exclude 속성으로 필드를 지정하면 지정한 필드만 제외하고 모든 필드를 폼에 포함합니다.



**modelform_factory 함수 방식**

모델 폼을 만드는 또 다른 방법은 modelform_factory 함수를 사용하는 것입니다. 앞에서 정의한 PhotoForm과 동일한 모델 폼을 함수를 사용해 정의하면 다음과 같습니다.

```python
# forms.py
from django.forms.models import modelform_factory
from photo.models import Photo

photoForm = modelform_factory(Photo, fields='__all__')

'''
modelform_factory(model, form=ModelForm, fields=None, exclude=None, formfield_callback=None, widgets=None, localized_fields=None, labels=None, help_texts=None, error_messages=None, field_classes=None)
'''
```

이 함수는 model을 베이스로 ModelForm 클래스를 만들어 리턴합니다. form 인자가 주어지면 그 폼으로 시작해 모델 폼을 만듭니다. 그리고 모델 폼의 Meta 클래스로 지정하는 항목인 fields 또는 exclude 항목 중 하나를 반드시 지정해서 모델 폼에 포함될 필드를 명시적으로 표시해야 합니다.

- `fields` : 리턴하는 ModelForm에 포함될 필드를 지정합니다.
- `exclude` : 리턴하는 ModelForm에 제외될 필드를 지정합니다. fields에 지정된 필드라 해도 exclude로 지정되면 제외됩니다.
- `formfield_callback` : 모델의 필드를 받아서 폼 필드를 리턴하는 콜백 함수를 지정합니다.
- `widgets` : 모델 필드와 위젯을 매핑한 사전입니다.
- `localized_fields` : 로컬 지역값이 필요한 필드를 리스트로 지정합니다.
- `labels` : 모델 필드와 레이블을 매핑한 사전입니다.
- `help_texts` : 모델 필드와 설명 문구를 매핑한 사전입니다.
- `error_messages` : 모델 필드와 에러 메시지를 매핑한 사전입니다.
- `field_classes` : 모델 필드와 폼의 필드 클래스를 매핑한 사전입니다.



**제네릭 뷰에서 폼 정의**

제네릭 뷰 중 CreateView와 UpdateView 뷰는 테이블의 레코드를 생성하거나 변경하는 역할을 합니다. 이 뷰를 사용하려면 뷰와 관련된 모델이 있어야 하고 레코드에 담을 데이터를 입력받을 폼이 필요합니다. 모델과 폼의 특징을 동시에 갖는다는 점에서 CreateView와 UpdateView 뷰는 ModelForm의 기능을 내부에 포함하고 있는 제네릭 뷰입니다.

```python
class PhotoCreateView(CreateView):
    model = Photo
    fields = '__all__'
    
class PhotoUpdateView(UpdateView):
    model = Photo
    fields = '__all__'
```

ModelForm에서 사용하는 Meta 클래스를 사용하지 않고, 간단하게 model과 fields 속성을 정의해주면 됩니다. 명시적으로 모델 폼을 정의하지 않아도 제네릭 뷰 내부적으로 적절한 모델 폼을 만들고 관련 뷰 처리를 합니다.



### 폼셋 정의

폼셋이란 폼의 집합입니다. 일반 폼을 여러 개 묶어서 하나의 폼으로 취급하기 위한 것입니다. 폼셋을 정의할 때는 BaseFormSet 클래스를 상속받아 작성할 수도 있지만, 보통은 formset_factory() 함수를 사용합니다.



**formset_factory 함수**

```python
from django.forms.formsets import formset_factory
from blog.forms import PostSearchForm

PostSearchFormSet = formset_factory(PostSearchForm)
```

폼셋을 만들려면 formset_factory() 함수를 잘 사용해야 합니다. 이 함수는 주어지 form 클래스를 베이스로 FormSet 클래스를 만들어 리턴합니다.

```python
formset_factory(form, formset=BaseFormSet, extra=1, can_order=False, can_delete=False, max_num=None, validate_max=False, min_num=None, validate_min=False)
```

- `form` : 폼셋을 만들 때 베이스가 되는 폼을 지정합니다.
- `formset` : 폼셋을 만들 때 상속받기 위한 부모 클래스를 지정합니다. 보통은 BaseFormSet 클래스를 변경 없이 사용하는데, 변경이 필요하면 BaseFormSet 클래스를 오버라이딩해 기능을 변경한 후 사용할 수 있습니다.
- `extra` : 폼셋을 보여줄 때 빈 폼을 몇 개 포함할지 지정합니다. 디폴트는 한 개입니다.
- `can_order` : 폼셋에 포함된 폼들의 순서를 변경할 수 있는지 여부를 지정합니다.
- `can_delete` : 폼셋에 포함된 폼들의 일부를 삭제할 수 있는지 여부를 지정합니다.
- `max_num` : 폼셋을 보여줄 때 포함될 폼의 최대 개수를 지정합니다. 기본값은 `None`인데, 1,000개를 의미합니다.
- `validate_max` : `True`면 폼셋에 대한 유효성 검사를 수행할 때 max_num에 대한 검사도 실시합니다. 삭제 표시가 된 폼을 제외한 폼의 개수가 max_num보다 작거나 같아야 유효성 검사를 통과합니다.
- `min_num` : 폼셋을 보여줄 때 포함될 폼의 최소 개수를 지정합니다.
- `validate_min` : `True`면 폼셋에 대한 유효성 검사를 수행할 때 min_num에 대한 검사도 실시합니다. 삭제 표시가 된 폼을 제외한 폼의 개수가 min_num보다 작거나 같아야 유효성 검사를 통과합니다.



**폼셋 실습**

폼의 initial 파라미터처럼 폼셋에서도 initial 파라미터를 사용해, 폼셋에 초기 데이터를 지정할 수 있습니다. 그리고 폼셋에는 관리폼<sup>ManagementForm</sup>이 추가로 들어 있어서 관리폼을 통해 폼의 개수 등을 관리합니다. 관리폼에서 관리하는 항목은 다음과 같습니다.

- `form-TOTAL_FORMS` : 폼의 총 개수를 지정합니다.
- `form-INITIAL_FORMS` : 폼의 초기 데이터가 들어 있는 폼의 개수를 지정합니다.
- `form-MAX_NUM_FORMS` : 폼셋의 max_num 값을 지정합니다.
- `form-MIN_NUM_FORMS` : 폼셋의 min_num 값을 지정합니다.



### 모델 폼셋 정의

모델 폼셋은 모델 폼과 폼셋의 특징을 둘 다 갖고 있는 폼입니다. 데이터베이스 모델에 기초해 모델 폼을 만들고, 그 모델 폼을 여러 개 묶은 것이 모델 폼셋입니다. 모델 폼셋을 정의할 때 사용하는 modelformset_factory() 함수도 모델 폼의 modelform_factory() 함수와 폼셋의 formset_factory() 함수를 합쳐 놓은 모습입니다. 모델 폼셋을 만들 때는 BaseModelFormSet 클래스를 상속받아 작성할 수도 있지만, 보통은 modelformset_factory() 함수를 사용합니다.

```python
from django.forms import modelformset_factory
from photo.models import Photo

PhotoFormSet = modelformset_factory(Photo, fields='__all__')
```

```python
modelformset_factory(model, form=ModelForm, formfield_callback=None, formset=BaseModelFormSet, extra=1, can_delete=False, can_order=False, max_num=None, fields=None, exclude=None, validate_max=False, localized_fields=None, labels=None, help_texts=None, error_messages=None, min_num=None, validate_min=False, field_classes=None)
```



### 인라인 폼셋 정의

인라인이라는 단어에서 유추할 수 있듯이 이것은 메인 폼에 종속된 폼셋이란 의미입니다. 주종 관계는 테이블의 관계가 1:N 관계에서 외래 키<sup>Foreign Key</sup>로 연결된 경우로부터 비롯된 것입니다. 이런 1:N 관계의 테이블을 기초로 폼을 만드는 경우, 1 테이블에 대한 폼을 메인 폼이라고 하고 N 테이블에 대한 폼을 인라인 폼셋이라고 합니다.

인라인 폼셋을 정의할 때는 BaseInlineFormSet 클래스를 상속받아 작성할 수도 있지만, 보통은 inlineformset_factory() 함수를 사용합니다.

```python
# views.py
class AlbumPhotoCV(LoginRequiredMixin, CreateView):
    model = Album
    fields = ['name', 'description']
```

```python
# forms.py
PhotoInlineFormSet = inlineformset_factory(Album, Photo, fields=['image', 'title', 'description'], extra=2)
```

Album 테이블용 메인 폼은 CreateView에 의해 모델 폼으로 만들어진 것이고, Photo 테이블용 인라인 폼셋은 Album과 Photo 테이블 관계가 1:N이기 때문에 가능한 것입니다.

```python
inlineformset_factory(parent_model, model, form=ModelForm, formset=BaseInlineFormSet, fk_name=None, fields=None, exclude=None, extra=3, can_order=False, can_delete=True, max_num=None, formfield_callback=None, widgets=None, validate_max=False, localized_fields=None, labels=None, help_texts=None, error_messages=None, min_num=None, validate_min=False, field_classes=None)
```

fk_name 인자는 부모 모델에 대한 외래 키가 둘 이상일 때 지정합니다.



### 파일 업로드 폼

폼을 정의할 때 FileField 또는 ImageField 필드가 들어 있으면 주의가 필요합니다. 이 필드들을 통해 파일 업로드가 이뤄지기 때문입니다. 파일 업로드 폼을 다룰 때는 다음 두 가지를 유의해야 합니다.

첫 번째는 \<form> 요소의 인코딩 속성을 멀티파트로 지정해야 합니다.

```html
<form enctype="multipart/form-data" method="post" action="/form/" />
```

두 번째는 폼에 데이터를 바인딩할 때 폼 데이터뿐만 아니라 파일 데이터도 같이 바인딩해야 합니다.

```python
# 웹 요청에 들어 있는 데이터로 폼을 바인딩하는 경우
f = ContactFormWithFile(request.POST, request.FILES)
```

다음 메소드를 사용하면 멀티파트 폼인지 아닌지 확인할 수 있습니다.

```python
f = ContactFormWithFile()
f.is_multipart()
```

