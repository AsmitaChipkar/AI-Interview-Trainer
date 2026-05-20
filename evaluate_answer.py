import sqlite3

conn = sqlite3.connect("interview.db")
cursor = conn.cursor()

cursor.execute("SELECT question, user_answer FROM answers ORDER BY id DESC LIMIT 1")
data = cursor.fetchone()

if data:
    question = data[0]
    answer = data[1]

    print("Question:", question)
    print("Your Answer:", answer)

    score = 0
    suggestions = []

    # Rule 1 — length
    if len(answer.split()) > 8:
        score += 5
        print("Good: Answer length is detailed")
    else:
        suggestions.append("Explain your answer in more detail")

    # Rule 2 — keywords
    keywords = ["project", "experience", "team", "skills", "learn"]
    found = False

    for word in keywords:
        if word in answer.lower():
            found = True
            score += 5
            break

    if not found:
        suggestions.append("Mention skills, projects or experience")

    # Final score
    print("Score:", score, "/10")

    # Suggestions output
    if suggestions:
        print("\nSuggestions:")
        for s in suggestions:
            print("-", s)
    else:
        print("Excellent answer!")

else:
    print("No answer found")

conn.close()
