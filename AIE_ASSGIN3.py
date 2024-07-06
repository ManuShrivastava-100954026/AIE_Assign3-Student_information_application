from flask import Flask, request, jsonify, render_template, redirect, url_for
import pyodbc
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

server = 'DESKTOP-BPUAQ4F'
database = 'Student_info'
username = 'DESKTOP-BPUAQ4F\mymai'
password = ''
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'


def get_db_connection():
    conn = pyodbc.connect(connection_string)
    return conn

class StudentResource(Resource):
    def get(self, student_id=None):
        conn = get_db_connection()
        cursor =conn.cursor()
        if student_id:
            cursor.execute("SELECT * FROM students WHERE students_id = ?", student_id)
            student = cursor.fetchone()
            if not student:
                return{'error':'Student not found'},404
            return jsonify(self.student_to_dict(student))
        cursor.execute("SELECT * FROM students")
        students= cursor.fetchall()
        return jsonify([self.student_to_dict(student) for student in students])
    
    def post(self):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (first_name, last_name, dob, amount_due) VALUES (?,?,?,?)",data['first_name'],data['last_name'],data['dob'],data['amount_due'])
        conn.commit()
        return {'message':'Student created'},201
    
    def put(self, student_id):
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET first_name = ?, last_name=?, dob=?, amount_due=? WHERE student_id=?",data['first_name'],data['last_name'],data['dob'],data['amount_due'])
        conn.commit()
        return {'message':'Student updated'}
    
    def delete(self,student_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id=?",student_id)
        conn.commit()
        return {'message':'Student record deleted!'}
    
    def student_to_dict(self,student):
        return{'student_id':student[0],'first_name':student[1],'last_name':student[2],'dob':student[3],'amount_due':student[4]}
    
api.add_resource(StudentResource,'/students','/students/<int:student_id>')

'''Front end part of the applcation using flask and HTML templates'''
@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        amount_due = request.form['amount_due']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (first_name, last_name, dob, amount_due) VALUES (?, ?, ?, ?)",
                       first_name, last_name, dob, amount_due)
        conn.commit()
        return redirect(url_for('index'))
    return render_template('students.html', action="Add")

@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        amount_due = request.form['amount_due']
        cursor.execute("UPDATE students SET first_name = ?, last_name = ?, dob = ?, amount_due = ? WHERE student_id = ?",
                       first_name, last_name, dob, amount_due, student_id)
        conn.commit()
        return redirect(url_for('index'))
    cursor.execute("SELECT * FROM students WHERE student_id = ?", student_id)
    student = cursor.fetchone()
    return render_template('students.html', student=student, action="Edit")

@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", student_id)
    conn.commit()
    return redirect(url_for('index'))


if __name__=='__main__':
    app.run(debug=True)