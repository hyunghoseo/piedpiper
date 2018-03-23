import sqlite3
import os

class UserExistsError (Exception):
    def _init_(self):
        self.string = "User Already Exists"
    def _str_(self):
        return self.string

class ScheduleOccupiedError (Exception):
    def _init_(self):
        self.string = "Schedule Already Occupied"
    def _str_(self):
        return self.string

class FileExistsError (Exception):
    def _init_(self):
        self.string = "File Already Exists"
    def _str_(self):
        return self.string

def createdb():
    conn = sqlite3.connect ('piedPiper.db')
    
    print "Opened database successfully";

    conn.execute ('pragma foreign_keys=on')
    conn.execute('begin transaction')
    conn.execute('CREATE TABLE IF NOT EXISTS user_account( userid bigint PRIMARY KEY ,firstname TEXT, lastname TEXT, email TEXT, imageurl TEXT, accounttype int, directory TEXT)')#accounttype 0 for student, 1 for teacher

    conn.execute ('CREATE TABLE IF NOT EXISTS schedules ( teacherid bigint, time TEXT,   studentid bigint  DEFAULT 0, FOREIGN KEY(teacherid) REFERENCES user_account(userid),FOREIGN KEY(studentid) REFERENCES user_account(userid))')

    conn.close()

def newuserdirectory(email):
    os.mkdir(email,0755)
    return os.getcwd()+"/"+email

def check_if_user_exists(userid):
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT * FROM user_account WHERE userid = (?)",(userid,))
    rows = c.fetchall()
    conn.close()
    return len(rows)!=0
def insert_new_user(userid,firstname, lastname, email, imageurl, accounttype):
    if check_if_user_exists(userid):
        raise UserExistsError()
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("INSERT INTO user_account(userid, firstname, lastname, email, imageurl, accounttype, directory) VALUES (?,?,?,?,?,?,?)", (userid,firstname, lastname, email,imageurl,accounttype,newuserdirectory(email)))
    conn.commit()
    conn.close()

def check_if_schedule_occupied(teacherid,time):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT * FROM schedules WHERE teacherid = ? AND time = ? AND studentid!=0 ",(teacherid,time))
    rows = c.fetchall()
    conn.close()
    return len(rows)>0
def insert_schedule_studentid(teacherid, time, studentid):
    if check_if_schedule_occupied(teacherid, time):
        raise ScheduleOccupiedError()
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE schedules SET studentid = ? WHERE teacherid = ? AND time=?", (studentid, teacherid, time))
    conn.commit()
    conn.close()
def remove_schedule_studentid(teacherid, time):
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE schedules SET studentid = ? WHERE teacherid = ? AND time=?", (0, teacherid, time))
    conn.commit()
    conn.close()
    
def insert_new_schedule(teacherid,time):
    conn = sqlite3.connect ('piedPiper.db')
    c = conn.cursor()
    c.execute("INSERT INTO schedules ( teacherid , time) VALUES (?,?)", (teacherid, time))
    conn.commit()
    conn.close()
def delete_schedule(teacherid,time)
    conn = sqlite3.connect ('piedPieper.db')
    c.execute("DELETE FROM schedules WHERE teacherid = ? AND time = ?", (teacherid, time))
    conn.commit()
    conn.close()
    
def get_userInfo(userid):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT  firstname, lastname, email, imageurl, accounttype, directory FROM user_account WHERE userid = (?)",(userid,))
    rows = c.fetchall()
    conn.close()
    return rows
def update_userInfo_firstname(firstname):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE user_account SET firstname = ? WHERE userid = ?",(firstname, userid))
    rows = c.fetchall()
    conn.close()
def update_userInfo_lastname(flastname):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE user_account SET lastname = ? WHERE userid = ?",(lastname, userid))
    rows = c.fetchall()
    conn.close()
def update_userInfo_accounttype(accounttype):
    conn = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("UPDATE user_account SET accounttype = ? WHERE userid = ?",(accounttype, userid))
    rows = c.fetchall()
    conn.close()

def check_if_file_exists(filename, directory):
    return os.path.isfile(directory + "/" + filename + ".txt")
def save_ide_state(userid, filename, programtext):
    con = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT directory FROM user_account WHERE userid = ?",(userid,))
    row = c.fetchall()
    if check_if_file_exists(filename, row):
        raise FileExistsError()
    program_file = open(row+"/"+filename+".txt", "w")
    program_file.write(programtext)
    program_file.close()
    conn.close()
def delete_ide_state(userid, filename):
    con = sqlite3.connect('piedPiper.db')
    c = conn.cursor()
    c.execute("SELECT directory FROM user_account WHERE userid = ?",(userid,))
    row = c.fetchall()
    if check_if_file_exists(filename, row):
        os.remove(row+"/"+filename+".txt")
    conn.close()