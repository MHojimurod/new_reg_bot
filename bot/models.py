from datetime import datetime
from email.policy import default
from xml.dom.minidom import Document
from django.db import models
from django.db.models.query import QuerySet
from django.core.files.base import File
from telegram import Message
# Create your models here.


class User(models.Model):
    id:int
    chat_id:int = models.IntegerField()
    name:str = models.CharField(max_length=255)
    region:"Region" = models.ForeignKey("Region", on_delete=models.SET_NULL, null=True, blank=True)
    number:int = models.CharField(max_length=255)
    birthday:int = models.IntegerField(null=True, blank=True)
    zoom:bool = models.BooleanField(default=False)
    def tasks(self) -> "QuerySet[Task]":
        return Task.objects.filter(user=self, accepted=1)
    
    class Meta:
        db_table = "Foydalanuvchilar"
        verbose_name = "Foydalanuvchilar"


    def add_task(self, doc, data_type:int) -> "Task":
        return Task.objects.create(user=self, number = self.tasks().count(), document=doc, data_type=data_type)
    
    def panding_answer(self) -> bool:
        return Task.objects.filter(user=self, accepted=0)
    
    def curent_task(self) -> "Question":
        questions = Question.objects.order_by('id').all()
        return questions[self.tasks().count()] if questions.count() > self.tasks().count() else None
    def __str__(self):
        return self.name


class ZoomUser(models.Model):
    id:int
    chat_id:int = models.IntegerField(default=0)
    name:str = models.CharField(max_length=255)
    number:int = models.CharField(max_length=255)
    def __str__(self):
        return self.name
    class Meta:
        db_table = "ZoomFoydalanuvchilar"
        verbose_name = "ZoomFoydalanuvchilar"

class Task(models.Model):
    id:int
    number:int = models.IntegerField(default=0)
    user:User = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    document = models.CharField(max_length=50000)
    data_type = models.IntegerField(default=0, choices=(
        (0, "text"),
        (1, "file"),
    ))
    accepted = models.IntegerField(choices=(
        (0, "Waiting"),
        (1, "Accepted"),
        (2, "Rejected"),
    ), default=0)

    def accept(self):
        self.accepted = 1
        self.save()
    
    def reject(self):
        self.accepted = 2
        self.save()
    
    def send(self, message:Message):
        return AnswerNotificationMessages.objects.create(task=self, chat_id=message.chat.id, message_id=message.message_id)
    
    def messages(self) -> "QuerySet[AnswerNotificationMessages]":
        return AnswerNotificationMessages.objects.filter(task=self)



class Region(models.Model):
    id:int
    name:str = models.CharField(max_length=255)
    class Meta:
        db_table = "Viloyatlar"
        verbose_name = "Viloyatlar"
    def __str__(self):
        return self.name


class Question(models.Model):
    id:int
    description:str = models.TextField()
    def __str__(self):
        return str(self.id)
    class Meta:
        db_table = "Topshiriqlar"
        verbose_name = "Topshiriqlar"
    


class AnswerNotificationMessages(models.Model):
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, null=True)
    chat_id = models.IntegerField()
    message_id = models.IntegerField()