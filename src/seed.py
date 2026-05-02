from app import create_app
from extensions import db
from models import User, Batch, Session, Attendance
from werkzeug.security import generate_password_hash
from datetime import datetime, time, date

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    # Create users
    users = []

    # Institutions
    inst1 = User(name="Institution 1", email="inst1@test.com", hashed_password=generate_password_hash("pass123"), role="institution")
    inst2 = User(name="Institution 2", email="inst2@test.com", hashed_password=generate_password_hash("pass123"), role="institution")

    # Trainers
    trainers = [
        User(name=f"Trainer {i}", email=f"trainer{i}@test.com", hashed_password=generate_password_hash("pass123"), role="trainer")
        for i in range(1, 5)
    ]

    # Students
    students = [
        User(name=f"Student {i}", email=f"student{i}@test.com", hashed_password=generate_password_hash("pass123"), role="student")
        for i in range(1, 16)
    ]

    # Programme Manager & Monitoring
    pm = User(name="PM", email="pm@test.com", hashed_password=generate_password_hash("pass123"), role="programme_manager")
    monitor = User(name="Monitor", email="monitor@test.com", hashed_password=generate_password_hash("pass123"), role="monitoring_officer")

    db.session.add_all([inst1, inst2] + trainers + students + [pm, monitor])
    db.session.commit()

    # Create batches
    batches = [
        Batch(name=f"Batch {i}", institution_id=1)
        for i in range(1, 4)
    ]

    db.session.add_all(batches)
    db.session.commit()

    # Assign students to batches
    for i, student in enumerate(students):
        batches[i % 3].students.append(student)

    db.session.commit()

    # Create sessions
    sessions = []
    for i in range(1, 9):
        session = Session(
            title=f"Session {i}",
            batch_id=batches[i % 3].id,
            trainer_id=trainers[i % 4].id,
            date=date(2026, 5, i),
            start_time=time(10, 0),
            end_time=time(12, 0)
        )
        sessions.append(session)

    db.session.add_all(sessions)
    db.session.commit()

    # Create attendance
    for session in sessions:
        for student in students[:5]:
            attendance = Attendance(
                session_id=session.id,
                student_id=student.id,
                status="present"
            )
            db.session.add(attendance)

    db.session.commit()

    print("Seed data created successfully")