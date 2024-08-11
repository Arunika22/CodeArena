from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('compiler/', views.compiler, name='compiler'), 
    path('compile_code/', views.compile_code, name='compile_code'),
    path('add/', views.add_problem, name='add_problem'),
    path('solve/', views.solve_problem, name='solve_problem'),
    path('problem/<int:id>/', views.problem_detail, name='problem_detail'),
    path('execute_code', views.execute_code, name='execute_code'),
    path('submit_code/', views.submit_code, name='submit_code'),
    path('contests/', views.contest_list, name='contest_list'),  # List of all contests
    path('contests/add/', views.add_contest, name='add_contest'),  # Add new contest
    path('contests/<int:contest_id>/', views.contest_detail, name='contest_detail'),  # Contest detail view
    path('problems/<int:problem_id>/', views.contest_problem_detail, name='contest_problem_detail'), 
    path('problem/<int:problem_id>/submit/', views.submit_solution, name='submit_solution'),
]
