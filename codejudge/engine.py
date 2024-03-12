import json
import subprocess
import os
import re
from typing import Dict

import openai as openai
from colorama import Fore, Style
from dotenv import load_dotenv

load_dotenv()
class CodeJudge:
    """A class designed to judge C++ code submissions by analyzing, compiling, and testing them."""

    def __init__(self, problem: str, submissions_dir: str = "students_submission",
                 testcases_dir: str = "testcases") -> None:
        self.submissions_dir = submissions_dir
        self.testcases_dir = testcases_dir
        self.patterns = {
            'for_loops': r'\bfor\s*\([^)]+\)',
            'while_loops': r'\bwhile\s*\([^)]+\)',
            'if_statements': r'\bif\s*\([^)]+\)',
            'variable_declarations': r'\b(int|float|double)\s+\w+',
            'proper_datatype_usage': r'\b(int|float|double)\s+\w+',
            'while_syntax': r'\bwhile\s*\(\s*\w+\s*(==|!=|<|>|<=|>=)\s*\w+\s*\)',
            'if_syntax': r'\bif\s*\(\s*\w+\s*(==|!=|<|>|<=|>=)\s*\w+\s*\)'
        }
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.problem = problem

    def _analyze_cpp_code(self, source_path: str) -> Dict[str, int]:
        """Analyzes C++ code for various patterns, returning a dictionary of pattern counts."""
        analysis_results = {key: 0 for key in self.patterns}
        try:
            with open(source_path, 'r', encoding='utf-8') as file:
                code = file.read()
                for key, pattern in self.patterns.items():
                    matches = re.findall(pattern, code)
                    analysis_results[key] = len(matches)
        except Exception as e:
            print(f"Error reading file {source_path}: {e}")
        return analysis_results

    def _compile_program(self, source_path: str, executable_name: str = "program") -> bool:
        """Compiles a C++ program, returning True if successful."""
        compile_command = ["g++", source_path, "-o", executable_name]
        try:
            result = subprocess.run(compile_command, capture_output=True, text=True)
            # if result.returncode != 0:
            # print(Fore.RED + result.stderr + Style.RESET_ALL)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(Fore.RED + f"Compilation error: {e}" + Style.RESET_ALL)
            return False

    def _run_test(self, executable_name: str, input_file: str, expected_output) -> tuple[bool, str]:
        """Runs a test case on the compiled executable against an expected output, returning True if the output matches."""
        try:
            with open(input_file, 'r', encoding='utf-8') as file:
                result = subprocess.run(["./" + executable_name], stdin=file, capture_output=True, text=True)
                # 🚨 this part is specific to the problem, so you need to change it according to your problem
                match = re.search(r'\d+\.\d{2}', result.stdout.strip().lower())
                _output = match.group(0)
                return (expected_output == _output, _output)
        except Exception as e:
            print(f"Error running test {executable_name} with input {input_file}: {e}")
            return False

    def _get_expected_output(self, expected_output_file: str) -> str:
        """Reads and returns the expected output from a file."""
        try:
            with open(expected_output_file, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            print(f"Error reading expected output file {expected_output_file}: {e}")
            return ""

    def _get_GPT3_response(self, submission_path: str) -> str:
        """Reads the student's submission and returns a response from GPT-3.5."""
        try:
            with open(submission_path, 'r', encoding='utf-8') as file:
                code = file.read().strip()
            chat_completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": f"""Review this student's submission to identify any errors that caused the compilation failure. Provide your findings in a list of bullet points. Evaluate the submission to determine if it worth a manual review. Consider the following criteria for your assessment:
*Are the mistakes minor, such as syntax errors that can be easily corrected, or are they fundamental misunderstandings of the programming concepts?
*Despite the errors, has the student demonstrated a logical and correct approach to solving the majority of the question?
Based on these considerations, advise whether the student's work, notwithstanding the identified errors, is essentially correct and whether it warrants my time for a more detailed manual reviewBased on this requirements: "{self.problem}"
CODE:
```cpp
{code}
```
%Response on JSON with the list and a boolean.NO YAPPING.
    """}],
                temperature=0.0
            )
            return json.loads(chat_completion.choices[0].message.content)
        except Exception as e:
            print(f"Error reading expected output file {submission_path}: {e}")
            return ""

    def process_submissions(self) -> None:
        """Processes all submissions by analyzing, compiling, and testing them. Reports results."""
        results = {}
        count = 0
        try:
            submissions = os.listdir(self.submissions_dir)
        except Exception as e:
            print(f"Error accessing submissions directory {self.submissions_dir}: {e}")
            return

        for submission in submissions:
            count += 1
            submission_path = os.path.join(self.submissions_dir, submission)
            submission_name = os.path.splitext(submission)[0]
            results[submission_name] = {'Compiled': False, 'Tests': {}, 'Analysis': {}}

            analysis_results = self._analyze_cpp_code(submission_path)
            results[submission_name]['Analysis'] = analysis_results
            print(f"\nAnalysis for {submission}: {analysis_results}")

            if self._compile_program(submission_path):
                results[submission_name]['Compiled'] = True
                for test in os.listdir(self.testcases_dir):
                    test_path = os.path.join(self.testcases_dir, test)
                    input_file = os.path.join(test_path, "input.txt")
                    expected_output = self._get_expected_output(
                        os.path.join(self.testcases_dir, test, "expected_output.txt"))
                    # 🚨 the next two lines are specific to the problem, so you need to change it according to your problem
                    match = re.search(r'\d+\.\d{2}', expected_output)
                    expected_output = match.group(0)
                    passed, actual_output = self._run_test("program", input_file, expected_output)
                    test_result = 'Passed' if passed else 'Failed'
                    results[submission_name]['Tests'][test] = test_result
                    print(
                        Fore.GREEN + f"{test}: Passed" + Style.RESET_ALL if passed else Fore.RED + f"{test}: Failed\nExpected: {expected_output}\nGot: {actual_output}" + Style.RESET_ALL)
            else:
                print(Fore.RED + f"{submission}: Compilation failed." + Style.RESET_ALL)
                response = self._get_GPT3_response(submission_path)
                print(Fore.BLUE + str(response) + Style.RESET_ALL)

        print(f"\nTotal submissions processed: {count}")