import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import (
    UserMixin,
    current_user,
    login_required,
    login_user,
    LoginManager,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)

app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'secret-key-fares-portfolio-2026'
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    BASE_DIR, 'portfolio.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'


class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(120), unique=True, nullable=False)
  password_hash = db.Column(db.String(200), nullable=False)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)


class Project(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(150), nullable=False)
  category = db.Column(db.String(50), nullable=False)
  short_desc = db.Column(db.Text, nullable=False)
  long_desc = db.Column(db.Text, nullable=True)
  client = db.Column(db.String(100), nullable=True)
  date = db.Column(db.String(50), nullable=True)
  website = db.Column(db.String(200), nullable=True)
  tech_stack = db.Column(db.String(200), nullable=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  images = db.relationship(
      'ProjectImage', backref='project', lazy=True, cascade='all, delete-orphan'
  )


class ProjectImage(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  image_path = db.Column(db.String(255), nullable=False)
  project_id = db.Column(
      db.Integer, db.ForeignKey('project.id'), nullable=False
  )


class Thought(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.Text, nullable=False)
  image_path = db.Column(db.String(255), nullable=True)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


def allowed_file(filename):
  return (
      '.' in filename
      and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
  )


# --- PUBLIC ROUTES ---
@app.route('/')
def index():
  projects = Project.query.order_by(Project.created_at.desc()).all()
  thoughts = Thought.query.order_by(Thought.created_at.desc()).all()
  return render_template('index.html', projects=projects, thoughts=thoughts)


@app.route('/portfolio-details.html')
def portfolio_details():
  projects = Project.query.order_by(Project.created_at.desc()).all()
  return render_template('portfolio-details.html', projects=projects)


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


# --- ADMIN ACTIONS ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
  if request.method == 'POST':
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
      login_user(user)
      flash('Logged in as Admin!', 'success')
      return redirect(url_for('index'))
    else:
      flash('Invalid email or password', 'danger')

  return render_template('admin_login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
  logout_user()
  flash('Logged out.', 'info')
  return redirect(url_for('index'))


@app.route('/admin/project/add', methods=['POST'])
@login_required
def add_project():
  title = request.form.get('title')
  category = request.form.get('category')
  short_desc = request.form.get('short_desc')
  long_desc = request.form.get('long_desc')
  client = request.form.get('client')
  date = request.form.get('date')
  website = request.form.get('website')
  tech_stack = request.form.get('tech_stack')

  new_project = Project(
      title=title,
      category=category,
      short_desc=short_desc,
      long_desc=long_desc,
      client=client,
      date=date,
      website=website,
      tech_stack=tech_stack,
  )
  db.session.add(new_project)
  db.session.commit()

  uploaded_files = request.files.getlist('images')
  for file in uploaded_files:
    if file and allowed_file(file.filename):
      filename = secure_filename(
          f"{int(datetime.now().timestamp())}_{file.filename}"
      )
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      project_img = ProjectImage(
          image_path=f'uploads/{filename}', project_id=new_project.id
      )
      db.session.add(project_img)

  db.session.commit()
  flash('New Project published!', 'success')
  return redirect(url_for('index') + '#portfolio')


@app.route('/admin/project/edit/<int:id>', methods=['POST'])
@login_required
def edit_project(id):
  project = Project.query.get_or_404(id)
  project.title = request.form.get('title')
  project.category = request.form.get('category')
  project.short_desc = request.form.get('short_desc')
  project.long_desc = request.form.get('long_desc')
  project.client = request.form.get('client')
  project.date = request.form.get('date')
  project.website = request.form.get('website')
  project.tech_stack = request.form.get('tech_stack')

  db.session.commit()
  flash('Project updated successfully!', 'success')
  return redirect(url_for('portfolio_details') + f'#project-{id}')


@app.route('/admin/project/<int:project_id>/add-photos', methods=['POST'])
@login_required
def add_project_photos(project_id):
  project = Project.query.get_or_404(project_id)
  uploaded_files = request.files.getlist('images')

  for file in uploaded_files:
    if file and allowed_file(file.filename):
      filename = secure_filename(
          f"add_{int(datetime.now().timestamp())}_{file.filename}"
      )
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      project_img = ProjectImage(
          image_path=f'uploads/{filename}', project_id=project.id
      )
      db.session.add(project_img)

  db.session.commit()
  flash('Photos added to project!', 'success')
  return redirect(url_for('portfolio_details') + f'#project-{project_id}')


# DELETE SPECIFIC SINGLE PHOTO FROM A PROJECT
@app.route('/admin/project-image/delete/<int:image_id>', methods=['POST'])
@login_required
def delete_project_image(image_id):
  image = ProjectImage.query.get_or_404(image_id)
  project_id = image.project_id

  # Attempt disk cleanup if uploaded file
  if image.image_path.startswith('uploads/'):
    file_path = os.path.join(
        app.config['UPLOAD_FOLDER'], os.path.basename(image.image_path)
    )
    if os.path.exists(file_path):
      try:
        os.remove(file_path)
      except Exception as e:
        print(f'Disk remove error: {e}')

  db.session.delete(image)
  db.session.commit()
  flash('Photo deleted from project.', 'info')
  return redirect(url_for('portfolio_details') + f'#project-{project_id}')


@app.route('/admin/project/delete/<int:id>', methods=['POST'])
@login_required
def delete_project(id):
  project = Project.query.get_or_404(id)
  db.session.delete(project)
  db.session.commit()
  flash('Project deleted.', 'info')
  return redirect(url_for('index') + '#portfolio')


@app.route('/admin/thought/add', methods=['POST'])
@login_required
def add_thought():
  content = request.form.get('content')
  image_path = None

  if 'image' in request.files:
    file = request.files['image']
    if file and allowed_file(file.filename):
      filename = secure_filename(
          f"thought_{int(datetime.now().timestamp())}_{file.filename}"
      )
      file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      image_path = f'uploads/{filename}'

  new_thought = Thought(content=content, image_path=image_path)
  db.session.add(new_thought)
  db.session.commit()
  flash('Thought published!', 'success')
  return redirect(url_for('index') + '#thoughts')


@app.route('/admin/thought/delete/<int:id>', methods=['POST'])
@login_required
def delete_thought(id):
  thought = Thought.query.get_or_404(id)
  db.session.delete(thought)
  db.session.commit()
  flash('Thought deleted.', 'info')
  return redirect(url_for('index') + '#thoughts')


# Initialize DB and seed initial data
with app.app_context():
  db.create_all()

  admin = User.query.filter_by(email='faresexpress2@gmail.com').first()
  if not admin:
    admin = User(email='faresexpress2@gmail.com')
    admin.set_password('AdminPass123!')
    db.session.add(admin)
    db.session.commit()

  # Seed restored thought
  if Thought.query.count() == 0:
    default_thought = Thought(
        content=(
            "People think you don't need a software engineer anymore! ok I"
            " agree, it is a matter of time until you visit a restaurant and"
            " think why can't i make all my food at home why the restaurant"
            " food is better lets be honest, we do it just always better!"
        )
    )
    db.session.add(default_thought)
    db.session.commit()

  # Seed 10 default projects if missing
  if Project.query.count() == 0:
    default_projects = [
        {
            'title': 'Taj Al Modon Trading Company',
            'category': 'Commercial Site',
            'short_desc': (
                'Showcase furniture catalog website for a trading company in'
                ' Saudi Arabia.'
            ),
            'long_desc': (
                'Official commercial website for Taj Al Modon Trading Company'
                ' in Saudi Arabia, specializing in furniture selling. Designed'
                ' to present their catalog and business contacts online.'
            ),
            'client': 'Taj Al Modon Company (KSA)',
            'date': 'Aug 2024',
            'website': 'https://www.tajalmodon.com',
            'tech_stack': 'Web Development, SEO',
            'img': 'img/masonry-portfolio/masonry-portfolio-10.webp',
        },
        {
            'title': 'ChatUTM - Telegram Community Chatbot',
            'category': 'AI Chatbot',
            'short_desc': (
                'Telegram API integrated chatbot that answers questions for'
                ' UTM university Arab community.'
            ),
            'long_desc': (
                'A Telegram API integrated chatbot trained on university'
                ' resources to serve the UTM Arab student community. It'
                ' utilizes PyTorch and Gemini NLP models to answer common'
                ' student questions instantly, streamlining community'
                ' communication.'
            ),
            'client': 'ISS-YEMEN Volunteering Project',
            'date': 'March 2025',
            'website': '',
            'tech_stack': 'Python, Flask, Telegram API, PyTorch NLP',
            'img': 'img/masonry-portfolio/masonry-portfolio-6.webp',
        },
        {
            'title': 'The Coffee Chronicles',
            'category': 'Web App & AI',
            'short_desc': (
                'Informative coffee origins website with an integrated chat'
                ' agent to answer coffee questions.'
            ),
            'long_desc': (
                'An informative web application that shares knowledge about'
                ' coffee origins, bean processing, and brewing methods.'
                ' Features an integrated conversational AI agent that answers'
                ' coffee queries in real time.'
            ),
            'client': 'Personal Project',
            'date': 'April 2024',
            'website': '',
            'tech_stack': 'HTML5, JavaScript, Gemini API',
            'img': 'img/masonry-portfolio/masonry-portfolio-7.webp',
        },
        {
            'title': 'React Performance Solutions',
            'category': 'React Engineering',
            'short_desc': (
                'Project solving performance bottlenecks to maximize speed'
                ' using React optimization tools.'
            ),
            'long_desc': (
                'A case study project focused on solving performance'
                ' bottlenecks in React applications. Utilized code-splitting,'
                ' lazy-loading, memoization (React.memo), and Webpack'
                ' optimization to increase page rendering speed and lower'
                ' initial bundle size.'
            ),
            'client': 'Personal Case Study',
            'date': 'August 2024',
            'website': '',
            'tech_stack': 'React, Lighthouse, Webpack',
            'img': 'img/masonry-portfolio/masonry-portfolio-8.webp',
        },
        {
            'title': 'PDF Parser & Text Extractor',
            'category': 'Python Scripting',
            'short_desc': (
                'Python script to parse PDF documents and extract clean text'
                ' content into text files.'
            ),
            'long_desc': (
                'A Python utility tool built to parse complex PDF documents and'
                ' extract raw text into structured .txt files. Created to'
                ' automate document reading workflows and prepare training'
                ' data for AI models.'
            ),
            'client': 'Personal Project',
            'date': 'June 2024',
            'website': '',
            'tech_stack': 'Python, PyPDF2',
            'img': 'img/masonry-portfolio/masonry-portfolio-9.webp',
        },
        {
            'title': 'PCEP – Certified Entry-Level Python Programmer',
            'category': 'Python Certification',
            'short_desc': (
                'Udemy certificate for completing Python fundamentals training.'
            ),
            'long_desc': (
                'Certificate awarded for attending and completing an intensive'
                ' course covering core Python programming concepts. Key topics'
                ' studied include foundational syntax, data structures, loops,'
                ' object-oriented programming basics, and algorithm design.'
            ),
            'client': 'Udemy / Python Institute',
            'date': '2023',
            'website': '',
            'tech_stack': 'Python 3, Programming Basics',
            'img': 'img/masonry-portfolio/masonry-portfolio-1.webp',
        },
        {
            'title': 'Excel & Macros Training Certificate',
            'category': 'Data Analytics',
            'short_desc': (
                'Attending course on Excel macros, spreadsheet automation, and'
                ' data workflows.'
            ),
            'long_desc': (
                'Attended a week-long intensive course covering Microsoft Excel'
                ' essentials, advanced formulas, macros, data organization,'
                ' and spreadsheet management workflow techniques.'
            ),
            'client': 'LinkedIn Learning',
            'date': 'Aug 2024',
            'website': '',
            'tech_stack': 'MS Excel, Macros, Data Analysis',
            'img': 'img/masonry-portfolio/masonry-portfolio-2.webp',
        },
        {
            'title': 'Cyber Security Workshop Certificate',
            'category': 'Security',
            'short_desc': (
                'Certificate for attending an intensive workshop on Cyber'
                ' Security fundamentals.'
            ),
            'long_desc': (
                'Certificate awarded for attending an interactive workshop on'
                ' cybersecurity fundamentals, threat awareness, system safety,'
                ' network vulnerabilities, and defensive concepts.'
            ),
            'client': 'CyberX Workshop',
            'date': 'June 2023',
            'website': '',
            'tech_stack': 'Cyber Security, Network Safety',
            'img': 'img/masonry-portfolio/masonry-portfolio-3.webp',
        },
        {
            'title': 'IELTS Preparation Certificate',
            'category': 'Language Competency',
            'short_desc': (
                'Certificate for completing IELTS preparation course at EMS'
                ' Institute.'
            ),
            'long_desc': (
                'Completed an intensive English preparation course at the EMS'
                ' Language Centre focused on academic reading, technical'
                ' writing, listening comprehension, and professional speaking'
                ' skills.'
            ),
            'client': 'EMS Language Centre',
            'date': 'Nov 2022',
            'website': '',
            'tech_stack': 'IELTS, Academic English',
            'img': 'img/masonry-portfolio/masonry-portfolio-4.webp',
        },
        {
            'title': 'ISS-YEMEN YSAG Head of Computing Faculty',
            'category': 'Volunteering & Leadership',
            'short_desc': (
                'Volunteering in ISS-YEMEN YSAG as the head of Computing Faculty'
                ' of Yemeni students.'
            ),
            'long_desc': (
                'Certificate recognizing leadership service as the Head of the'
                ' Computing Faculty for Yemeni students at Universiti Teknologi'
                ' Malaysia (UTM) under ISS-YEMEN YSAG. Led tech initiatives,'
                ' community workshops, and academic guidance.'
            ),
            'client': 'ISS-YEMEN YSAG (UTM)',
            'date': 'Jan 2025',
            'website': '',
            'tech_stack': 'Leadership, Computing Community',
            'img': 'img/masonry-portfolio/masonry-portfolio-5.webp',
        },
    ]

    for p in default_projects:
      proj = Project(
          title=p['title'],
          category=p['category'],
          short_desc=p['short_desc'],
          long_desc=p['long_desc'],
          client=p['client'],
          date=p['date'],
          website=p['website'],
          tech_stack=p['tech_stack'],
      )
      db.session.add(proj)
      db.session.commit()
      img = ProjectImage(image_path=p['img'], project_id=proj.id)
      db.session.add(img)
      db.session.commit()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000, debug=True)