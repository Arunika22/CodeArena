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



def add_problem(request):
    if request.method == 'POST':
        form = ProblemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('solve_problem')  # Redirect to a list view or any other page
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import subprocess
import os
@csrf_exempt
def execute_code(request):
    if request.method == 'POST':
        try:
            # Load and debug the request data
            data = json.loads(request.body)
            code = data.get('code')
            additional_testcase_input = data.get('additional_testcase_input', '')
            additional_testcase_output = data.get('additional_testcase_output', '')

            print("Received request data:")
            print(f"Code:\n{code}")
            print(f"Test case input:\n{additional_testcase_input}")
            print(f"Expected Output:\n{additional_testcase_output}")

            cpp_file = 'temp_code.cpp'
            executable_file = 'temp_code'

            # Save and compile
            with open(cpp_file, 'w') as file:
                file.write(code)
            print(f"Saved code to {cpp_file}")

            # Compile the code
            print(f"Compiling {cpp_file}...")
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)
            
            # Print compilation details
            print("Compilation output:")
            print(compile_result.stdout)
            print("Compilation errors:")
            print(compile_result.stderr)

            if compile_result.returncode != 0:
                return JsonResponse({'error': 'Compilation Error:\n' + compile_result.stderr}, status=400)

            # Run the compiled executable with example test cases
            print(f"Running {executable_file} with provided test case input...")
            run_result = subprocess.run(
                [executable_file],
                input=additional_testcase_input,
                text=True,
                capture_output=True
            )

            # Print execution details
            print("Execution output:")
            print(run_result.stdout)
            print("Execution errors:")
            print(run_result.stderr)

            output = run_result.stdout
            errors = run_result.stderr

            # Determine if the additional test case passed
            result_message = ''
            if additional_testcase_output.strip() == output.strip():
                result_message = 'Test case passed!'
            else:
                result_message = 'Test case failed!'

            # Cleanup
            os.remove(cpp_file)
            if os.path.exists(executable_file):
                os.remove(executable_file)

            # Prepare and return the response
            response_data = {
                'input': additional_testcase_input,
                'output': output,
                'errors': errors,
                'expected_output': additional_testcase_output,
                'result_message': result_message
            }
            print("Response data:")
            print(response_data)
            
            return JsonResponse(response_data)

        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {str(e)}'
            print(f"Error: {error_message}")
            return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            print(f"Error: {error_message}")
            return JsonResponse({'error': error_message}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
@csrf_exempt
def submit_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code')

            # Process the code submission (e.g., save it to the database)
            # For demonstration, we'll just return a success message
            return JsonResponse({'message': 'Code submitted successfully!'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def problem_detail(request, id):
    problem = get_object_or_404(Problem, id=id)
    return render(request, 'problem_detail.html', {'problem': problem})



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