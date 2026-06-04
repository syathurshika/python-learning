# Quiz App

questions = [
    {
        "question": "What is the capital of France?",
        "options": ["A. London", "B. Paris", "C. Berlin", "D. Madrid"],
        "answer": "B"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["A. Venus", "B. Jupiter", "C. Mars", "D. Saturn"],
        "answer": "C"
    },
    {
        "question": "What is 8 × 7?",
        "options": ["A. 54", "B. 56", "C. 64", "D. 48"],
        "answer": "B"
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": [
            "A. William Shakespeare",
            "B. Charles Dickens",
            "C. Mark Twain",
            "D. Jane Austen"
        ],
        "answer": "A"
    },
    {
        "question": "Which programming language is this code written in?",
        "options": ["A. Java", "B. C++", "C. Python", "D. JavaScript"],
        "answer": "C"
    }
]

score = 0

print("=" * 50)
print("WELCOME TO THE QUIZ APP")
print("=" * 50)

for i, q in enumerate(questions, start=1):
    print(f"\nQuestion {i}:")
    print(q["question"])

    for option in q["options"]:
        print(option)

    user_answer = input("Your answer (A/B/C/D): ").upper().strip()

    if user_answer == q["answer"]:
        print("✅ Correct!")
        score += 1
    else:
        print(f"❌ Wrong! Correct answer: {q['answer']}")

print("\n" + "=" * 50)
print("QUIZ COMPLETE")
print("=" * 50)

print(f"Your score: {score}/{len(questions)}")

percentage = (score / len(questions)) * 100
print(f"Percentage: {percentage:.1f}%")

if percentage >= 80:
    print("🏆 Excellent!")
elif percentage >= 60:
    print("👍 Good job!")
else:
    print("📚 Keep practicing!")