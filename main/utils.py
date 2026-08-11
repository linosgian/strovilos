from .models import UpImages, BodyText, Category
from django.core.cache import cache as redis_cache

def get_final_context(context, form_errors=None):
	"""
	This is used to obtain the basic, shared by all views, context.
	In-Memory cache is being used to quickly access this context.
	"""
	logo = redis_cache.get('logo')
	if not logo:
		try:
			logo = UpImages.objects.get(image_title="Logo")
			redis_cache.set('logo', logo)
		except UpImages.DoesNotExist:
			logo = None

	categories = redis_cache.get('categories')
	if not categories:
		categories = Category.objects.all()
		redis_cache.set('categories', categories, timeout=600)
	context['logo'] = logo
	context['categories'] = categories
	if form_errors:
		context['form_errors']=form_errors
	return context

def truncate(content, length=100, suffix='...'):
    if len(content) <= length:
        return content
    else:
        return ' '.join(content[:length+1].split(' ')[0:-1]) + suffix

