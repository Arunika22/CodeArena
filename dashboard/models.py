from django.db import models
from django.contrib.auth.models import User
import uuid

# models.py
class Problem(models.Model):
    id = models.AutoField(primary_key=True) 
    title = models.CharField(max_length=200)
    description = models.TextField()
    testcase_input = models.TextField()
    testcase_output = models.TextField()
    additional_testcase_input = models.TextField()
    additional_testcase_output = models.TextField()
    constraints = models.TextField()
    editorial = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User

class Contest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    problems = models.ManyToManyField(Problem, related_name='contests')

    def __str__(self):
        return self.name


# models.py

class Submission(models.Model):
    temporary_username = models.CharField(max_length=50, blank=True, null=True)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE)
    code = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50)
    score = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.temporary_username} - {self.problem.title}'

class Leaderboard(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    temporary_username = models.CharField(max_length=50, blank=True, null=True)
    total_score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('contest', 'temporary_username')

    def __str__(self):
        return f'{self.temporary_username} - {self.total_score} points'
