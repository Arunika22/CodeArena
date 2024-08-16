from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
import subprocess
from django.views.decorators.csrf import csrf_exempt
import os
import tempfile
import json
from time import time
import psutil
import time
from django.shortcuts import render, redirect
from .forms import ProblemForm
from django.shortcuts import render
from .models import Problem


 
    
def index(request):
    problems = Problem.objects.all()
    print(problems)
    print("here")
    return render(request, 'index.html', {'problems': problems})

def compiler(request):
    return render(request, 'compiler.html')

import re


def requires_input(code):
    """Determine the number of cin operations and count variables per cin operation, ignoring comments and strings."""
    
    # Remove single-line comments (//)
    code = re.sub(r'//.*', '', code)
    
    # Remove multi-line comments (/* ... */)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    
    # Remove string literals to avoid counting cin within strings
    code = re.sub(r'".*?"', '', code)
    
    # Find all cin operations
    cin_operations = re.findall(r'\bcin\s*>>\s*(\w+(\s*>>\s*\w+)*)', code)
    
    # Count total number of cin operations
    total_cin_operations = len(cin_operations)
    
    # Count number of variables per cin operation
    num_variables_per_cin = [len(re.findall(r'\w+', op[0])) for op in cin_operations]
    
    # Total number of variables across all cin operations
    total_variables = sum(num_variables_per_cin)
    
    # Determine if input is required
    input_required = total_cin_operations > 0
    
    # Print for debugging
    print(total_variables)
    print(input_required)
    print(num_variables_per_cin)
    
    return total_variables, input_required


@csrf_exempt
def compile_code(request):
    if request.method == 'POST':
        try:
            body = json.loads(request.body)
            code = body.get('code', '')
            user_input = body.get('input', '')

            if not code.strip():
                return JsonResponse({'output': '', 'errors': 'Code is empty.'}, status=400)

            # num_input_operations,has_input = requires_input(code)
            num_input_operations, has_input = requires_input(code)
            print(num_input_operations)
            # Get the variable types from the code
            # variable_types = get_variable_data_types(code)
            
            user_input_lines = re.split(r'\s+', user_input.strip())
            num_user_input_lines = len(user_input_lines)
            print(num_user_input_lines)
            
            print(has_input)
            if has_input and num_user_input_lines < num_input_operations:
                error_message = (
                    f"Compilation Error: Expected {num_input_operations} input(s) but received {num_user_input_lines}. "
                    "Ensure that your input matches the expected format and number of inputs required by your code."
                )
                return JsonResponse({
                    'output': '',
                    'errors': error_message,
                    'execution_time': None,
                    'memory_usage': None
                }, status=400)

            if num_user_input_lines > num_input_operations:
                warning_message = (
                    f"Warning: Received more inputs ({num_user_input_lines}) than required ({num_input_operations}). "
                    "Extra inputs will be ignored."
                )
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".cpp") as temp_file:
                temp_file.write(code.encode('utf-8'))
                temp_file.flush()
                temp_file_name = temp_file.name
          
            try:
                # Compile the code
                compile_command = f"g++ {temp_file_name} -o {temp_file_name}.out"
                start_time = time.time()
                compilation_result = subprocess.run(
                    compile_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                end_time = time.time()
                process = psutil.Process(os.getpid())
                execution_time = (end_time - start_time) * 1000  # in milliseconds

                if compilation_result.returncode != 0:
                    errors = compilation_result.stderr.decode('utf-8')
                    formatted_errors = extract_error_lines(errors)
                    return JsonResponse({'output': '', 'errors': formatted_errors, 'execution_time': execution_time}, status=400)

                # Run the compiled executable
                run_command = f"{temp_file_name}.out"
                run_start_time = time.time()
                run_result = subprocess.run(
                    run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=user_input.encode('utf-8')
                )
                run_end_time = time.time()

                run_execution_time = (run_end_time - run_start_time) * 1000  # in milliseconds
                memory_usage = process.memory_info().rss / 1024
                output = run_result.stdout.decode('utf-8')
                errors = run_result.stderr.decode('utf-8')

            finally:
                if os.path.exists(temp_file_name):
                    os.remove(temp_file_name)
                if os.path.exists(f"{temp_file_name}.out"):
                    os.remove(f"{temp_file_name}.out")

            return JsonResponse({'output': output, 'errors': errors, 'execution_time': run_execution_time,
                                'memory_usage': memory_usage})

        except json.JSONDecodeError as e:
            return JsonResponse({'output': '', 'errors': f'Invalid JSON format: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'output': '', 'errors': f'An unexpected error occurred: {str(e)}'}, status=500)
    else:
        return HttpResponse("This endpoint only accepts POST requests.")


def extract_error_lines(errors):
    # This function parses the compiler error output and extracts relevant lines with line numbers
    error_lines = []
    error_pattern = re.compile(r'(.+):(\d+):(\d+): error: (.+)')

    for line in errors.splitlines():
        match = error_pattern.match(line)
        if match:
            file_path, line_number, column_number, error_message = match.groups()
            error_lines.append(f"Line {line_number}, Column {column_number}: {error_message}")

    return '\n'.join(error_lines)

from django.shortcuts import render, redirect
from .forms import ProblemForm
from .models import Problem, TestCase
from django.shortcuts import render, redirect
from .forms import ProblemForm
from .models import Problem, TestCase

from django.http import JsonResponse
from django.shortcuts import render, redirect
from .forms import ProblemForm
from .models import TestCase, Problem

def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            # Save the problem and get the instance
            problem = form.save()
            
            # Handle saving test cases
            test_case_input_keys = [key for key in request.POST if key.startswith('testcase_input_')]
            for input_key in test_case_input_keys:
                index = input_key.split('_')[-1]
                test_case = TestCase(
                    problem=problem,
                    input_data=request.POST.get(f'testcase_input_{index}'),
                    output_data=request.POST.get(f'testcase_output_{index}'),
                    is_sample=True  # Assuming all test cases are sample
                )
                test_case.save()
            
            # Handle saving additional test cases
            additional_test_case_input_keys = [key for key in request.POST if key.startswith('additional_testcase_input_')]
            for input_key in additional_test_case_input_keys:
                index = input_key.split('_')[-1]
                test_case = TestCase(
                    problem=problem,
                    input_data=request.POST.get(f'additional_testcase_input_{index}'),
                    output_data=request.POST.get(f'additional_testcase_output_{index}'),
                    is_sample=False  # Assuming additional test cases are not sample
                )
                test_case.save()
            
            # Debugging information
            print(f"Problem added with ID: {problem.id}")
            print("Redirecting to solve_problem...")

            # JSON response for AJAX
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect_url': '/solve/'})
            
            # Redirect to 'solve_problem'
            return redirect('solve_problem')
        else:
            # If form is not valid, log errors and return JSON response
            print("Form is not valid.")
            print(form.errors)
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ProblemForm()
    
    return render(request, 'add_problem.html', {'form': form})





def solve_problem(request):
    problems = Problem.objects.all()
    return render(request, 'solve_problems.html', {'problems': problems})



import json
import subprocess
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import subprocess
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Problem, TestCase

@csrf_exempt
def parse_errors(error_output):
    # Function to parse the error output from the compiler or runtime
    errors = []
    lines = error_output.splitlines()
    for line in lines:
        if line.startswith('temp_code.cpp:'):
            parts = line.split(':')
            if len(parts) > 2:
                line_number = parts[1]
                message = ':'.join(parts[2:])
                errors.append({'line': line_number, 'message': message.strip()})
        else:
            errors.append({'line': 'unknown', 'message': line.strip()})
    return errors

@csrf_exempt
def execute_code(request, problem_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')

            # Debug statement
            print("Received code:\n", code)

            # Fetch the problem by ID
            problem = Problem.objects.get(id=problem_id)
            test_cases = problem.test_cases.filter(is_sample=True)

            # Debug statement
            print(f"Fetched {test_cases.count()} test cases for problem ID {problem_id}")

            cpp_file = 'temp_code.cpp'
            executable_file = 'temp_code'

            # Save the code to a temporary file
            with open(cpp_file, 'w') as file:
                file.write(code)

            # Compile the code
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)

            # Debug statement
            print("Compilation stderr:\n", compile_result.stderr)

            if compile_result.returncode != 0:
                errors = parse_errors(compile_result.stderr)
                return JsonResponse({'error': 'Compilation Error', 'details': errors}, status=400)

            results = []
            for test_case in test_cases:
                # Debug statement
                print(f"Running test case with input:\n{test_case.input_data}")

                # Run the compiled executable with the test case input
                run_result = subprocess.run(
                    [executable_file],
                    input=test_case.input_data,
                    text=True,
                    capture_output=True
                )

                output = run_result.stdout
                errors = run_result.stderr

                # Debug statement
                print(f"Test case input:\n{test_case.input_data}")
                print(f"Test case output:\n{output}")
                print(f"Test case errors:\n{errors}")
                print(f"Expected output:\n{test_case.output_data}")

                # Determine if the test case passed
                result_message = ''
                if test_case.output_data.strip() == output.strip():
                    result_message = 'Test case passed!'
                else:
                    result_message = 'Test case failed!'
                print(f"Result message for input '{test_case.input_data}': {result_message}")

                
                results.append({
                    'input': test_case.input_data,
                    'output': output,
                    'errors': errors,
                    'expected_output': test_case.output_data,
                    'result_message': result_message
                })

            # Cleanup
            os.remove(cpp_file)
            if os.path.exists(executable_file):
                os.remove(executable_file)

            # Prepare and return the response
            return JsonResponse({'results': results})

        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {str(e)}'
            return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def submit_code(request, problem_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')

            # Debug statement
            print("Received code:\n", code)

            # Fetch the problem by ID
            problem = Problem.objects.get(id=problem_id)
            test_cases = problem.test_cases.filter(is_sample=False)  # Fetch additional test cases

            cpp_file = 'temp_code.cpp'
            executable_file = 'temp_code'

            # Save the code to a temporary file
            with open(cpp_file, 'w') as file:
                file.write(code)

            # Compile the code
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)

            # Debug statement
            print("Compilation stderr:\n", compile_result.stderr)

            if compile_result.returncode != 0:
                errors = parse_errors(compile_result.stderr)
                return JsonResponse({'error': 'Compilation Error', 'details': errors}, status=400)

            results = []
            for test_case in test_cases:
                # Debug statement
                print(f"Running additional test case with input:\n{test_case.input_data}")

                # Run the compiled executable with the test case input
                run_result = subprocess.run(
                    [executable_file],
                    input=test_case.input_data,
                    text=True,
                    capture_output=True
                )

                output = run_result.stdout
                errors = run_result.stderr

                # Debug statement
                print(f"Additional test case output:\n{output}")
                print(f"Additional test case errors:\n{errors}")

                # Determine if the test case passed
                result_message = ''
                if test_case.output_data.strip() == output.strip():
                    result_message = 'All test cases passed!'
                else:
                    result_message = 'Test cases failed!'

                results.append({
                    'input': test_case.input_data,
                    'output': output,
                    'errors': errors,
                    'expected_output': test_case.output_data,
                    'result_message': result_message
                })

            # Cleanup
            os.remove(cpp_file)
            if os.path.exists(executable_file):
                os.remove(executable_file)

            # Prepare and return the response
            return JsonResponse({'results': results})

        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {str(e)}'
            return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)






def problem_detail(request,problem_id):
    
    problem = get_object_or_404(Problem, pk=problem_id)
    sample_test_cases = problem.test_cases.filter(is_sample=True)
    context = {
        'problem': problem,
        'sample_test_cases': sample_test_cases
    }
    return render(request, 'problem_detail.html', context)
    



#contest
# views.py

import random
import string
from django.shortcuts import render, get_object_or_404, redirect
from .models import Contest, Problem, Submission, Leaderboard

def generate_random_username():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def get_session_username(request):
    if 'username' not in request.session:
        request.session['username'] = generate_random_username()
    return request.session['username']

# views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Contest, Problem, Leaderboard, Submission
from .forms import ContestForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required



# View to list all contests and delete past contests
def contest_list(request):
    # Delete contests whose end time has passed
    Contest.objects.filter(end_time__lt=timezone.now()).delete()

    # Fetch all remaining contests
    contests = Contest.objects.all()
    
    return render(request, 'contest_list.html', {'contests': contests})
@login_required
def add_contest(request):
    problems = Problem.objects.all()
    if request.method == 'POST':
        form = ContestForm(request.POST)
        if form.is_valid():
            print("Form is valid. Saving the contest...")

            # Save the contest instance first
            contest = form.save()

            # Process many-to-many relationships
            selected_problem_ids = request.POST.get('selected_problems', '').split(',')
            for problem_id in selected_problem_ids:
                if problem_id:
                    try:
                        problem = Problem.objects.get(id=problem_id)
                        contest.problems.add(problem)
                    except Problem.DoesNotExist:
                        print(f"Problem with ID {problem_id} does not exist.")
            
            # Save many-to-many relationships
            contest.save()

            return redirect('contest_list')
        else:
            print("Form is not valid. Errors:", form.errors)
    else:
        form = ContestForm()
    return render(request, 'add_contest.html', {'form': form, 'problems': problems})
def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    leaderboard = Leaderboard.objects.filter(contest=contest).order_by('-total_score')
    
    return render(request, 'contest_detail.html', {
        'contest': contest,
        'leaderboard': leaderboard,
    })

# Renamed view for problem details in the context of a contest
def contest_problem_detail(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    if request.method == 'POST':
        code = request.POST.get('code')
        username = get_session_username(request)  # Or any session-based identification logic

        # Dummy judge logic
        status = "Passed" if "print" in code else "Failed"
        score = 100 if status == "Passed" else 0

        # Save submission
        submission = Submission.objects.create(
            user=None,  # No user since it's session-based
            problem=problem,
            code=code,
            status=status,
            score=score,
            temporary_username=username
        )

        # Update leaderboard
        contest = problem.contests.first()
        leaderboard_entry, created = Leaderboard.objects.get_or_create(
            contest=contest,
            user=None,
            temporary_username=username,
        )
        leaderboard_entry.total_score += score
        leaderboard_entry.save()

        return redirect('contest_detail', contest_id=contest.id)
    
    return render(request, 'contest_problem_detail.html', {'problem': problem})


def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, pk=problem_id)
    
    if request.method == 'POST':
        code = request.POST.get('code')
        
        # Prepare the code for execution
        with tempfile.NamedTemporaryFile(suffix=".cpp", delete=False) as temp_code_file:
            temp_code_file.write(code.encode('utf-8'))
            temp_code_path = temp_code_file.name
        
        # Compilation step
        compile_command = f"g++ {temp_code_path} -o {temp_code_path}.out"
        compile_process = subprocess.run(compile_command, shell=True, capture_output=True)
        
        if compile_process.returncode != 0:
            compile_error = compile_process.stderr.decode('utf-8')
            return HttpResponse(f"Compilation Error: {compile_error}")
        
        # Execution step
        exec_command = f"{temp_code_path}.out"
        exec_process = subprocess.run(exec_command, input=problem.testcase_input.encode('utf-8'),
                                      capture_output=True, timeout=5)

        if exec_process.returncode != 0:
            exec_error = exec_process.stderr.decode('utf-8')
            return HttpResponse(f"Runtime Error: {exec_error}")
        
        output = exec_process.stdout.decode('utf-8').strip()
        
        # Compare the output with the expected output
        if output == problem.testcase_output.strip():
            result = "Success"
        else:
            result = f"Wrong Answer: Expected '{problem.testcase_output.strip()}', but got '{output}'"
        
        # Optionally, save the submission to the database
        submission = Submission(problem=problem, code=code, result=result)
        submission.save()
        
        return HttpResponse(result)

    return redirect('contest_problem_detail', problem_id=problem_id)