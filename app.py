import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/portfolio-details.html')
def portfolio_details():
  return render_template('portfolio-details.html')


@app.route('/send_email', methods=['POST'])
def send_email():
  name = request.form.get('name')
  email = request.form.get('email')
  subject = request.form.get('subject')
  message = request.form.get('message')

  if not all([name, email, subject, message]):
    return (
        jsonify({'status': 'error', 'message': 'All fields are required.'}),
        400,
    )

  sender_email = os.environ.get('SENDER_EMAIL')
  sender_password = os.environ.get('SENDER_PASSWORD')
  receiver_email = os.environ.get('RECEIVER_EMAIL')

  if not all([sender_email, sender_password, receiver_email]):
    return (
        jsonify({
            'status': 'error',
            'message': 'Server email environment configuration missing.',
        }),
        500,
    )

  msg = MIMEText(
      f'Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}'
  )
  msg['Subject'] = f'Portfolio Contact: {subject}'
  msg['From'] = sender_email
  msg['To'] = receiver_email

  try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
      smtp.login(sender_email, sender_password)
      smtp.sendmail(sender_email, receiver_email, msg.as_string())
    return (
        jsonify({'status': 'success', 'message': 'Email sent successfully!'}),
        200,
    )
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)