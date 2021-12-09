import datetime

from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage, send_mail
from django.views.decorators.csrf import csrf_exempt

from Ecommerce import settings
from .models import product_gallery,Category, Product, Cart, Cartitem, Variation, Customer, Order, Payment, OrderProduct, ReviewRating
from django.contrib import messages
#for payment system
# from sslcommerz_python.payment import SSLCSession
from decimal import Decimal

# Create your views here.
def home(request):
    category=Category.objects.all()
    product=Product.objects.all().order_by('-created_date')
    return render(request,"index.html",{"category":category,"products":product,"cart_count":_cart_count(request)})
def signIn(request):
    if request.method == "POST":
        print("success")
        email = request.POST.get('Email')
        pass1 = request.POST.get('Password')

        try:

            user = Customer.objects.get(email=email)

        except:
            print("incorrect")
            messages.warning(request, "User doesn't exist!!!")
            return render(request, "signin.html", {})
        if (user.email == email):
            print("correct email")
            if(user.is_active):
                if (check_password(pass1,user.password)):
                    print("correct password")
                    print(_cart_id(request))
                    try:

                        c_exist=Cart.objects.filter(cart_id=user.id).exists()
                        print(c_exist)
                        if c_exist:
                            print("find user cart1")
                            cus_cart = Cart.objects.get(cart_id=user.id)
                            print("find user cart2")
                            cart = Cart.objects.get(cart_id=_cart_id(request))
                            print("find user cart")
                            is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                            if is_cart_item_exists:
                                cart_item = Cartitem.objects.filter(cart=cart)
                                print("find cart item from session")
                                for item in cart_item:
                                    item.user = user
                                    item.cart = cus_cart
                                    item.save()
                        else:
                            cart = Cart.objects.get(cart_id=_cart_id(request))
                            print("find cart")
                            is_cart_item_exists = Cartitem.objects.filter(cart=cart).exists()
                            if is_cart_item_exists:
                                cart_item = Cartitem.objects.filter(cart=cart)

                                for item in cart_item:
                                    item.user = user
                                    item.cart.cart_id=user.id
                                    item.save()
                            cart.cart_id=user.id
                            cart.save()
                    except:
                        pass
                    request.session['customer'] = user.id
                    request.session['pro_name'] = user.first_name
                    messages.success(request, "You are logged in")
                    return redirect('/dashboard')
                else:
                    print("icorrect password")
                    messages.warning(request, "Incorrect password!!!")
                    return redirect('/signin')
            else:
                print("Please active your account")
                messages.warning(request, "Please active your account")
                return redirect('/signin')
        else:
            print("Wrong email address!!!")
            messages.warning(request, "Wrong email address!!!")
            return render(request, "signin.html", {})

    if request.session.get('customer'):
        return redirect('/')
    else:
        return render(request, "signin.html", {"cart_count":_cart_count(request)})
def register(request):
    if request.method == "POST":
        Fname = request.POST.get('Fname')
        Lname = request.POST.get('Lname')
        Email = request.POST.get('email')
        phone = request.POST.get('phone')

        try:
            user = Customer.objects.get(email=Email)
            messages.warning(request, "Account already exist with this email address!!!")
            return render(request, "register.html", {})
        except:
            if(request.POST.get('confirm_password')!=request.POST.get('pass')):
                messages.warning(request, "Password doesn't match!!!")
                return render(request, "register.html", {})

            else:
                Password = make_password(request.POST.get('confirm_password'))
                signup = Customer(first_name=Fname, last_name=Lname, email=Email,phone=phone,
                                     password=Password)
                signup.save()
                print("success input")
                #user activation
                current_site=get_current_site(request)
                mail_subject="Please activate your account"
                messsage=render_to_string('account_varifiaction_mail.html',{
                    'user':signup,
                    'domain':current_site,
                    'uid':urlsafe_base64_encode(force_bytes(signup.pk)),
                    'token':default_token_generator.make_token(signup),
                })

                email_from = settings.EMAIL_HOST_USER
                recipient_list = [Email, ]
                send_mail(mail_subject,messsage,email_from,recipient_list)
                print("send activation link successfully")

                return redirect('/register?verification=True&email='+Email)
    elif request.session.get('customer'):
        return redirect('/')
    else:
        return render(request, "register.html", {"cart_count":_cart_count(request)})
def logout(request):
    if request.session.get('customer'):
        request.session.clear()
        messages.success(request, "You are Logged out!!!")
        return redirect('/signin')
    else:
        return redirect('/')
def productView(request,pname):

    category=Category.objects.all()
    product=Product.objects.get(productName=pname)
    in_cart=Cartitem.objects.filter(cart__cart_id=_cart_id(request),product=product)
    product_galleries=product_gallery.objects.filter(product=product)
    if request.session.get('customer'):
        try:
            orderproduct = OrderProduct.objects.filter(user=request.session.get('customer'), product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    return render(request,"productDetails.html",{"category":category,"product":product,"in_cart":in_cart,"cart_count":_cart_count(request),"reviews":reviews,"orderproduct":orderproduct,"product_galleries":product_galleries})
def storeView(request):

    category=Category.objects.all()
    product=Product.objects.all().filter(is_available=True)
    total=product.count()
    paginator = Paginator(product, 1) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"store.html",{"category":category,"products":page_obj,"total":total,"cart_count":_cart_count(request)})
def categoryView(request,cname):

    category=Category.objects.all()
    c=Category.objects.get(category_name=cname)
    product=Product.objects.filter(category=c,is_available=True)
    total=product.count()
    paginator = Paginator(product, 1) # Show 25 contacts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request,"store.html",{"category":category,"products":page_obj,"total":total,"cart_count":_cart_count(request)})
def searchView(request):

    category=Category.objects.all()

    print(request.GET.get('page'))
    print(request.GET.get('keyword'))
    if request.GET.get('keyword'):
        keyw=request.GET.get('keyword')
    else:
        keyw=request.POST.get("keyword")
    product=Product.objects.filter(productName__contains=keyw,is_available=True)

    total=product.count()
    paginator = Paginator(product, 1) # Show 25 contacts per page.

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)
    return render(request,"store.html",{"category":category,"products":page_obj,"total":total,"cart_count":_cart_count(request),"keyword":keyw})
def _cart_id(request):
    if request.session.get('customer'):
        print("sign in cart")
        cart=request.session.get('customer')
    else:
        cart=request.session.session_key
        print("without sign in cart")

        if not cart:
            cart=request.session.create()

    return cart
def _cart_count(request, cart_count=0):
    if request.session.get('customer'):
        try:
            user=Customer.objects.get(id=request.session.get('customer'))
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=Cartitem.objects.filter(user=user,cart=cart)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except:
            cart_count=0;
    else:
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=Cartitem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except:
            cart_count=0;
    return cart_count

def add_cart(request,product_id):
    if request.method=="POST":
        size=request.POST.get('size')
        color=request.POST.get('color')

        product=Product.objects.get(id=product_id)
        variation=Variation.objects.get(product=product,variation_value=size)

        variation1=Variation.objects.get(product=product,variation_value=color)
        print(variation)
        print(variation1)
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart=Cart.objects.create(cart_id=_cart_id(request))
        cart.save()

        try:

            in_cart_item=Cartitem.objects.filter(product=product,cart=cart,variation=variation).count()
            print(in_cart_item)

            in_cart_item2= Cartitem.objects.filter(product=product, cart=cart, variation=variation1).count()
            in_cart_item3 = Cartitem.objects.get(product=product, cart=cart, variation=variation1)
            in_cart_item4=Cartitem.objects.get(product=product, cart=cart, variation=variation)
            print(in_cart_item2)
            if in_cart_item3.id==in_cart_item4.id:
                cart_item=Cartitem.objects.get(product=product,id=in_cart_item3.id)
                cart_item.quantity += 1
                cart_item.save()
            else:
                cart_item = Cartitem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
                cart_item.variation.add(variation)
                cart_item.variation.add(variation1)
                cart_item.save()
        except Cartitem.DoesNotExist:
            if request.session.get('customer'):
                user=Customer.objects.get(id=request.session.get('customer'))
                cart_item=Cartitem.objects.create(
                    user=user,
                    product=product,
                    quantity=1,
                    cart=cart
                )
            else:
                cart_item=Cartitem.objects.create(
                    product=product,
                    quantity=1,
                    cart=cart
                )
            cart_item.variation.add(variation)
            cart_item.variation.add(variation1)
            cart_item.save()
        print(cart_item.product)
        return redirect('/cart')

def add_cart_quantity(request,cartitem_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    # product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(id=cartitem_id,cart=cart)
    print(cart_item.quantity)
    if cart_item.quantity>0:
        cart_item.quantity+=1
        cart_item.save()
    else:
        pass
    return redirect('/cart')
def remove_cart(request,cartitem_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    # product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(id=cartitem_id,cart=cart)
    if cart_item.quantity>1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('/cart')
def remove_cartItems(request,cartitem_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    # product=get_object_or_404(Product,id=product_id)
    cart_item=Cartitem.objects.get(id=cartitem_id,cart=cart)
    cart_item.delete()
    return redirect('/cart')
def cart(request, total=0,tax=0,quantity=0,grand_total=0,cart_items=None):

    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
        print(cart)
        cart_items=Cartitem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total+=(cart_item.product.price*cart_item.quantity)
            quantity+=cart_item.quantity
        tax=(2*total)/100
        grand_total=total+tax;
    except:
        pass

    print(cart_items)

    return  render(request,'cart.html',{"cart_items":cart_items,"total":total,"quantity":quantity,"tax":tax,"grand_total":grand_total,"cart_count":_cart_count(request)})
def activate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        print(uid)
        user=Customer.objects.get(pk=uid)

    except:
        user=None
        print("failed")
    if user is not None and default_token_generator.check_token(user,token):
        if(user.is_active):
            messages.warning(request, "Account already activated")
            return redirect('/signin')
        else:
            user.is_active=True
            user.save()
            messages.success(request,"Congratulation your account is activated")
        return redirect('/signin')
    else:
        messages.error(request,"invalid activation link")
        return redirect('/register')


def dashboard(request):
    if request.session.get('customer'):
        user=Customer.objects.get(id=request.session.get('customer'))
        order=Order.objects.filter(user=user).order_by('-created_at')
        order_count=order.count()
        context={"user":user,
                 "orders":order,
                 "order_count":order_count,
                 "cart_count": _cart_count(request)
                 }
        return render(request,'dashboard.html',context)
    else:
        return redirect('/')


def forgotpassword(request):
    if request.method == "POST":
        email=request.POST.get("Email")
        if Customer.objects.filter(email=email).exists():
            user=Customer.objects.get(email=email)
            #reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset password"
            messsage = render_to_string('reset_password_mail.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })

            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email, ]
            send_mail(mail_subject, messsage, email_from, recipient_list)
            print("send reset password link successfully")
            messages.success(request, "Password rest mail has been sent to your email address")
            return redirect('/signin')
        else:
            messages.warning(request,"Account doesn't exist")
            return redirect('/forgotpassword')
    return render(request,'forgot_password.html')

def resetpassword_validate(request,uidb64,token):
    try:
        uid=urlsafe_base64_decode(uidb64).decode()
        print(uid)
        user=Customer.objects.get(pk=uid)

    except:
        user=None
        print("failed")

    if user is not None and default_token_generator.check_token(user,token):
        request.session['cid']=uid


        messages.success(request,"please reset your password")
        return redirect('/reset_password')
    else:
        messages.warning(request,"Link expired!!!")
        return redirect('/signin')
def reset_password(request):
    if request.session.get('cid'):
        if request.method == "POST":
            password=request.POST.get("create_password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                cid=request.session.get('cid')
                user=Customer.objects.get(pk=cid)
                new_pass=make_password(confirm_password)
                user.password=new_pass
                user.save()
                messages.success(request, "Reset password successfully!!!")
                return redirect('/signin')
            else:
                messages.error(request, "Password doesn't match!!!")
                return redirect('/reset_password')
        else:
            return render(request,'reset_password.html')
    else:
        return redirect('/')
def checkout(request,total=0,tax=0,quantity=0,grand_total=0,cart_items=None):
    if request.session.get('customer'):
        try:
            cart=Cart.objects.get(cart_id=_cart_id(request))
            print(cart)
            cart_items=Cartitem.objects.filter(cart=cart,is_active=True)
            for cart_item in cart_items:
                total+=(cart_item.product.price*cart_item.quantity)
                quantity+=cart_item.quantity
            tax=(2*total)/100
            grand_total=total+tax;
        except:
            pass

        print(cart_items)
        return render(request,"checkout.html",{"cart_items":cart_items,"total":total,"quantity":quantity,"tax":tax,"grand_total":grand_total,"cart_count":_cart_count(request)})
    else:
        return redirect('/signin')
def placeorder(request, total=0,quantity=0):
    if request.session.get('customer'):
        user = Customer.objects.get(id=request.session.get('customer'))

        # If the cart count is less than or equal to 0, then redirect back to shop
        cart_items = Cartitem.objects.filter(user=user)
        cart_count = cart_items.count()
        if cart_count <= 0:
            return redirect('/store')

        grand_total = 0
        tax = 0
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        if request.method == 'POST':
            fname=request.POST.get("first_name")
            lname = request.POST.get("last_name")
            email=request.POST.get("email")
            phone=request.POST.get("phone")
            address_line_1=request.POST.get("address_line_1")
            address_line_2 = request.POST.get("address_line_2")
            city=request.POST.get("city")
            state=request.POST.get("state")
            country=request.POST.get("country")
            order_note=request.POST.get("order_note")
            ip = request.META.get('REMOTE_ADDR')
            order=Order.objects.create(user=user,first_name=fname,last_name=lname,email=email,phone=phone,address_line_1=address_line_1,address_line_2=address_line_2,state=state,city=city,country=country,ip=ip,order_note=order_note,tax=tax,order_total=grand_total)
            order.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()
            order = Order.objects.get(user=user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'payments.html', context)
        else:
            return redirect('/checkout')
    else:
        return redirect('/')

def payment(request,order_id):
    if request.session.get('customer'):
        order=Order.objects.get(order_number=order_id)

#         mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id=settings.STORE_ID,
#                                 sslc_store_pass=settings.STORE_PASS)
#         current_site = str(get_current_site(request))
#         status_url="http://"+current_site+"/order_complete/?order_no="+str(order_id)+"&cid="+str(request.session.get('customer'))
#         mypayment.set_urls(success_url=status_url, fail_url=status_url,
#                            cancel_url=status_url, ipn_url=status_url)

#         mypayment.set_product_integration(total_amount=Decimal(order.order_total), currency='BDT', product_category='clothing',
#                                           product_name='demo-product', num_of_item=2, shipping_method='YES',
#                                           product_profile='None')

#         mypayment.set_customer_info(name=order.first_name, email=order.email, address1=order.address_line_1,
#                                     address2=order.address_line_2, city=order.city, postcode='1207', country='Bangladesh',
#                                     phone=order.phone)

#         mypayment.set_shipping_info(shipping_to=order.first_name, address=order.address_line_1, city=order.city, postcode='1209',
#                                     country='Bangladesh')

#         # If you want to post some additional values
#         # mypayment.set_additional_values(value_a='cusotmer@email.com', value_b='portalcustomerid', value_c='1234',
#         #                                 value_d='uuid')

#         response_data = mypayment.init_payment()
#         print("--------------------------------")
#         print(response_data)
#         print("--------------------------------")
#         return redirect(response_data['GatewayPageURL'])
          return redirect('order_complete/')
    else:
        return redirect('/')
@csrf_exempt
def order_complete(request):
    if request.method == 'POST' or request.method == 'post':
        payment_data=request.POST
        status=payment_data['status']
        if status == 'VALID':
            tran_id=payment_data['tran_id']
            val_id=payment_data['val_id']
            print(payment_data)
            print(request.session.get('customer'))
            order_cus=Order.objects.get(is_ordered=False, order_number=request.GET.get('order_no'))
            user=Customer.objects.get(id=order_cus.user.id)
            order = Order.objects.get(user=user, is_ordered=False, order_number=request.GET.get('order_no'))
            # Store transaction details inside Payment model
            payment = Payment(
                user=user,
                payment_id=payment_data['tran_id'],
                payment_method=payment_data['card_type'],
                amount_paid=order.order_total,
                status=payment_data['status'],
            )
            payment.save()
            order.payment = payment
            order.is_ordered = True
            order.save()
            # Move the cart items to Order Product table
            cart_items = Cartitem.objects.filter(user=user)

            for item in cart_items:
                orderproduct = OrderProduct()
                orderproduct.order_id = order.id
                orderproduct.payment = payment
                orderproduct.user_id = user.id
                orderproduct.product_id = item.product_id
                orderproduct.quantity = item.quantity
                orderproduct.product_price = item.product.price
                orderproduct.ordered = True
                orderproduct.save()

                cart_item = Cartitem.objects.get(id=item.id)
                product_variation = cart_item.variation.all()
                orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                orderproduct.variations.set(product_variation)
                orderproduct.save()

                # Reduce the quantity of the sold products
                product = Product.objects.get(id=item.product_id)
                product.stock -= item.quantity
                product.save()

            # Clear cart
            Cartitem.objects.filter(user=user).delete()
            #for order email
            mail_subject = "Thank you for your order!"
            messsage = render_to_string('order_recieved_email.html', {
                'user': user,
                'order': order,

            })

            email_from = settings.EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(mail_subject, messsage, email_from, recipient_list)
            print("send confirm order")
            #for render in oder complete page
            try:

                ordered_products = OrderProduct.objects.filter(order_id=order.id)

                subtotal = 0
                for i in ordered_products:
                    subtotal += i.product_price * i.quantity



                context = {
                    'order': order,
                    'ordered_products': ordered_products,
                    'order_number': order.order_number,
                    'transID': payment.payment_id,
                    'payment': payment,
                    'subtotal': subtotal,
                }
                request.session['customer']=request.GET.get('cid')
                return render(request, 'order_complete.html', context)
            except (Payment.DoesNotExist, Order.DoesNotExist):
                return redirect('/storeview')

def submit_review(request,p_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        rating=request.POST.get('rating')
        subject=request.POST.get('subject')
        review=request.POST.get('review')
        ip = request.META.get('REMOTE_ADDR')
        try:

            reviews = ReviewRating.objects.get(user__id=request.session.get('customer'), product__id=p_id)
            reviews.subject=subject
            reviews.rating=rating
            reviews.review=review
            reviews.ip=ip
            reviews.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            reviews=ReviewRating()
            reviews.subject=subject
            reviews.rating=rating
            reviews.review=review
            reviews.ip=ip
            reviews.product_id = p_id
            reviews.user_id = request.session.get('customer')
            reviews.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect(url)

def order_details(request,order_no):
    if request.session.get('customer'):
        try:
            order=Order.objects.get(order_number=order_no)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,

                'subtotal': subtotal,
            }
            print(ordered_products)
        except:
            context={}
            pass
        return render(request,"order_details.html",context)
    else:
        return redirect('/')
def track_order(request,order_no):
    if request.session.get('customer'):
        try:
            order = Order.objects.get(order_number=order_no)
            ordered_products = OrderProduct.objects.filter(order_id=order.id)

            subtotal = 0
            for i in ordered_products:
                subtotal += i.product_price * i.quantity

            context = {
                'order': order,
                'ordered_products': ordered_products,
                'order_number': order.order_number,
            }
            print(ordered_products)
        except:
            context = {}
            pass
        return render(request,"trackorder.html",context)
    else:
        return redirect('/')
@csrf_exempt
def edit_profile(request):
    url = request.META.get('HTTP_REFERER')

    if request.session.get('customer'):
        try:
            user=Customer.objects.get(id=request.session.get('customer'))

            if request.method == "POST":
                user.first_name=request.POST.get('first_name')
                user.last_name= request.POST.get('last_name')
                user.phone = request.POST.get('phone_number')
                user.image = request.FILES['profile_picture']
                user.address_line_1= request.POST.get('address_line_1')
                user.add_2 = request.POST.get('address_line_2')
                user.address_line_2 = request.POST.get('city')
                user.state = request.POST.get('state')
                user.country = request.POST.get('country')
                user.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect(url)
        except:
            pass

    else:
        messages.alert(request, 'Profile updated unsuccessfull.')
        return redirect('/')


@csrf_exempt
def change_password(request):
    url = request.META.get('HTTP_REFERER')
    if request.session.get('customer'):
        try:
            user = Customer.objects.get(id=request.session.get('customer'))

            if request.method == "POST":
                current_password= request.POST.get('current_password')
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                if(check_password(current_password,user.password)):
                    if new_password == confirm_password:
                        user.password=make_password(confirm_password)
                        user.save()
                        messages.success(request, 'Password change successfully.')
                        return redirect('/logout')
                    else:
                        messages.warning(request, "Password doesn't match!!!")
                        return redirect(url)
                else:
                    messages.warning(request, 'Wrong password')
                    return redirect(url)
        except:
            pass
