# -*-coding:utf-8-*-

import random
import string
import os

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from rapidshare_v2.settings import USER_CONTENT_ROOT, MEDIA_ROOT, FILE_PRIVATE, FILE_LINK, FILE_GROUP, FILE_DEFAULT, FILES_PER_DAY
import logging
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import logout_then_login
from rapidshare_v2.models import File, UserGroup, UserGroupAssignation, Downloads
from django.utils.translation import ugettext_lazy as _
from django import forms
from captcha.fields import ReCaptchaField
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User

logger = logging.getLogger('rapidshare.views')
CHAR_SET = string.ascii_uppercase + string.digits
WIDOCZNOSC_PLIKOW = ([('0', 'Domyślny'), ('1', 'Prywatny'), ('2', 'Dla osób z linkiem'), ('3', 'Moi znajomi'), ])

class ContactForm(forms.Form):
	Nazwa = forms.CharField(max_length=100, required=False)
	Opis = forms.CharField(required=False)
	Plik = forms.FileField(required=True)
	Widocznosc = forms.ChoiceField(choices=WIDOCZNOSC_PLIKOW, initial='0', required=True)
	Grupy = forms.ModelMultipleChoiceField(required=False, queryset=UserGroup.objects.all(), widget=FilteredSelectMultiple("verbose name", is_stacked=False, attrs={'rows':'2'}))
	recaptcha_challenge_field = ReCaptchaField(error_messages={'captcha_invalid': _('Captcha nie jest poprawna')})
	
class GroupForm(forms.Form):
	Nazwa = forms.CharField(max_length=100, required=True)
	Opis = forms.CharField(max_length=100, required=True)

def home(request):
	logger.debug('home')
	return render_to_response('index.html', {}, context_instance=RequestContext(request))

def addFile(request):
	max_size = maxSize(request)
	if request.method == 'POST':
		logger.debug('Addind file')
		
		
		form = ContactForm(request.POST, request.FILES)
		if form.is_valid():
			# nazwa = form.cleaned_data['Nazwa']
			opis = form.cleaned_data['Opis']
			widocznosc = form.cleaned_data['Widocznosc']
			plik = request.FILES['Plik']
			# groups = request.cleaned_data['Grupy']
			
			if not canUpload(request, plik):
				return render_to_response('error.html', {'msg':'Twoje konto nie pozwala na wysłanie tego pliku'}, context_instance=RequestContext(request))
			
			if(request.user.is_authenticated()):
				user_file = File(owner=request.user, name=plik._get_name(), despription=opis, file=plik, code=getFileCode(), visibility=widocznosc)
				user_file.save()
				user_file.groups = form.cleaned_data['Grupy']
				user_file.save()
			else:
				user_ip = get_client_ip(request)
				user_files = File.objects.filter(ip=user_ip)
				if len(user_files) >= 10:
					return render_to_response('error.html', {'msg':'Nie zalogowany, max 10'}, context_instance=RequestContext(request))
				user_file = File(ip=user_ip, name=plik._get_name(), despription="", file=plik, code=getFileCode(), visibility=FILE_DEFAULT)
				user_file.save()
			return HttpResponseRedirect('/pliki')
	else:
		form = ContactForm()
	return render_to_response('addFile.html', {'form': form,'maxSize':max_size}, context_instance=RequestContext(request))

def maxSize(request):
	MB = 1024 * 1024
	if(request.user.is_authenticated()):
		if request.user.has_perm('each_up_to_100'):
			return 100*MB
		elif request.user.has_perm('each_up_to_25'):
			return 25*MB
		elif request.user.has_perm('each_up_to_10'):
			return 10*MB
		else: 
			return 1*MB
	else:
		return 1*MB
		
def canUpload(request, plik):
	MB = 1024 * 1024
	if(request.user.is_authenticated()):
		if request.user.has_perm('each_up_to_100'):
			if plik.size < 100 * MB:
				return True 
		elif request.user.has_perm('each_up_to_25'):
			if plik.size < 25 * MB:
				return True 
		elif request.user.has_perm('each_up_to_10'):
			if plik.size < 10 * MB:
				return True 	
		elif plik.size > MB:
			return False
		else: 
			return True
	else:
		if plik.size > MB:
			return False
		else: 
			return True
		

def getFileCode():
	return ''.join(random.sample(CHAR_SET, 9))

def error(request):
	pass

def delete(request, fileCode):
	try:
		userFile = File.objects.get(code=fileCode)
		os.remove(os.path.join(MEDIA_ROOT, userFile.file.name))
		userFile.delete()
		msg = "Plik został usunięty"
	except File.DoesNotExist:
		msg = "Brak pliku na serwerze"
	return render_to_response('delete.html', {'msg':msg}, context_instance=RequestContext(request))

def download(request, fileCode):
	user = request.user
	ip = get_client_ip(request)
	try:
		userFile = File.objects.get(code=fileCode)
		if request.user.is_anonymous():
			user = None
			if userFile.visibility == FILE_LINK or userFile.visibility == FILE_DEFAULT :
				downloads = Downloads.objects.filter(ip=ip)
				if len(downloads) > FILES_PER_DAY:
					return render_to_response('error.html', {'msg':'Limit ściągnięć przekroczony'}, context_instance=RequestContext(request))
			else:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
		else:
			ip = None
				
		if userFile.visibility == FILE_GROUP and userFile.owner != request.user:
			uga = UserGroupAssignation.objects.filter(group__in=userFile.groups.all()).filter(owner=request.user)
			if not uga:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
			else:
				pass
		if userFile.visibility == FILE_LINK or userFile.visibility == FILE_DEFAULT:
			pass  # jest ok
		if userFile.visibility == FILE_PRIVATE:
			if userFile.owner != request.user:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
	except File.DoesNotExist:
		return render_to_response('error.html', {'msg':''}, context_instance=RequestContext(request))
	
	download = Downloads(user=user, ip=ip, file=userFile)
	download.save()
	return HttpResponseRedirect('/files/'+userFile.file.name)
	
def more(request, fileCode):
	try:
		userFile = File.objects.get(code=fileCode)
		if request.user.is_anonymous():
			if userFile.visibility == FILE_LINK:
				pass  # jest ok
			else:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
			
		if userFile.visibility == FILE_GROUP and userFile.owner != request.user:
			uga = UserGroupAssignation.objects.filter(group__in=userFile.groups.all()).filter(owner=request.user)
			if not uga:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
			else:
				pass
		if userFile.visibility == FILE_LINK:
			pass  # jest ok
		if userFile.visibility == FILE_PRIVATE:
			if userFile.owner != request.user:
				return render_to_response('error.html', {'msg':'nie ma dla ciebie pliku'}, context_instance=RequestContext(request))
	except File.DoesNotExist:
		return render_to_response('error.html', {'msg':''}, context_instance=RequestContext(request))
	return render_to_response('more.html', {'userFile':userFile}, context_instance=RequestContext(request))

def handle_uploaded_file(f, path=''):
	filename = f._get_name()
	with open('%s/%s' % (USER_CONTENT_ROOT, str(path) + str(filename)), 'wb+') as destination:
		for chunk in f.chunks():
			destination.write(chunk)

def packages(request):
	return render_to_response('packages.html', {}, context_instance=RequestContext(request))

def userFiles(request):
	if(request.user.is_authenticated()):
		user_files = File.objects.filter(owner=request.user)
	else:
		user_ip = get_client_ip(request)
		user_files = File.objects.filter(ip=user_ip)
		
	return render_to_response('userFiles.html', {'userFiles':user_files}, context_instance=RequestContext(request))

def myGroups(request):
	if(request.user.is_authenticated()):
		userGroups = UserGroup.objects.filter(owner=request.user)
	else:
		return HttpResponseRedirect('/')
		
	if request.method == 'POST':
		form = GroupForm(request.POST, request.FILES)
		if form.is_valid():
			nazwa = form.cleaned_data['Nazwa']
			opis = form.cleaned_data['Opis']
			
			userGroup = UserGroup(owner=request.user, name=nazwa, description=opis)
			userGroup.save()
	else:
		form = GroupForm()
		
	return render_to_response('myGroups.html', {'userGroups':userGroups, 'form': form}, context_instance=RequestContext(request))

def inGroup(request, groupId):
	group = UserGroup.objects.get(id=groupId)
	uga = UserGroupAssignation.objects.filter(group=group)
	users = User.objects.all()
	userList = list(users)
	for user in userList:
		for user2 in uga:
			if user == user2.owner:
				try:
					userList.remove(user)
				except:
					pass
	return render_to_response('inGroup.html', {'inGroup':uga, 'users':userList, 'groupId':groupId}, context_instance=RequestContext(request))

def addToGroup(request, groupId, userId):
	user = User.objects.get(id=userId)
	group = UserGroup.objects.get(id=groupId)
	uga = UserGroupAssignation(group=group, owner=user)
	uga.save()
	uga = UserGroupAssignation.objects.filter(group=group)
	users = User.objects.all()
	userList = list(users)
	for user in userList:
		for user2 in uga:
			if user == user2.owner:
				try:
					userList.remove(user)
				except:
					pass
	msg = "Użytkonwik został dodany do grupy"
	return render_to_response('inGroup.html', {'inGroup':uga, 'msg':msg, 'users':userList, 'groupId':groupId}, context_instance=RequestContext(request))


def deleteFromGroup(request, groupId, userId):
	
	group = UserGroup.objects.get(id=groupId)
	user = User.objects.get(id=userId)
	uga = UserGroupAssignation.objects.filter(group=group).filter(owner=user).delete()
	uga = UserGroupAssignation.objects.filter(group=group)
	users = User.objects.all()
	userList = list(users)
	for user in userList:
		for user2 in uga:
			if user == user2.owner:
				try:
					userList.remove(user)
				except:
					pass
	msg = "Użytkonwik został usunięty z grupy"
	return render_to_response('inGroup.html', {'inGroup':uga, 'msg':msg, 'users':userList, 'groupId':groupId}, context_instance=RequestContext(request))


def deleteMyGroup(request, groupId):
	try:
		group = UserGroup.objects.get(id=groupId)
		group.delete()
		msg = "Grupa została usunięty"
		return HttpResponseRedirect('/grupy')
	except File.DoesNotExist:
		msg = "Brak grupy na serwerze"
	return render_to_response('delete.html', {'msg':msg}, context_instance=RequestContext(request))

			
def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip
			
@login_required(login_url='/logowanie')
def logout(request):
	logger.debug('user private_file perm: ')
	logger.debug(request.user.has_perm("private_file"))
	return logout_then_login(request, login_url='/')

	# return logout_then_login(request, login_url='/')
def loginUser(request, next_page=None):
	if request.user.is_authenticated():
		return HttpResponseRedirect('/profil')
	if request.method == 'POST':
		logger.debug('logowanie 1')
		username = request.POST['login']
		password = request.POST['pass']
		user = authenticate(username=username, password=password)
		if user is not None:
			logger.debug('user ' + username + ' jest ok')
			login(request, user)
			logger.debug('logowanie ok')
			if next_page is None:
				return HttpResponseRedirect('/profil')
			else:
				return HttpResponseRedirect(next_page or request.path)
		else:
			logger.debug('logowanie nie')
			return HttpResponseRedirect('/logowanie')
	else:
		return render_to_response('login.html', {}, context_instance=RequestContext(request))

@login_required(login_url='/logowanie')
def profil(request):
	return render_to_response('profil.html', {}, context_instance=RequestContext(request))
