from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.db.models import Q
from django.db import transaction, IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist,MultipleObjectsReturned
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.http import require_safe
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.conf import settings as django_settings
from django.db.models import F
from django.core.mail import EmailMultiAlternatives

from .forms import ContactForm
from .models import *
from .utils import get_final_context
from strovilos import settings
import logging, os, json

logger = logging.getLogger('main')
#####################################################
#################### Main Views #####################
#####################################################

def index(request, category_id=None):
	""" This covers the index page and
	error/success message output when
	submiting the email form 
	"""
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		if category_id:
			posts = Posts.objects.filter(category=category_id).exclude(status='d').order_by('-viewcount')
			main_title = Category.objects.get(pk=category_id)
		else:
			posts = Posts.objects.exclude(Q(status='d')).order_by('-viewcount')
			main_title = "Στρόβιλος"
		posts_paginated = paginate_posts(request, posts)
		cntx = {
			'posts_paginated'	: posts_paginated,
			'main_title'		: main_title,
		}
		return render(request, 'main/async.html', cntx)
	form_errors = None
	if request.method == 'POST':
		form = ContactForm(data=request.POST)
		if form.is_valid():
			# This is a honeypot field for spambots.
			# So if it's not empty, some spambot filled it in.	
			honeypot = form.cleaned_data['pot']
			if honeypot:
				logger.warn("Possible SpamBot Detected")
				return HttpResponseRedirect('/')			
			msg = EmailMultiAlternatives(
				subject=form.cleaned_data['subject'],
				body=form.cleaned_data['message'],
				from_email=form.cleaned_data['name'] + '<' + django_settings.DEFAULT_FROM_EMAIL + '>',
				to=[django_settings.DEFAULT_TO_EMAIL],
				headers={'Reply-To': form.cleaned_data['email']},
			)
			msg.send()
			messages.success(request, 'Επιτυχής Αποστολή. Σας Ευχαριστούμε.')
			return HttpResponseRedirect('/')
		else:
			form_errors = form.errors
	try:
		quote = BodyText.objects.get(active=True)
	except ObjectDoesNotExist:
		quote = None
	if category_id is not None:
		latest_posts = list(Posts.objects.filter(category=category_id).exclude(status='d')[:5])
		posts = Posts.objects.filter(category=category_id).exclude(status='d').order_by('-viewcount')
		try:
			main_title = Category.objects.get(pk=category_id)
		except ObjectDoesNotExist:
			raise Http404('Δεν υπάρχει αυτή η κατηγορία.')			
		if not posts:
			raise Http404('Δεν υπάρχουν δημοσιεύσεις σε αυτή την κατηγορία.')
	else:
		latest_posts = list(Posts.objects.exclude(status='d')[:5])
		main_title = "Στρόβιλος"
		posts = Posts.objects.exclude(Q(status='d')).order_by('-viewcount')
	
	posts_paginated = paginate_posts(request, posts)

	view_context = {
		'main_title'			: main_title,
		'latest_posts'			: latest_posts,
		'posts_paginated'		: posts_paginated,
		'quote'					: quote,
	}
	final_context = get_final_context(view_context, form_errors)
	return render(request, 'main/index.html',  final_context)

def articles(request, post_id):
	""" Request articles by id """

	main_post = get_object_or_404(Posts ,pk=post_id)
	if main_post.status == 'd' and not request.user.is_staff:
		return HttpResponseRedirect('/')
	latest_posts = Posts.objects.exclude(Q(pk=main_post.id) | Q(status='d'))[:4]
	if main_post.pub_date is not None:
		next_post = Posts.objects.filter(
			category=main_post.category, status='p'
		).filter(
			Q(pub_date__gt=main_post.pub_date) |
			Q(pub_date=main_post.pub_date, pk__gt=main_post.pk)
		).order_by('pub_date', 'pk').first()
		previous_post = Posts.objects.filter(
			category=main_post.category, status='p'
		).filter(
			Q(pub_date__lt=main_post.pub_date) |
			Q(pub_date=main_post.pub_date, pk__lt=main_post.pk)
		).order_by('-pub_date', '-pk').first()
	else:
		next_post = None
		previous_post = None
	
	view_context = {
		'main_post'  	: main_post,
		'latest_posts' 	: latest_posts,
		'next_post'		: next_post,
		'previous_post'	: previous_post,
	}

	final_context = get_final_context(view_context)
	if main_post.status != 'd':
		Posts.objects.filter(pk=post_id).update(viewcount=F('viewcount') + 1)
	return render(request, 'main/left-sidebar.html', final_context)

def authors(request, author_id):
	""" Request articles by author_id """

	author = User.objects.get(pk=author_id)
	main_title = "Αρθρογράφος: "+ author.first_name + " " + author.last_name
	
	posts = Posts.objects.filter(author__id=author_id).exclude(status='d').order_by('-viewcount')
	posts_paginated = paginate_posts(request, posts)
	
	if request.headers.get('x-requested-with') == 'XMLHttpRequest':
		cntx = {
			'posts_paginated'	: posts_paginated,
			'main_title'		: main_title,
		}
		return render(request, 'main/async.html', cntx)
	
	latest_posts = list(Posts.objects.filter(author__id=author_id).exclude(status='d')[:5])
	try:
		quote = BodyText.objects.get(active=True)
	except ObjectDoesNotExist:
		quote = None

	view_context = {
		'posts_paginated'	: posts_paginated,
		'latest_posts' 		: latest_posts,
		'main_title'		: main_title,
		'quote'				: quote,
	}

	final_context = get_final_context(view_context)
	return render(request, 'main/secret_articles.html', final_context)

@user_passes_test(lambda u:u.is_staff, login_url='/admin/login/?next=/admin/')
def secret_articles(request):
	""" This is used to display
	unpublished articles only to
	staff users.
	"""
	posts = Posts.objects.filter(status='d')
	main_title = "Αδημοσίευτα Άρθρα"

	posts_paginated = paginate_posts(request, posts)

	view_context = {
		'posts_paginated'	: posts_paginated,
		'main_title'		: main_title,
	}
	 
	final_context = get_final_context(view_context)
	return render(request, 'main/secret_articles.html', final_context)

def about(request):
	latest_posts = Posts.objects.exclude(status='d')[:3]
	bios = Bios.objects.all()
	view_context = {
		'latest_posts' 	: latest_posts,
		'bios'			: bios,
	}
	 
	final_context = get_final_context(view_context)
	return render(request, 'main/about.html', final_context)

# Makes sure we only allow GET and HEAD methods
@require_safe
def search(request):
	try:
		quote = BodyText.objects.get(active=True)
	except ObjectDoesNotExist:
		quote = None
	querystring = request.GET.get('search')
	posts = Posts.objects.exclude(status='d').filter(title__icontains=querystring)
	latest_posts = list(Posts.objects.exclude(status='d')[:5])

	posts_paginated = paginate_posts(request, posts)

	main_title = "Αποτελέσματα για: \"" + querystring +"\""

	view_context = {
		'main_title'			: main_title,
		'latest_posts'			: latest_posts,
		'posts_paginated'		: posts_paginated,
		'quote'					: quote,
	}
	 
	final_context = get_final_context(view_context)
	return render(request, 'main/secret_articles.html',  final_context)

#####################################################
################# Additional Views ##################
#####################################################

@user_passes_test(lambda u:u.is_staff, login_url='/admin/login/?next=/admin/')
def activate(request):
	""" This activates a quote and disables the previously active """
	quote_id = request.GET.get('q')
	quote = BodyText.objects.get(pk=quote_id)
	quote.active = True
	quote.save()
	return HttpResponseRedirect('/admin/main/bodytext/')


def get_title(request):
	"""This is used to dynamically change
	the thumbnails on Posts' change form,
	using ajax requests.
	"""
	image_title = request.GET['title']
	try:
		image = UpImages.objects.get(image_title=image_title)
		if not os.path.exists(image.image.path):
			return HttpResponse(status=404)
	except ObjectDoesNotExist:
		return HttpResponse(status=404)		
	except MultipleObjectsReturned:
		return HttpResponse(status=410)
	return HttpResponse(image.image.url)

def update_cvs(request):
	if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		json_data = json.loads(body_unicode)
		keys = list(json_data.keys())
		try:
			with transaction.atomic():
				bios = Bios.objects.filter(position__in=keys)
				for bio in bios:
					bio.position = json_data[str(bio.position)]
					bio.save()
					logger.warn("updated")
		except IntegrityError:
			transaction.rollback()
	return HttpResponse()



#####################################################
################# Views' Functions ##################
#####################################################

@csrf_exempt
@login_required
def tinymce_upload_image(request):
	if request.method != 'POST' or not request.user.is_staff:
		return JsonResponse({'error': 'Forbidden'}, status=403)
	file = request.FILES.get('file')
	if not file:
		return JsonResponse({'error': 'No file'}, status=400)
	path = default_storage.save('images/tinymce/' + file.name, file)
	return JsonResponse({'location': django_settings.MEDIA_URL + path})

def paginate_posts(request, posts):
	paginator = Paginator(posts, settings.POSTS_PER_PAGE)
	page = request.GET.get('page')
	try:
		posts_paginated = paginator.page(page)
	except PageNotAnInteger:
		posts_paginated = paginator.page(1)
	except EmptyPage:
		posts_paginated = paginator.page(paginator.num_pages)
	return posts_paginated