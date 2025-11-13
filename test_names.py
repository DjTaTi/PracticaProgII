from app import load_questions, prepare_quiz

questions = load_questions()
prepared = prepare_quiz(questions[:5], False, False)

for q in prepared:
    print(f"ID: {q['id']}")
    print(f"Name would be: q_{q['id']}")
    print(f"Safe ID: {q['id'].replace('.', '_')}")
    print("---")
