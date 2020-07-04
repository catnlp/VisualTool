import json

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

merge_info = []
gold_info = []
pred_info = []
gold_label = {}
pred_label = {}


@csrf_exempt
def index(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = auth.authenticate(username=username, password=password)
    if user:
        auth.login(request, user)
        request.session['user'] = username  # 将session信息记录到浏览器
        return render(request, "services/index.html")
    else:
        return HttpResponseRedirect(reverse('authorize:index'))


@csrf_exempt
def upload(request):
    global merge_info
    global gold_label
    global pred_label
    global gold_info
    global pred_info
    gold_file = request.FILES.get('gold_file')
    pred_file = request.FILES.get('pred_file')
    if gold_file:
        gold_info = []
        gold_label = {}
        for line in gold_file:
            line = line.decode('UTF-8').rstrip()
            if not line:
                continue
            line = eval(line)
            gold_info.append(line)
            labels = line['label']
            for label in labels:
                label = label[-1]
                if label not in gold_label:
                    gold_label[label] = 1
                else:
                    gold_label[label] += 1

    if pred_file:
        pred_info = []
        pred_label = {}
        for line in pred_file:
            line = line.decode('UTF-8').rstrip()
            if not line:
                continue
            line = eval(line)
            pred_info.append(line)
            labels = line['label']
            for label in labels:
                label = label[-1]
                if label not in pred_label:
                    pred_label[label] = 1
                else:
                    pred_label[label] += 1

    if gold_file or pred_file:
        merge_info = []
        if gold_info and pred_info:
            for gold, pred in zip(gold_info, pred_info):
                assert gold["text"] == pred["text"]
                merge_info.append(
                    {
                        "text": gold["text"],
                        "gold": gold["label"],
                        "pred": pred["label"]
                    })
        elif gold_info:
            for gold in gold_info:
                merge_info.append(
                    {
                        "text": gold["text"],
                        "gold": gold["label"],
                        "pred": []
                    }
                )
        elif pred_info:
            for pred in pred_info:
                merge_info.append(
                    {
                        {
                            "text": pred["text"],
                            "gold": [],
                            "pred": pred["label"]
                        }
                    }
                )

    return JsonResponse({"gold": gold_label,
                         "pred": pred_label})
