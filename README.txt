EDUSUCCESS AI - PYTHON 3.14 VERSION

Run:
py -m pip install -r requirements.txt
py -m streamlit run app.py

NEW STUDENT WORKFLOW
1. Open AI Risk Simulator.
2. Enter Student Name, Department and Year.
3. Adjust attendance, Maths, Programming, Assignment score and missed assignments.
4. Click Predict Student Risk.
5. The AI predicts High/Medium/Low risk.
6. The student is automatically appended to students.csv.
7. A unique Student ID (STU016, STU017, ...) is generated.
8. The saved student appears in Student Analysis, Teacher Analytics and Overview.

The CSV contains a Student Name column and keeps the original sample students.
The AI is a lightweight K-Nearest Neighbours implementation using Python standard-library code.
