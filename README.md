# SkillBridge Attendance API

##  Live API

(Add after deployment)

```
Base URL: https://your-api-url.com
```

---

## Tech Stack

* Python (Flask)
* MySQL
* SQLAlchemy
* JWT (PyJWT)
* Pytest

---

##  Local Setup

```bash
git clone <your-repo>
cd skillbridge-api

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt

# create .env
copy .env.example .env

# run migrations / create tables
python src\create_tables.py

# seed data
python src\seed.py

# run server
python src\app.py
```

---

##  Test Accounts

| Role               | Email                                         | Password |
| ------------------ | --------------------------------------------- | -------- |
| Student            | [student1@test.com](mailto:student1@test.com) | pass123  |
| Trainer            | [trainer1@test.com](mailto:trainer1@test.com) | pass123  |
| Institution        | [inst1@test.com](mailto:inst1@test.com)       | pass123  |
| Programme Manager  | [pm@test.com](mailto:pm@test.com)             | pass123  |
| Monitoring Officer | [monitor@test.com](mailto:monitor@test.com)   | pass123  |

---

##  JWT Structure

### Access Token

```json
{
  "user_id": 1,
  "role": "student",
  "iat": "...",
  "exp": "...",
  "type": "access"
}
```

### Monitoring Token

```json
{
  "user_id": 5,
  "role": "monitoring_officer",
  "type": "monitoring",
  "exp": "1 hour"
}
```

---

## 📡 API Endpoints

### Auth

* POST /auth/signup
* POST /auth/login
* POST /auth/monitoring-token

### Batch

* POST /batches
* POST /batches/{id}/invite
* POST /batches/join

### Sessions

* POST /sessions
* GET /sessions/{id}/attendance

### Attendance

* POST /attendance/mark

### Summary

* GET /batches/{id}/summary
* GET /institutions/{id}/summary
* GET /programme/summary

### Monitoring

* GET /monitoring/attendance

---

##  Key Design Decisions

* Used JWT for authentication and RBAC
* Implemented invite-token system for batch joining
* Used many-to-many relationship for students and batches
* Separate monitoring token for secure read-only access

---

## ⚠️What’s Working

* All endpoints implemented
* Role-based access control enforced
* Validation and error handling implemented
* Monitoring dual-token system working
* Tests passing

---

##  What could be improved

* Better centralized error handling
* Pagination for large datasets
* Token revocation system (not implemented)
* Rate limiting

---

##  Security Consideration

Current issue:

* Tokens are not revocable once issued

Improvement:

* Use token blacklist / Redis-based invalidation

---

##  Tests

Run:

```bash
pytest
```

---

##  Deployment

(Add your deployed URL here)

---

##  With more time

* Add refresh tokens
* Add admin dashboard
* Improve logging and monitoring
