# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import UserCreationForm,UserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form= UserCreationForm
    form= UserChangeForm
    model= User
    list_display=['email','username','first_name','last_name','is_staff']
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Other info', {
         'fields': ('first_name', 'last_name')}),
        ('Permissions', {
         'fields': ( 'is_staff', )}),
    )
class CommentInline(admin.StackedInline):
    model=Comment
class BidInline(admin.StackedInline):
    model=Bid
class AuctionAdmin(admin.ModelAdmin):
    inlines=[
        CommentInline,
        BidInline,
    ]


admin.site.register(User,CustomUserAdmin)
admin.site.register(AuctionItem,AuctionAdmin)
admin.site.register(WatchList)
admin.site.register(Bid)
admin.site.register(Winner)
admin.site.register(Comment)
