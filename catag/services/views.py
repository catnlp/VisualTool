import json
import numpy as np
import colorsys

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
gold_pie_legend_data = []
gold_pie_series_data = []
pred_pie_legend_data = []
pred_pie_series_data = []
bar_dataset_source = []
html_texts = []

page = 0
red = '<span style="background:red;">'
blue = '<span style="background:blue;">'
grey = '<span style="background:grey;">'
green = '<span style="background:green;">'
end_span = '</span>'


def _get_colors(num_colors):
    colors = []
    for i in np.arange(0., 360., 360. / num_colors):
        hue = i/360.
        lightness = (50 + np.random.rand() * 10)/100.
        saturation = (90 + np.random.rand() * 10)/100.
        colors.append(colorsys.hls_to_rgb(hue, lightness, saturation))
    return colors


def _get_html_text(text, gold_list, pred_list):
    color_texts = []
    gold_idx = 0
    pred_idx = 0
    while gold_idx < len(gold_list) and \
            pred_idx < len(pred_list):
        gold_start, gold_end, gold_type = gold_list[gold_idx]
        pred_start, pred_end, pred_type = pred_list[pred_idx]
        if gold_start == pred_start and \
                gold_end == pred_end:
            if gold_type == pred_type:
                tmp = green + text[gold_start: gold_end] + end_span
                color_texts.append([gold_start, gold_end, tmp])
            else:
                # html_text += grey + text[gold_start, gold_end] + end_span
                tmp = grey + text[gold_start: gold_end] + end_span
                color_texts.append([gold_start, gold_end, tmp])
            gold_idx += 1
            pred_idx += 1
        elif gold_start < pred_start and gold_end < pred_end and gold_end > pred_start:
            # html_text += red + text[gold_start, pred_start] + end_span
            tmp = red + text[gold_start: pred_start] + end_span
            color_texts.append([gold_start, pred_start, tmp])
            if gold_type == pred_type:
                # html_text += green + text[pred_start, gold_end] + end_span
                tmp = green + text[pred_start: gold_end] + end_span
                color_texts.append([pred_start, gold_end, tmp])
            else:
                # html_text += grey + text[pred_start, gold_end] + end_span
                tmp = grey + text[pred_start: gold_end] + end_span
                color_texts.append([pred_start, gold_end, tmp])
            pred_list[pred_idx][0] = gold_end
            gold_idx += 1
        elif gold_start > pred_start and gold_end > pred_end and gold_start < pred_end:
            # html_text += blue + text[pred_start, gold_start] + end_span
            tmp = blue + text[pred_start: gold_start] + end_span
            color_texts.append([pred_start, gold_start, tmp])
            if gold_type == pred_type:
                # html_text += green + text[gold_start, pred_end] + end_span
                tmp = green + text[gold_start: pred_end] + end_span
                color_texts.append([gold_start, pred_end, tmp])
            else:
                # html_text += grey + text[gold_start, pred_end] + end_span
                tmp = grey + text[gold_start: pred_end] + end_span
                color_texts.append([gold_start, pred_end, tmp])
            gold_list[gold_idx][0] = pred_end
            pred_idx += 1
        elif gold_start >= pred_start and gold_end <= pred_end:
            if gold_start == pred_start:
                if gold_type == pred_type:
                    # html_text += green + text[gold_start, gold_end] + end_span
                    tmp = green + text[gold_start: gold_end] + end_span
                    color_texts.append([gold_start, gold_end, tmp])
                else:
                    # html_text += grey + text[gold_start, gold_end] + end_span
                    tmp = grey + text[gold_start: gold_end] + end_span
                    color_texts.append([gold_start, gold_end, tmp])
                pred_list[pred_idx][0] = gold_end
                gold_idx += 1
            else:
                # html_text += blue + text[pred_start, gold_start] + end_span
                tmp = blue + text[pred_start: gold_start] + end_span
                color_texts.append([pred_start, gold_start, tmp])
                if gold_type == pred_type:
                    # html_text += green + text[gold_start, gold_end] + end_span
                    tmp = green + text[gold_start: gold_end] + end_span
                    color_texts.append([gold_start, gold_end, tmp])
                else:
                    # html_text += grey + text[gold_start, gold_end] + end_span
                    tmp = grey + text[gold_start: gold_end] + end_span
                    color_texts.append([gold_start, gold_end, tmp])
                if gold_end == pred_end:
                    pred_idx += 1
                else:
                    pred_list[pred_idx][0] = gold_end
                gold_idx += 1
        elif gold_start <= pred_start and gold_end >= pred_end:
            if gold_start == pred_start:
                if gold_type == pred_type:
                    # html_text += green + text[pred_start, pred_end] + end_span
                    tmp = green + text[pred_start: pred_end] + end_span
                    color_texts.append([pred_start, pred_end, tmp])
                else:
                    # html_text += grey + text[pred_start, pred_end] + end_span
                    tmp = grey + text[pred_start: pred_end] + end_span
                    color_texts.append([pred_start, pred_end, tmp])
                gold_list[gold_idx][0] = pred_end
                pred_idx += 1
            else:
                # html_text += red + text[gold_start, pred_start] + end_span
                tmp = red + text[gold_start: pred_start] + end_span
                color_texts.append([gold_start, pred_start, tmp])
                if gold_type == pred_type:
                    # html_text += green + text[pred_start, pred_end] + end_span
                    tmp = green + text[pred_start: pred_end] + end_span
                    color_texts.append([pred_start, pred_end, tmp])
                else:
                    # html_text += grey + text[pred_start, pred_end] + end_span
                    tmp = grey + text[pred_start: pred_end] + end_span
                    color_texts.append([pred_start, pred_end, tmp])
                if gold_end == pred_end:
                    gold_idx += 1
                else:
                    gold_list[gold_idx][0] = pred_end
                pred_idx += 1
        elif gold_end <= pred_start:
            # html_text += red + text[gold_start, gold_end] + end_span
            tmp = red + text[gold_start: gold_end] + end_span
            color_texts.append([gold_start, gold_end, tmp])
            gold_idx += 1
        elif gold_start >= pred_end:
            # html_text += blue + text[pred_start, pred_end] + end_span
            tmp = blue + text[pred_start: pred_end] + end_span
            color_texts.append([pred_start, pred_end, tmp])
            pred_idx += 1
        else:
            raise RuntimeError("Other situation!")

    while gold_idx < len(gold_list):
        gold_start, gold_end, gold_type = gold_list[gold_idx]
        # html_text += red + text[gold_start, gold_end] + end_span
        tmp = red + text[gold_start: gold_end] + end_span
        color_texts.append([gold_start, gold_end, tmp])
        gold_idx += 1

    while pred_idx < len(pred_list):
        pred_start, pred_end, pred_type = pred_list[pred_idx]
        # html_text += red + text[pred_start, pred_end] + end_span
        tmp = blue + text[pred_start: pred_end] + end_span
        color_texts.append([pred_start, pred_end, tmp])
        pred_idx += 1

    idx = 0
    html_text = ""
    for color_text in color_texts:
        start, end, ctext = color_text
        if idx < start:
            html_text += text[idx: start]
        html_text += ctext
        idx = end
    if idx < len(text):
        html_text += text[idx: len(text)]

    return html_text


@csrf_exempt
def detail(request):
    global page
    html_text = html_texts[page]
    return render(request, "services/detail.html", {"result": json.dumps({"text": html_text, "page": page, "total": len(html_texts)})})


@csrf_exempt
def change(request):
    global page
    if request.method == 'GET':
        page = int(request.GET.get('page'))
        if page < 0:
            page = 0
        if page >= len(merge_info):
            page = len(merge_info) - 1
        html_text = html_texts[page]
        return JsonResponse({"text": html_text, "total": len(html_texts)})


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
    global html_texts
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
        html_texts = []
        if gold_info and pred_info:
            for gold, pred in zip(gold_info, pred_info):
                assert gold["text"] == pred["text"]
                merge_info.append(
                    {
                        "text": gold["text"],
                        "gold": gold["label"],
                        "pred": pred["label"]
                    })
                html_text = _get_html_text(gold["text"],
                                           gold["label"],
                                           pred["label"])
                html_texts.append(html_text)
        elif gold_info:
            for gold in gold_info:
                merge_info.append(
                    {
                        "text": gold["text"],
                        "gold": gold["label"],
                        "pred": []
                    }
                )
                html_text = _get_html_text(gold["text"],
                                           gold["label"],
                                           [])
                html_texts.append(html_text)
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
                html_text = _get_html_text(pred["text"],
                                           [],
                                           pred["label"])
                html_texts.append(html_text)

    result = {
        "gold_pie_legend_data": gold_pie_legend_data,
        "gold_pie_series_data": gold_pie_series_data,
        "pred_pie_legend_data": pred_pie_legend_data,
        "pred_pie_series_data": pred_pie_series_data,
        "bar_dataset_source": bar_dataset_source
    }
    return JsonResponse(result)


if __name__ == "__main__":
    res = _get_colors(4)
    print(res)
    text = "彭小军认为，国内银行现在走的是台湾的发卡模式，先通过跑马圈地再在圈的地里面选择客户，"
    gold = [[0, 3, "name"], [15, 17, "address"]]
    pred = [[0, 3, "name"], [14, 16, "address"]]
    print(_get_html_text(text, gold, pred))
