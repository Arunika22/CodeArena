# forms.py
from django import forms
from .models import Problem

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = '__all__'  # Include all fields in the form
# forms.py

from django import forms
from .models import Contest

# forms.py

from django import forms
from .models import Contest, Problem

class ContestForm(forms.ModelForm):
    selected_problems = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Contest
        fields = ['name', 'description', 'start_time', 'end_time']

    def save(self, commit=True):
        contest = super().save(commit=False)
        if commit:
            contest.save()
        selected_problem_ids = self.cleaned_data['selected_problems'].split(',')
        for problem_id in selected_problem_ids:
            if problem_id:
                problem = Problem.objects.get(id=problem_id)
                contest.problems.add(problem)
        return contest

