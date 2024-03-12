# CodeJudge: C++ Code Evaluation System

Automate the assessment of C++ programming assignments by analyzing, compiling, and testing against predefined test cases. Leverages OpenAI's GPT for feedback on failed compilations 🤖.

## Features ✨

- Code Analysis for patterns like loops and conditionals.
- Compilation & Testing against test cases.
- Feedback Generation using OpenAI's GPT for failed compilations.
- Interactive Jupyter Notebook for manual review and interaction.

## Setup   🛠️

1. **Clone**: `git clone https://github.com/yourusername/codejudge.git`
2. **Install Dependencies**: `pip install -r requirements.txt`
3. **Environment Variable**: `export OPENAI_API_KEY='your_key_here'`
4. **Launch Notebook**: navigate to lab.ipynb and run the cells.
## Initial Data Setup 📂

Populate the `students_submission` and `testcases` folders with your initial data as follows:

- **students_submission/**: Place the C++ source files (.cpp) here. Each file should be named as `studentName_assignmentName.cpp`.

- **testcases/**: Create a directory for each testcase containing two files: `input.txt` and `expected_output.txt`. Each directory should be named according to the testcase, for example, `Single Item Purchase Below Discount Threshold/`.

## Usage📚

- Analyze and compile C++ submissions.
- Run compiled programs against test cases.
- Generate feedback for compilation failures using GPT.