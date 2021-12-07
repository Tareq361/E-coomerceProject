from django.contrib import admin
from . import models
# Register your models here.
admin.site.register(models.Category)
class product_admin_view(admin.ModelAdmin):
    list_display = ('productName','price','stock','category','modified_date','is_available')
admin.site.register(models.Product,product_admin_view)
admin.site.register(models.Cart)
admin.site.register(models.Cartitem)
class variationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter =  ('product','variation_category','variation_value','is_active')
admin.site.register(models.Variation,variationAdmin)
admin.site.register(models.Customer)
admin.site.register(models.Order)
admin.site.register(models.OrderProduct)
admin.site.register(models.Payment)
admin.site.register(models.ReviewRating)