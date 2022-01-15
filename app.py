from flask import Flask, render_template, request, redirect, flash, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import flask
from flask import Response
import json
import os
from werkzeug.utils import secure_filename
from os import walk

#ocr imports
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
import codecs
import io
import sys
from nltk.tokenize import word_tokenize

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"
app.config['UPLOAD_EXTENSIONS'] = ['.pdf']

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

filepath = 'placeholder'
text = 'Text here'
file_list = next(walk(app.config['UPLOAD_FOLDER']), (None, None, []))[2]

class Post(db.Model):
    number = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    text = db.Column(db.String(8000), nullable=False)


    def __repr__(self) -> str:
        return f"{self.number} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        text = request.form['text']
        post = Post(title=title, desc=desc, text=text)
        db.session.add(post)
        db.session.commit()

    allPosts = Post.query.all()
    return render_template('index.html', allPosts=allPosts)


@app.route('/create_record', methods=['GET', 'POST'])
def create_upload():
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        text = request.form['text']
        post = Post(title=title, desc=desc, test=test)
        db.session.add(post)
        db.session.commit()

    allPosts = Post.query.all()
    return render_template('index.html', allPosts=allPosts)

@app.route("/upload_form" , methods=['GET', 'POST'])
def upload_form():
    global filepath
    select = request.form.get('file_select')
    filepath = (app.config['UPLOAD_FOLDER'] + '/' + select)
    pages=None
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(filepath, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    print(text)
    return render_template('upload.html', text = text, file_list = file_list)

@app.route('/upload', methods=['GET', 'POST'])
def redirect_upload():
    global filepath
    global file_list
    global text
    if request.method == 'POST':
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
             file_ext = os.path.splitext(uploaded_file.filename)[1]
             if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                 abort(400)
             uploaded_file.save(os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))

             filepath = (os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename))
             file_list.append(uploaded_file.filename)

             pages=None
             if not pages:
                 pagenums = set()
             else:
                 pagenums = set(pages)

             output = StringIO()
             manager = PDFResourceManager()
             converter = TextConverter(manager, output, laparams=LAParams())
             interpreter = PDFPageInterpreter(manager, converter)

             infile = open(filepath, 'rb')
             for page in PDFPage.get_pages(infile, pagenums):
                 interpreter.process_page(page)
             infile.close()
             converter.close()
             text = output.getvalue()
             output.close()
             print(text)


        return redirect(url_for('redirect_upload'))
    return render_template('upload.html', file_list = file_list, text = text)

@app.route('/ocr_document', methods=['GET', 'POST'])
def ocr_pdf():
    global filepath
    print('working')
    pages=None
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = open(filepath, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()
    print(text)


    return flask.jsonify({'html':text})

@app.route('/dropdown_files')
def get_dropdown():
    directory = app.config['UPLOAD_FOLDER']
    global file_list

@app.route('/update/<int:number>', methods=['GET', 'POST'])
def update(number):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        text = request.form['text']
        post = Post.query.filter_by(number=number).first()
        post.title = title
        post.desc = desc
        post.text = text
        db.session.add(post)
        db.session.commit()
        return redirect("/")

    post = Post.query.filter_by(number=number).first()
    return render_template('update.html', post=post)

@app.route('/delete/<int:number>')
def delete(number):
    post = Post.query.filter_by(number=number).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/")

@app.route('/get_word')
def get_prediction():
  allPosts = Post.query.all()
  title_list = []
  for el in allPosts:
    print(el.title)
    title_list.append(el.title)
  test_title = title_list[0]
  word = flask.request.args.get('word')
  return flask.jsonify({'html':title_list})

@app.route('/run_full_an', methods=['GET', 'POST'])
def full_analysis():
   print('ran')
   allPosts = Post.query.all()
   text_list = []
   for el in allPosts:
       text_list.append(el.text)
   title_list = []
   for el in allPosts:
       print(el.title)
       title_list.append(el.title)

   import nltk
   from nltk.sentiment.vader import SentimentIntensityAnalyzer
   from nltk.tokenize import word_tokenize
   import string

   analyzer = SentimentIntensityAnalyzer()

   list_of_results = []
   indposts = request.form.get("indposts")
   allposts = request.form.get("allposts")
   length_all = request.form.get("length_all")
   length_summary = request.form.get("length_summary")
   word_cloud_box = request.form.get("word_cloud_box")


   if indposts is not None:
       i = 0
       while i < len(text_list):
          text = text_list[i]
          text.translate(str.maketrans('', '', string.punctuation))
          snt = analyzer.polarity_scores(text)
          results_nltk = ("{:-<40} {}".format(text, str(snt)))
          list_of_results.append(results_nltk)
          i = i + 1

   if allposts is not None:
        text = ' '.join(text_list)
        text.translate(str.maketrans('', '', string.punctuation))
        snt = analyzer.polarity_scores(text)
        results_nltk = ("{:-<40} {}".format(text, str(snt)))
        list_of_results.append(results_nltk)


   word_lengths = []
   list_of_tokenized_posts = []
   word_averages = []
   list_of_post_lengths = []
   word_length_summary = []
   tokenized_summary = []
   zipped_word_lengths = []
   zipped_word_averages = []

   if length_all is not None:
        for x in text_list:
            tokenizing_posts = word_tokenize(x)
            tokenized_post = [word for word in tokenizing_posts if word.isalnum()]
            list_of_tokenized_posts.append(tokenized_post)
            word_lengths.append(len(tokenized_post))
            if len(tokenized_post) > 0:
                average = sum(len(word) for word in tokenized_post) / len(tokenized_post)
            word_averages.append(average)

        zip_titles_word_lengths = zip(title_list, word_lengths)
        zipped_word_lengths = list(zip_titles_word_lengths)

        zip_titles_word_avgs = zip(title_list, word_averages)
        zipped_word_averages = list(zip_titles_word_avgs)


   if length_summary is not None:
       all_posts = (' '.join(text_list))
       tokenizing_all_posts = word_tokenize(all_posts)
       tokenized_all_posts = [word for word in tokenizing_all_posts if word.isalnum()]
       tokenized_summary.append(len(tokenized_all_posts))

   if word_cloud_box is not None:

       from wordcloud import WordCloud, ImageColorGenerator
       import matplotlib.pyplot as plt

       default_stopwords = set(nltk.corpus.stopwords.words('english'))

       filtered_words = [w for w in text_list if not w in default_stopwords]

       #convert list to string and generate
       unique_string=(" ").join(filtered_words)
       wordcloud = WordCloud(width = 1000, height = 500).generate(unique_string)
       plt.figure(figsize=(15,8))
       plt.imshow(wordcloud)
       plt.axis("off")
       plt.savefig("static/posts_wordcloud.png", bbox_inches='tight')
       plt.close()


   return render_template('nlp.html', list_of_results=list_of_results, zipped_word_lengths=zipped_word_lengths, zipped_word_averages=zipped_word_averages, tokenized_summary=tokenized_summary)


@app.route('/get_full_an')
def full_an():
   return render_template('nlp.html')

@app.route('/get_sent_an')
def sentiment_test():
   allPosts = Post.query.all()
   text_list = []
   for el in allPosts:
       print(el.text)
       text_list.append(el.text)

   import nltk
   from nltk.sentiment.vader import SentimentIntensityAnalyzer
   from nltk.tokenize import word_tokenize
   import string

   analyzer = SentimentIntensityAnalyzer()

   list_of_results = []

   i = 0
   while i < len(text_list):
      text = text_list[i]
      text.translate(str.maketrans('', '', string.punctuation))
      snt = analyzer.polarity_scores(text)
      results_nltk = ("{:-<40} {}".format(text, str(snt)))
      print(results_nltk)
      list_of_results.append(results_nltk)
      i = i + 1

   return flask.jsonify({'html':("<p>" + "</p><p>".join(list_of_results) + "</p>")})



@app.route('/nlp', methods=['GET', 'POST'])
def redirect_nlp():
    return render_template('nlp.html')

def foo():
    print('hi - this worked')

if __name__ == "__main__":
    app.run(debug=True, port=8000)
