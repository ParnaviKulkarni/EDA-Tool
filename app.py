from flask import Flask, render_template,request
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)



def index():
    return render_template('index.html')

@app.route('/') 
def upload():  
    return render_template("file_upload.html")  
 
@app.route('/results', methods = ['POST','GET'])  
def results():  
    if request.method == 'POST':  
        f = request.files['file']  
        f.save(f.filename)  
        global dataset
        dataset = parseCSV(f.filename)
        global summary_table
        summary_table = get_summary(dataset)

        #class_feature = request.form.get("class_feature")
        return render_template("results.html", name = f.filename, tables=[summary_table.to_html(), dataset.describe().to_html()],titles = ['na','Dataset Summary', 'Columns Summary'])

def parseCSV(filepath):
    dataset = pd.read_csv(filepath)
    return dataset

@app.route('/dataset')
def view_dataset():
    return render_template("dataset.html",tables=[dataset.to_html()],titles=['na',"DATASET"])

@app.route('/eda',methods=['POST'])
def eda():
    
    if request.method == "POST":
        class_feature = str(request.form.get("class_feature"))
        get_visualizations(class_feature)
        return render_template('eda.html', class_feature = class_feature)

def get_visualizations(class_feature):
    columns = list(dataset.columns)
    print(columns)
    class_feature_index = columns.index(class_feature)
    datatypes = list([str(i) for i in list(dataset.dtypes)])
    print(datatypes)
    sns_pp = sns.pairplot(dataset)
    sns_pp.savefig("./static/sns-heatmap.png")
    
    fig,ax=plt.subplots(figsize=(6,6))
    ax=sns.set(style="darkgrid")
    sns.countplot(dataset[class_feature])
    canvas=FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig('./static/plots/'+class_feature+'_countplot.png')
    img.seek(0)


    for i in range(len(columns)):
        print('processing '+columns[i])
        if i!= class_feature_index:
            
            if list(dataset.nunique(dropna=True))[i]!=len(dataset.index):
                if datatypes[i][0:5]=='float':
                    interval = list(range(0,int(dataset[columns[i]].max()),10))
                    binned = pd.cut(dataset[columns[i]],interval)
                    fig,ax=plt.subplots(figsize=(6,6))
                    ax=sns.set(style="darkgrid")
                    sns.countplot(x=binned,hue=class_feature,data=dataset)
                    canvas=FigureCanvas(fig)
                    img = io.BytesIO()
                    fig.savefig('./static/plots/'+columns[i]+'_countplot.png')
                    img.seek(0)
                else:
                    fig,ax=plt.subplots(figsize=(6,6))
                    ax=sns.set(style="darkgrid")
                    sns.countplot(x = columns[i], hue = class_feature, data = dataset)
                    canvas=FigureCanvas(fig)
                    img = io.BytesIO()
                    fig.savefig('./static/plots/'+columns[i]+'_countplot.png')
                    img.seek(0)
            if datatypes[i][0:5]=='float':
                
                fig,ax=plt.subplots(figsize=(6,6))
                ax=sns.set(style="darkgrid")
                sns.histplot(dataset[columns[i]])
                canvas=FigureCanvas(fig)
                img = io.BytesIO()
                fig.savefig('./static/plots/'+columns[i]+'_histplot.png')
                img.seek(0)
                
                fig,ax=plt.subplots(figsize=(6,6))
                ax=sns.set(style="darkgrid")
                sns.boxplot(dataset[columns[i]])
                canvas=FigureCanvas(fig)
                img = io.BytesIO()
                fig.savefig('./static/plots/'+columns[i]+'_boxplot.png')
                img.seek(0)

            if datatypes[i][0:3]=='int':
                if list(dataset.nunique(dropna=True))[i]<len(dataset.index):
                    fig,ax=plt.subplots(figsize=(6,6))
                    ax=sns.set(style="darkgrid")
                    sns.histplot(dataset[columns[i]])
                    canvas=FigureCanvas(fig)
                    img = io.BytesIO()
                    fig.savefig('./static/plots/'+columns[i]+'_histplot.png')
                    img.seek(0)
                    if 10<list(dataset.nunique(dropna=True))[i]:
                        fig,ax=plt.subplots(figsize=(6,6))
                        ax=sns.set(style="darkgrid")
                        sns.boxplot(dataset[columns[i]])
                        canvas=FigureCanvas(fig)
                        img = io.BytesIO()
                        fig.savefig('./static/plots/'+columns[i]+'_boxplot.png')
                        img.seek(0)

def get_summary(dataset):
    summary_result = {}
    summary_result['Column name'] = list(dataset.columns)
    summary_result['Datatype'] = list([str(i) for i in list(dataset.dtypes)])
    summary_result['Non-Null count'] = list(dataset.notnull().sum())
    summary_result['Missing values'] = list(dataset.isnull().sum())
    summary_result['No. of unique values'] = list(dataset.nunique(dropna=True))

    summary_table = pd.DataFrame.from_dict(summary_result)

    return summary_table




if __name__ == "__main__":
    app.run(debug=True)