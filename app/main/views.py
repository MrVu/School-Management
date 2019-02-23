from flask import render_template, session, redirect, url_for, request, sessions, flash
from flask_login import login_required, logout_user, login_user, current_user
from .forms import SubjectsAdd, StudentForm, AttendanceClass, AttendanceForm, AttendanceQuery
from . import main
from app.models import Subject, User, Student, Attendance
from app import db
from datetime import datetime

from functools import wraps


def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.role.name == "admin":
            return f(*args, **kwargs)
        else:
            flash("You need to be an admin to view this page.")
            return redirect(url_for('main.index'))

    return wrap


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('admin/admin.html', current_user=current_user)


# -----SUBJECTS VIEWS -------#
@main.route('/admin/addsubjects', methods=['GET', 'POST'])
@login_required
@admin_required
def addSubject():
    add_subject_form = SubjectsAdd()
    users = User.query.all()
    if add_subject_form.validate_on_submit() and request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('Teacher')).first()
        subject = Subject(name=add_subject_form.subject_name.data, teacher=user)
        db.session.add(subject)
        db.session.commit()
        return redirect(url_for('main.getSubjects'))
    return render_template('admin/subjects_add.html', add_subject_form=add_subject_form, users=users)


@main.route('/admin/subjects/')
@login_required
def getSubjects():
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)


@main.route('/admin/subject/remove/<int:id>')
@login_required
@admin_required
def removeSubject(id):
    subject = Subject.query.get(id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('main.getSubjects'))


@main.route('/admin/subject/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editSubject(id):
    add_subject_form = SubjectsAdd()
    users = User.query.all()
    current_subject = Subject.query.get(id)
    if add_subject_form.validate_on_submit():
        user = User.query.filter_by(username=request.form.get('Teacher')).first()
        current_subject.name = add_subject_form.subject_name.data
        current_subject.teacher = user
        db.session.add(current_subject)
        db.session.commit()
        return redirect(url_for('main.getSubjects'))
    add_subject_form.subject_name.data = current_subject.name
    return render_template('admin/subjects_add.html', add_subject_form=add_subject_form, users=users)


# -----END SUBJECTS VIEWS -----#

# ----- STUDENTS VIEWS -----#
@main.route('/admin/addstudent', methods=['GET', 'POST'])
@admin_required
def studentAdd():
    student_form = StudentForm()
    subjects = Subject.query.all()
    if student_form.validate_on_submit():
        subject = Subject.query.filter_by(name=request.form.get('subject')).first()
        student = Student(name=student_form.name.data, phone_number=student_form.phone_number.data,
                          pay_day=student_form.pay_day.data,
                          address=student_form.address.data,
                          subject=subject)
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('main.getStudents'))
    return render_template('admin/student_form.html', student_form=student_form, subjects=subjects)


@main.route('/admin/students')
@login_required
def getStudents():
    students = Student.query.all()
    return render_template('admin/students.html', students=students)


@main.route('/admin/student/remove/<int:id>')
@login_required
@admin_required
def removeStudent(id):
    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('main.getStudents'))


@main.route('/admin/student/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editStudent(id):
    student = Student.query.get(id)
    student_form = StudentForm()
    subjects = Subject.query.all()
    if student_form.validate_on_submit():
        subject = Subject.query.filter_by(name=request.form.get('subject')).first()
        student.name = student_form.name.data
        student.pay_day= student_form.pay_day.data
        student.phone_number = student_form.phone_number.data
        student.address = student_form.address.data
        student.subject = subject
        db.session.add(student)
        db.session.commit()
        return redirect(url_for('main.getStudents'))
    student_form.pay_day.data=student.pay_day
    student_form.name.data = student.name
    student_form.phone_number.data = student.phone_number
    student_form.address.data = student.address
    return render_template('admin/student_form.html', student_form=student_form, subjects=subjects)


# ----- END STUDENTS VIEWS -----#

# ----- ATTENDANCE VIEWS -----#
@main.route('/admin/newattendance', methods=['GET', 'POST'])
@login_required
def newAttendance():
    subjects = Subject.query.all()
    class_pick = AttendanceClass()
    if class_pick.validate_on_submit():
        subject = Subject.query.filter_by(name=request.form.get('subject')).first()
        return redirect(url_for('main.newAttendanceQuery', id=subject.id))
    return render_template('admin/class_picking.html', subjects=subjects, class_pick=class_pick)


@main.route('/admin/newattendance/<int:id>', methods=['GET', 'POST'])
@login_required
def newAttendanceQuery(id):
    students = Student.query.filter_by(subject_id=id).all()
    current_subject = Subject.query.get(id)
    form = AttendanceForm()
    if form.validate_on_submit() and request.method == 'POST':
        for student in students:
            absent = request.form.get(str(student.id))
            if absent == 'on':
                absent = False
            else:
                absent = True
            attendance = Attendance(student=student, absent=absent, subject=current_subject)
            db.session.add(attendance)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('admin/attendanceform.html', form=form, students=students)


@main.route('/admin/attendancequery', methods=['GET', 'POST'])
@login_required
def attendanceQuery():
    form = AttendanceQuery()
    subjects = Subject.query.all()
    if form.validate_on_submit():
        subject = Subject.query.filter_by(name=request.form.get('subject')).first()
        raw_date = form.date.data
        return redirect(url_for('main.getAttendance', id=subject.id, raw_date=raw_date))
    return render_template('admin/attendance_query.html', subjects=subjects, form=form)


@main.route('/admin/attendance/<int:id>/<raw_date>')
@login_required
def getAttendance(id, raw_date):
    date_plit = raw_date.split('-')
    date_query = datetime(year=int(date_plit[2]), month=int(date_plit[1]), day=int(date_plit[0]))
    print(date_query)
    attendances = Attendance.query.filter(Attendance.subject_id == id, Attendance.date == date_query).all()
    print(attendances)
    return render_template('admin/attendances.html', attendances=attendances)

# ----- END ATTENDANCE VIEWS -----#
