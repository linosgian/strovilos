from django import forms
from .models import Posts, UpImages
from tinymce.widgets import TinyMCE
from django.contrib.auth.models import User

class PostsForm(forms.ModelForm):
	""" Add/Change Post form. """
	text = forms.CharField(widget=TinyMCE(), label='Κείμενο')
	# The id change on this form field is used to assist the "thumbnails.js" script
	class Meta:
		model = Posts
		exclude = ['viewcount']
	# A script to dynamically change the thumbnails in Posts' change form using Ajax and JQuery
	class Media:
		js=('main/assets/js/thumbnails.js',)

	def clean(self):
		""" This is used to output errors
		only if the post is going to be
		published.
		"""
		super(PostsForm, self).clean()
		status = self.cleaned_data.get('status')
		text = self.cleaned_data.get('text')
		title = self.cleaned_data.get('title')
		image = self.cleaned_data.get('image')
		author = self.cleaned_data.get('author')
		category = self.cleaned_data.get('category')
		if status == 'p':
			if not text:
				self.add_error('text', 'Βάλε Κείμενο Φίλε')
			if not title:
				self.add_error('title', 'Βάλε Τίτλο Φίλε')
			if not image:
				self.add_error('image', 'Βάλε Φωτογραφία Φίλε')
			if not author:
				self.add_error('author', 'Βάλε Αρθρογράφο Φίλε')
			if not category:
				self.add_error('category', 'Βάλε Κατηγορία Φίλε')
		return self.cleaned_data

class ContactForm(forms.Form):
	""" Index's contact-us form. """

	# Overriding the error_messages
	greek_errors_mail = {
		'required' : 'Αυτό το πεδίο είναι απαραίτητο',
		'invalid'  : 'Μη αποδεκτό email',
	}
	greek_errors = {
		'required' : 'Αυτό το πεδίο είναι απαραίτητο',
	}
	name = forms.CharField(required=True, error_messages=greek_errors)
	subject = forms.CharField(required=True, error_messages=greek_errors)
	email = forms.EmailField(required=True, error_messages=greek_errors_mail)
	message = forms.CharField(
		max_length = 500,
		required = True,
		error_messages = greek_errors,
		)
	# This is supposed to be empty.
	pot = forms.CharField(required=False)

