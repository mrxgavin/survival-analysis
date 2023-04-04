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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)