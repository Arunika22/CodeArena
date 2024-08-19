from collections import defaultdict
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
            print("Received code:\n", code)
            
            if not code.strip():
                return JsonResponse({'output': '', 'errors': 'Code is empty.'}, status=400)

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
                    f"Compilation Error: Expected {num_input_operations} input(s)"
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
            error_lines.append(f"Line {int(line_number)-1}, Column {column_number}: {error_message}")

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


def parse_errors(error_output):
  
    errors = []
    lines = error_output.splitlines()
    
    # Debug statement to show the raw error output
    print("Raw error output:")
    print(error_output)

    for line in lines:
        
        print(f"Processing line: {line}")

       
        if 'error' in line.lower() or 'warning' in line.lower():
            # Example format: 
            # C:\path\to\file.cpp: line:column: error: message
            parts = line.split(':')
            
            # Debug statement to show parts after splitting by ':'
            print(f"Split parts: {parts}")

            if len(parts) >= 4:
                try:
                    # Extract line number and message, assuming format is consistent
                    line_number = int(parts[2].strip())-1
                    char_position = parts[3].strip() if len(parts) > 3 else ''
                    message = ':'.join(parts[4:]).strip()
                    
                    # Debug statement to show extracted line number and message
                    print(f"Extracted line number: {line_number}")
                    print(f"Extracted character position: {char_position}")
                    print(f"Extracted message: {message}")

                    # Clean up the message to remove extra details
                    if 'error' in message.lower() or 'warning' in message.lower():
                        # Format message to remove extra details
                        message_parts = message.split(':', 1)
                        if len(message_parts) > 1:
                            message = message_parts[1].strip()
                        
                        # Debug statement to show cleaned-up message
                        print(f"Cleaned message: {message}")
                        
                    errors.append(f"Line {line_number}: Char {char_position}: {message}")
                except IndexError as e:
                    # Debug statement for handling IndexError
                    print(f"IndexError encountered: {e}")
                    errors.append(line.strip())
            else:
                # Debug statement for lines not matching expected format
                print("Line does not match expected format")
                errors.append(line.strip())
        else:
            # General errors without line and char info
            print("General error line")
            

    # Return errors after processing all lines
    return errors





import uuid
@csrf_exempt
def execute_code(request, problem_id):
    if request.method == 'POST':
        unique_id = str(uuid.uuid4())
        base_dir = os.path.dirname(os.path.abspath(__file__))
        cpp_file = os.path.join(base_dir, f'temp_code_{unique_id}.cpp')
        executable_file = os.path.join(base_dir, f'temp_code_{unique_id}.exe')

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

            # Save the code to a temporary file
            with open(cpp_file, 'w') as file:
                file.write(code)

            # Compile the code
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)

            # Debug statement
            print("Compilation stderr:\n", compile_result.stderr)

            if compile_result.returncode != 0:
                # Return only the error without other fields if compilation fails
                parsed_errors = parse_errors(compile_result.stderr)
                return JsonResponse({'error': parsed_errors}, status=400)

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
                result_message = 'Test case passed!' if test_case.output_data.strip() == output.strip() else 'Test case failed!'
                print(f"Result message for input '{test_case.input_data}': {result_message}")

                results.append({
                    'input': test_case.input_data,
                    'output': output,
                    'errors': errors,
                    'expected_output': test_case.output_data,
                    'result_message': result_message
                })

            # Return the results
            return JsonResponse({'results': results})

        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {str(e)}'
            return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            return JsonResponse({'error': error_message}, status=500)
        finally:
            try:
                print(f"Attempting to delete CPP file: {cpp_file}")
                print(f"Attempting to delete executable file: {executable_file}")

                if os.path.exists(cpp_file):
                    os.remove(cpp_file)
                    print(f"Deleted temporary CPP file: {cpp_file}")
                else:
                    print(f"CPP file {cpp_file} does not exist.")

                if os.path.exists(executable_file):
                    os.remove(executable_file)
                    print(f"Deleted temporary executable file: {executable_file}")
                else:
                    print(f"Executable file {executable_file} does not exist.")
            except Exception as e:
                print(f"Error deleting files: {str(e)}")

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

            unique_id = str(uuid.uuid4())
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cpp_file = os.path.join(base_dir, f'temp_code_{unique_id}.cpp')
            executable_file = os.path.join(base_dir, f'temp_code_{unique_id}.exe')

            # Save the code to a temporary file
            with open(cpp_file, 'w') as file:
                file.write(code)

            # Compile the code
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)

            # Debug statement
            print("Compilation stderr:\n", compile_result.stderr)

            if compile_result.returncode != 0:
                parsed_errors = parse_errors(compile_result.stderr)
                return JsonResponse({'error': parsed_errors}, status=400)

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
        finally:
            try:
                

                if os.path.exists(cpp_file):
                    os.remove(cpp_file)
                   
                else:
                    print(f"CPP file {cpp_file} does not exist.")

                if os.path.exists(executable_file):
                    os.remove(executable_file)
                   
                else:
                    print(f"Executable file {executable_file} does not exist.")
            except Exception as e:
                print(f"Error deleting files: {str(e)}")
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


from django.utils import timezone
# View to list all contests and delete past contests
def contest_list(request):
    now = timezone.now()
    contests = Contest.objects.filter(end_time__gte=now)
    return render(request, 'contest_list.html', {'contests': contests})
def add_contest(request):
    problems = Problem.objects.all()
    if request.method == 'POST':
        form = ContestForm(request.POST)
        if form.is_valid():
            print("Form is valid. Saving the contest...")

           
            contest = form.save()

          
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
from django.utils.timezone import localtime



def contest_detail(request, contest_id):
    contest = get_object_or_404(Contest, id=contest_id)
    now = localtime(timezone.now())  # Convert current time to local timezone

    # Convert contest start and end times to local timezone
    contest_start_time = localtime(contest.start_time)
    contest_end_time = localtime(contest.end_time)

    # Check if the contest has not started yet
    if contest_start_time > now:
        return render(request, 'contest_not_started.html', {'contest': contest})

    # Check if the contest has ended
    if contest_end_time < now:
        return render(request, 'contest_ended.html', {'contest': contest})

    # If the contest is ongoing, get the leaderboard
    submissions = Submission.objects.filter(problem__in=contest.problems.all())
    
    # Dictionary to store the highest score for each problem by each user
    user_problem_scores = defaultdict(lambda: defaultdict(int))
    
    # Collect the highest scores for each user-problem pair
    for submission in submissions:
        username = submission.temporary_username if submission.temporary_username else 'Anonymous'
        problem_id = submission.problem.id
        score = submission.score
        
        if score > user_problem_scores[username][problem_id]:
            user_problem_scores[username][problem_id] = score

    # Dictionary to store the total score for each user
    leaderboard_data = defaultdict(int)

    # Calculate the total score by summing the highest scores for all problems
    for user, problem_scores in user_problem_scores.items():
        total_score = sum(problem_scores.values())
        leaderboard_data[user] = total_score

    # Create a sorted leaderboard list (by total score)
    leaderboard_list = sorted(
        [{'username': username, 'total_score': score} 
         for username, score in leaderboard_data.items()],
        key=lambda x: x['total_score'],
        reverse=True
    )

    # Add rank to each user
    for rank, entry in enumerate(leaderboard_list, start=1):
        entry['rank'] = rank

    # Pass contest and leaderboard data to the template
    return render(request, 'contest_detail.html', {
        'contest': contest,
        'leaderboard': leaderboard_list,
    })



# Renamed view for problem details in the context of a contest
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from .models import Problem, TestCase
def contest_problem_detail(request, problem_id):
    # Get the problem using the problem_id, return 404 if not found
    problem = get_object_or_404(Problem, id=problem_id)

    # Fetch the sample test cases associated with this problem
    sample_test_cases = problem.test_cases.filter(is_sample=True)

    # Render the problem detail page along with the sample test cases
    context = {
        'problem': problem,
        'sample_test_cases': sample_test_cases
    }
    return render(request, 'contest_problem_detail.html', context)


# View to handle the submission of a solution for a problem
@csrf_exempt
def submit_solution(request, problem_id):
    problem = get_object_or_404(Problem, id=problem_id)
    print("Submit solution request received.")

    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            code = data.get('code')

            # Debug statement to check the received code
            print("Received code:\n", code)

            # Fetch additional test cases for the problem
            test_cases = problem.test_cases.filter(is_sample=False)

            # Create unique filenames for the temporary code and executable
            unique_id = str(uuid.uuid4())
            base_dir = os.path.dirname(os.path.abspath(__file__))
            cpp_file = os.path.join(base_dir, f'temp_code_{unique_id}.cpp')
            executable_file = os.path.join(base_dir, f'temp_code_{unique_id}.exe')

            # Save the code to a temporary file
            print(f"Saving code to: {cpp_file}")
            with open(cpp_file, 'w') as file:
                file.write(code)

            # Compile the code
            print(f"Compiling code: {cpp_file}")
            compile_result = subprocess.run(['g++', cpp_file, '-o', executable_file], capture_output=True, text=True)

            # Debug statements for compilation result
            print("Compilation stdout:", compile_result.stdout)
            print("Compilation stderr:", compile_result.stderr)

            if compile_result.returncode != 0:
                parsed_errors = parse_errors(compile_result.stderr)
                return JsonResponse({'error': parsed_errors}, status=400)

            results = []
            score = 0
            # Loop over each test case and run the compiled code
            for test_case in test_cases:
                print(f"Running test case: {test_case.id} with input: {test_case.input_data}")
                # Run the compiled executable with the test case input
                run_result = subprocess.run(
                    [executable_file],
                    input=test_case.input_data,
                    text=True,
                    capture_output=True
                )
                output = run_result.stdout
                errors = run_result.stderr
                print(f"Additional test case output:\n{output}")
                print(f"Additional test case errors:\n{errors}")
                # Compare the output with the expected output
                if output.strip() == test_case.output_data.strip():
                    result_message = 'Test case passed!'
                    score += 20  # Adjust score for each passed test case
                else:
                    result_message = 'Test cases failed!'

                results.append({
                    'input': test_case.input_data,
                    'output': output,
                    'errors': errors,
                    'expected_output': test_case.output_data,
                    'result_message': result_message
                })

            # Save the submission in the database
            username = get_session_username(request)

            submission = Submission.objects.create(
                temporary_username=username,  # For now, no user handling
                problem=problem,
                code=code,
                status="Passed" if score > 0 else "Failed",  # Set status based on score
                score=score
            )

            # Cleanup temporary files
            if os.path.exists(cpp_file):
                os.remove(cpp_file)
                print(f"Removed temporary file: {cpp_file}")
            else:
                print(f"CPP file not found: {cpp_file}")

            if os.path.exists(executable_file):
                os.remove(executable_file)
                print(f"Removed executable file: {executable_file}")
            else:
                print(f"Executable file not found: {executable_file}")

            return JsonResponse({'results': results})

        except Problem.DoesNotExist:
            return JsonResponse({'error': 'Problem not found'}, status=404)
        except json.JSONDecodeError as e:
            error_message = f'Invalid JSON format: {str(e)}'
            return JsonResponse({'error': error_message}, status=400)
        except Exception as e:
            error_message = f'An unexpected error occurred: {str(e)}'
            return JsonResponse({'error': error_message}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# def parse_errors(stderr):
#     return stderr.strip()

























def contest_not_started(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    time_until_start = (contest.start_time - now()).total_seconds()
    return render(request, 'contest_not_started.html', {
        'contest': contest,
        'time_until_start_seconds': int(time_until_start),
        'start_time_formatted': contest.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })

def contest_started(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    time_left = (contest.end_time - now()).total_seconds()
    return render(request, 'contest_started.html', {
        'contest': contest,
        'time_left_seconds': int(time_left),
    })

def contest_ended(request, contest_id):
    contest = get_object_or_404(Contest, pk=contest_id)
    leaderboard = contest.get_leaderboard()  # Assumes a method to retrieve the leaderboard
    return render(request, 'contest_ended.html', {
        'contest': contest,
        'leaderboard': leaderboard,
    })
