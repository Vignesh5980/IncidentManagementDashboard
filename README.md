# 🚨 Enterprise Incident & Service Request Management System

<p align="center">

**A Django-based IT Service Management (ITSM) platform for managing Incidents, Service Requests, Changes, SLAs, Approvals and Support Operations.**

</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.12-blue?logo=python">
<img src="https://img.shields.io/badge/Django-6.x-green?logo=django">
<img src="https://img.shields.io/badge/MySQL-8.x-orange?logo=mysql">
<img src="https://img.shields.io/badge/REST%20API-Django%20REST%20Framework-red?logo=django">
<img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker">
<img src="https://img.shields.io/badge/Linux-Supported-black?logo=linux">
<img src="https://img.shields.io/badge/Git-GitHub-lightgrey?logo=github">

</p>

---

## 📌 Overview

The **Enterprise Incident & Service Request Management System** is a web-based IT Service Management platform developed using **Python and Django**.

The application simulates a real-world enterprise IT support environment where employees can raise incidents and service requests, support engineers can investigate and resolve tickets, and administrators can monitor SLA compliance, workload, approvals and operational performance.

The system is designed around common **L1/L2/L3 Application Support and ITSM workflows**.

### The platform provides:

* Incident Management
* Service Request Management
* Change Management
* SLA Tracking
* Approval Management
* Engineer Assignment
* Role-Based Access Control
* Incident History
* Comments and Collaboration
* Advanced Search & Filtering
* Operational Dashboard
* Engineer Workload Analytics
* Monthly Request Trends
* REST API integration
* Docker containerization
* Cloud deployment readiness

---

# 🏢 Real-World Business Scenario

Consider an organization with hundreds or thousands of employees.

An employee may face issues such as:

* Application is unavailable
* VPN is not connecting
* Database access is required
* Password reset is required
* Software installation is required
* Email is not working
* Server access is required
* Production application is slow

Instead of handling these requests through email or chat, the organization uses a centralized ITSM platform.

```text
                    ┌─────────────────────┐
                    │      Employee       │
                    │      / End User     │
                    └──────────┬──────────┘
                               │
                               │ Raise Ticket
                               ▼
                    ┌─────────────────────┐
                    │   ITSM Application  │
                    │      Django         │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┼─────────────┐
                 │             │             │
                 ▼             ▼             ▼
          ┌────────────┐ ┌────────────┐ ┌────────────┐
          │  Incident  │ │  Service   │ │   Change   │
          │ Management  │ │  Request   │ │ Management │
          └──────┬─────┘ └─────┬──────┘ └──────┬─────┘
                 │             │               │
                 └─────────────┼───────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Assignment /        │
                    │ Approval Workflow   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Support Engineer    │
                    │       L1 / L2        │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Resolution & SLA    │
                    │      Tracking       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Closed        │
                    └─────────────────────┘
```

---

# 🏗️ System Architecture

The application follows a layered architecture separating the presentation, business logic and data layers.

```text
                         USERS
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
       Web Browser                  REST Client
             │                           │
             └─────────────┬─────────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │   Django Web App   │
                 │                   │
                 │  Authentication   │
                 │  Authorization    │
                 │  Views            │
                 │  Forms            │
                 │  REST APIs        │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │   Business Logic  │
                 │                   │
                 │ SLA Calculation   │
                 │ Assignment        │
                 │ Approval          │
                 │ Status Workflow   │
                 │ Analytics         │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │    Django ORM     │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │       MySQL       │
                 │     Database      │
                 └───────────────────┘
```

---

# 🧩 Application Modules

```text
┌─────────────────────────────────────────────────────────────┐
│                  IT SERVICE MANAGEMENT SYSTEM                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🔐 Authentication & Authorization                          │
│                                                             │
│  🚨 Incident Management                                     │
│                                                             │
│  🛠️ Service Request Management                              │
│                                                             │
│  🔄 Change Management                                       │
│                                                             │
│  ⏱️ SLA Management                                           │
│                                                             │
│  ✅ Approval Workflow                                        │
│                                                             │
│  👨‍💻 Engineer Assignment                                    │
│                                                             │
│  💬 Comments & History                                       │
│                                                             │
│  📊 Dashboard & Analytics                                    │
│                                                             │
│  🔎 Search & Filtering                                       │
│                                                             │
│  🔌 REST API                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

# 🚨 Incident Management

Incidents represent **unplanned interruptions or degradation of an IT service**.

### Example

> Production application is unavailable for all users.

### Incident lifecycle

```text
       ┌────────────┐
       │   New      │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │ Assigned   │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │In Progress │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │  Resolved  │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │   Closed   │
       └────────────┘
```

### Incident information

* Incident number
* Title
* Description
* Application
* Category
* Priority
* Impact
* Urgency
* Assigned engineer
* Status
* SLA deadline
* Resolution
* Created date
* Resolved date
* Comments
* Incident history

---

# 🛠️ Service Request Management

Service Requests are standard requests raised by employees.

### Real-world examples

| Request             | Service        | Category              | Priority |
| ------------------- | -------------- | --------------------- | -------- |
| VPN Access          | Network        | Access Management     | High     |
| Database Access     | Database       | Access Management     | Medium   |
| Python Installation | Software       | Software Installation | Low      |
| Email Access        | Email          | Access Management     | Medium   |
| Server Access       | Infrastructure | Access Management     | High     |
| Application Access  | Application    | Access Management     | Medium   |

### Service Request Workflow

```text
                  User
                   │
                   ▼
          ┌─────────────────┐
          │ Create Request  │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Service         │
          │ Selection       │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Category /      │
          │ Subcategory     │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │ Priority / SLA  │
          └────────┬────────┘
                   │
                   ▼
            ┌──────────────┐
            │   Approval   │
            │   Required?  │
            └──────┬───────┘
                   │
             ┌─────┴─────┐
             │           │
            YES          NO
             │           │
             ▼           │
       ┌────────────┐     │
       │  Approval  │     │
       └─────┬──────┘     │
             │            │
             └─────┬──────┘
                   ▼
          ┌─────────────────┐
          │ Assign Engineer │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │   In Progress   │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │    Resolved     │
          └────────┬────────┘
                   │
                   ▼
          ┌─────────────────┐
          │     Closed      │
          └─────────────────┘
```

---

# 🔄 Change Management

Changes are used to control modifications to production systems.

Examples:

* Application deployment
* Database changes
* Server configuration
* Network changes
* Security patching
* Infrastructure upgrades

### Change Lifecycle

```text
Request
   │
   ▼
Assessment
   │
   ▼
Risk & Impact Analysis
   │
   ▼
Approval
   │
   ▼
Scheduled
   │
   ▼
Implementation
   │
   ├───────────────┐
   │               │
 Success        Failure
   │               │
   ▼               ▼
Validation      Rollback
   │               │
   └───────┬───────┘
           ▼
          PIR
           │
           ▼
         Closed
```

---

# ⏱️ SLA Management

The platform tracks Service Level Agreements to help support teams meet operational targets.

### SLA monitoring includes:

* Response deadline
* Resolution deadline
* SLA status
* Breach detection
* Resolution duration
* Average resolution time

```text
Ticket Created
      │
      ▼
 SLA Timer Starts
      │
      ▼
┌───────────────────┐
│ SLA Monitoring    │
│                   │
│ Remaining Time    │
└─────────┬─────────┘
          │
     ┌────┴─────┐
     │          │
 Within SLA   Breached
     │          │
     ▼          ▼
 Resolved    Escalation
```

---

# 📊 Operations Dashboard

The dashboard provides an operational overview for support teams and managers.

### Key metrics

```text
┌────────────────┬────────────────┬────────────────┐
│ Total Requests │ Open Requests  │ SLA Breached   │
│      125       │       42       │       8        │
└────────────────┴────────────────┴────────────────┘

┌────────────────┬────────────────┬────────────────┐
│ In Progress    │ Pending        │ Resolved       │
│      31        │      12        │      82        │
└────────────────┴────────────────┴────────────────┘
```

### Analytics

The dashboard provides:

* Monthly request trends
* Request status distribution
* Priority distribution
* SLA breach analysis
* Engineer workload
* Average resolution time

---

# 👨‍💻 Engineer Workload

The system tracks tickets assigned to support engineers.

Example:

```text
Engineer             Assigned Tickets
──────────────────────────────────────
Rahul                       18
Arun                        14
Priya                       11
Kiran                        9
Vijay                        6
```

This helps support managers identify:

* Overloaded engineers
* Available engineers
* Assignment imbalance
* Operational bottlenecks

---

# 🔐 Role-Based Access Control

The application uses role-based permissions.

```text
                    ┌─────────────┐
                    │    Admin    │
                    └──────┬──────┘
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Manage Users   Manage Tickets   Analytics
             │
             ▼
     ┌────────────────┐
     │ Support        │
     │ Engineer       │
     └───────┬────────┘
             │
             ▼
      Assigned Tickets
             │
             ▼
        ┌───────────┐
        │ End User  │
        └───────────┘
```

### End User

* Create tickets
* View own tickets
* Add comments
* Track status

### Support Engineer

* View assigned tickets
* Update status
* Add technical notes
* Resolve tickets

### Administrator

* Manage users
* Assign engineers
* Manage tickets
* Monitor SLA
* View analytics
* Manage changes

---

# 🗄️ Database Design

The application uses a relational database structure.

High-level entity relationship:

```text
┌──────────────┐
│    User      │
└──────┬───────┘
       │
       ├──────────────────┐
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│   Incident   │   │   Service    │
└──────┬───────┘   │   Request    │
       │           └──────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│   Comments   │   │   Approval   │
└──────────────┘   └──────────────┘
       │
       ▼
┌──────────────┐
│    History   │
└──────────────┘

┌──────────────┐
│    Change    │
└──────┬───────┘
       │
       ├──────────────► Approval
       │
       └──────────────► History
```

---

# 🧱 Technology Architecture

```text
┌─────────────────────────────────────────────┐
│                 Frontend                    │
│                                             │
│ HTML5 │ CSS3 │ Bootstrap │ JavaScript      │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│                Application                  │
│                                             │
│ Django │ Python │ Forms │ Views │ ORM       │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│                   APIs                      │
│                                             │
│ Django REST Framework │ JSON                │
└───────────────────┬─────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│                 Database                    │
│                                             │
│                 MySQL                       │
└─────────────────────────────────────────────┘
```

---

# 🌐 REST API Architecture

The platform can expose ITSM functionality through REST APIs.

Example endpoints:

```text
GET     /api/incidents/
POST    /api/incidents/
GET     /api/incidents/{id}/
PUT     /api/incidents/{id}/
DELETE  /api/incidents/{id}/

GET     /api/service-requests/
POST    /api/service-requests/
GET     /api/service-requests/{id}/

GET     /api/changes/
POST    /api/changes/

GET     /api/dashboard/
```

Example response:

```json
{
    "request_number": "SR-2026-00125",
    "title": "VPN Access Required",
    "service": "VPN",
    "category": "Network Access",
    "priority": "High",
    "status": "In Progress",
    "assigned_to": "support.engineer",
    "sla_status": "Within SLA"
}
```

---

# 🐳 Docker Architecture

The application can be containerized for consistent development and deployment.

```text
                 ┌─────────────────┐
                 │     Browser     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │     Docker      │
                 │     Network     │
                 └────────┬────────┘
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
       ┌──────────────┐       ┌──────────────┐
       │ Django App   │       │    MySQL     │
       │  Container   │──────▶│  Container   │
       └──────────────┘       └──────────────┘
```

---

# ☁️ Production Cloud Architecture

The application is designed with a path toward AWS deployment.

```text
                         Internet
                            │
                            ▼
                    ┌──────────────┐
                    │     ALB      │
                    │ Load Balancer│
                    └──────┬───────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │    EC2 / ECS      │
                 │   Django App      │
                 │     Docker        │
                 └─────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           ┌──────┐     ┌──────┐    ┌──────────┐
           │ RDS  │     │ S3   │    │CloudWatch│
           │MySQL │     │Files │    │Monitoring│
           └──────┘     └──────┘    └──────────┘
```

---

# 🔎 Advanced Search

Support engineers can quickly find tickets using multiple filters.

Supported filters include:

```text
Request Number
      │
      ├── Title
      │
      ├── Service
      │
      ├── Category
      │
      ├── Subcategory
      │
      ├── Priority
      │
      ├── Status
      │
      ├── Assigned Engineer
      │
      └── Created Date
```

This is useful when handling large ticket volumes in an enterprise support environment.

---

# 📁 Project Structure

```text
incident-management/
│
├── accounts/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── incidents/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── service_requests/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
│
├── changes/
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── incidents/
│   ├── service_requests/
│   └── changes/
│
├── static/
│
├── media/
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── manage.py
└── README.md
```

---

# ⚙️ Local Development Setup

## 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/incident-management.git
cd incident-management
```

## 2. Create virtual environment

```bash
python3.12 -m venv venv
```

Activate:

### Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure database

Create a MySQL database:

```sql
CREATE DATABASE incident_management;
```

Configure database credentials using environment variables.

## 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## 6. Create admin user

```bash
python manage.py createsuperuser
```

## 7. Start application

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

---

# 🧪 Testing

Run Django tests:

```bash
python manage.py test
```

Recommended testing areas:

* Authentication
* Authorization
* Incident creation
* Service request creation
* Engineer assignment
* SLA calculation
* Approval workflow
* Change management
* Search and filtering
* Dashboard analytics
* REST APIs

---

# 🔒 Security

For production deployment:

* `DEBUG=False`
* Environment-based secrets
* Secure database credentials
* HTTPS
* CSRF protection
* Secure cookies
* Restricted `ALLOWED_HOSTS`
* Proper authentication
* Role-based authorization
* Database access restrictions

Never commit:

```text
.env
database passwords
API keys
secret keys
private credentials
```

Recommended `.gitignore`:

```text
venv/
.env
__pycache__/
*.pyc
*.log
db.sqlite3
.idea/
.vscode/
```

---

# 📈 Future Enhancements

The next phase of the project can include:

### Backend

* Django REST Framework
* JWT authentication
* API pagination
* API filtering
* Swagger/OpenAPI documentation
* Celery background processing
* Redis caching

### Cloud

* AWS EC2
* AWS RDS
* AWS S3
* AWS CloudWatch
* AWS IAM
* AWS VPC
* Application Load Balancer

### DevOps

* Docker
* Docker Compose
* GitHub Actions
* CI/CD pipeline
* Automated testing
* Automated deployment

### Monitoring

```text
Django Application
       │
       ▼
   Prometheus
       │
       ▼
    Grafana
       │
       ▼
Application Metrics
```

Potential monitoring metrics:

* CPU utilization
* Memory utilization
* Request latency
* HTTP errors
* Database performance
* Application availability

---

# 🎯 Project Objectives

The primary objective of this project is to build a realistic ITSM platform while demonstrating practical experience in:

* Application Support
* Python
* Django
* SQL
* MySQL
* Linux
* REST APIs
* Git/GitHub
* Docker
* AWS
* Monitoring
* Incident Management
* Service Request Management
* SLA Management

---

# 💼 Real-World Support Scenario

### Scenario

A production application becomes unavailable.

### L1 Support

```text
User reports issue
       ↓
L1 validates issue
       ↓
Checks application health
       ↓
Checks monitoring/logs
```

### L2 Application Support

```text
L1 Escalation
      ↓
Application logs
      ↓
Database validation
      ↓
API validation
      ↓
Root Cause Analysis
      ↓
Fix / Workaround
```

### L3 / Development

```text
Complex application defect
          ↓
Code-level investigation
          ↓
Permanent fix
          ↓
Change Request
          ↓
Production deployment
```

### Final workflow

```text
Incident
   ↓
Investigation
   ↓
Root Cause
   ↓
Change
   ↓
Implementation
   ↓
Validation
   ↓
Incident Resolution
   ↓
Closure
```

This reflects a typical **enterprise application support escalation model**.

---

# 🏆 Key Learning Outcomes

Through this project, I gained practical experience in:

* Designing a multi-module Django application
* Building enterprise-style workflows
* Implementing custom user authentication
* Implementing role-based authorization
* Working with Django ORM
* Designing relational database models
* Implementing SLA calculations
* Building operational dashboards
* Creating search and filtering functionality
* Implementing approval workflows
* Working with Git/GitHub
* Linux-based development
* Docker containerization
* REST API architecture
* Cloud deployment planning
* Application support processes

---

# 👨‍💻 Author

## Vignesh R.

**Application Support | Python | Django | SQL | AWS | Linux | Docker**

This project represents my practical work combining **Application Support knowledge with backend development and cloud/DevOps technologies**.

---

# ⭐ If you find this project useful

Feel free to explore the source code, raise issues, or suggest improvements.

**Built with Python, Django, MySQL and a strong focus on real-world IT Service Management workflows.**

---

## 📌 Project Status

**Current Status:** 🚧 Active Development

### Completed

* [x] Authentication
* [x] Role-based access
* [x] Incident Management
* [x] Incident History
* [x] Comments
* [x] Service Request Management
* [x] Service / Category / Subcategory selection
* [x] SLA tracking
* [x] Engineer assignment
* [x] Change Management
* [x] Dashboard
* [x] Advanced Search & Filtering
* [x] Engineer Workload Analytics
* [x] Monthly Request Trends

### Planned

* [ ] REST API
* [ ] Swagger Documentation
* [ ] Docker Production Setup
* [ ] CI/CD
* [ ] AWS Deployment
* [ ] CloudWatch Monitoring
* [ ] Automated Notifications
* [ ] Celery + Redis
* [ ] Production Monitoring
