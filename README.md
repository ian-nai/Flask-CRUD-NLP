# Flask-CRUD-NLP
A simple Flask site that allows users to create, update, and delete posts in a database, as well as perform basic NLP tasks on the posts. The app allows for PDF uploads, and will perform OCR on the PDFs and add the text to the database. NLP tasks include sentiment analysis (on individual posts or all posts combined as one text), returning word counts and average word lengths for posts, and generating a word cloud from the posts.

<p align="center">
<img src="https://raw.githubusercontent.com/ian-nai/Flask-CRUD-NLP/main/homepage.png" height="692" width="343"/>
</p>

## Getting Started
Install dependencies using pip:
```
pip install -r requirements.txt
```
Then run Flask:
```
flask run
```

