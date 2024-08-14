# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from users.models import CustomUser, Profile
#
#
# class CustomUserAdmin(UserAdmin):
#
#     model = CustomUser
#     list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
#     list_filter = ('is_staff', 'is_active')
#     fieldsets = (
#         (None, {'fields': ('email', 'password')}),
#         ('Personal Info', {'fields': ('first_name', 'last_name')}),
#         ('Permissions', {'fields': ('is_staff', 'is_active')}),
#     )
#
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_active'),
#         }),
#     )
#     search_fields = ('email',)
#     ordering = ('email',)
#
# class ProfileAdmin(admin.ModelAdmin):
#     model = Profile
#     list_display = ('phone_number', 'date_of_birth', 'gender', 'last_updated')
#
#
# admin.site.register(Profile, ProfileAdmin)
# admin.site.register(CustomUser, CustomUserAdmin)
