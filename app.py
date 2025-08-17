from flask import Flask, request, jsonify, render_template
import smtplib
from email.mime.text import MIMEText
import os

# Determine the base directory of the application (where app.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
# Explicitly tell Flask where to find the 'templates' and 'static' folders
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'), # Look for HTML templates here
    static_folder=os.path.join(BASE_DIR, 'static')     # Look for static files (CSS, JS, img) here
)

# Route for the home page (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Routes for other HTML pages (if you want Flask to serve them directly)
@app.route('/portfolio-details.html')
def portfolio_details():
    return render_template('portfolio-details.html')

@app.route('/starter-page.html')
def starter_page():
    return render_template('starter-page.html')


# Route for handling email submissions
@app.route('/send_email', methods=['POST'])
def send_email():
    if request.method == 'POST':
        # You might need to adjust 'request.form' to 'request.json' or 'request.data'
        # depending on how your JavaScript sends the data. Based on previous, request.form should be fine.
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not all([name, email, subject, message]):
            return jsonify({'status': 'error', 'message': 'All fields are required.'}), 400

        # Configure your email settings
        sender_email = os.environ.get("SENDER_EMAIL")
        sender_password = os.environ.get("SENDER_PASSWORD")
        receiver_email = os.environ.get("RECEIVER_EMAIL")

        if not all([sender_email, sender_password, receiver_email]):
            print("WARNING: Email credentials not loaded from environment variables!")
            
        # Create the email message
        msg = MIMEText(f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}")
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Send the email
        try:
            # For Gmail, use SMTP_SSL and port 465
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(sender_email, sender_password)
                smtp.sendmail(sender_email, receiver_email, msg.as_string())
            return jsonify({'status': 'success', 'message': 'Email sent successfully!'}), 200
        except Exception as e:
            print(f"Email sending failed: {e}") # Log the actual error
            return jsonify({'status': 'error', 'message': f'Email sending failed: {str(e)}. Check server logs.'}), 500

# Run the Flask application
if __name__ == '__main__':
    # Flask's template_folder and static_folder setup (above) handles paths relative to BASE_DIR.
    # No need for os.chdir(script_dir) here anymore, it was causing confusion.
    app.run(debug=True) # debug=True is good for development, shows errors