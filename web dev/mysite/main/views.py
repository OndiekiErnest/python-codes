from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import ToDoList
from .forms import CreateNewList

# Create your views here.


def index(request):
    """ render home view """
    return render(request, "main/home.html", {})


def get(request, list_id: int):
    """ query the database using id while accepting edits """
    lst = ToDoList.objects.get(id=list_id)

    if lst in request.user.todolist.all():
        # print("query RESPONSE:", request.POST)
        if request.method == "POST":
            if request.POST.get("save"):
                for item in lst.item_set.all():
                    if request.POST.get(f"c{item.id}") == "clicked":
                        item.complete = True
                    else:
                        item.complete = False
                    item.save()
            elif request.POST.get("newItem"):
                txt = request.POST.get("new")
                if len(txt) > 3:
                    lst.item_set.create(text=txt, complete=False)
                else:
                    print("INVALID ITEM!")

        return render(request, "main/query.html", {"ls": lst})

    return render(request, "main/todolists.html", {})


def create(request):
    """ create new todo list and save it to the database, then redirect """
    # print("create RESPONSE:", request.POST)
    if request.method == "POST":
        form = CreateNewList(request.POST)

        if form.is_valid():
            n = form.cleaned_data["name"]
            t = ToDoList(name=n)
            t.save()
            request.user.todolist.add(t)

        return HttpResponseRedirect(f"/{t.id}")

    else:
        form = CreateNewList()
    return render(request, "main/create.html", {"form": form})


def todolists(request):
    return render(request, "main/todolists.html", {})
