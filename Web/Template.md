# Template

템플릿 내부 처리 과정을 알아봅시다. 템플릿 파일을 코딩할 때, 정적 파일을 다루는 경우가 많습니다. 템플릿 주제와는 다소 거리감이 있지만, 정적 파일을 처리하는 staticfiles 애플리케이션에 대해서도 추가적으로 설명합니다.



### 템플릿 설정 항목(1.8 버전 이상)

장고의 코어 템플릿 엔진을 DTL<sup>Django Template Language</sup>이라고 합니다. 그리고 장고는 DTL 이외에도 Jinja 템플릿 엔진을 기본적으로 지원하며, 다른 템플릿 엔진도 설치하면 사용이 가능합니다. 템플릿은 어떤 템플릿 엔진을 사용할 것인지 지정하는 것부터 시작합니다. 이는 설정 파일에서 이뤄지는데, 템플릿 엔진과 그 엔진에 적용될 옵션들을 지정합니다.

```python
# settings.py
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

**BACKEND** 항목은 사용할 템플릿 엔진을 지정합니다. 장고에서는 다음 2가지 템플릿 엔진을 기본적으로 지원하며, 필요하다면 장고의 템플릿 API를 이용해서 만든 서드 파티 엔진을 지정하는 것도 가능합니다.

- `django.template.backends.django.DjangoTemplates` : 장고의 자체 템플릿 엔진입니다.
- `django.template.backends.jinja2.Jinja2` : 파이썬 언어의 대표적인 템플릿 엔진입니다. 시스템에 Jinja2 라이브러리가 설치되어 있으면 장고가 제공하는 설정이나 API 등을 이용할 수 있습니다.



**DIRS** 항목은 프로젝트 템플릿 파일이 위치한 디렉토리를 지정합니다. 다음에 나오는 APP_DIRS 항목과 관련된 애플리케이션 템플릿 디렉토리보다 우선해 파일을 찾습니다. 기본값은 빈 리스트입니다. 보통은 다음과 같이 최상단에 'templates' 폴더를 생성하여 입력합니다.

```python
'DIRS' : [os.path.join(BASE_DIR, 'templates')],
```



**APP_DIRS** 항목은 템플릿 파일을 찾을 때, 애플리케이션 내의 템플릿 디렉토리에서도 찾을지 여부를 지정합니다. 기본값은 `False`지만 startproject 명령에 의해 settings.py 파일이 만들어질 때는 True로 설정됩니다.



**OPTIONS** 항목은 템플릿 엔진에 따라 해당하는 옵션 항목들을 설정합니다. 장고 템플릿 엔진을 사용하는 경우는 다음과 같은 옵션 항목이 있습니다.

- `context_processors` : 웹 요청에 들어 있는 파라미터들(request)을 인자로 받아서 컨텍스트 데이터로 사용될 사전을 만드는 호출 가능한 객체(callable)를 지정합니다. 보통은 함수로 정의되는데 이 함수들이 반환하는 사전은 최종 컨텍스트 데이터를 만들 때 추가됩니다. 기본값은 빈 리스트입니다.
- `debug` : 템플릿 디버그 모드를 설정합니다. `True`로 설정하면 템플릿 렌더링 과정에서 에러가 발생했을 때 템플릿 파일 내에서 에러가 발생한 줄을 다른 색으로 표시합니다. 기본값은 다른 설정 항목인 DEBUG 항목의 값을 따릅니다.
- `loaders` : 템플릿 로더 클래스를 지정합니다. 로더는 템플릿 파일을 찾아 메모리로 로딩하는 역할을 수행합니다.
- `string_if_invalid` : 템플릿 변수가 잘못된 경우 대신 사용할 문자열을 지정합니다. 기본값은 공백 문자열입니다.
- `file_charset` : 템플릿 파일을 읽어 디코딩할 때 사용하는 문자셋을 지정합니다. 기본값은 'utf-8'입니다.



### 템플릿 내부 처리 과정

장고 내부에서 동작하는 템플릿 처리 과정은 크게 3가지로 나눌 수 있습니다.

1. **템플릿 설정에 따라 Engine 객체를 생성합니다.**

   Engine 객체를 생성할 때 사용하는 인자들이 TEMPLATES 설정 항목에 지정된 값들입니다. 이 중에서 `loaders` 옵션 항목은 2번, `context_processors` 옵션 항목은 3번에서 사용됩니다. 또한, 이 단계에서 Engine 객체뿐 아니라 Engine 객체에 소속된 Loader 객체도 같이 생성됩니다. 그 다음 Loader 객체가 동작해 다음 단계에서 설명하는 템플릿 파일 검색 작업이 수행됩니다.

2. **템플릿 파일 로딩 및 Template 객체를 생성합니다.**

   설정 옵션 항목에 loaders가 지정되지 않은 경우, 기본 로더로 다음 2개의 클래스를 사용합니다. 그 밖에 캐시 로더 또는 개발자가 만든 커스텀 로더 등을 사용할 수도 있지만, 특별한 경우가 아니라면 기본 로더 2개를 변경 없이 사용하는 것이 일반적입니다.

   - `django.template.loaders.filesystem.Loader` : 템플릿 파일을 찾기 위해 설정 항목 TEMPLATES의 DIRS 항목에 지정된 디렉토리를 검색합니다. DIRS 항목이 비어 있으면 로더는 검색을 수행하지 않습니다.
   - `django.template.loaders.app_directories.Loader` : 템플릿 파일을 찾기 위해 각 애플리케이션 디렉토리 하위에 있는 `templates/` 디렉토리를 검색합니다. 애플리케이션은 `INSTALLED_APPS` 설정 항목에 등록된 앱들이 대상입니다. 이 로더는 `TEMPLATES` 설정 항목의 `APP_DIRS` 항목이 `True`인 경우에만 작동합니다.

   한 가지 더 유의할 점은 템플릿 파일을 찾는 순서입니다. loaders 기본 설정에 `filesystem.Loader`가 `app_directories.Loader`보다 먼저 나오므로 `DIRS` 항목에 지정된 디렉토리를 가장 먼저 찾게 됩니다. 그리고 `INSTALLED_APPS` 항목에 지정된 앱의 순서에 따라 각 앱의 `templates/` 디렉토리를 검색합니다. 이 단계에서 Loader 객체는 템플릿 파일들을 찾은 후에 Template 객체를 생성합니다. 이때 찾은 템플릿 파일들의 템플릿 코드들을 하나로 모아서 Template 객체 생성자로 전달합니다. 이 단계에서 생성된 Template 객체는 다음 단계에서 사용됩니다.

3. **렌더링을 실시해, 최종 HTML 텍스트 파일을 생성합니다.**

   렌더링을 위해서는 템플릿 코드와 컨텍스트 데이터가 필요합니다. 템플릿 코드는 앞 단계에서 만들어지고, 컨텍스트 데이터는 뷰 함수에서 만들어진 템플릿 시스템으로 전달됩니다. 한 가지 더 있다면 웹 요청 객체인 HttpRequest 객체에 들어 있는 데이터도 컨텍스트 데이터로 사용됩니다.
   
   뷰에서 전달된 데이터만으로 최종 컨텍스트 데이터를 만들 때는 Context 객체를 사용하고, HttpRequest 데이터를 포함해 최종 컨텍스트 데이터를 만들 때는 RequestContext 객체를 사용합니다.
   
   HttpRequest 객체에는 다양한 데이터가 포함되어 있습니다. 이 중에서 어떤 데이터를 컨텍스트 데이터로 사용할지를 결정하는 것이 템플릿 엔진 설정 항목의 context_processors 옵션 항목입니다. 처음 startproject 명령으로 프로젝트 생성 시 다음과 같은 4가지 컨텍스트 프로세서가 지정됩니다.
   
   - `django.template.context_processors.debug` : 현재 실행 환경의 DEBUG 모드를 지칭하는 debug 변수 및 웹 요청 처리 과정에 사용된 SQL 쿼리 정보를 담은 sql_queries 변수, 2가지가 최종 컨텍스트 데이터에 추가됩니다.
   - `django.template.context_processors.request` : 현 요청의 HttpRequest를 지칭하는 request 변수가 최종 컨텍스트 데이터에 추가됩니다.
   - `django.template.context_processors.auth` : 로그인 사용자를 지칭하는 user 변수 및 그 사용자의 권한을 지칭하는 perms 변수가 최종 컨텍스트 데이터에 추가됩니다.
   - `django.template.context_processors.messages` : 메시지 리스트를 지칭하는 messages 변수와 메시지 레벨을 지칭하는 DEFAULT_MESSAGE_LEVELS 변수가 최종 컨텍스트 데이터에 추가됩니다.
   
   RequestContext 객체가 생성될 때는 위 4개의 컨텍스트 프로세서 이외에도 CSRF<sup>Cross-Site Request Forgery</sup> 보안 공격을 방지하기 위한 다음 프로세서가 자동으로 추가됩니다.
   
   - `django.template.context_processors.csrf` : `{% csrf %}` 템플릿 태그 처리에 필요한 토큰이 최종 컨텍스트 데이터에 추가됩니다.
   
   템플릿 코드에 컨텍스트 데이터를 대입해 처리하는 과정을 렌더링이라 합니다. 좀 더 풀어서 말하자면, 템플릿 코드가 담겨 있는 Template 객체가 생성된 후, 템플릿 코드에 포함된 변수들을 그에 맞는 데이터로 치환해 최종 텍스트를 만드는 과정입니다.



### 제네릭 뷰의 디폴트 템플릿

모델을 대상으로 로직을 처리하는 제네릭 뷰들 대부분은 디폴트 템플릿명을 가지고 있습니다. 디폴트 템플릿명이란 제네릭 뷰에서 template_name 속성을 지정하지 않는 경우에 사용하는 템플릿 파일 이름을 의미합니다.

기본 템플릿명은 다음과 같은 규칙에 따라 정해집니다.

- `<app_label>/<model_name(소문자)>_<template_name_suffix>.html`

참고로 TemplateView, RedirectView 등은 모델을 지정할 필요가 없는 제네릭 뷰이므로, 기본 템플릿명을 갖지 않습니다.



### {% include %} 태그

장고에서는 DRY<sup>Don't Repeat Yourself</sup> 원칙에 따라 코드의 중복을 줄일 수 있는 여러 가지 기능을 제공합니다. 템플릿 분야에서는 {% extends %} 태그를 사용한 템플릿 상속 기능이 가장 대표적인 기능입니다. 또한, 공통된 태그를 재활용하면서 코드 중복을 줄이기 위해 그 다음으로 많이 쓰이는 태그가 {% include %} 태그라고 할 수 있습니다. 공통적으로 사용하는 템플릿 파일을 따로 만들어 둔 다음 {% include %} 태그로 공통 파일을 가져와 사용하는 방식입니다.

{% include %} 태그는 다른 템플릿 파일을 현재의 템플릿 파일에 포함시키는 기능을 합니다. 다른 템플릿 파일을 가져와서 렌더링 할 때는 현재의 템플릿 컨텍스트로 렌더링합니다.

- `{% include "foo/bar.html" %}` : 템플릿 파일명을 따옴표로 묶습니다.
- `{% include template_name %}` : 템플릿 파일명이 들어 있는 변수명을 사용해도 됩니다.

예시로 `foo/bar.html` 파일의 내용이 아래와 같다면 다음의 3가지 형식으로 {% include %} 태그를 사용할 수 있습니다.

```html
{{ greeting }}, {{ person | default:"friend" }}
```

- `{% include "foo/bar.html" %}` : 이 경우는 `foo/bar.html` 템플릿을 사용하는 현재의 뷰에서 제공하는 컨텍스트 변수를 사용합니다. 만일 컨텍스트 변수가 greeting은 "Hello"로, person은 "John"으로 주어진다면 위 문장을 렌더링한 결과는 "Hello, John"이 될 것입니다.
- `{% include "foo/bar.html" with person="winters" greeting="Hello" %}` : {% include %} 태그에서 키워드 인자로 변수를 지정할 수도 있습니다.
- `{% include "foo/bar.html" with greeting="Hi" only %}` : 이와같이 {% include %} 태그에서 변수를 고정할 수도 있습니다.



### {% static %} 템플릿 태그

장고에서는 이미지, 자바스크립트, CSS 파일들을 정적<sup>Static</sup> 파일이라고 합니다. 템플릿에서도 이런 정적 파일을 자주 사용하므로 장고 {% static %} 태그를 제공해 정적 파일을 쉽게 처리할 수 있도록 하고 있습니다.

템플릿 파일에서 정적 파일을 사용하는 경우는 정적 파일을 찾을 수 있는 URL을 구성하는 경우가 대부분입니다. 그래서 {% static arg %} 태그도 URL을 구성해 반환하는데, 구성 방법은 STATIC_URL 설정 항목과 arg로 주어진 정적 파일을 합쳐서 URL을 만듭니다.

```html
<!--
     settings.py 파일
     STATIC_URL = '/static/'
-->

{% load static %}
<img src="{% static 'images/hi.jpg' %}" alt="Hi!" />

<img src="static/images/hi.jpg" alt="Hi!" />
```

{% static arg %}에서 인자에 해당하는 arg는 문자열 외에도 컨텍스트 변수를 사용할 수도 있습니다.

장고는 {% static %} 템플릿을 두 곳의 소스 파일에서 제공합니다.

- `python/site-packages/django/templatetags/static.py`
- `python/site-packages/django/contrib/templatetags/staticfiles.py`

위에 있는 파일은 장고의 기본 템플릿 태그로 {% static %} 태그를 정의하고, 아래 파일은 staticfiles 애플리케이션의 템플릿 태그로 {% staticfiles %} 태그를 정의합니다. 버전 1.10부터는 두 기능의 구분이 없어지면서 {% load static %} 사용을 권장하고 있으며, {% load staticfiles %}는 장고 3.0 버전에서 삭제될 예정입니다.



### staticfiles 애플리케이션 기능

정적 파일을 처리하기 위해 장고는 staticfiles 애플리케이션을 제공합니다. 물론 이 애플리케이션은 개발 환경에서 사용되는 애플리케이션입니다. 상용 환경에서는 정적 파일을 처리하기 위해 훨씬 더 처리 능력이 뛰어난 Apache, Nginx 등의 웹 서버를 사용하기 때문입니다.

장고의 개발 환경에서 사용하는 웹 서버가 바로 runserver입니다. runserver를 실행시키고 정적 파일 처리가 필요하면, runserver는 staticfiles 앱을 사용해서 정적 파일을 처리합니다. 단, DEBUG 모드가 True인 경우만 staticfiles 앱이 동작합니다. 개념적으로 장고의 runserver는 다음 순서로 정적 파일을 처리합니다.

1. **웹 클라이언트(브라우저)는 URL을 포함한 웹 요청을 서버에 보냅니다.**

   웹 요청을 보내는 한 가지 예시가 바로 템플릿 파일에서 {% static %} 태그를 사용하는 것입니다. {% static %} 태그가 사용되었다면 그 기능에 의해 적절히 변환된 URL(STATIC_URL)을 포함하여 웹 서버에 요청을 보냅니다.

2. **장고는 웹 요청이 URL이 STATIC_URL로 시작하는지 검사합니다.**

   장고의 runserver는 웹 요청 URL을 검사합니다. 웹 요청 URL을 분석하여 STATIC_URL의 포함 여부를 확인합니다.

3. **URL이 STATIC_URL로 시작하면 장고는 staticfiles 앱을 사용해 처리를 시작합니다.**

   장고의 runserver는 URL을 처리하기 위해 staticfiles 앱의 views, serve() 뷰 함수를 호출합니다. staticfiles 앱을 사용하기 위해서는 `INSTALLED_APPS` 항목에 staticfiles 앱이 등록되어야 한다는 점을 유의해야 합니다.

4. **staticfiles 앱은 `STATICFILES_FINDERS`에 지정된 파인더로 정적 파일을 검색합니다.**

   뷰 함수 serve()는 파인더를 지정된 순서대로 사용하여 정적 파일을 찾습니다. 그래서 FileSystemFinder 파인더를 먼저 사용하고, 그 후에 AppDirectoriesFinder 파인더를 사용합니다.

5. **파인더에 따라 검색하는 디렉토리가 달라집니다.**

   FileSystemFinder 파인더는 STATICFILES_DIRS 설정 항목에 지정된 디렉토리를 검색합니다. 그리고 AppDirectoriesFinder 파인더는 `INSTALLED_APPS` 설정 항목에 등록된 앱을 등록된 순서대로 순회하면서 각 앱의 디렉토리 하위의 `static/` 디렉토리를 검색합니다.

   `STATICFILES_FINDERS` 설정 항목에 FileSystemFinder 파인더가 먼저 지정되어 있으므로 정적 파일을 검색 시 `STATICFILES_DIRS` 항목에 지정된 디렉토리가 각 앱의 `static/` 디렉토리보다 먼저 찾게 됩니다.

6. **정적 파일을 찾으면 해당 파일을 웹 클라이언트에 응답합니다.**

   파인더에 의해 원하는 정적 파일을 찾으면 장고의 runserver는 찾은 파일을 브라우저에 응답으로 보냅니다. 정적 파일을 못찾으면 `404 Not Found` 에러 응답을 브라우저로 보냅니다.

staticfiles 앱은 정적 파일을 처리하기 위해 미리 설정된 항목을 사용하는데, 이들은 settings 설정 파일에 지정되어 있습니다.

- **`STATIC_ROOT(Default:None)`**

  배포 과정에서 collectstatic 명령을 실행하는데, collectstatic 명령이 정적 파일을 모아주는 목적지 디렉토리를 지정합니다. 즉 collectstatic 명령을 실행하면 이 명령은 정적 파일들을 찾아서 `STATIC_ROOT` 디렉토리에 복사합니다. Apache와 같은 상용 웹 서버는 정적 파일들을 서비스하기 위해 이 디렉토리를 찾지만, 개발용 웹 서버인 runserver는 정적 파일을 `STATIC_ROOT` 디렉토리가 아니라 다른 곳에서 찾습니다.

- **`STATIC_URL(Default:None)`**

  정적 파일을 간주해 처리하라고 알려주는 URL을 지정합니다. 프로젝트 생성 시 startproject 명령에 의해 **`STATIC_URL='/static/'`**으로 설정되고, 변경 없이 사용하는 것이 일반적입니다.

- **`STATICFILES_DIRS(Default:[])`**

  정적 파일 처리를 위해 staticfiles 앱이 검색하는 디렉토리들을 리스트 또는 튜플로 지정합니다. 단 FileSystemFinder 파인더가 활성화된 경우에만 이 설정 항목을 사용합니다. 일반적으로 이 디렉토리는 프로젝트에 공통인 정적 파일들을 모아두는 용도로 사용합니다.

- **`STATICFILES_STORAGE(Default:'django.contrib.staticfiles.storage.StaticFilesStorage')`**

  collectstatic 명령으로 정적 파일을 모을 때 사용하는 파일 저장소 엔진용 클래스를 지정합니다. 개발 모드에서는 기본 설정을 그대로 사용하는 경우가 많지만, 상용 모드라면 별도의 저장소를 사용하는 경우를 고려해야 합니다. 이미지, 동영상 등의 정적 파일은 용량이 커서 아마존 S3 등 별도의 저장소 서버를 사용하는 경우가 많기 때문입니다. 기본 설정인 StaticFilesStorage 클래스는 `STATIC_ROOT` 항목으로 지정된 로컬 디렉토리에 정적 파일을 모아줍니다.

- **`STATICFILES_FINDERS(Default:("django.contrib.staticfiles.finders.FileSystemFinder", "django.contrib.staticfiles.finders.AppDirectoriesFinder"))`**

  정적 파일을 찾아주는 파인더 클래스를 튜플로 지정합니다. 보통은 별도의 설정 없이 기본 설정을 주로 사용합니다. FileSystemFinder 파인더는 `STATICFILES_DIRS` 설정 항목으로 지정된 디렉토리를 검색하고, AppDirectoriesFinder 파인더는 각 앱 디렉토리 하위의 static 디렉토리에서 정적 파일을 검색합니다. 정적 파일 검색 시 동일한 이름의 파일이 여러 개 발견되면 처음으로 찾은 파일을 사용합니다.

  참고로 `django.contrib.staticfiles.finders.DefaultStorageFinder`라는 파인더가 한 가지 더 있는데, 이 파인더는 `DEFAULT_FILE_STORAGE` 설정 항목으로 지정된 디렉토리를 검색합니다.



**STATIC_ROOT vs MEDIA_ROOT**

장고에서는 위의 두 항목이 같으면 안됩니다. MEDIA_ROOT 디렉토리에는 사용자가 업로드한 파일들이 있어서 보안에 취약하기 때문입니다. 따라서 runserver 실행 시 위의 두 항목이 같으면 예외가 발생합니다. 또한 파일 저장소로 로컬 시스템을 사용하는 경우 MEDIA_ROOT 디렉토리는 업로드한 파일이 저장되는 영구 저장소를 의미하지만, STATIC_ROOT 디렉토리는 정적 파일의 배포 및 서비스를 위한 임시 저장소를 의미합니다. 정적 파일에 대한 영구 저장소는 각 앱의 `static/` 디렉토리 또는 STATICFILES_DIRS 항목에 지정한 디렉토리입니다.



**미디어 파일의 뷰 함수**

staticfiles 앱의 **views.serve()** 뷰 함수는 정적 파일 처리뿐만 아니라 미디어 파일을 서비스 해주는 데에도 사용합니다. 미디어 파일이란 사용자에 의해 업로드된 파일을 의미하는데 이런 미디어 파일도 정적 파일로 간주하므로 views.serve() 뷰 함수가 처리합니다.