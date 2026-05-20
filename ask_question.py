import sqlite3

# keep asking until user enters a number
while True:
    user_input = input("Enter interview session number: ")

    if user_input.isdigit():
        session_id = int(user_input)
        break
    else:
        print("Please enter a valid number!")


conn = sqlite3.connect("interview.db")
cursor = conn.cursor()

category = "HR"

# get random question
cursor.execute(
    "SELECT question FROM questions WHERE category = ? ORDER BY RANDOM() LIMIT 1",
    (category,)
)

result = cursor.fetchone()

if result:
    question = result[0]
    print("Interviewer:", question)

    # user types answer
    answer = input("You: ")

    # save answer into database
    cursor.execute(
    "INSERT INTO answers (session_id, question, user_answer) VALUES (?, ?, ?)",
    (session_id, question, answer)
)


    conn.commit()
    print("Answer saved!")
else:
    print("No question found")

conn.close()
