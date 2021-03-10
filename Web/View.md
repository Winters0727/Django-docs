# View

뷰는 웹 요청을 받아서 최종 응답 데이터를 웹 클라이언트로 반환하는 함수(정확히는 호출 가능한 객체, callable)입니다. 웹 요청을 분석하고 데이터베이스 처리 등 필요한 로직을 수행하며 템플릿을 통해 화면에 표시할 데이터를 만들어서 최종 데이터를 웹 클라이언트에게 응답해줍니다.

장고에서는 뷰를 함수로 작성할 수 있고 클래스로도 작성할 수 있습니다. 함수형 뷰보다는 클래스형 뷰가 장점이 많기 때문에 클래스형 뷰를 많이 사용하는 추세입니다. 클래스형 뷰를 사용하면 상속과 믹스인 기능을 사용해서 코드를 재사용할 수 있고, 뷰를 체계적으로 구성할 수 있어 읽기도 쉬워집니다. 또한, 장고는 잘 준비된 클래스형 제네릭 뷰를 제공하고 있습니다.

이번 장에서는 클래스 형 뷰의 핵심 원리들을 설명합니다. 상속의 중요 기능인 오버라이딩, 클래스형 뷰의 내부 처리 과정을 이해할 수 있는 Method Flowchart, 다중 상속에 필요한 MRO 등을 설명합니다. 추가로 뷰 작성 시 자주 사용하는 페이징 처리와 단축 함수도 살펴봅니다.



### 제네릭 뷰 선택

클래스형 뷰를 작성하기 위해서는 클래스형 제네릭 뷰를 상속받아서 필요한 속성과 메소드를 오버라이딩하는 작업이 필요합니다. 먼저 개발하고자 하는 로직에 가장 알맞은 제네릭 뷰가 무엇인지 선택하고 어떤 속성과 메소드를 오버라이딩할지 판단해야 합니다.



**제네릭 뷰 요약**

장고는 웹 프로그램 개발 시 공통적으로 사용하는 로직을 미리 개발해놓고 기본 클래스로 제공하고 있는데, 이들을 제네릭 뷰라고 합니다. 개발자는 자신의 로직에 맞는 제네릭 뷰를 잘 선택해서 사용하면 그만입니다. 그래서 적절한 제네릭 뷰를 선택할 수 있도록 제네릭 뷰의 종류와 역할을 이해하는 것이 클래스형 뷰를 사용하기 위한 첫걸음입니다.

|  **제네릭 뷰 분류**  | **제네릭 뷰 이름** |                   **뷰의 기능 또는 역할**                    |
| :------------------: | :----------------: | :----------------------------------------------------------: |
|      Base View       |        View        | 가장 기본이 되는 최상위 제네릭 뷰<br />다른 모든 제네릭 뷰는 View의 하위 클래스 |
|                      |    TemplateView    |            템플릿이 주어지면 해당 템플릿을 렌더링            |
|                      |    RedirectView    |             URL이 주어지면 해당 URL로 리다이렉트             |
| Generic Display View |      ListView      |          조건에 맞는 여러 개의 객체 리스트를 보여줌          |
|                      |     DetailView     |            객체 하나에 대한 상세한 정보를 보여줌             |
|  Generic Edit View   |      FormView      |                폼이 주어지면 해당 폼을 보여줌                |
|                      |     CreateView     |      폼을 보여주고 폼의 내용으로 DB 레코드를 신규 생성       |
|                      |     UpdateView     |      폼을 보여주고 폼의 내용으로 기존 DB 레코드를 수정       |
|                      |     DeleteView     |        삭제 컨펌 폼을 보여주고 기존 DB 레코드를 삭제         |
|  Generic Date View   |  ArchiveIndexView  | 조건에 맞는 여러 개의 객체 및 그 객체들에 대한 날짜 정보를 보여줌 |
|                      |  YearArchiveView   |      연도가 주어지면 그 연도에 해당하는 객체들을 보여줌      |
|                      |  MonthArchiveView  |       연, 월이 주어지면 그에 해당하는 객체들을 보여줌        |
|                      |  WeekArchiveView   |  연도와 주차(week)가 주어지면 그에 해당하는 객체들을 보여줌  |
|                      |   DayArchiveView   |   연, 월, 일이 주어지면 그 날짜에 해당하는 객체들을 보여줌   |
|                      |  TodayArchiveView  |             오늘 날짜에 해당하는 객체들을 보여줌             |
|                      |   DateDetailView   | 연, 월, 일, 기본키(또는 슬러그)가 주어지면 그에 해당하는 특정 객체 하나에 대한 상세한 정보를 보여줌 |



**View**

모든 클래스형 뷰의 기본이 되는 최상위 뷰입니다. 따라서 모든 클래스형 뷰는 이 View 클래스를 상속받습니다. 일반적으로 이 뷰를 상속받아 사용하는 경우는 많지 않지만, 원하는 로직에 맞는 제네릭 뷰가 없다면 이 뷰를 상속받은 커스텀 클래스형 뷰를 작성할 수 있습니다.

```python
class TestView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, world!')
```



**TemplateView**

TemplateView는 단순하게 화면에 보여줄 템플릿 파일을 처리하는 정도의 간단한 뷰입니다. 아주 간단하게는 템플릿 파일만 지정해주면 됩니다.

```python
class HomeView(TemplateView):
    template_name = 'main.html'
```



**RedirectView**

RedirectView는 주어진 URL로 리다이렉트시켜주는 제네릭 뷰입니다. 그래서 URL 속성이 필수입니다. URL 대신 URL 패턴명이 주어져도 URL을 알아낼 수 있습니다. 만일 URL을 알 수 없다면, RedirectView는 HttpResponseGone(410) 에러 응답을 발생시킵니다. 복잡한 로직 없이 리다이렉트만을 원할 때 사용하는 뷰입니다.

```python
class TestRedirectView(RedirectView):
    url = '/blog/post'
    # 다음처럼 URL 대신에 패턴명을 지정해도 됩니다.
    # pattern_name = 'blog:post_list'
```



**DetailView**

DetailView는 특정 객체 하나에 대한 정보를 보여주는 뷰입니다. 자주 사용되는 예는 테이블에서 기본 키(PK)로 지정된 레코드 하나에 대한 정보들을 보여주는 것입니다.

예제로 PostDetailView 뷰를 작성해보겠습니다. Post 테이블에서 특정 레코드 하나를 읽은 후, 그 레코드를 object 컨텍스트 변수에 담아서 템플릿에 넘겨줍니다. 템플릿 파일에서는 {{ object }} 변수를 사용해 레코드 정보들을 출력합니다.

```python
class PostDetailView(DetailView):
    model = Post
```

또 한가지 중요한 점은 위 코드에서 Post 테이블만 지정했는데 어떻게 특정 레코드를 읽어올 수 있는가 하는 점입니다. 해답은 URLconf에 있습니다.

```python
# 예시 : /blog/post/django-example/
re_path(r'^post/?P<slug>[-\w]+/$', views.PostDetailView.as_view(), name='post_detail')
```

위의 URL 정의에 따르면 `/blog/post/django-example/`이라는 URL이 들어오면 PostDetailView.as_view()를 호출할 때 인자로 사전 데이터 `{'slug' : 'django-example'}`을 넘겨줍니다. 이 slug 인자로 Post 테이블을 검색할 때 slug 컬럼이 `'django-exmaple'`인 레코드를 찾게 됩니다. 즉, DetailView 제네릭 뷰를 사용할 경우 테이블은 뷰 클래스에서 지정하고 레코드 검색용 키는 URLconf에서 지정하는 것입니다.



**ListView**

ListView는 여러 객체의 리스트를 보여주는 뷰입니다. 일반적으로 테이블의 모든 레코드에 대한 목록을 보여주는데 사용합니다.

예제로 PostListView를 작성해보겠습니다. Post 테이블에서 모든 레코드를 읽은 후, 그 레코드들을 object_list 컨텍스트 변수에 담아서 템플릿에 넘겨줍니다. 템플릿 파일에서는 {{ object_list }} 변수를 사용해 레코드 리스트를 출력합니다.

```python
class PostListView(ListView):
    model = Post
```



**FormView**

폼을 보여주기 위한 제네릭 뷰입니다. 그래서 폼을 지정해주는 form_class와 이 폼을 렌더링하는데 필요한 template_name 속성이 주요 속성들입니다. 추가적으로 폼 처리가 성공한 후에 리다이렉트 목적지 URL을 지정하는 success_url 속성도 필요합니다.

폼을 처리하는 작업은 꽤 복잡한 편입니다. get() 메소드와 post() 메소드를 구분해서 서로 처리하는 내용이 다르고 폼을 보여준 다음, 사용자가 폼에 입력한 데이터가 유용한지도 검사해야 하며 처리가 완료된 후 적당한 페이지로 이동도 해야합니다. 이런 복잡한 과정은 FormView가 알아서 처리해주고, 개발자는 필요한 속성을 입력해주거나 메소드를 오버라이딩해주면 됩니다.

```python
class SearchFormView(FormView):
    form_class = PostSearchForm
    template_name = 'blog/post_search.html'
    
    def form_valid(self, form):
        searchWord = form.cleaned_data['search_word']
        post_list = Post.objects.filter(Q(title__icontains=searchWord) | Q(description__icontains=searchWord) | Q(contenxt__icontains=searchWord)).distinct()
        
        context = {}
        context['form'] = form
        context['search_term'] = searchWord
        context['object_list'] = post_list
        
        return render(self.request, self.template_name, context) # No Redirection
```



**CreateView**

CreateView는 새로운 레코드를 생성해서 테이블에 저장해주는 뷰입니다. 새로운 레코드를 생성하기 위해서는 레코드 정보를 입력받을 수 있는 폼이 필요합니다. 그래서 CreateView는 FormView의 기능을 포함하고 있습니다.

CreateView는 FormView의 기능 외에 모델 정의로부터 폼을 자동으로 만들어주는 기능과 데이터베이스에 레코드를 저장하는 기능이 더 추가된 것으로 이해하면 됩니다.

```python
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'slug', 'description', 'content', 'tags']
    initial = {'slug': 'auto-filling-do-not-input'}
    success_url = reverse_lazy('blog:index')
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
```



**UpdateView**

UpdateView는 테이블에 이미 있는 레코드를 수정하는 제네릭 뷰입니다. CreateView의 기능과 매우 유사하고, 레코드를 신규로 생성하는 게 아니라 기존의 레코드를 수정한다는 점만 유의해서 이해하면 됩니다.

CreateView와 마찬가지로 UpdateView로 FormView의 기능을 포함하고 있고 작업 대상이 테이블로부터 폼을 만들어주며, 최종적으로 테이블에 있는 기존 레코드를 수정합니다.

```python
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    fields = ['title', 'slug', 'description', 'content', 'tag']
    success_url = reverse_lazy('blog:index')
```

UpdateView에서 유의할 점은 DetailView와 동일하게 수정할 레코드를 URLconf에서 지정한다는 것입니다.

```python
# 예제 : /blog/99/update/
path('<int:pk>/update/', views.PostUpdateView.as_view(), name='update')
```



**DeleteView**

DeleteView는 기존 객체를 삭제하기 위한 제네릭 뷰입니다. 삭제 처리는 내부에서 이뤄지고 코드에 나타나는 것은 삭제 확인 화면입니다. UpdateView와 처리 과정이 비슷하지만 폼 모습이 다르다는 점만 유의하면 이해하기 쉽습니다.

CreateView와 UpdateView는 모두 데이터를 입력받는 항목을 가지는 폼이 필요하며, 모델 정의를 바탕으로 폼을 만들지만 DeleteView는 삭제 확인용 폼만 필요하므로 입력 항목이 없으며 모델 정의를 참조하지도 않습니다.

```python
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('blog:index')
```

UpdateView와 동일하게 DeleteView도 수정할 레코드를 URLconf에서 지정합니다.

```python
# 예제 : /blog/99/delete/
path('<int:pk>/delete/', views.PostDeleteView.as_view(), name='delete')
```



**ArchiveIndexView**

ArchiveIndexView 제네릭 뷰는 여러 개의 객체를 대상으로 하여 날짜를 기준으로 리스팅해주는 뷰입니다. 날짜 기반 제네릭 뷰의 최상위 뷰이며, 대상이 되는 모든 객체를 날짜 기준 내림차순으로 보여줍니다. 날짜와 관련된 필드들 중에서 어느 필드를 기준으로 정렬할지를 결정하는 date_field 속성이 가장 중요합니다.

```python
class PostAV(ArchiveIndexView):
    model = Post
    date_field = 'modify_dt'
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 연도를 담고 있습니다.



**YearArchiveView**

YearArchiveView 제네릭 뷰는 연도가 주어지면 여러 개의 객체를 대상으로 가능한 월<sup>month</sup>를 알려주는 제네릭 뷰입니다. 기본 동작은 객체들을 출력하는 것이 아니라 객체의 날짜 필드를 조사해 월을 추출한다는 점을 유의하기 바랍니다. 만일 주어진 연도에 해당하는 객체들을 알고 싶다면 make_object_list 속성을 `True`로 지정하면 됩니다. model 속성이나 date_field 속성을 지정하는 것은 ArchiveIndexView와 동일합니다.

```python
class PostYAV(YearArchiveView):
    model = Post
    date_field = 'modify_dt'
    make_object_list = True
```

YearArchiveView 제네릭 뷰도 인자를 URLconf에서 추출합니다.

```python
# 예제 : /blog/archive/2019/
path('archive/<int:year>/', views.PostYAV.as_view(), name='post_year_archive')
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 인자로 주어진 연도에 해당하는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 월을 담고 있습니다. 물론 make_object_list가 `False`면 object_list는 `None`이 됩니다.



**MonthArchiveView**

MonthArchiveView 제네릭 뷰는 주어진 연/월에 해당하는 객체를 보여주는 제네릭 뷰입니다. 연/월 인자는 URLconf에 지정합니다. model 속성이나 date_field 속성을 지정하는 것은 ArchiveIndexView 뷰와 동일하고, make_object_list 속성은 없습니다.

```python
class PostMAV(MonthArchiveView):
    model = Post
    date_field = 'modify_dt'
```

```python
# 예제 : /blog/archive/2019/nov/
path('archive/<int:year>/<str:month>/', views.PostMAV.as_view(), name='post_month_archive')
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 인자로 주어진 연/월에 해당하는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 일을 담고 있습니다.



**WeekArchiveView**

WeekArchiveView 제네릭 뷰는 연도와 주<sup>week</sup>가 주어지면 그에 해당하는 객체를 보여주는 제네릭 뷰입니다. 연/주 인자는 URLconf에서 지정합니다. 주 인자는 1년을 표현하므로 1부터 53까지의 값을 가집니다. model 속성이나 date_field 속성을 지정하는 것은 ArchiveIndexView 뷰와 동일합니다.

```python
class PostWAV(WeekArchiveView):
    model = Post
    date_field = 'modify_dt'
```

```python
# 예제 : /blog/archive/2019/week/23/
path('archive/<int:year>/week/<int:week>/', views.PostWAV.as_view(), name='post_week_archive')
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 주어진 연/주에 해당하는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 연도를 담고 있습니다.



**DayArchiveView**

DayArchiveView 제네릭 뷰는 연/월/일이 주어지면 그에 해당하는 객체를 보여주는 제네릭 뷰입니다. 역시 연/월/일 인자는 URLconf에서 지정합니다. model 속성이나 date_field 속성을 지정하는 것은 ArchiveIndexView 뷰와 동일합니다.

```python
class PostDAV(DayArchiveView):
    model = Post
    date_field = 'modify_dt'
```

```python
# 예제 : /blog/archive/2019/nov/10/
path('archive/<int:year>/<str:month>/<int:day>/', views.PostDAV.as_view(), name='post_day_archive')
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 인자로 주어진 연/월/일에 해당하는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 연도를 담고 있습니다.



**TodayArchiveView**

TodayArchiveView 제네릭 뷰는 오늘 날짜에 해당하는 객체를 보여주는 제네릭 뷰입니다. 오늘 날짜를 사용하므로 연/월/일 인자가 필요 없다는 점을 제외하면 DayArchiveView와 동일한 제네릭 뷰입니다.

```python
class PostTAV(TodayArchiveView):
    model = Post
    date_field = 'modify_dt'
```

```python
# 예제 : /blog/archive/today/
path('archive/today/', views.PostTAV.as_view(), name='post_today_archive')
```

템플릿에 넘겨주는 컨텍스트 변수 중에서 object_list는 오늘 날짜에 해당하는 객체들의 리스트를 담고 있고 date_list는 대상 객체들의 연도를 담고 있습니다.



**DateDetailView**

DateDetailView 제네릭 뷰는 날짜 기준으로 특정 객체를 찾아서 그 객체의 상세 정보를 보여주는 뷰입니다. 특정 객체의 상세 정보를 보여준다는 점에서 DetailView와 동일하지만, 객체를 찾는 데 사용하는 인자로 연/월/일 정보를 추가적으로 사용한다는 점이 다릅니다. 물론 기본 키 또는 slug 인자도 사용하므로 /연/월/일/pk/ 등 4개의 인자가 필요하며, 이들은 URLconf에서 추출합니다. model 속성이나 date_field 속성을 지정하는 것은 ArchiveIndexView와 동일합니다.

```python
class PostDateDetailView(DateDetailView):
    model = Post
    date_field = 'modify_dt'
```

```python
# 예제 : /blog/archive/2019/nov/10/99/
path('archive/<int:year>/<str:month>/<int:day>/<int:pk>/', views.PostDateDetailView.as_view(), name='post_archive_detail')
```

날짜 기반의 다른 제네릭 뷰들은 복수의 객체들을 출력하는 데 비해 DateDetailView 뷰는 특정 객체 하나만 다룹니다. 따라서 템플릿에 넘겨주는 컨텍스트 변수는 object_list가 아니라 object 변수를 사용하고 date_list 변수도 사용하지 않습니다. object 변수에는 연/월/일/pk 인자로 찾은 객체 하나가 들어 있습니다.



### 제네릭 뷰 오버라이딩

적절한 제네릭 뷰를 선택했다면 해당 제네릭 뷰에서 제공하는 속성과 메소드를 검사해서 무엇을 오버라이딩할지 결정해야 합니다. 각 제네릭 뷰에서 제공하는 속성과 메소드가 많으므로 자주 사용하는 속성과 메소드부터 익혀나가면 됩니다.



**속성 오버라이딩**

제네릭 뷰에서 제공하는 속성들을 살펴보고 그대로 사용할지, 변경해서 사용할지 결정해야 합니다.

- `model` : 기본 뷰(View, TemplateView, RedirectView) 3개와 FormView를 제외하고는 모든 제네릭 뷰에서 사용하는 속성입니다. 작업 대상 데이터가 들어 있는 모델을 지정합니다. model 대신 queryset 속성으로 지정할 수도 있습니다.
  - `model = Bookmark`
  - `queryset = Bookmark.objects.all()`
- `queryset` : 기본 뷰(View, TemplateView, RedirectView) 3개와 FormView를 제외하고는 모든 제네릭 뷰에서 사용하는 속성입니다. 작업 대상이 되는 QuerySet 객체를 지정합니다. queryset 속성을 지정하면 model 속성은 무시됩니다.
- `template_name` : TemplateView를 포함해 모든 제네릭 뷰에서 사용하는 속성입니다. 템플릿 파일명을 문자열로 지정합니다.
- `context_object_name` : 기본 뷰(View, TemplateView, RedirectView) 3개를 제외하고는 모든 제네릭 뷰에서 사용하는 속성입니다. 템플릿 파일에서 사용할 컨텍스트 변수명을 지정합니다.
- `paginate_by` : ListView와 날짜 기반 뷰에서 사용합니다. 페이징 기능이 활성화된 경우, 페이지당 몇 개 항목을 출력할지 정수로 지정합니다.
- `date_field` : 날짜 기반 뷰에서 기준이 되는 필드를 지정합니다. 이 필드를 기준으로 년/월/일을 검사합니다. 이 필드의 타입은 DateField 또는 DateTimeField여야 합니다.
- `make_object_list` : YearArchiveView 사용 시 해당 년에 맞는 객체들의 리스트를 생성할지 여부를 지정합니다. `True`면 객체들의 리스트를 만들고 그 리스트를 템플릿에서 사용할 수 있습니다. `False`면 queryset 속성에 None이 할당됩니다.
- `form_class` : FormView, CreateView, UpdateView에서 사용합니다. 폼을 만드는 데 사용할 클래스를 지정합니다.
- `initial` : FormView, CreateView, UpdateView에서 사용합니다. 폼에 사용할 초기 데이터를 사전({})으로 지정합니다.
- `fields` : CreateView, UpdateView에서 사용합니다. 폼에 사용할 필드를 지정합니다. ModelForm 클래스의 `Meta.fields` 속성과 동일한 의미입니다.
- `success_url` : FormView, CreateView, UpdateView, DeleteView에서 사용합니다. 폼에 대한 처리가 성공한 후 리다이렉트될 URL을 지정합니다.



**메소드 오버라이딩**

- `get_queryset()` : 기본 뷰(View, TemplateView, RedirectView) 3개와 FormView를 제외하고는 모든 제네릭 뷰에서 사용하는 메소드입니다.

  출력 객체를 검색하기 위한 대상 QuerySet 객체 또는 출력 대상인 객체 리스트를 반환합니다. 기본값은 queryset 속성값을 반환합니다. queryset 속성이 지정되지 않은 경우는 모델 매니저 클래스의 all() 메소드를 호출해 QuerySet 객체를 생성하고 이를 반환합니다.

- `get_context_data(**kwargs)` : TemplateView를 포함해 모든 제네릭 뷰에서 사용하는 메소드입니다. 템플릿에서 사용할 컨텍스트 데이터를 반환합니다.

- `form_valid(form)` : FormView, CreateView, UpdateView에서 사용합니다. get_success_url() 메소드가 반환하는 URL로 리다이렉트를 수행합니다.



### 제네릭 뷰의 처리 흐름

클래스 상속과 오버라이딩 기능이 가능한 제네릭 뷰는 하위 클래스에서 오버라이딩이 쉽고 여러가지 애플리케이션에 다양하게 사용될 수 있도록 설계되었습니다. 특히 제네릭 뷰의 메소드들은 단위 기능으로 잘게 나누어 메소드의 응집도를 높이고 템플릿 메소드 디자인 패턴을 적용해 개발자가 제네릭 뷰의 처리 흐름을 쉽게 예상할 수 있습니다. 템플릿 메소드 디자인 패턴은 상위 클래스에서 처리 흐름의 뼈대를 결정하고 하위 클래스에서 그 구체적인 내용을 결정하는 디자인 패턴입니다.

이번 절에서는 대표적인 제네릭 뷰인 ListView와 DetailView의 처리 흐름을 살펴보겠습니다.



**ListView**

ListView는 복수 개의 객체에 대한 목록을 보여주기 위한 뷰이며, 메인 처리 흐름은 다음과 같습니다.

- 클라이언트의 HTTP 요청 GET 메소드에 따라 get() 메인 메소드가 실행됩니다.
- 대상 테이블로부터 조건에 맞는 복수 개의 객체를 가져옵니다.
- 필요하다면 이 객체들에 추가 로직을 반영합니다.
- 최종 결과 객체 리스트를 object_list라는 컨텍스트 변수에 넣어 템플릿에 전달합니다.
- 템플릿 파일에 따라 최종 HTML 응답을 만들고 이를 클라이언트에 응답합니다.

|       **메소드명**        |                       **메소드 설명**                        |
| :-----------------------: | :----------------------------------------------------------: |
|          setup()          | 공통으로 사용할 속성들을 미리 정의하는 메소드입니다. 기본적으로 self.request, self.args, self.kwargs는 미리 정의되고 그 외에 추가할 것이 있으면 오버라이딩합니다. |
|        dispatch()         | 클라이언트 요청의 HTTP 메소드를 검사해 뷰 클래스에 정의된 적절하 처리 메소드를 호출합니다. GET 요청이면 get(), POST 요청이면 post() 메소드 등 HTTP 메소드 단어의 소문자에 해당하는 메소드를 호출합니다. |
| http_method_now_allowed() | dispatch() 메소드에 의해 호출되는 HTTP 메소드에 해당하는 메인 처리 메소드를 찾지 못한 경우, 이 메소드를 호출합니다. |
|           get()           |                   메인 처리 메소드입니다.                    |
|      get_queryset()       | 작업 대상 객체들의 리스트를 반환합니다. 리스트는 QuerySet 객체와 같은 순환 가능한(iterable) 객체여야 합니다. |
|    get_context_data()     | 템플릿에서 사용할 컨텍스트 데이터를 반환하는 메소드입니다. get_context_object_name() 메소드를 호출합니다. |
| get_context_object_name() | 템플릿에서 사용할 컨텍스트 변수명을 반환합니다. context_object_name 속성이 지정되지 않은 경우는 모델명소문자_list로 해서 컨텍스트 변수명으로 사용합니다. |
|   render_to_response()    | 최종 응답인 self.response_class 객체를 반환합니다. get_template_name() 메소드를 호출합니다. |
|   get_template_names()    | 템플릿 파일명을 담은 리스트를 반환합니다. template_name 속성이 지정된 경우는 template_name을 리스트에 담아 반환합니다. |



**DetailView**

- 클라이언트의 HTTP 요청 GET 메소드에 따라 get() 메인 메소드가 실행됩니다.
- 대상 테이블로부터 조건에 맞는 객체 하나를 가져옵니다.
- 필요하다면 이 객체에 추가 로직을 반영합니다.
- 최종 결과 객체를 object라는 컨텍스트 변수에 넣어 템플릿에 전달합니다.
- 템플릿 파일에 따라 최종 HTML 응답을 만들고 이를 클라이언트에 응답합니다.

|       **메소드명**        |                       **메소드 설명**                        |
| :-----------------------: | :----------------------------------------------------------: |
|          setup()          | 공통으로 사용할 속성들을 미리 정의하는 메소드입니다. 기본적으로 self.request, self.args, self.kwargs는 미리 정의되고 그 외에 추가할 것이 있으면 오버라이딩합니다. |
|        dispatch()         | 클라이언트 요청의 HTTP 메소드를 검사해 뷰 클래스에 정의된 적절하 처리 메소드를 호출합니다. GET 요청이면 get(), POST 요청이면 post() 메소드 등 HTTP 메소드 단어의 소문자에 해당하는 메소드를 호출합니다. |
|           get()           |                   메인 처리 메소드입니다.                    |
|       get_object()        | 작업 대상 객체 하나를 반환합니다. 이를 위해 먼저 get_queryset()을 호출해 검색 대상 객체 리스트를 얻습니다. 검색 시 pk로 먼저 검색을 시도하고 pk가 주어지지 않은 경우 slug로 검색을 수행합니다. |
|      get_queryset()       | 특정 객체를 검색하기 위한 대상 QuerySet 객체를 반환합니다. 기본값은 queryset 속성값을 반환합니다. queryset 속성이 지정되지 않은 경우는 모델 매니저 클래스의 all() 메소드를 호출해 QuerySet 객체를 생성하고 이를 반환합니다. |
|    get_context_data()     | 템플릿에서 사용할 컨텍스트 데이터를 반환하는 메소드입니다. get_context_object_name() 메소드를 호출합니다. |
| get_context_object_name() | 템플릿에서 사용할 컨텍스트 변수명을 반환합니다. context_object_name 속성이 지정되지 않은 경우는 모델명소문자_list로 해서 컨텍스트 변수명으로 사용합니다. |
|   render_to_response()    | 최종 응답인 self.response_class 객체를 반환합니다. get_template_names() 메소드를 호출합니다. |
|   get_template_names()    | 템플릿 파일명을 담은 리스트를 반환합니다. template_name 속성이 지정된 경우는 template_name을 리스트에 담아 반환합니다. |



### MRO

파이썬은 다중 상속이 가능한 언어이므로 장고의 제네릭 뷰에서도 다중 상속을 허용합니다. 다중 상속에서는 동일한 이름을 가진 메소드가 둘 이상의 부모 클래스에 존재할 경우 어느 메소드를 먼저 사용해야 할지 결정하는 알고리즘이 필요합니다. 이런 문제를 해결하기 위해 파이썬에서는 클래스마다 메소드를 찾는 순서를 정한 MRO(Method Resolution Order) 속성을 제공합니다.

장고의 제네릭 뷰를 사용하는 경우 MRO 문제로 어려움을 겪는 경우는 많지 않습니다. 제네릭 뷰 설계 시 각 클래스 간에 메소드명이 중복되지 않도록 설계되었기 때문입니다. 하지만 개발자가 직접 작성한 클래스를 상속받은 경우는 MRO에 따른 메소드 순서를 잘 따져봐야 합니다. 또한 클래스의 상속 계층도를 파악하기 위해 MRO 속성을 보는 경우도 있습니다.

ListView 클래스를 예로 들어보겠습니다. ListView 클래스의 MRO는 자신에서부터 시작해 하위 클래스에서 상위 클래스 순서로 정해집니다. 그리고 class(A,B)와 같이 다중 상속의 경우에는 A,B 순서대로 MRO가 정해집니다. 파이썬에서는 모든 클래스마다 MRO 순서를 보여주는 \_\_mro\_\_ 속성을 제공합니다.



**믹스인(Mixin) 클래스**

보통의 클래스와 달리 믹스인 클래스는 자신의 인스턴스를 만드는 용도보다는 다른 클래스에게 부가 기능을 제공하기 위한 용도로 사용되는 클래스를 의미합니다. 장고에서는 파이썬의 다중 상속 기능을 활용해 꼭 필요한 단위 기능들을 믹스인 클래스로 만들고, 제네릭 뷰에서 이런 믹스인 클래스들을 상속받는 방식으로 제네릭 뷰들을 설계했습니다.



### 제네릭 뷰의 페이징 처리

화면에 보여줄 데이터가 많은 경우에 한 페이지 분량에 맞게 적절한 크기로 나눠서 페이지 별로 보여주는 기능이 필요합니다. 이런 기능을 페이징 기능 또는 페이지네이션<sup>Pagination</sup>이라고 합니다. 여기서는 제네릭 뷰를 대상으로 페이징 기능을 설명하지만, 클래스형 뷰뿐만 아니라 함수형 뷰에서도 사용할 수 있는 기능입니다.



**페이징 기능 활성화**

ListView처럼 객체의 리스트를 처리하는 제네릭 뷰는 paginate_by 속성을 가집니다. 이런 제네릭 뷰에 paginate_by 속성이 지정되면, 장고의 페이징 기능이 활성화되고 객체 리스트는 페이지 별로 구분되어 보입니다. paginate_by(MultipleObjectMixin에 정의) 속성은 페이지당 객체의 수를 의미합니다.

페이징 기능이 활성화되면 객체 리스트는 몇 개의 페이지로 나뉘고, 페이지 번호를 지정함으로써 해당 페이지를 화면에 표시할 수 있게 됩니다. 몇 번째 페이지를 화면에 보여줄지는 웹 요청 URL에서부터 지정되고 이를 뷰에서 처리하는데, URL에 페이지를 지정하는 방법은 2가지입니다.

첫 번째는 URL 경로에 페이지 번호를 지정하며, URLconf에서 이를 추출해 뷰에 넘겨주는 방법입니다.

```python
path('objects/page<int:page>/', PaginatedView.as_view())
```

두 번째 방법은 URL의 쿼리 문자열에 페이지 번호를 지정하는 방법입니다.

```python
'objects/?page=3'
```

이 경우는 쿼리 문자열의 page 파라미터에 페이지 번호를 지정하고, 뷰가 직접 request.GET.get('page')와 같은 구문으로 페이지 번호를 추출합니다.

두 경우 모두 파라미터 이름이 page라는 데 유의하기 바랍니다. page라는 파라미터 이름은 변경할 수 있는데, 이를 변경한 경우에는 뷰에 page_kwarg 속성으로 알려줘야 합니다.

이처럼 URL에 페이지 번호가 지정되면 뷰는 페이징 처리를 하고 나서 HTML 처리에 필요한 컨텍스트 변수를 템플릿에 넘겨줍니다. 템플릿 파일에서 페이징 기능을 위해 사용되는 컨텍스트 변수는 다음과 같습니다.

- `object_list` : 화면에 보여줄 객체의 리스트. context_object_name 속성으로 지정된 컨텍스트 변수도 object_list와 동일한 값을 갖습니다.
- `is_paginated` : 출력 결과가 페이징 처리되는지 여부를 알려주는 불린 변수. 만일 페이지 크기가 지정되지 않았거나 대상 객체 리스트가 페이지로 구분되지 않는 경우는 값이 `False`가 됩니다.
- `paginator` : `django.core.paginator.Paginator` 클래스의 객체. 페이징 처리가 안되는 경우 이 값은 `None`으로 설정됩니다.
- `page_obj` : `django.core.paginator.Page` 클래스의 객체. 페이징 처리가 안 되는 경우 이 값은 `None`으로 설정됩니다.

이처럼 페이징 기능을 사용하기 위해서는 제네릭 뷰에서 paginate_by 속성을 지정하고 원하는 페이지를 URL에 지정하며, 템플릿 파일에서 컨텍스트 변수만 적절히 사용하면 됩니다.



**Paginator 클래스**

페이징 기능의 메인 클래스이며, 주요 역할은 객체의 리스트와 페이지당 항목 수를 필수 인자로 받아서 각 페이지 객체를 생성하는 것입니다.

```python
class Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)
```



**인자(Argument)**

앞의 2개는 필수 인자이고, 뒤의 2개는 선택 인자입니다.

- `object_list` : 페이징 대상이 되는 객체 리스트. 객체 리스트는 파이썬의 리스트 또는 튜플 타입이면 가능하며 장고의 QuerySet 객체도 가능합니다. 중요한 점은 count() 또는 \_\_len\_\_() 메소드를 갖고 있는 객체여야 한다는 점입니다.
- `per_page` : 페이지당 최대 항목 수
- `orphans` : 마지막 페이지에 넣을 수 있는 항목의 최소 개수. 기본 값은 0. 마지막 페이지의 항목 개수는 orphans보다 커야 합니다. 이 인자는 마지막 페이지의 항목 개수가 너무 적은 경우, 그 전 페이지에 포함되도록 하기 위해 사용합니다.
- `allow_empty_first_page` : 첫 페이지가 비어 있어도 되는지 결정하는 불린 타입 인자. 항목 개수가 0인 경우, 이 인자가 `True`면 정상 처리를 하지만 이 인자가 `False`면 EmptyPage 에러가 발생합니다.



**메소드(Method)**

- `Paginator.page(number)` : Page 객체를 반환합니다. number 인자는 1부터 시작합니다. 인자로 주어진 페이지가 존재하지 않으면 InvalidPage 예외가 발생합니다.
- `Paginator.get_page(number)` : Page 객체를 반환합니다. number 인자는 1부터 시작합니다. 인자가 숫자가 아니면 첫 페이지를 반환하고, 인자가 음수이거나 최대 페이지 숫자보다 크면 마지막 페이지를 반환합니다.



**속성(Attribute)**

- `Paginator.count` : 항목의 총 개수
- `Paginator.num_pages` : 페이지의 총 개수
- `Paginator.page_range` : 1부터 시작하는 페이지 범위



**Page 클래스**

Paginator 객체에 의해 생성된 단위 페이지를 나타내는 객체로 Page 객체를 생성하는 방법은 생성자 메소드 호출보다 Paginator.page() 메소드를 호출하는 방법을 더 많이 사용합니다.

```python
class Page(object_list, number, paginator)
```



**인자(Argument)**

- `object_list` : Paginator 클래스의 object_list 인자와 동일
- `number` : 몇 번째 페이지인지를 지정하는 페이지 인덱스
- `paginator` : 페이지를 생성해주는 Paginator 객체



**메소드(Method)**

- `Page.has_next()` : 다음 페이지가 있으면 `True`를 반환
- `Page.has_previous()` : 이전 페이지가 있으면 `True`를 반환
- `Page.has_other_page()` : 다음 또는 이전 페이지가 있으면 `True`를 반환
- `Page.next_page_number()` : 다음 페이지 번호를 반환합니다. 없으면 InvalidPage 예외가 발생합니다.
- `Page.previous_page_number()` : 이전 페이지 번호를 반환합니다. 없으면 InvalidPage 예외가 발생합니다.
- `Page.start_index()` : 해당 페이지 첫 번째 항목의 인덱스를 반환합니다. 인덱스는 1부터 카운트합니다.
- `Page.end_index()` : 해당 페이지 마지막 항목의 인덱스를 반환합니다. 인덱스는 1부터 카운트합니다.



**속성(Attribute)**

- `Page.object_list` : 현재 페이지의 객체 리스트
- `Page.number` : 현재 페이지의 번호(1부터 카운트)
- `Page.paginator` : 현재 페이지를 생성한 Paginator 객체



### 단축 함수

웹 프로그램 개발 시 자주 사용되는 기능들을 장고에서는 이미 개발해 자체 함수로 제공하고 있습니다. 이런 함수들을 단축 함수<sup>shortcut</sup>라고 하는데, 함수형 뷰와 클래스형 뷰 모두 단축 함수를 자주 사용합니다.



**render_to_response()**

```python
render_to_response(template_name, context=None, content_type=None, status=None, using=None)
```

템플릿 파일과 컨텍스트 사전을 받아 렌더링 처리한 후, HttpResponse 객체를 반환하는 함수입니다. template_name을 제외한 인자는 모두 선택 인자들입니다. 버전 2.0부터 폐지 예고된 상태이므로 이 함수 대신 render() 함수의 사용을 권장합니다.

- `template_name` : 템플릿 파일명. 복수 개가 주어지면 가장 먼저 찾게 되는 파일이 사용됩니다.
- `context` : 템플릿 컨텍스트 데이터가 담긴 파이썬 사전형 객체
- `content_type` : 최종 결과에 사용될 MIME 타입. 기본값은 `DEFAULT_CONTEXT_TYPE` 설정 항목값을 따릅니다.
- `status` : 응답에 포함될 상태 코드. 기본값은 200입니다.
- `using` : 템플릿 로딩에 사용되는 템플릿 엔진 이름



**render()**

```python
render(request, template_name, context=None, context_type=None, status=None, using=None)
```

템플릿 파일과 컨텍스트 사전을 인자로 받아 렌더링 처리한 후, HttpResponse 객체를 반환하는 함수입니다.

request 및 template_name을 제외한 인자는 모두 선택 인자들입니다.

- `request` : 클라이언트로부터 보내온 요청 객체. 내부적으로는 요청 객체에 담겨 있는 파라미터들을 사용해 RequestContext 객체를 만들고, 이 데이터들을 컨텍스트 데이터에 추가합니다.

- `template_name` : 템플릿 파일명. 복수 개가 주어지면 가장 먼저 찾게 되는 파일이 사용됩니다.
- `context` : 템플릿 컨텍스트 데이터가 담긴 파이썬 사전형 객체
- `content_type` : 최종 결과에 사용될 MIME 타입. 기본값은 `DEFAULT_CONTEXT_TYPE` 설정 항목값을 따릅니다.
- `status` : 응답에 포함될 상태 코드. 기본값은 200입니다.
- `using` : 템플릿 로딩에 사용되는 템플릿 엔진 이름

```python
# render 함수 미사용 시
from django.http import HttpResponse
from django.template import loader

def my_view(request):
    # View code...
    t = loader.get_template('myapp/index.html')
    c = {'foo' : 'bar'}
    return HttpResponse(t.render(c, request), content_type='application/xhtml+xml')

# render 함수 사용 시
from django.shortcut import render

def my_view(request):
    # View code...
    return render(request, 'myapp/index.html', {'foo' : 'bar'}, content_type='application/xhtml+xml')
```



**redirect()**

```python
redirect(to, *args, permanent=False, **kwargs)
```

to 인자로 주어진 URL로 이동하기 위한 HttpResponseRedirect 객체를 반환합니다. Permanent 인자가 `True`면 영구 리다이렉션(응답 코드 301)을 하고, `False`(기본값)면 임시 리다이렉션(응답 코드 302 또는 307) 응답을 합니다.

to 인자는 다음과 같이 3가지 종류로 주어집니다.

- 이동하기 위한 URL을 직접 지정합니다. 절대 URL과 상대 URL 모두 가능합니다. 지정한 URL로 리다이렉트됩니다.
- 모델명을 지정하면 그 모델의 get_absolute_url() 메소드에서 반환하는 URL로 리다이렉트됩니다.
- URL 패턴의 이름을 지정하면 reverse() 함수를 호출하면서 그 패턴명을 인자로 넘겨줍니다. 그리고 reverse() 함수의 결과로 반환되는 URL로 리다이렉트됩니다.



**get_object_or_404()**

```python
get_object_or_404(klass, *args, **kwargs)
```

klass 모델에 해당하는 테이블에서 args 또는 kwargs 조건에 맞는 레코드를 검색합니다. 있으면 해당 레코드를 반환하고, 없으면 Http404 예외를 발생시킵니다. 조건에 맞는 레코드가 둘 이상이면 MultipleObjectsReturned 예외를 발생시킵니다. klass는 Model 또는 Manager 클래스일 수도 있고, QuerySet 객체일 수도 있습니다.



**get_list_or_404()**

```python
get_list_or_404(klass, *args, **kwargs)
```

klass 모델에 해당하는 테이블에서 args 또는 kwargs 조건에 맞는 레코드들을 검색합니다. 있으면 해당 레코드들의 리스트를 반환하고, 결과가 빈 리스트이면 Http404 예외를 발생시킵니다. klass는 Model 또는 Manager 클래스일 수도 있고, QuerySet 객체일 수도 있습니다.