import json

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import auth
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

merge_info = []
gold_info = []
pred_info = []
gold_label = {}
pred_label = {}
gold_pie_legend_data = []
gold_pie_series_data = []
pred_pie_legend_data = []
pred_pie_series_data = []
bar_dataset_source = []


from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage, InvalidPage

def detail(request):
    global merge_info
    paginator = Paginator(merge_info, 1)

    if request.method == "GET":
        # 获取 url 后面的 page 参数的值, 首页不显示 page 参数, 默认值是 1
        page = request.GET.get('page')
        try:
            merges = paginator.page(page)
        # todo: 注意捕获异常
        except PageNotAnInteger:
            # 如果请求的页数不是整数, 返回第一页。
            merges = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            merges = paginator.page(paginator.num_pages)
        except InvalidPage:
            # 如果请求的页数不存在, 重定向页面
            return HttpResponse('找不到页面的内容')

    return render(request, "services/detail.html", {'merges': merges})


@csrf_exempt
def index(request):
    global gold_pie_legend_data
    global gold_pie_series_data
    global pred_pie_legend_data
    global pred_pie_series_data
    global bar_dataset_source
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            request.session['user'] = username  # 将session信息记录到浏览器

            result = {
                "gold_pie_legend_data": gold_pie_legend_data,
                "gold_pie_series_data": gold_pie_series_data,
                "pred_pie_legend_data": pred_pie_legend_data,
                "pred_pie_series_data": pred_pie_series_data,
                "bar_dataset_source": bar_dataset_source
            }
            return render(request, "services/index.html", {"result": json.dumps(result)})
        else:
            return HttpResponseRedirect(reverse('authorize:index'))
    else:
        result = {
            "gold_pie_legend_data": gold_pie_legend_data,
            "gold_pie_series_data": gold_pie_series_data,
            "pred_pie_legend_data": pred_pie_legend_data,
            "pred_pie_series_data": pred_pie_series_data,
            "bar_dataset_source": bar_dataset_source
        }
        return render(request, "services/index.html", {"result": json.dumps(result)})


# @csrf_exempt
# def detail(request):
#     global merge_info
#     return render(request, "services/detail.html", {"result": json.dumps(merge_info)})


@csrf_exempt
def upload(request):
    global merge_info
    global gold_label
    global pred_label
    global gold_info
    global pred_info
    global gold_pie_legend_data
    global gold_pie_series_data
    global pred_pie_legend_data
    global pred_pie_series_data
    global bar_dataset_source
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

        gold_pie_legend_data = []
        gold_pie_series_data = []
        for key in gold_label:
            gold_pie_legend_data.append(key)
            gold_pie_series_data.append({"name": key, "value": gold_label[key]})
            if key in pred_label:
                bar_dataset_source.append([key, gold_label[key], pred_label[key]])
            else:
                bar_dataset_source.append([key, gold_label[key], 0])

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

        pred_pie_legend_data = []
        pred_pie_series_data = []
        for key in pred_label:
            pred_pie_legend_data.append(key)
            pred_pie_series_data.append({"name": key, "value": pred_label[key]})
            if key in gold_label:
                bar_dataset_source.append([key, gold_label[key], pred_label[key]])
            else:
                bar_dataset_source.append([key, 0, pred_label[key]])

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

    result = {
        "gold_pie_legend_data": gold_pie_legend_data,
        "gold_pie_series_data": gold_pie_series_data,
        "pred_pie_legend_data": pred_pie_legend_data,
        "pred_pie_series_data": pred_pie_series_data,
        "bar_dataset_source": bar_dataset_source
    }
    return JsonResponse(result)
