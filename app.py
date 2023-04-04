from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from lifelines import KaplanMeierFitter, CoxPHFitter
import io
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # 从表单获取用户输入
    group1_conditions = {
        'ERBB2': [int(request.form['group1_erbb2_min']), int(request.form['group1_erbb2_max'])],
        'PIK3CA': [int(request.form['group1_pik3ca_min']), int(request.form['group1_pik3ca_max'])]
    }
    group2_conditions = {
        'ERBB2': [int(request.form['group2_erbb2_min']), int(request.form['group2_erbb2_max'])],
        'PIK3CA': [int(request.form['group2_pik3ca_min']), int(request.form['group2_pik3ca_max'])]
    }

    # 在这里将您的数据分析和可视化代码放入一个函数，并将group1_conditions和group2_conditions作为参数传递
    img_base64, summary = analyze_data(group1_conditions, group2_conditions)

    return render_template('results.html', img_base64=img_base64, summary=summary)

def analyze_data(group1_conditions, group2_conditions):
    dataset_name = 'brca_tcga_pub2015'
    data = pd.read_csv(dataset_name + ".csv")

    # filter patients
    group1 = filter_patients(data, group1_conditions)
    group2 = filter_patients(data, group2_conditions)

    # output
    group1_count = len(group1)
    group2_count = len(group2)

    # Kaplan-Meier
    kmf = KaplanMeierFitter()
    kmf.fit(group1['OS_MONTHS'], group1['OS_STATUS'], label="Group 1")
    ax = kmf.plot(show_censors=True)
    kmf.fit(group2['OS_MONTHS'], group2['OS_STATUS'], label="Group 2")
    kmf.plot(show_censors=True, ax=ax)

    plt.xlabel("Survival Time (Months)")
    plt.ylabel("Survival Probability")
    plt.title("Kaplan-Meier Survival Curve")

    # 将图像保存到字节缓冲区
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    # 将图像转换为Base64编码的字符串
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # Cox Proportional Hazards
    cph = CoxPHFitter()
    combined = pd.concat([group1, group2])
    combined['group'] = [1] * len(group1) + [2] * len(group2)
    cph.fit(combined[['OS_MONTHS', 'OS_STATUS', 'group']], duration_col='OS_MONTHS', event_col='OS_STATUS')
    summary_str = cph.summary.to_string()

    # 获取摘要
    summary = f"Group 1: {group1_count} patients\nGroup 2: {group2_count} patients\n\nCox Proportional Hazards Summary:\n{summary_str}"

    return img_base64, summary



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)