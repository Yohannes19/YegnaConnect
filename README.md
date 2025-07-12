# 🌟 YegnaConnect

**A modern social networking platform built with FastAPI and Python**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 Overview

YegnaConnect is a feature-rich social networking platform that brings people together through posts, categories, and meaningful interactions. Built with modern web technologies, it provides a seamless experience for users to connect, share, and engage with content.

## ✨ Features

### 🔐 Authentication & User Management
- **User Registration & Login** - Secure JWT-based authentication
- **Profile Management** - Customizable user profiles with bio and avatar
- **Follow System** - Follow/unfollow users and view followers/following lists
- **User Search** - Find and connect with other users

### 📱 Social Feed
- **Post Creation** - Share text posts with rich formatting
- **Interactive Feed** - Like, comment, and engage with posts
- **Comment System** - Threaded comments with replies
- **Like System** - Like posts and comments with real-time updates

### 🏷️ Categories & Groups
- **Category Creation** - Create and manage interest-based categories
- **Category Membership** - Join/leave categories and view members
- **Category Posts** - Post content to specific categories
- **Category Discovery** - Browse and discover new categories

### 🎨 Modern UI/UX
- **Responsive Design** - Works perfectly on desktop and mobile
- **Real-time Updates** - Dynamic content updates without page refresh
- **Clean Interface** - Modern, intuitive user interface
- **AJAX Integration** - Smooth, fast user interactions

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Robust, open-source database
- **Alembic** - Database migration tool
- **JWT** - JSON Web Tokens for authentication
- **Pydantic** - Data validation using Python type annotations

### Frontend
- **Jinja2 Templates** - Server-side templating
- **Tailwind CSS** - Utility-first CSS framework
- **JavaScript** - Interactive client-side functionality
- **AJAX** - Asynchronous data loading

### AI Integration
- **OpenAI API** - AI-powered features
- **Hugging Face** - Machine learning capabilities
- **Redis** - Caching and session management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 13+
- Redis (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/yegnaconnect.git
   cd yegnaconnect
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   DATABASE_URL=postgresql+psycopg2://username:password@localhost:5432/yegnaconnect
   JWT_SECRET_KEY=your_super_secret_key_here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
   AI_HF_API_KEY=your_huggingface_api_key_here
   AI_OPENAI_API_KEY=your_openai_api_key_here
   REDIS_URL=redis://localhost:6379
   ```

5. **Set up database**
   ```bash
   # Create database
   createdb yegnaconnect
   
   # Run migrations
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

7. **Visit the application**
   Open your browser and go to `http://localhost:8000`

## 📁 Project Structure

```
YegnaConnect/
├── alembic/                 # Database migrations
├── models/                  # SQLAlchemy models
│   ├── user.py             # User model
│   ├── post.py             # Post model
│   ├── category.py         # Category model
│   └── __init__.py
├── routes/                  # API routes
│   ├── auth.py             # Authentication routes
│   ├── feed.py             # Feed and posts
│   ├── profile.py          # User profiles
│   ├── search.py           # User search
│   └── category.py         # Category management
├── services/               # Business logic
│   ├── auth_service.py     # Authentication logic
│   ├── post_service.py     # Post management
│   └── category_service.py # Category logic
├── templates/              # HTML templates
│   ├── base.html           # Base template
│   ├── feed.html           # Main feed
│   ├── profile.html        # User profiles
│   └── ...
├── static/                 # Static files (CSS, JS, images)
├── config.py               # Configuration settings
├── main.py                 # FastAPI application
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | No | 60 |
| `AI_HF_API_KEY` | Hugging Face API key | No | None |
| `AI_OPENAI_API_KEY` | OpenAI API key | No | None |
| `REDIS_URL` | Redis connection string | No | None |

### Database Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS
   brew install postgresql
   
   # Windows
   # Download from https://postgresql.org/download/windows/
   ```

2. **Create database**
   ```bash
   createdb yegnaconnect
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

## 🎯 API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Posts & Feed
- `GET /feed` - View main feed
- `POST /posts` - Create new post
- `POST /posts/{post_id}/like` - Like/unlike post
- `DELETE /posts/{post_id}` - Delete post

### Comments
- `POST /posts/{post_id}/comments` - Add comment
- `POST /comments/{comment_id}/like` - Like/unlike comment
- `DELETE /comments/{comment_id}` - Delete comment
- `POST /comments/{comment_id}/replies` - Reply to comment

### User Profiles
- `GET /profile/{username}` - View user profile
- `POST /profile/edit` - Edit profile
- `POST /profile/{username}/follow` - Follow/unfollow user
- `GET /profile/{username}/followers` - View followers
- `GET /profile/{username}/following` - View following

### Categories
- `GET /categories` - List all categories
- `POST /categories` - Create new category
- `GET /categories/{category_id}` - View category
- `POST /categories/{category_id}/join` - Join/leave category
- `GET /categories/{category_id}/members` - View category members

### Search
- `GET /search` - Search users

## 🎨 Features in Detail

### 🔐 Authentication System
- Secure JWT-based authentication
- Password hashing with bcrypt
- Session management
- Protected routes

### 📱 Social Feed
- Real-time post creation and display
- Like/unlike functionality with AJAX
- Comment system with threaded replies
- Dynamic content loading

### 👥 User Profiles
- Customizable profile information
- Follow/unfollow system
- Follower and following lists
- Profile picture support

### 🏷️ Categories & Groups
- Interest-based category creation
- Category membership management
- Category-specific posts
- Member discovery

### 🔍 Search Functionality
- User search with real-time results
- Search suggestions
- User discovery

## 🚀 Deployment

### Using Docker

1. **Build the image**
   ```bash
   docker build -t yegnaconnect .
   ```

2. **Run the container**
   ```bash
   docker run -p 8000:8000 yegnaconnect
   ```

### Using Docker Compose

1. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/yegnaconnect
       depends_on:
         - db
       volumes:
         - .:/app
     
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=yegnaconnect
         - POSTGRES_USER=postgres
         - POSTGRES_PASSWORD=password
       volumes:
         - postgres_data:/var/lib/postgresql/data
   
   volumes:
     postgres_data:
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the excellent web framework
- SQLAlchemy for the powerful ORM
- Tailwind CSS for the beautiful styling
- The open-source community for inspiration

## 📞 Support

If you have any questions or need help, please:

- Open an issue on GitHub
- Check the documentation
- Join our community discussions

---

**Made with ❤️ by the YegnaConnect Team** 