from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "careertrack-secret-key"


# =========================
# DATABASE
# =========================

def create_database():

    conn = sqlite3.connect("student.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            college TEXT,
            skills TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================
# HOME
# =========================

@app.route("/")
def home():

    return render_template("index.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        college = request.form["college"]

        conn = sqlite3.connect("student.db")

        conn.execute("""
            INSERT INTO students
            (name, email, password, college, skills)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, password, college, ""))

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("student.db")

        student = conn.execute("""
            SELECT * FROM students
            WHERE email = ? AND password = ?
        """, (email, password)).fetchone()

        conn.close()

        if student:

            session["student_id"] = student[0]

            return redirect(
                url_for(
                    "dashboard",
                    student_id=student[0]
                )
            )

        return "Invalid email or password!"

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]

    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    if student is None:
        return "Student not found. Please login again."

    if len(student) >= 6 and student[5]:

        student_skills = [
            skill.strip().lower()
            for skill in student[5].split(",")
            if skill.strip()
        ]

    else:

        student_skills = []


    career_skills = {

        "Java Developer": [
            "java",
            "sql",
            "spring boot",
            "git",
            "html",
            "css"
        ],

        "Python Developer": [
            "python",
            "sql",
            "flask",
            "git",
            "html",
            "css"
        ],

        "Data Analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "pandas"
        ],

        "Web Developer": [
            "html",
            "css",
            "javascript",
            "python",
            "sql"
        ]

    }


    career_results = []

    for career, required_skills in career_skills.items():

        matched_skills = []

        for skill in required_skills:

            if skill in student_skills:
                matched_skills.append(skill)

        percentage = round(
            (len(matched_skills) /
             len(required_skills)) * 100
        )

        career_results.append({

            "career": career,

            "percentage": percentage,

            "matched_skills": matched_skills

        })


    career_results.sort(
        key=lambda x: x["percentage"],
        reverse=True
    )


    if career_results:

        top_career = career_results[0]

    else:

        top_career = {

            "career": "Explore Your Career",

            "percentage": 0,

            "matched_skills": []

        }


    return render_template(

        "dashboard.html",

        student=student,

        top_career=top_career

    )


# =========================
# PROFILE
# =========================

@app.route("/profile")
def profile():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]

    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    if student is None:

        return "Student not found. Please login again."

    return render_template(
        "profile.html",
        student=student
    )


# =========================
# SKILLS
# =========================

@app.route("/skills", methods=["GET", "POST"])
def skills():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]


    if request.method == "POST":

        student_id = request.form.get("student_id")

        if not student_id:
            student_id = session["student_id"]

        new_skills = request.form.get(
            "skills",
            ""
        )

        conn = sqlite3.connect("student.db")

        conn.execute("""
            UPDATE students
            SET skills = ?
            WHERE id = ?
        """, (new_skills, student_id))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "skills",
                student_id=student_id
            )
        )


    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()


    if student is None:

        return "Student not found. Please login again."


    return render_template(
        "skills.html",
        student=student
    )


# =========================
# SKILL GAP
# =========================

@app.route("/skill-gap", methods=["GET", "POST"])
def skill_gap():

    # Check if student is logged in
    if "student_id" not in session:
        return redirect(url_for("login"))

    # Get student ID
    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]

    # Connect to database
    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()

    # Check student exists
    if student is None:
        return (
            "Student not found. "
            "Please open Skill Gap from your Dashboard."
        )

    # Career required skills
    career_skills = {

        "Java Developer": [
            "Java",
            "SQL",
            "Spring Boot",
            "Git",
            "HTML",
            "CSS"
        ],

        "Python Developer": [
            "Python",
            "SQL",
            "Flask",
            "Git",
            "HTML",
            "CSS"
        ],

        "Data Analyst": [
            "Python",
            "SQL",
            "Excel",
            "Power BI",
            "Pandas"
        ],

        "Web Developer": [
            "HTML",
            "CSS",
            "JavaScript",
            "Python",
            "SQL"
        ]
    }

    # Skill recommendations
    recommendations = {

        "SQL":
            "Learn SQL basics and practice database queries.",

        "Spring Boot":
            "Learn Spring Boot and build a simple REST API.",

        "Git":
            "Learn Git commands and practice using GitHub.",

        "HTML":
            "Learn HTML and create basic web pages.",

        "CSS":
            "Learn CSS and practice designing web pages.",

        "Java":
            "Learn Java fundamentals and practice coding problems.",

        "Python":
            "Learn Python fundamentals and build small projects.",

        "Flask":
            "Learn Flask and build a simple web application.",

        "JavaScript":
            "Learn JavaScript basics and practice DOM manipulation.",

        "Excel":
            "Learn Excel formulas, charts, and data analysis.",

        "Power BI":
            "Learn Power BI and create interactive dashboards.",

        "Pandas":
            "Learn Pandas for data cleaning and analysis."
    }

    # Default values
    career = ""
    required_skills = []
    matched_skills = []
    missing_skills = []
    skill_recommendations = []
    percentage = 0

    # When user selects a career
    if request.method == "POST":

        career = request.form.get("career", "")

        # Get required skills for selected career
        required_skills = career_skills.get(career, [])

        # Get student's existing skills
        if len(student) >= 6 and student[5]:

            student_skills = [
                skill.strip().lower()
                for skill in student[5].split(",")
                if skill.strip()
            ]

        else:
            student_skills = []

        # Compare student's skills with required skills
        for skill in required_skills:

            if skill.lower() in student_skills:

                matched_skills.append(skill)

            else:

                missing_skills.append(skill)

                if skill in recommendations:

                    skill_recommendations.append(
                        recommendations[skill]
                    )

        # Calculate skill percentage
        if required_skills:

            percentage = round(
                (len(matched_skills) /
                 len(required_skills)) * 100
            )

        else:

            percentage = 0

    # Send data to skill_gap.html
    return render_template(
        "skill_gap.html",

        student=student,

        career=career,

        required_skills=required_skills,

        matched_skills=matched_skills,

        # Your HTML uses have_skills
        have_skills=matched_skills,

        missing_skills=missing_skills,

        skill_recommendations=skill_recommendations,

        percentage=percentage
    )


# =========================
# INTERNSHIPS
# =========================

@app.route("/internships")
def internships():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]


    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()


    if student is None:

        return "Student not found. Please login again."


    if len(student) >= 6 and student[5]:

        student_skills = [

            skill.strip().lower()

            for skill in student[5].split(",")

            if skill.strip()

        ]

    else:

        student_skills = []


    internship_data = [

        {
            "title": "Python Developer Intern",
            "company": "ABC Technologies",
            "skills": ["Python", "Flask", "SQL"],
            "location": "Coimbatore",
            "duration": "3 Months",
            "link": "https://www.linkedin.com/jobs/"
        },

        {
            "title": "Java Developer Intern",
            "company": "XYZ Solutions",
            "skills": ["Java", "SQL", "Spring Boot"],
            "location": "Chennai",
            "duration": "6 Months",
            "link": "https://www.linkedin.com/jobs/"
        },

        {
            "title": "Data Analyst Intern",
            "company": "DataTech",
            "skills": ["Python", "SQL", "Excel", "Power BI"],
            "location": "Coimbatore",
            "duration": "3 Months",
            "link": "https://www.linkedin.com/jobs/"
        }

    ]


    internships_list = []


    for internship in internship_data:

        matched_skills = []
        missing_skills = []


        for skill in internship["skills"]:

            if skill.lower() in student_skills:

                matched_skills.append(skill.lower())

            else:

                missing_skills.append(skill.lower())


        total_skills = len(internship["skills"])

        match_count = len(matched_skills)


        match_percentage = round(

            (match_count /
             total_skills) * 100

        )


        internship["matched_skills"] = matched_skills

        internship["missing_skills"] = missing_skills

        internship["match_count"] = match_count

        internship["total_skills"] = total_skills

        internship["match_percentage"] = match_percentage


        internship["skills"] = ", ".join(
            internship["skills"]
        )


        internships_list.append(internship)


    internships_list.sort(

        key=lambda x:
            x["match_percentage"],

        reverse=True

    )


    return render_template(

        "internships.html",

        student=student,

        internships=internships_list

    )


# =========================
# CAREER RECOMMENDATIONS
# =========================

@app.route("/recommendations")
def recommendations():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]


    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()


    if student is None:

        return "Student not found. Please login again."


    if len(student) >= 6 and student[5]:

        student_skills = [

            skill.strip().lower()

            for skill in student[5].split(",")

            if skill.strip()

        ]

    else:

        student_skills = []


    career_skills = {

        "Java Developer": [
            "java",
            "sql",
            "spring boot",
            "git",
            "html",
            "css"
        ],

        "Python Developer": [
            "python",
            "sql",
            "flask",
            "git",
            "html",
            "css"
        ],

        "Data Analyst": [
            "python",
            "sql",
            "excel",
            "power bi",
            "pandas"
        ],

        "Web Developer": [
            "html",
            "css",
            "javascript",
            "python",
            "sql"
        ]

    }


    career_results = []


    for career, required_skills in career_skills.items():

        matched_skills = []


        for skill in required_skills:

            if skill in student_skills:

                matched_skills.append(skill)


        match_percentage = round(

            (len(matched_skills) /
             len(required_skills)) * 100

        )


        career_results.append({

            "career": career,

            "matched_skills": matched_skills,

            "match_percentage": match_percentage

        })


    career_results.sort(

        key=lambda x:
            x["match_percentage"],

        reverse=True

    )


    return render_template(

        "recommendations.html",

        student=student,

        career_results=career_results

    )


# =========================
# COURSES
# =========================

@app.route("/courses")
def courses():

    if "student_id" not in session:
        return redirect(url_for("login"))

    student_id = request.args.get("student_id")

    if not student_id:
        student_id = session["student_id"]


    conn = sqlite3.connect("student.db")

    student = conn.execute("""
        SELECT * FROM students
        WHERE id = ?
    """, (student_id,)).fetchone()

    conn.close()


    if student is None:

        return "Student not found. Please login again."


    if len(student) >= 6 and student[5]:

        student_skills = [

            skill.strip().lower()

            for skill in student[5].split(",")

            if skill.strip()

        ]

    else:

        student_skills = []


    # =========================
    # COURSE DATA
    # =========================

    course_data = {

        "sql": {

            "course": "SQL for Beginners",

            "description":
                "Learn SQL basics, queries, joins and databases.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/sql/"

        },

        "python": {

            "course": "Python Programming",

            "description":
                "Learn Python fundamentals and build small projects.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/python/"

        },

        "java": {

            "course": "Java Programming",

            "description":
                "Learn Java fundamentals, OOP and coding concepts.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/java/"

        },

        "spring boot": {

            "course": "Spring Boot",

            "description":
                "Learn Spring Boot and build REST APIs.",

            "platform": "Spring",

            "link":
                "https://spring.io/quickstart"

        },

        "git": {

            "course": "Git & GitHub",

            "description":
                "Learn version control and manage your projects.",

            "platform": "GitHub",

            "link":
                "https://skills.github.com/"

        },

        "html": {

            "course": "HTML Fundamentals",

            "description":
                "Learn HTML and create structured web pages.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/html/"

        },

        "css": {

            "course": "CSS Fundamentals",

            "description":
                "Learn CSS and design modern web pages.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/css/"

        },

        "javascript": {

            "course": "JavaScript Basics",

            "description":
                "Learn JavaScript and add interactivity to websites.",

            "platform": "W3Schools",

            "link":
                "https://www.w3schools.com/js/"

        },

        "flask": {

            "course": "Flask Web Development",

            "description":
                "Learn Flask and build Python web applications.",

            "platform": "Flask",

            "link":
                "https://flask.palletsprojects.com/en/stable/tutorial/"

        },

        "excel": {

            "course": "Excel for Data Analysis",

            "description":
                "Learn formulas, charts and data analysis using Excel.",

            "platform": "Microsoft",

            "link":
                "https://support.microsoft.com/en-us/excel"

        },

        "power bi": {

            "course": "Power BI",

            "description":
                "Learn to create interactive dashboards and reports.",

            "platform": "Microsoft",

            "link":
                "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"

        },

        "pandas": {

            "course": "Pandas for Data Analysis",

            "description":
                "Learn data cleaning and analysis using Pandas.",

            "platform": "Pandas",

            "link":
                "https://pandas.pydata.org/docs/getting_started/intro_tutorials/"

        }

    }


    # =========================
    # RECOMMENDED COURSES
    # =========================

    recommended_courses = []


    for skill, course in course_data.items():

        if skill not in student_skills:

            recommended_courses.append(course)


    return render_template(

        "courses.html",

        student=student,

        recommended_courses=recommended_courses

    )


# =========================
# SETTINGS
# =========================

@app.route("/settings")
def settings():

    if "student_id" not in session:
        return redirect(url_for("login"))

    return render_template("settings.html")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    create_database()

    app.run(debug=True)