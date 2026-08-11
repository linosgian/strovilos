from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import *
from .forms import PostsForm

import logging
logger = logging.getLogger('main')

admin.site.index_title = ' '

admin.site.register(Category)

class UpImagesModelAdmin(admin.ModelAdmin):
	exclude = ['uploaded_by','image_title', 'upload_date']

	list_display = ('upload_date', 'image_title', 'thumbnail')
	search_fields = ['image_title']

	def save_model(self, request, obj, form, change):
		""" model's save() method does not have access
		to the request so this method allows us to override
		uploaded_by field
		"""
		obj.uploaded_by = request.user
		obj.save()
admin.site.register(UpImages, UpImagesModelAdmin)

class PostsModelAdmin(admin.ModelAdmin):
	actions = ['publish']
	form = PostsForm
	# Which fields to display ( that's only for listview )
	list_display = ('__str__', 'thumbnail', 'category', 'author', 'status', 'viewcount', 'pub_date', 'show_link')
	
	# That also appears when changing the object
	readonly_fields = ('thumbnail',)
	search_fields = ['title']
	
	# Custom action to bulk publish posts 
	def publish(self, request, queryset):
		rows_updated = queryset.update(status='p')
		if rows_updated == 1:
			message_bit = "1  Άρθρο Δημοσιέυτηκε"
		else:
			message_bit = "%s Άρθρα Δημοσιεύτηκαν" % rows_updated
		self.message_user(request, "%s Επιτυχώς" % message_bit)
	publish.short_description = 'Δημοσίευση επιλεγμένων άρθρων'
admin.site.register(Posts, PostsModelAdmin)

admin.site.unregister(User)
class UserModelAdmin(UserAdmin):
	""" Hiding permissions to non-superusers
	And also making first_name and last_name available
	upon creating a new user.
	"""
	dad_fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        # No permissions
        (('Ημερομηνίες'), {'fields': ('last_login', 'date_joined')}),
    )

	# If you are staff hide the superuser record
	def get_queryset(self, request):
		qs = super(UserModelAdmin, self).get_queryset(request)
		if request.user.is_superuser:
			return qs
		return qs.exclude(is_superuser=True)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields' : ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')}
		),
	)
	def change_view(self, request, *args, **kwargs):
        # for non-superuser
		if not request.user.is_superuser:
			try:
				self.fieldsets = self.dad_fieldsets
				response = super(UserModelAdmin, self).change_view(request, *args, **kwargs)
			finally:
				# Reset fieldsets to its original value
				self.fieldsets = UserAdmin.fieldsets
			return response
		else:
			return super(UserModelAdmin, self).change_view(request, *args, **kwargs)
admin.site.register(User,UserModelAdmin)

class BodyTextAdmin(admin.ModelAdmin):
	list_display = ('text', 'author', 'pub_date','active', 'activate')
	exclude = ['pub_date',]
admin.site.register(BodyText, BodyTextAdmin)

class BiosAdmin(admin.ModelAdmin):
	change_list_template = 'main/bios_changelist.html'
	exclude = ['minified_cv']
	list_display = ('author_name', 'position', 'minified_cv',)
admin.site.register(Bios, BiosAdmin)