from html import escape

import requests
from django.http import HttpResponse
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt

from .models import HTMLTag


def home(request):
    table_code = HTMLTag.objects.get(html_tag="table").content
    url = request.build_absolute_uri("")
    code = (
        f"<button hx-get='{url}tag/table?class=table%20table-bordered'> Get </button>"
    )
    gist = f"<button hx-get='{url}gist/c9fd72b8f8a265d8bfcdb4338ffc76fa'> Get Gist </button>"
    tags = HTMLTag.objects.all()
    return render(
        request,
        "home.html",
        {"table_code": table_code, "code": code, "tags": tags, "gist": gist},
    )


def documentation(request):
    # get root url
    url = request.build_absolute_uri(reverse("home"))
    return render(request, "documentation.html", {"url": url})


@csrf_exempt
def tag_name(request, tag_name):
    try:
        fragment = HTMLTag.objects.get(html_tag=tag_name.lower())
    except HTMLTag.DoesNotExist:
        return HttpResponse(
            "We don't have a html tag called "
            + tag_name
            + ". Please try again with a common html tag."
        )
    if request.method == "GET":
        classes = request.GET.get("class", "")
        content = fragment.content
        if classes:
            content = content.replace(">", f' class="{classes}">', 1)
        return HttpResponse(content)
    elif request.method == "POST":
        values = request.POST.values()
        return HttpResponse(
            fragment.content + "You Posted the following values: " + " ".join(values)
        )
    elif request.method == "PUT":
        return HttpResponse("Put Request Received")
    elif request.method == "DELETE":
        return HttpResponse("Delete Request Received")


@csrf_exempt
def tag_name_escaped(request):
    # this to demonstrate in the documentation siste
    try:
        fragment = HTMLTag.objects.get(html_tag=tag_name.lower())
    except HTMLTag.DoesNotExist:
        return HttpResponse(
            escape(
                "We don't have a html tag called "
                + tag_name
                + ". Please try again with a common html tag."
            )
        )
    if request.method == "GET":
        classes = request.GET.get("class", "")
        content = fragment.content
        if classes:
            content = content.replace(">", f' class="{classes}">', 1)
        return HttpResponse(escape(content))
    elif request.method == "POST":
        values = request.POST.values()
        return HttpResponse(
            escape(
                fragment.content
                + "<br> You Posted the following values: "
                + " ".join(values)
            )
        )
    elif request.method == "PUT":
        values = request.PUT.values()
        return HttpResponse(
            escape(
                fragment.content
                + "<br> You Put the following values: "
                + " ".join(values)
            )
        )
    elif request.method == "DELETE":
        return HttpResponse("Delete Request Received")


def github_gist(request, gist_id):
    api_url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(api_url)
    gist_data = response.json()
    html_content = None
    if "files" in gist_data:
        files = gist_data["files"]
        for filename, file_data in files.items():
            if file_data["language"] == "HTML":
                html_content = file_data["content"]
                return HttpResponse(html_content)

    return HttpResponse(
        "No HTML file found in this gist. Please make sure your gist is public, and contains an HTML file. See example here: https://gist.github.com/Jonathan-Adly/c9fd72b8f8a265d8bfcdb4338ffc76fa"
    )
