from django.shortcuts import render

# Create your views here.
def render_react(request):
    return render(request, template_name="index.html")
