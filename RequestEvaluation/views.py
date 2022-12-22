from django.shortcuts import render, redirect
from .models import EvaluateRequest
from django.contrib import messages


# Create your views here.
def home(request):
    if request.user.is_superuser:
        evaluation_requests = EvaluateRequest.objects.all()
        dict_obj = {'evaluation_requests': evaluation_requests}
        return render(request, 'authentication/index.html', dict_obj)
    return render(request, 'authentication/index.html')


def create_request(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            text = request.POST.get('text')
            medium = request.POST.get('medium')
            image = request.FILES['image']

            extension = str(image).split('.')[-1].lower()
            allowed_extensions = ['jpg', 'jpeg', 'png', 'gif']
            if extension not in allowed_extensions:
                messages.error(request, "Only Image of type jpg, png, and gif is allowed")
                return render(request, 'RequestEvaluation/create_request.html')

            EvaluateRequest.objects.create(text=text, contact_via=medium, image=image, author=request.user)
            messages.success(request, "your request has been submitted")
            return redirect('home')
        return render(request, 'RequestEvaluation/create_request.html')

    return render(request, 'authentication/index.html')