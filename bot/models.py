from datetime import datetime
from xml.dom.minidom import Document
from django.db import models
from django.db.models.query import QuerySet
from django.core.files.base import File
# Create your models here.


class User(models.Model):
    chat_id:int = models.IntegerField()
    name:str = models.CharField(max_length=255)
    region:"Region" = models.ForeignKey("Region", on_delete=models.SET_NULL, null=True)
    number:int = models.CharField(max_length=255)
    birthday:int = models.IntegerField()
    def tasks(self) -> "QuerySet[Task]":
        return Task.objects.filter(user=self)


    def add_task(self, doc):
        return Task.objects.create(user=self, number = self.tasks().count(), document=doc)
    
    def curent_task(self) -> "Question":
        print()
        # return Question.objects.filter(id=self.tasks().count()).first()
        questions = Question.objects.order_by('id').all()
        return questions[self.tasks().count()] if questions.count() > self.tasks().count() else None

class Task(models.Model):
    number:int = models.IntegerField(default=0)
    user:User = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    document = models.CharField(max_length=50000)



class Region(models.Model):
    name:str = models.CharField(max_length=255)


class Question(models.Model):
    description:str = models.TextField()