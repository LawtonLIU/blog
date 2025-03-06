from django.urls import path,re_path
from accounts import views
from accounts import forms  

app_name='accounts'

# 登录 登出 注册 忘记密码 忘记密码验证码
urlpatterns=[
    re_path(r'^login/$',views.LoginView.as_view(success_url='/'),name='login',
            kwargs={'authentication_form':forms.LoginForm}),
    re_path(r'^logout/$',views.LogoutView.as_view(),name='logout'),
    re_path(r'^register/$',views.RegisterView.as_view(success_url='/'),name='register'),
    path(r'account/result/',views.account_result,name='result'),
    re_path(r'^forget_password/$',views.ForgetPasswordView.as_view(),name='forget_password'),
    re_path(r'^forget_password_code/$',views.ForgetPasswordEmailCode.as_view(),name='forget_password_code'),
]