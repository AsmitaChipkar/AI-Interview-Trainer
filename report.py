import sqlite3


session_id = int(input("Enter session number to generate report: "))

conn = sqlite3.connect("interview.db")
cursor = conn.cursor()

# get all answers given in interview
cursor.execute("SELECT user_answer FROM answers WHERE session_id = ?", (session_id,))

answers = cursor.fetchall()

total_questions = len(answers)
total_score = 0

for ans in answers:
    answer = ans[0]

    score = 0

    # same evaluation logic
    if len(answer.split()) > 8:
        score += 5

    keywords = ["project", "experience", "team", "skills", "learn"]
    for word in keywords:
        if word in answer.lower():
            score += 5
            break

    total_score += score

# avoid divide by zero
if total_questions > 0:
    average = total_score / total_questions
else:
    average = 0

print("\n----- INTERVIEW REPORT -----")
print("Questions Attempted:", total_questions)
print("Average Score:", round(average, 2), "/10")

# performance category
if average >= 8:
    print("Performance: Excellent")
elif average >= 5:
    print("Performance: Good")
else:
    print("Performance: Needs Improvement")

conn.close()
