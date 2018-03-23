import sqlite3
import os

class UserExistsError (Exception):
    def _init_(self):
        self.string = "user already exists"
    def _str_(self):
        return self.string

def createdb ():
    conn = sqlite3.connect ('piedPiper.db')
    
    print "Opened database successfully";

    conn.execute ('pragma foreign_keys=on')
    conn.execute('begin transaction')
    conn.execute('CREATE TABLE user_account( userid bigint PRIMARY KEY ,firstname TEXT, lastname TEXT, email TEXT, imageurl TEXT, accounttype int, directory TEXT)')#accounttype 0 for student, 1 for teacher

    conn.execute ('CREATE TABLE schedules ( teacherid bigint, time TEXT,   studentid bigint  DEFAULT 0, FOREIGN KEY(teacherid) REFERENCES user_account(userid),FOREIGN KEY(studentid) REFERENCES user_account(userid))')

    conn.close()
def newuserdirectory(email):
    os.mkdir(email,0755)
    return os.getcwd()+"/"+email

def insert_new_user(userid,firstname, lastname, email, imageurl, accounttype):
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_account where userid = (?)",(userid,))
    rows = c.fetchall();
    if len(rows)!=0:
        conn.close()
        raise UserExistsError();
    c = conn.cursor();
    c.execute("INSERT INTO user_account(userid, firstname, lastname, email, imageurl, accounttype, directory) VALUES (?,?,?,?,?,?,?)", (userid,firstname, lastname, email,imageurl,accounttype,newuserdirectory(email)))
    conn.commit()
    conn.close()

def check_if_schedule_occupied(teacherid,time):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT * FROM schedules where teacherid = ? AND time = ? AND studentid!=0 ",(teacherid,time))
    rows = c.fetchall();
    return len(rows)>0
def insert_schedule_studentid(teacherid, time,studentid):#first check if schedule is occupied as this function just updates the studentid associated with the teacher id
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE  schedules  SET studentid = ? where teacherid = ? and time=?", (studentid, teacherid, time))
    conn.commit();
    conn.close()
def insert_new_schedule(teacherid,time):
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("INSERT INTO schedules ( teacherid , time) VALUES (?,?)", (teacherid, time))
    conn.commit();
    conn.close()
def get_userInfo(userid):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT  firstname, lastname, email, imageurl, accounttype, directory FROM user_account where userid = (?)",(userid,))
    rows = c.fetchall();
    conn.close();
    return rows

