from flask import Flask, jsonify, redirect, render_template, request, session, url_for
import datetime
import calendar

app = Flask(__name__)
app.secret_key = "learning-progress-demo-key"

USERS = {
    "riya@example.com": {
        "name": "Riya Sharma",
        "email": "riya@example.com",
        "password": "1234",
        "role": "Full Stack Python Student",
        "batch": "API Training - Day 4",
        "city": "Hyderabad",
        "avatar": "RS"
    }
}

# Add a teacher account (also referenced in USERS) and mapping to their students
USERS["teacher@example.com"] = {
    "name": "Asha Gupta",
    "email": "teacher@example.com",
    "password": "teachpass",
    "role": "Teacher",
    "batch": "Instructors",
    "city": "Hyderabad",
    "avatar": "AG"
}

TEACHERS = {
    "teacher@example.com": {
        "name": "Asha Gupta",
        "email": "teacher@example.com",
        # List student emails this teacher is responsible for
        "students": ["riya@example.com"]
    }
}

STUDENTS = {
    "riya@example.com": {
        "course": "Full Stack Python",
        "lms_progress": {
            "completed_lessons": 34,
            "total_lessons": 50,
            "attendance_percentage": 92,
            "last_topic": "REST API Basics"
        },
        "coding_platform_stats": {
            "problems_solved": 76,
            "easy": 36,
            "medium": 30,
            "hard": 10,
            "current_streak": 8
        },
        "weekly_problems": [8, 12, 9, 15, 11, 13, 8],
        "monthly_performance": [62, 68, 73, 79, 84, 88],
        "weak_areas": ["Authentication", "SQL Joins", "Error Handling"],
        "skills": {
            "Python": 82,
            "Flask": 70,
            "SQL": 64,
            "HTML/CSS": 78,
            "JavaScript": 58
        },
        "assignments": [
            {"title": "Build Login API", "status": "Completed", "score": 90, "due": "May 22"},
            {"title": "CRUD API Practice", "status": "In Progress", "score": 65, "due": "May 27"},
            {"title": "API Documentation", "status": "Pending", "score": 0, "due": "May 30"}
        ],
        "course_modules": [
            {"title": "REST API Basics", "lessons": 8, "completed": 8, "level": "Beginner"},
            {"title": "Flask Routing", "lessons": 10, "completed": 7, "level": "Beginner"},
            {"title": "Authentication", "lessons": 7, "completed": 3, "level": "Intermediate"},
            {"title": "Database APIs", "lessons": 9, "completed": 5, "level": "Intermediate"}
        ],
        "problem_bank": [
            {"title": "Return Student Progress", "difficulty": "Easy", "topic": "GET API", "status": "Solved", "accuracy": 96},
            {"title": "Create Assignment Record", "difficulty": "Medium", "topic": "POST API", "status": "Attempted", "accuracy": 72},
            {"title": "Validate Login Request", "difficulty": "Medium", "topic": "Validation", "status": "Todo", "accuracy": 0},
            {"title": "Build Analytics Response", "difficulty": "Hard", "topic": "Data Aggregation", "status": "Todo", "accuracy": 0}
        ],
        "study_plan": [
            {"time": "09:00 AM", "task": "Revise Flask routes", "type": "Lesson"},
            {"time": "11:30 AM", "task": "Solve 3 API problems", "type": "Practice"},
            {"time": "04:00 PM", "task": "Complete CRUD assignment", "type": "Assignment"}
        ],
        "recommended_actions": [
            "Revise API authentication flow",
            "Practice 5 SQL join questions",
            "Add validation and error responses in Flask routes"
        ]
        ,
        # login_history stores ISO dates (YYYY-MM-DD) when the student logged in
        "login_history": ["2026-05-28", "2026-05-30", "2026-05-31"]
    }
}


def current_user():
    email = session.get("user_email")
    if not email:
        return None, None
    return USERS.get(email), STUDENTS.get(email)


def require_login():
    user, progress = current_user()
    if user is None:
        return None, None, redirect(url_for("login"))
    return user, progress, None


def require_teacher():
    email = session.get("user_email")
    if not email:
        return None, redirect(url_for("teacher_login"))
    user = USERS.get(email)
    if not user or str(user.get("role","")).lower() != "teacher":
        return None, redirect(url_for("teacher_login"))
    return user, None


def completion_percentage(progress):
    lms = progress["lms_progress"]
    return round((lms["completed_lessons"] / lms["total_lessons"]) * 100)


def assignment_percentage(progress):
    assignments = progress["assignments"]
    completed = sum(1 for item in assignments if item["status"] == "Completed")
    return round((completed / len(assignments)) * 100)


def dashboard_data(email):
    user = USERS[email]
    progress = STUDENTS[email]
    return {
        "profile": {
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "batch": user["batch"],
            "city": user["city"]
        },
        "completion_percentages": {
            "lms_completion": completion_percentage(progress),
            "assignment_completion": assignment_percentage(progress),
            "attendance": progress["lms_progress"]["attendance_percentage"]
        },
        "skill_dashboard": progress["skills"],
        "coding_platform_stats": progress["coding_platform_stats"],
        "weak_areas": progress["weak_areas"],
        "assignments": progress["assignments"],
        "course_modules": progress["course_modules"],
        "problem_bank": progress["problem_bank"],
        "study_plan": progress["study_plan"],
        "weekly_problems": progress["weekly_problems"],
        "monthly_performance": progress["monthly_performance"],
        "recommended_actions": progress["recommended_actions"]
    }


@app.context_processor
def inject_user():
    user, progress = current_user()
    return {"nav_user": user, "nav_progress": progress}


@app.route("/")
def home():
    if session.get("user_email"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        city = request.form.get("city", "").strip() or "Not added"

        if not name or not email or not password:
            return render_template("signup.html", error="Please fill all required fields.")

        USERS[email] = {
            "name": name,
            "email": email,
            "password": password,
            "role": "API Learning Student",
            "batch": "API Training - Day 4",
            "city": city,
            "avatar": "".join(part[0].upper() for part in name.split()[:2]) or "ST"
        }
        STUDENTS[email] = {
            "course": "Unified Learning Progress API",
            "lms_progress": {
                "completed_lessons": 18,
                "total_lessons": 50,
                "attendance_percentage": 84,
                "last_topic": "API Request Methods"
            },
            "coding_platform_stats": {
                "problems_solved": 32,
                "easy": 18,
                "medium": 11,
                "hard": 3,
                "current_streak": 4
            },
            "weekly_problems": [4, 6, 5, 7, 3, 4, 3],
            "monthly_performance": [44, 51, 58, 63, 68, 72],
            "weak_areas": ["POST Requests", "Input Validation", "Status Codes"],
            "skills": {"Python": 62, "Flask": 55, "SQL": 48, "HTML/CSS": 66, "JavaScript": 42},
            "assignments": [
                {"title": "Create Home Page", "status": "Completed", "score": 82, "due": "May 24"},
                {"title": "Signup/Login Flow", "status": "In Progress", "score": 55, "due": "May 27"},
                {"title": "Dashboard API", "status": "Pending", "score": 0, "due": "May 30"}
            ],
            "course_modules": [
                {"title": "API Request Methods", "lessons": 6, "completed": 4, "level": "Beginner"},
                {"title": "Templates and Forms", "lessons": 8, "completed": 3, "level": "Beginner"},
                {"title": "JSON Responses", "lessons": 7, "completed": 2, "level": "Intermediate"}
            ],
            "problem_bank": [
                {"title": "List All Students", "difficulty": "Easy", "topic": "GET API", "status": "Solved", "accuracy": 88},
                {"title": "Signup Form Submit", "difficulty": "Medium", "topic": "Forms", "status": "Attempted", "accuracy": 64},
                {"title": "Dashboard JSON API", "difficulty": "Medium", "topic": "JSON", "status": "Todo", "accuracy": 0}
            ],
            "study_plan": [
                {"time": "10:00 AM", "task": "Revise GET and POST", "type": "Lesson"},
                {"time": "02:00 PM", "task": "Practice form validation", "type": "Practice"},
                {"time": "06:00 PM", "task": "Update dashboard project", "type": "Project"}
            ],
            "recommended_actions": [
                "Understand GET and POST clearly",
                "Practice sending JSON in Postman",
                "Learn common HTTP status codes"
            ]
            ,
            "login_history": []
        }
        session["user_email"] = email
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = USERS.get(email)
        if user is None or user["password"] != password:
            return render_template("login.html", error="Invalid email or password.")
        session["user_email"] = email
        # Record student login day for attendance tracking (only for students)
        if email in STUDENTS:
            today = datetime.date.today().isoformat()
            history = STUDENTS[email].setdefault("login_history", [])
            if today not in history:
                history.append(today)
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = USERS.get(email)
        if user is None or user.get("password") != password or str(user.get("role","")).lower() != "teacher":
            return render_template("teacher_login.html", error="Invalid teacher credentials.")
        session["user_email"] = email
        return redirect(url_for("teacher_dashboard"))
    return render_template("teacher_login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template(
        "dashboard.html",
        user=user,
        progress=progress,
        lms_completion=completion_percentage(progress),
        assignment_completion=assignment_percentage(progress)
    )


@app.route("/profile")
def profile():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("profile.html", user=user, progress=progress)


@app.route("/analytics")
def analytics():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("analytics.html", user=user, progress=progress)


@app.route("/assignments")
def assignments():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("assignments.html", user=user, progress=progress)


@app.route("/practice")
def practice():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("practice.html", user=user, progress=progress)


@app.route("/courses")
def courses():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("courses.html", user=user, progress=progress)


@app.route("/study-plan")
def study_plan():
    user, progress, redirect_response = require_login()
    if redirect_response:
        return redirect_response
    return render_template("study_plan.html", user=user, progress=progress)


@app.route("/api/students")
def api_students():
    return jsonify({
        "students": [
            {"email": email, "name": user["name"], "batch": user["batch"]}
            for email, user in USERS.items()
        ]
    })


@app.route("/api/progress/<email>")
def api_progress(email):
    email = email.lower()
    if email not in USERS:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(dashboard_data(email))


@app.route("/api/dashboard")
def api_dashboard():
    return jsonify({email: dashboard_data(email) for email in USERS})


@app.route("/teacher/dashboard")
def teacher_dashboard():
    teacher, redirect_response = require_teacher()
    if redirect_response:
        return redirect_response
    teacher_info = TEACHERS.get(teacher["email"], {})
    student_emails = teacher_info.get("students", [])
    students = []
    for e in student_emails:
        if e in USERS and e in STUDENTS:
            # compute attendance summary: last login and last-30-days activity
            history = STUDENTS[e].get("login_history", [])
            last_login = max(history) if history else None
            # count unique login days in last 30 days
            today = datetime.date.today()
            cutoff = (today - datetime.timedelta(days=30)).isoformat()
            recent = [d for d in history if d >= cutoff]
            recent_count = len(set(recent))
            percent_30 = round((recent_count / 30) * 100)
            students.append({
                "email": e,
                "name": USERS[e]["name"],
                "summary": dashboard_data(e),
                "last_login": last_login,
                "last_30_days_active": recent_count,
                "last_30_days_percent": percent_30
            })
    return render_template("teacher_dashboard.html", teacher=teacher, students=students)


@app.route("/teacher/student/<email>")
def teacher_student(email):
    teacher, redirect_response = require_teacher()
    if redirect_response:
        return redirect_response
    email = email.lower()
    if email not in USERS or email not in STUDENTS:
        return render_template("teacher_student.html", error="Student not found."), 404
    data = dashboard_data(email)
    student = USERS[email]
    # prepare calendar days for current month with activation status
    today = datetime.date.today()
    year = today.year
    month = today.month
    _, ndays = calendar.monthrange(year, month)
    login_set = set(STUDENTS[email].get("login_history", []))
    month_days = []
    for day in range(1, ndays + 1):
        dt = datetime.date(year, month, day)
        iso = dt.isoformat()
        month_days.append({"day": day, "date": iso, "active": iso in login_set})
    # recent attendance summary for display
    last_login = max(STUDENTS[email].get("login_history", [])) if STUDENTS[email].get("login_history") else None
    last_30 = 0
    cutoff = (today - datetime.timedelta(days=30)).isoformat()
    for d in set(STUDENTS[email].get("login_history", [])):
        if d >= cutoff:
            last_30 += 1
    last_30_percent = round((last_30 / 30) * 100)
    month_name = calendar.month_name[month]
    return render_template("teacher_student.html", teacher=teacher, student=student, data=data, month_days=month_days, last_login=last_login, last_30=last_30, last_30_percent=last_30_percent, month_name=month_name, year=year)
    return render_template("teacher_student.html", teacher=teacher, student=student, data=data)


if __name__ == "__main__":
    app.run(debug=True)
