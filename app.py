from flask import Flask, render_template, request
# from flask.ext.sqlalchemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
import smtplib
from sqlalchemy.sql import func


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost/height_collector'
db=SQLAlchemy(app)

class Data(db.Model):
	__tablename__="data"
	id=db.Column(db.Integer, primary_key=True)
	email=db.Column(db.String(120), unique=True)
	height=db.Column(db.Integer)

	def __init__(self, email_, height_):
		self.email = email_
		self.height = height_


def send_email(email, height, average_height, count):
	from_email="test.for.only.no.reply@gmail.com"
	from_password="python777"
	to_email=email

	subject="Height data"
	message="Hey there, your height is <strong>%s</strong>. \
	<br> Average height of all is <strong>%s</strong> \
	and that is calculated out of <strong>%s</strong> people. \
	<br> Thanks!" % (height, average_height, count)

	msg=MIMEText(message, 'html')
	msg['Subject']=subject
	msg['To']=to_email
	msg['From']=from_email

	gmail=smtplib.SMTP('smtp.gmail.com',587)
	gmail.ehlo()
	gmail.starttls()
	gmail.login(from_email, from_password)
	gmail.send_message(msg)


@app.route("/")
def index():
	return render_template("index.html")


@app.route("/success", methods=['POST'])
def success():
	if request.method=='POST':
		email=request.form["email_name"]
		height=request.form["height_name"]
		if db.session.query(Data).filter(Data.email==email).count() == 0:
			data=Data(email, height)
			db.session.add(data)
			db.session.commit()
			average_height=db.session.query(func.avg(Data.height)).scalar()
			average_height=round(average_height, 2)
			count=db.session.query(Data.height).count()
			send_email(email, height, average_height, count)
			# print(request.form)
			return render_template("success.html")
		return render_template("index.html", 
			text="Seem like we've got something from that email address already!")

if __name__ == "__main__":
	# db.create_all()
	app.debug=True
	app.run()