# Komodo Hub - Animal Protection Education Platform

Komodo Hub is a comprehensive platform designed to support animal protection education through collaborative learning, community engagement, and educational resource management.

## 🎯 Project Overview

Komodo Hub serves three main user groups with specialized features:

### 🏫 School Users
- **Teachers**: Easy-to-use tools for developing and managing animal protection courses and activities
- **Students**: Personalized accounts for course participation, activity engagement, and project submissions
- **Administrators**: Account management, subscription handling, and student registration

### 🌍 Community Users
- Organizations like #SaveOurAnimals can share articles, maintain species observation records, and showcase member contributions
- Community engagement and collaboration features

### ⚙️ Platform Management
- Comprehensive account and organization management
- Business intelligence dashboards
- User behavior monitoring and service performance tracking
- Strong emphasis on data security and privacy protection

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- SQLite

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/liffsss/Software-Engineering-Coursework.git
cd komodo-hub
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install flask
pip install bcrypt
```

4. **Initialize the database**
```bash
python database/init_database.py
```

5. **Run the application**
```bash
python run.py
Enter the account and password for the corresponding role.
All users initial password: 123123
Teacher account: teacher@komodohub.edu
Student accounts: student1@komodohub.edu, student2@komodohub.edu, student3@komodohub.edu, student4@komodohub.edu
Admin account: admin@komodohub.edu
Community organization account: org@komodohub.org
```

The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
komodo-hub/
├── app.py                 # Main application entry point
├── config.py              # Application configuration
├── database/              # Database layer
│   ├── init_database.py   # Database initialization
│   ├── komodo_hub.db      # SQLite database file
│   └── models.py          # Data models and operations
├── routes/                # Route handlers
│   ├── admin.py           # Administrator routes
│   ├── auth.py            # Authentication routes
│   ├── community.py       # Community organization routes
│   ├── student.py         # Student routes
│   └── teacher.py         # Teacher routes
├── static/                # Static assets
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript files
│   └── pages/             # Page-specific resources
├── templates/             # Jinja2 templates
│   ├── base/              # Base template components
│   ├── components/        # Reusable components
│   └── pages/             # Page templates
├── utils/                 # Utility functions
│   └── helpers.py         # Helper functions
├── run.py                 # Application startup script
└── requirements.txt       # Python dependencies
```

## 🛠 Development Guide

### Adding New Features

#### 1. Database Operations
Add query functions in `database/models.py`:

```python
def get_course_details(course_id):
    """Get detailed course information"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, u.username as teacher_name
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.id = ?
        """, (course_id,))
        return cursor.fetchone()
    finally:
        conn.close()
```

#### 2. Route Handlers
Add routes in the appropriate role file in `routes/`:

```python
@teacher_bp.route('/course/<int:course_id>/details')
def course_details(course_id):
    if 'role' in session and session['role'] == 'teacher':
        course = get_course_details(course_id)
        return render_template(
            'pages/teacher/course_details.html',
            course=course,
            username=session['username']
        )
    return redirect(url_for('auth.login'))
```

#### 3. Frontend Templates
Create templates in `templates/pages/{role}/`:

```html
{% extends 'base/base.html' %}

{% block title %}Course Details - Komodo Hub{% endblock %}

{% block content %}
<div class="dashboard-container">
    <h1>{{ course.title }}</h1>
    <!-- Page content -->
</div>
{% endblock %}
```

#### 4. Static Assets
Add styles in `static/css/` and scripts in `static/js/`:

```css
/* static/css/components/course-details.css */
.course-details {
    background: white;
    border-radius: 12px;
    padding: 25px;
}
```

### Code Organization

- **Database Layer**: All database models and operations in `/database`
- **Route Handlers**: HTTP request handling in `/routes` (organized by role)
- **Templates**: HTML views in `/templates` with reusable components
- **Static Assets**: CSS, JS, and images in `/static`
- **Utilities**: Helper functions in `/utils`

## 🔐 Security Features

- Secure session management
- Role-based access control
- Parameterized SQL queries to prevent injection
- Data encryption for sensitive information
- Privacy protection for children and teachers

## 👥 User Roles & Access

| Role | Dashboard Access | Features |
|------|------------------|----------|
| Student | `/student` | Course participation, project submission |
| Teacher | `/teacher` | Course management, student tracking |
| Community | `/community` | Article publishing, species records |
| Admin | `/admin` | User management, platform analytics |

## 🗄 Database Schema

Key tables include:
- `users` - User accounts and authentication
- `courses` - Course information and materials
- `enrollments` - Student course registrations
- `articles` - Community articles and content
- `observations` - Species observation records
- `submissions` - Student work submissions

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the project documentation
- Contact the development team

## 🔄 Version History

- **v1.0.0** - Initial release with core platform features
- **v1.1.0** - Enhanced community features and improved UI

---

**Komodo Hub** - Empowering animal protection education through technology 🐾
