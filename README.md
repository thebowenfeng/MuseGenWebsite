# MuseGenWebsite

Interactive website for [MuseGen](https://github.com/thebowenfeng/MuseGen), which is an AI that can generate music.

Demo: 

[![Video](http://img.youtube.com/vi/-TX8kUK7zos/0.jpg)](http://www.youtube.com/watch?v=-TX8kUK7zos)

## Celery

Celery doesn't work and has been deprecated from this project, as the paging size is not enough to run the tensorflow models. An alternative asynchronous method of training the network, by simply having the training done on a separate request (hence, a separate thread) is used.
