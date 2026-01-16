# Online Fitness Store
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-4.x-darkgreen)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-blue)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![AWS](https://img.shields.io/badge/AWS-EC2-orange)
![Stripe](https://img.shields.io/badge/Payments-Stripe-6772E5)
![License](https://img.shields.io/badge/License-Educational-lightgrey)


A production-ready Django e-commerce platform for fitness products, digital downloads, and services. Features include user authentication, multi-product type management, shopping cart, order processing, and AWS EC2 deployment.

## 🔐 Demo Access

**🌐 [Visit Live Site](https://fitness.lwsoc.com/)**

**Demo Credentials:**
- Email: `demo@fitness-demo.com`
- Password: `Demo123!`

> ⚠️ **Note**: This is a demo account. All data is reset periodically. The demo account is pre-verified for instant access. In production, email verification is required for all new users.




## 📸 Screenshots

### Home Page
Public landing page with featured products and membership access.
![Home](screenshots/home.png)

### Product Listing
Search, category filters, and pagination for physical, digital, and service products.
![Products](screenshots/products.png)

### Product Detail
Detailed product view with media gallery, stock tracking, and add-to-cart.
![Product Detail](screenshots/product_detail.png)

### Shopping Cart
Cart management with tax calculation and shipping rules.
![Cart](screenshots/cart.png)

### Admin Dashboard
Django admin interface for managing products, orders, inventory, and memberships.
![Admin](screenshots/dashboard.png)



## 🚀 Features

### Core Features
- **Multi-Product Types**: Physical products, digital downloads, and bookable services
- **Smart Shopping Cart**: Session-based cart for anonymous users, transfers to database on login
- **Flexible Checkout**: Adaptive checkout flow (shipping for physical, instant for digital/services)
- **Inventory Management**: Real-time stock tracking and service seat management
- **User Authentication**: Email verification, profiles, and membership tracking
- **Admin Dashboard**: Full CRUD operations with Django admin customization
- **Order Processing**: Digital download links, pickup locations, tax calculation
- **Production Ready**: Docker containerization, Nginx reverse proxy, AWS EC2 deployment

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/online-fitness-store-P.git
cd online-fitness-store-P

# Using Docker
docker compose up -d

# Or local setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ec2.env.example .env
# Edit .env with your settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://localhost:8000` in your browser.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Development](#-development)
- [Deployment](#-deployment)
- [Documentation](#-documentation)
- [Contributing](#-contributing)

## 🛠 Tech Stack

### Backend
- **Django 5.0.2**: Web framework
- **PostgreSQL**: Production database
- **SQLite**: Development database
- **Django Allauth**: Authentication and account management
- **Django REST Framework**: API support (optional)

### Frontend
- **HTML5/CSS3**: Responsive design
- **JavaScript**: Dynamic form interactions
- **Bootstrap-inspired**: Custom styling

### DevOps
- **Docker & Docker Compose**: Containerization
- **Nginx**: Reverse proxy and static file serving
- **Gunicorn**: WSGI HTTP server
- **AWS EC2**: Cloud hosting

## 🏗️ Architecture

### System Design
- **MVC Pattern**: Django follows Model-View-Template architecture
- **Database Design**: Normalized schema with proper relationships and foreign keys
- **Session Management**: Anonymous cart support with session-based storage that transfers to database on login
- **Security**: CSRF protection, SQL injection prevention, XSS protection, secure password hashing
- **Scalability**: Docker containerization, Nginx reverse proxy, static file optimization with WhiteNoise

### Technical Highlights
- Session-based anonymous cart with automatic transfer to database on login
- Dynamic checkout flow adapting to product types
- Multi-image product galleries with main image selection
- Admin-configurable featured products with singleton content management
- Full-text search with category filtering and pagination

## 📁 Project Structure

```
online-fitness-store/
├── accounts/              # User authentication and account management
├── api/                   # REST API endpoints (optional)
├── cart/                  # Shopping cart functionality
├── core/                  # Core utilities and shared functionality
├── fitness_club/          # Main Django project settings
│   └── fitness_club/      # Settings, URLs, WSGI/ASGI configs
├── home/                  # Home page and landing
├── members/               # Membership management
├── orders/                # Order processing and management
├── payment/               # Checkout and payment processing
├── products/              # Product catalog and management
├── profiles/              # User profile management
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── media/                 # User-uploaded files (product images, digital files)
├── nginx/                 # Nginx configuration
├── tools/                 # Utility scripts (backup, restore, diagnostics)
├── docs/                  # Documentation files
├── docker-compose.yml     # Development Docker setup
├── docker-compose.prod.yml # Production Docker setup
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Key Apps Explained

- **accounts/**: Handles user registration, login, email verification, and account settings
- **cart/**: Shopping cart models and views for adding/removing items
- **orders/**: Order models, order processing, digital download management, pickup locations
- **payment/**: Checkout flow, payment processing (simulated), order creation
- **products/**: Product catalog, categories, inventory management, product types (physical/digital/service)
- **profiles/**: User profile management, shipping addresses
- **members/**: Membership tracking and management
- **core/**: Shared utilities, admin customizations, contact page

## 🚀 Installation

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Docker & Docker Compose (optional, for containerized deployment)
- Git

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/online-fitness-store-P.git
   cd online-fitness-store-P
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp ec2.env.example .env
   ```
   
   Edit `.env` with your settings:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_DEBUG=1
   POSTGRES_DB=fitness_club_db
   POSTGRES_USER=fitness_user
   POSTGRES_PASSWORD=your-password
   DB_HOST=localhost
   POSTGRES_PORT=5432
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

   Visit `http://localhost:8000` in your browser.

### Docker Setup

See [docs/setup/DOCKER_SETUP.md](docs/setup/DOCKER_SETUP.md) for detailed Docker setup instructions.

## ⚙️ Configuration

### Environment Variables

Key environment variables (set in `.env` file):

- `DJANGO_SECRET_KEY`: Secret key for Django (required)
- `DJANGO_DEBUG`: Set to `1` for development, `0` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins for CSRF
- `POSTGRES_DB`: Database name
- `POSTGRES_USER`: Database user
- `POSTGRES_PASSWORD`: Database password
- `DB_HOST`: Database host (use `db` for Docker, `localhost` for local)
- `POSTGRES_PORT`: Database port (default: 5432)

### Django Settings

Main settings file: `fitness_club/fitness_club/settings.py`

Key configurations:
- **Database**: PostgreSQL for production, SQLite for development
- **Static Files**: Served via WhiteNoise in production
- **Media Files**: Served via Nginx in production
- **Email**: Configured for email verification (see [docs/setup/EMAIL_VERIFICATION.md](docs/setup/EMAIL_VERIFICATION.md))
- **Authentication**: Django Allauth for user management

## 💻 Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Admin Panel

1. Create a superuser (if not already created):
   ```bash
   python manage.py createsuperuser
   ```

2. Visit `https://fitness.lwsoc.com/admin/` and login

### Key Development Commands

```bash
# Collect static files
python manage.py collectstatic

# Create a new app
python manage.py startapp app_name

# Open Django shell
python manage.py shell

# Check for issues
python manage.py check
```

## 🚢 Deployment

### AWS EC2 Deployment

Complete deployment guide: [docs/deployment/AWS_DEPLOYMENT.md](docs/deployment/AWS_DEPLOYMENT.md)

Quick steps:
1. Set up EC2 instance
2. Install Docker and Docker Compose
3. Clone repository
4. Configure environment variables
5. Set up Nginx reverse proxy
6. Configure SSL/HTTPS
7. Deploy with Docker Compose

### Production Checklist

- [ ] Set `DJANGO_DEBUG=0` in `.env`
- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Configure email backend for production
- [ ] Set up database backups
- [ ] Configure static file serving
- [ ] Set up monitoring and logging

## 📚 Documentation

All documentation is organized in the `docs/` folder. See [docs/README.md](docs/README.md) for a complete index.

**Essential Guides:**
- **[AWS Deployment](docs/deployment/AWS_DEPLOYMENT.md)**: Complete EC2 deployment guide
- **[Docker Setup](docs/setup/DOCKER_SETUP.md)**: Containerization and configuration
- **[Project Structure](docs/PROJECT_STRUCTURE.md)**: Project organization and architecture

**Additional Resources:**
- **[Deployment Guides](docs/deployment/)**: All deployment documentation
- **[Setup Guides](docs/setup/)**: Configuration instructions
- **[User Guides](docs/guides/)**: Testing and feature guides

## 🎯 Product Types & Checkout

**Physical Products**: Stock management, shipping/pickup options, address collection  
**Digital Products**: Instant download with secure link generation and email delivery  
**Service Products**: Seat management with date/time scheduling

The checkout flow automatically adapts: full checkout with shipping for physical products, simplified checkout for digital/services only, and mixed cart support.

## 🤝 Contributing

This is a learning project. Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests
- Report issues

## 📝 License

This project is for educational purposes.

---

**Built with Django, Docker, and modern web technologies. Production-ready with comprehensive error handling, security best practices, and deployment configurations.**

