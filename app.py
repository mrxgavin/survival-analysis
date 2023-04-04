# app.py
from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from lifelines import KaplanMeierFitter, CoxPHFitter

app = Flask(__name__)

def filter_patients(data, conditions):
    selected = [True] * len(data)
    for gene, percentile_range in conditions.items():
        lower_bound, upper_bound = np.percentile(data[gene], percentile_range)
        selected &= (data[gene] >= lower_bound) & (data[gene] <= upper_bound)
    return data[selected]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get user input from form
        group1_conditions = request.form.get("group1_conditions")
        group2_conditions = request.form.get("group2_conditions")

        # Process user input
        group1_conditions = eval(group1_conditions)
        group2_conditions = eval(group2_conditions)

        # Perform the same analysis as in the original code
        dataset_name = 'brca_tcga_pub2015'
        data = pd.read_csv(dataset_name + ".csv")

        group1 = filter_patients(data, group1_conditions)
        group2 = filter_patients(data, group2_conditions)

        kmf = KaplanMeierFitter()
        kmf.fit(group1['OS_MONTHS'], group1['OS_STATUS'], label="Group 1")
        ax = kmf.plot(show_censors=True)
        kmf.fit(group2['OS_MONTHS'], group2['OS_STATUS'], label="Group 2")
        kmf.plot(show_censors=True, ax=ax)

        plt.xlabel("Survival Time (Months)")
        plt.ylabel("Survival Probability")
        plt.title("Kaplan-Meier Survival Curve")

        # Generate Kaplan-Meier plot
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plot_url = base64.b64encode(img.getvalue()).decode()

        return render_template("index.html", plot_url=plot_url)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
