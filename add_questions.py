import sqlite3

conn = sqlite3.connect("interview.db")
cursor = conn.cursor()

questions = [
    ("HR", "Tell me about yourself"),
    ("HR", "Why should we hire you"),
    ("HR", "What are your strengths and weaknesses"),
    ("Python", "What is a list in Python"),
    ("Python", "Difference between list and tuple"),
    ("Java", "What is OOPs"),
    ("Java", "What is inheritance"),
    ("C", "What is a pointer"),
    ("C", "Difference between malloc and calloc")
]

cursor.executemany("INSERT INTO questions (category, question) VALUES (?, ?)", questions)

conn.commit()
conn.close()

print("Questions added successfully!")
