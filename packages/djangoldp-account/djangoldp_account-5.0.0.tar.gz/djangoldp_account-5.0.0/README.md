## Synopsis

This module is an add-on for Django that provides WebID-OIDC accounts management. It plays two roles:
- The Relying Party
- The Authentification provider

## Requirements
* djangoldp~=4.0
* django_registration~=3.4
* validators~=0.20
* oic~=1.6
* django-webidoidc-provider~=1.0
* djangorestframework>=3.14

## Installation

1. Install this module and all its dependencies

```
pip install djangoldp_account
```

2. Update settings.py on your server

```
DJANGOLDP_PACKAGES = [
    ...
    'djangoldp_account',
    ...
]
LOGIN_URL = '/auth/login/'

OIDC_USERINFO = 'djangoldp_account.settings.userinfo'
OIDC_REGISTRATION_ENDPOINT_REQ_TOKEN = False
OIDC_REGISTRATION_ENDPOINT_ALLOW_HTTP_ORIGIN = True
OIDC_IDTOKEN_SUB_GENERATOR = 'djangoldp_account.settings.sub_generator'
OIDC_IDTOKEN_EXPIRE = 60 * 60

AUTHENTICATION_BACKENDS = [...,'djangoldp_account.auth.backends.ExternalUserBackend']

MIDDLEWARE = [ ..., 'djangoldp_account.auth.middleware.JWTUserMiddleware']

```

You should also ensure that `SITE_URL` and `BASE_URL` are set correctly.

## User registration
User registration use django_registration module : https://django-registration.readthedocs.io/en/3.0.1/

To use it :
Firts, add these settings on settings.py :

```python
REGISTRATION_OPEN=True
ACCOUNT_ACTIVATION_DAYS=7 #Number of days you want to keep the activation token valid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'you@gmail.com'
EMAIL_HOST_PASSWORD = 'password'
EMAIL_PORT = 587
```

Optionally you can configure which user fields which you would like to include on the registration form by including `REGISTRATION_FIELDS` in settings.py

```python
REGISTRATION_FIELDS = ('username', 'email', 'password1', 'password2')
```

This will be sufficient to change the user fields on display on the form. If you want to customise the form (for example by [adding a model relationship to the user](https://stackoverflow.com/questions/14726725/python-django-django-registration-add-an-extra-field/14879316#14879316)), then you can override the setting `REGISTRATION_USER_FORM` to replace it altogether. The form you supply should extend `djangoldp_account.forms.LDPUserForm` or at minimum `django_registration.forms.RegistrationForm`

```yaml
REGISTRATION_USER_FORM: "djangoldp_hiphopcommunity.forms.HipHopUserForm"
```

In either case, at a minimum the registration form fields must include the fields `('username', 'email', 'password1', 'password2')`

the setting `REGISTRATION_TEMPLATE_PATH` changes the path of the template serving the form, e.g.

```yaml
REGISTRATION_TEMPLATE_PATH: "hiphopcommunity/registration_form.html"
```

Visit http://127.0.0.1:8000/auth/register/ to access the registration form

### Enabling account activation without mail

Optionally, you can also enable the user account activation without sending the activation mail, by setting:

```yaml
SIMPLE_REGISTRATION: True
```

### Sending email on account activation

When the user is created, you can optionally send a notification by email using the setting:

```yaml
EMAIL_ON_ACCOUNT_CREATION: True
```

## Enabling login by email and username

Modify the `AUTHENTICATION_BACKENDS` variable in `settings.py` to replace 
`'django.contrib.auth.backends.ModelBackend'` by 
`'djangoldp_account.auth.backends.EmailOrUsernameAuthBackend'`.

Ensure `'djangoldp_account.auth.backends.EmailOrUsernameAuthBackend'` is 
first in the list.

## Enabling default_redirect_uri behaviour

For many linked-data platforms, there will be multiple authentication providers, and potential multiple client-side apps/websites. In this case it can be difficult to know where to redirect the user. On login it's possible to set `next` as a query parameter pointing to the new site, but the user may have come from sources without this parameter set (e.g. a forgot password link in an email). For user experience, we offer a system which keeps track of the location the user previously logged in from, and falls back onto this if there is not a `next` specified in the URL. To use system this simply add the following to your settings.py

```python
LOGIN_REDIRECT_URL = '/redirect-default/'
```

If the user has no redirect preference set, DjangoLDP will try the preferred client-side app, set automatically on `INSTANCE_DEFAULT_CLIENT`. If this is not set, the server will try `LOGIN_REDIRECT_DEFAULT`

```python
LOGIN_REDIRECT_DEFAULT = '/accounts/profile/'
```

## Authenticate from an external provider

- go to mysite.org/accounts/login
- On the second form, put your email (me@theothersite.com) or the Authorization server url (https://theothersite.com/openid) 

Note: The url provided must contains /openid-configuration (for instance : https://theothersite.com/openid/openid-configuration must exists)

Once authentication on theothersite.com an account will be create on mysite.org and you'll be authentified both on theothersite.com and on mysite.com. 

## How to know a user is authenticated (Not on any specification)
Useful in case of the client do NOT wants to store token in storage for security reason.

When a user is authenticated on the server, any request will contains the header `User` with user webid
For instance :
```
GET https://mysite.com

HEADERS:
User: https://theothersite.com/users/2
```

Note that `GET https://mysite.com/user/1` will return something like :

```
HEADERS
User: https://anysite.com/users/X

BODY
{
  "@id": "https://theothersite.com/users/2",
  "first_name": "John",
}
```

Because `/user/1` is an account of an external user with webid `https://theothersite.com/users/2`  

## Extending User serialization

djangoldp_account uses `django.contribs.auth.User` and manages its serialization into JsonLd format
If you need to extend it with you own relation use `USER_NESTED_FIELDS` on settings.py :

```
USER_NESTED_FIELDS=['skills']
```

Finally, to expand on the `empty_containers` setting ([see DjangoLDP docs](https://git.startinblox.com/djangoldp-packages/djangoldp#custom-meta-options-on-models)) you can use `USER_EMPTY_CONTAINERS`:

```
USER_EMPTY_CONTAINERS = ['skills']
```

On the server settings (should be overriden only one time)

## Federation
If you want to enable full federation capabilities you have to use the `LDPUser` instead of django `User`

Add to your `settings.py` :
```
AUTH_USER_MODEL = 'djangoldp_account.LDPUser'
# Also, you can allow distant users to login to your server
DISTANT_LOGIN = True
```

### Create an administrator account for a distant user

You can create an administrator account for a distant user with the `create_distant_admin` command:

```bash
./manage.py create_distant_admin --urlid="http://server/users/xyz/"
```

## Import users in batch mode

To create a huge number of accounts from an existing database, you can use the `import_csv` command. The imported CSV file must contain user first name in the first column, user last name in the second column and user email in the third column. For example ; 

| First name    | Last Name  | Email           |
| ------------- | ---------- | --------------- |
| Dummy         | Dude       | dummy@email.co  |
| John          | Doe        | john@email.co   |
| Doe           | Minic      | doe@email.co    |

Usernames will be generated automatically from first and last name by converting capitals and accents and replacing any forbidden character by a dash (-). Any already existing email will be skipped.

```bash
python manage.py import_csv example-accounts.csv 
```

## Apply i18n
Default translation files are embedded with the packages with support for English and French for now. More coming.
To use them, you should activate the feature by adding both the proper i18n context processor and LocaleMiddleware:

```
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ... Your context processors ...
                'django.template.context_processors.i18n',
            ],
        },
    },
]

MIDDLEWARE = [
        #... Your Middlewares ...
        'django.middleware.locale.LocaleMiddleware',
]

USE_L10N = True
```

## ACCOUNT DEFAULT PICTURE

There is a way to set a profile picture in the account section of every created user by default, and it is using the following settings key:

```
ACCOUNT_DEFAULT_PICTURE = 'https://example.com/profile.jpg'
```

That allows to avoid having an empty picture client side.
