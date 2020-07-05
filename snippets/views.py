from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from .models import Code, Like
from .mailhelp import sendEmail

def home(request):
	a = Code.objects.order_by('-pub_date')
	context = {"codes_list": a}
	return render(request, 'snippets/home.html', context)


#manages infinite scrolling
def samplereq(request, start):
	articles = Code.objects.order_by('-pub_date').filter(id__lt = start)[:6]
	temp = []
	for yo in articles:
		temp.append((yo.id, yo.pub_date,yo.author, yo.title, yo.code_snippet))

	return JsonResponse({'articles':temp})



def register(request):
	if(request.user.is_authenticated):
		return HttpResponseRedirect('/snippets')
	else:
		context = {'errors': ''}
		return render(request, 'snippets/register.html', context)

def redirectToHome(request):
	return HttpResponseRedirect('/snippets')

def redirectToCode(request, codeid):
	return HttpResponseRedirect('/snippets/' + str(codeid))


def createuser(request):
	if(request.method == "POST"):
		if(request.user.is_authenticated):
		
			return HttpResponseRedirect('/snippets')
		else:
			email = request.POST["email"]
			username = request.POST["username"]
			if User.objects.filter(username=username).exists():
				return render(request, 'snippets/errorPage.html', {'errorMessage': 'A user with this username is already registered with us'})



			password = request.POST["password"]
			user = User.objects.create_user(username, email, password)
			user.save()


			new_user = authenticate(username=username, password=password)
			login(request, new_user)

			return HttpResponseRedirect('/snippets')
	else:
		return HttpResponse("Po ra kuyya.")

def viewCode(request, code_id):
	
	if(Code.objects.filter(id=code_id)):
		a = Code.objects.get(pk=code_id)
		
		s = ""
		like_bool = 0
		if(True):
			context = {"code_object": a}
			if(request.user.is_authenticated):

				is_liked = Like.objects.filter(code=a, liked_by=request.user.get_username)
				is_liked = Like.objects.filter(code=a)
				for like in is_liked:
					if(like.liked_by == request.user.username):
						like_bool = 1
						break
				
				# if(is_liked):
				# 	like_bool = 1
			context["like_bool"] = like_bool
					
				

			return render(request, 'snippets/codeView.html', context)
		else:
			return None
	else:
		context = {"errorMessage" : "Invalid article code 😢"}
		return render(request, 'snippets/errorPage.html', context)

def newCodeSnippet(request):
	if(request.user.is_authenticated):
		context = {}
		return render(request, 'snippets/newCodeSnippet.html', context)
	else:
		context = {"errorMessage" : "Please login to add new code."}
		return render(request, 'snippets/errorPage.html', context)

def submitNewCodeSnippet(request):
	c = Code(title=request.POST['title'], author = request.POST['username'], code_snippet = request.POST["code_snippet"], pub_date = timezone.now())
	c.save()
	context = {"code_object":c}
	return render(request, 'snippets/success.html', context)

def showProfile(request, username):

	articles = Code.objects.filter(author= username)
	context = {'articles':articles, 'username':username, 'no_of_articles':len(articles)}

	return render(request, 'snippets/showProfile.html', context)

def search(request):

	search_term = request.POST['search_term'].lower()

	all_articles = Code.objects.order_by('-pub_date')
	results = []

	for article in all_articles:
		if((search_term in article.code_snippet.lower()) or (search_term in article.title.lower()) or (search_term in article.author.lower())):
			results.append(article)

	context = {'results':results}

	return render(request, 'snippets/searchResults.html', context)


def likePost(request):
	if(request.method == "POST"):
		username = request.POST["username"]
		codeid = request.POST["codeid"]
		c = Code.objects.get(pk = codeid)
		likeobject = Like.objects.filter(code=c, liked_by=username)
		if(likeobject):
			likeobject.delete()
			c.likes = int(c.likes)-1
			c.save()
			
			return HttpResponse("unliked")
		else:
			like = Like(code= c, liked_by = username)
			like.save()
			c.likes = int(c.likes) + 1
			c.save()
			return HttpResponse("Liked")

	else:
		return HttpResponse("get request");
