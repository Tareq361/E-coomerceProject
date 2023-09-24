from django.urls import path,include
from . import views
from django.conf.urls.static import static
from django.conf import settings
app_name="onlineshop"
urlpatterns = [

path('',views.home,name='home'),
path('product/<int:pid>',views.productView, name="productview"),
path('store/',views.storeView, name="storeview"),
path('store/category/<str:cname>',views.categoryView, name="categoryView"),
path('store/search/',views.searchView, name="searchView"),
path('add_cart/<int:product_id>/',views.add_cart,name='add_cart'),
path('cart/',views.cart,name='cart'),
path('remove_cart/<int:cartitem_id>/',views.remove_cart,name='remove_cart'),
path('remove_cart_items/<int:cartitem_id>/',views.remove_cartItems,name='remove_cartItems'),
path('add_cart_quantity/<int:cartitem_id>/',views.add_cart_quantity,name='add_cart_quantity'),
path('signin/',views.signIn,name='signIn'),
path('logout/',views.logout,name='logout'),
path('register/',views.register,name='register'),
path('activate/<uidb64>/<token>/',views.activate,name='activate'),
path('dashboard/',views.dashboard,name='dashboard'),
path('myorder/',views.myorder,name='myorder'),
path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
path('reset_password/',views.reset_password,name='reset_password'),
path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate,name='resetpassword_validate'),
path('checkout/',views.checkout,name='checkout'),
path('placeorder/',views.placeorder,name='placeorder'),
path('payment/<int:order_id>',views.payment,name="payment"),
path('Paypalpayment/',views.paypalPayment,name="Paypalpayment"),
path('order_complete/',views.order_complete,name="order_complete"),
path('order_details/<int:order_no>',views.order_details,name="order_details"),
path('track_order/<int:order_no>',views.track_order,name="track_order"),
path('edit_profile/',views.edit_profile,name="edit_profile"),
path('change_password/',views.change_password,name="change_password"),
path('submit_review/<int:p_id>',views.submit_review,name="submit_review"),
path('aboutus/',views.aboutus,name='aboutus'),
path('rulesandterms/',views.rulesandterms,name='rulesandterms'),
path('blogs/',views.blogs,name='blogs'),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)