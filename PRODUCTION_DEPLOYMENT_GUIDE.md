# MemoryCare - Deployment & Production Guide

## 📋 Table of Contents
1. [Production Checklist](#production-checklist)
2. [Production Settings](#production-settings)
3. [Database Configuration](#database-configuration)
4. [Static Files Setup](#static-files-setup)
5. [Web Server Configuration](#web-server-configuration)
6. [Security Hardening](#security-hardening)
7. [Monitoring & Logging](#monitoring--logging)
8. [Backup & Recovery](#backup--recovery)

---

## ✅ Production Checklist

Before deploying to production, complete these items:

### Pre-Deployment
- [ ] Run Django system checks: `python manage.py check --deploy`
- [ ] All tests passing: `python manage.py test`
- [ ] Static files collected: `python manage.py collectstatic`
- [ ] Database migrated: `python manage.py migrate`
- [ ] SECRET_KEY changed from default
- [ ] DEBUG set to False
- [ ] ALLOWED_HOSTS configured for domain
- [ ] Email backend configured
- [ ] SSL/HTTPS certificate installed
- [ ] Database backup strategy in place

### Code Review
- [ ] No hardcoded passwords or secrets
- [ ] All security middlewares enabled
- [ ] CSRF protection active
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection enabled
- [ ] Rate limiting configured
- [ ] Error handling proper
- [ ] Logging configured

### Infrastructure
- [ ] Web server (Gunicorn/Nginx) installed
- [ ] Database server running
- [ ] Redis cache server (optional)
- [ ] Firewall configured
- [ ] SSH keys configured
- [ ] Backup system operational

---

## ⚙️ Production Settings

### Update settings.py for Production

```python
# SECURITY SETTINGS
SECRET_KEY = os.environ.get('SECRET_KEY')  # Use environment variable!
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', '127.0.0.1']

# HTTPS/SSL
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 1209600  # 2 weeks

# Additional Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'",),
    'style-src': ("'self'", "'unsafe-inline'"),
}

# Allowed Hosts
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
]

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your mail server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/memorycare/django.log',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Environment Variables (.env)
```
SECRET_KEY=your-super-secret-key-change-this
DEBUG=False
DATABASE_URL=mysql://user:password@localhost/memorycare_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS (Optional for media files)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

---

## 🗄️ Database Configuration

### Production MySQL Setup

#### 1. Create Production Database
```sql
CREATE DATABASE memorycare_prod CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'memorycare_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON memorycare_prod.* TO 'memorycare_user'@'localhost';
FLUSH PRIVILEGES;
```

#### 2. Configure in settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'memorycare_prod',
        'USER': 'memorycare_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 600,
    }
}
```

#### 3. Run Migrations
```bash
python manage.py migrate
```

#### 4. Create Superuser
```bash
python manage.py create_doctor \
  --username admin \
  --email admin@yourdomain.com \
  --password secure_password \
  --first-name Admin \
  --last-name User
```

#### 5. Backup Database Regularly
```bash
# Daily backup script
mysqldump -u memorycare_user -p memorycare_prod > /backups/memorycare_$(date +%Y%m%d).sql

# Automated daily backup (cron)
0 2 * * * /usr/local/bin/backup_memorycare.sh
```

---

## 📁 Static Files Setup

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Configure Nginx to Serve Static Files
```nginx
location /static/ {
    alias /home/memorycare/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}

location /media/ {
    alias /home/memorycare/media/;
    expires 7d;
}
```

### Alternative: AWS S3 Storage
```python
# Install
pip install django-storages boto3

# In settings.py
if not DEBUG:
    # S3 Configuration
    USE_S3 = True
    
    AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    
    S3_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}'
    STATIC_URL = f'{S3_URL}/static/'
    MEDIA_URL = f'{S3_URL}/media/'
    
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 🌐 Web Server Configuration

### Option 1: Gunicorn + Nginx

#### Install Gunicorn
```bash
pip install gunicorn
```

#### Create systemd Service File
File: `/etc/systemd/system/memorycare.service`
```ini
[Unit]
Description=MemoryCare Gunicorn Application
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/home/memorycare/project
Environment="PATH=/home/memorycare/venv/bin"
ExecStart=/home/memorycare/venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/home/memorycare/memorycare.sock \
    --error-logfile /var/log/memorycare/error.log \
    --access-logfile /var/log/memorycare/access.log \
    --log-level info \
    memorycare.wsgi:application

[Install]
WantedBy=multi-user.target
```

#### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl start memorycare
sudo systemctl enable memorycare
sudo systemctl status memorycare
```

#### Configure Nginx
File: `/etc/nginx/sites-available/memorycare`
```nginx
upstream memorycare {
    server unix:/home/memorycare/memorycare.sock fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificate
    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    client_max_body_size 10M;
    
    location /static/ {
        alias /home/memorycare/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /home/memorycare/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://memorycare;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Enable Nginx Site
```bash
sudo ln -s /etc/nginx/sites-available/memorycare /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Run Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "memorycare.wsgi:application"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: memorycare_prod
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_USER: memorycare_user
      MYSQL_PASSWORD: user_password
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

  web:
    build: .
    command: gunicorn --bind 0.0.0.0:8000 memorycare.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DEBUG=False
      - DATABASE_URL=mysql://memorycare_user:user_password@db:3306/memorycare_prod

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
    depends_on:
      - web

volumes:
  mysql_data:
  static_volume:
```

Deploy:
```bash
docker-compose up -d
```

---

## 🔒 Security Hardening

### 1. Firewall Configuration
```bash
# UFW (Ubuntu Firewall)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. SSL/TLS Certificate (Let's Encrypt)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 3. Django Security Middleware
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Security Headers
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_SECURITY_POLICY = {
    'default-src': ("'self'",),
    'script-src': ("'self'", "'unsafe-inline'"),
    'style-src': ("'self'", "'unsafe-inline'"),
    'img-src': ("'self'", "data:", "https:"),
}
```

### 4. Regular Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade pip
pip install -U -r requirements.txt
```

### 5. Disable Unnecessary Services
```bash
# Disable if not needed
sudo systemctl disable apache2
sudo systemctl disable sendmail
```

---

## 📊 Monitoring & Logging

### Django Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/memorycare/django.log',
            'maxBytes': 1024 * 1024 * 15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/memorycare/error.log',
            'maxBytes': 1024 * 1024 * 15,
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
```

### Monitor Application Health
```bash
# Check Gunicorn status
sudo systemctl status memorycare

# Check logs
tail -f /var/log/memorycare/django.log
tail -f /var/log/memorycare/error.log

# Monitor resource usage
top
ps aux | grep gunicorn

# Check database connection
mysql -u memorycare_user -p memorycare_prod
```

### Set Up Monitoring Tools
```bash
# Install Prometheus + Grafana for metrics
# Install ELK Stack (Elasticsearch, Logstash, Kibana) for logs
# Install New Relic or DataDog for APM
```

---

## 💾 Backup & Recovery

### Automated Daily Backups

Create backup script: `/usr/local/bin/backup_memorycare.sh`
```bash
#!/bin/bash

BACKUP_DIR="/backups/memorycare"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="memorycare_prod"
DB_USER="memorycare_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u $DB_USER -p"${DB_PASSWORD}" $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /home/memorycare/media/

# Upload to cloud storage (optional)
aws s3 cp $BACKUP_DIR/db_$DATE.sql s3://your-backup-bucket/
aws s3 cp $BACKUP_DIR/media_$DATE.tar.gz s3://your-backup-bucket/

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed at $(date)" >> /var/log/memorycare/backup.log
```

Make executable:
```bash
chmod +x /usr/local/bin/backup_memorycare.sh
```

Add to crontab (daily at 2 AM):
```bash
0 2 * * * /usr/local/bin/backup_memorycare.sh
```

### Restore from Backup

```bash
# Restore database
mysql -u memorycare_user -p memorycare_prod < /backups/memorycare/db_YYYYMMDD_HHMMSS.sql

# Restore media files
tar -xzf /backups/memorycare/media_YYYYMMDD_HHMMSS.tar.gz -C /
```

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing locally
- [ ] Static files collected
- [ ] Database migrations verified
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Backup system tested
- [ ] Monitoring configured
- [ ] Logging configured

### Deployment
- [ ] Deploy code to server
- [ ] Set environment variables
- [ ] Run migrations: `python manage.py migrate`
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Start web server
- [ ] Verify HTTPS redirect
- [ ] Test login functionality
- [ ] Test all major features

### Post-Deployment
- [ ] Monitor error logs
- [ ] Check performance metrics
- [ ] Verify backups running
- [ ] Test recovery process
- [ ] Document deployment steps
- [ ] Schedule security updates
- [ ] Set up alerts

---

## 📞 Troubleshooting Production

### Application Won't Start
```bash
# Check logs
sudo systemctl status memorycare
sudo journalctl -u memorycare -n 50

# Check Python errors
cd /home/memorycare
source venv/bin/activate
python manage.py check
```

### Database Connection Issues
```bash
# Check MySQL status
sudo systemctl status mysql
mysql -u memorycare_user -p

# Check connection settings in settings.py
# Verify database exists
show databases;
use memorycare_prod;
show tables;
```

### Static Files Not Loading
```bash
# Collect static files again
python manage.py collectstatic --clear --noinput

# Check permissions
sudo chown -R www-data:www-data /home/memorycare/staticfiles

# Verify Nginx configuration
sudo nginx -t
```

### High Memory/CPU Usage
```bash
# Monitor processes
top
ps aux | grep gunicorn

# Increase Gunicorn workers if needed
# Optimize database queries
# Enable caching (Redis)
```

---

**Production deployment complete! Monitor regularly for optimal performance.** 🎉
