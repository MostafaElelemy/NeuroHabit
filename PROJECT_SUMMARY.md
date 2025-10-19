# NeuroHabit - Project Summary

## 🎯 Overview

NeuroHabit is a full-stack AI-powered habit tracking application that helps users build and maintain positive habits through intelligent coaching, gamification, and predictive analytics.

## 📋 Project Structure

```
neurohabit/
├── backend/                    # FastAPI Python backend
│   ├── app/
│   │   ├── main.py            # FastAPI application entry point
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic validation schemas
│   │   ├── database.py        # Database configuration
│   │   ├── auth.py            # Authentication & JWT utilities
│   │   ├── crud.py            # Database CRUD operations
│   │   └── ml/
│   │       ├── trainer.py     # LightGBM model training
│   │       └── predictor.py   # ML prediction service
│   ├── alembic/               # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_migration.py
│   ├── tests/                 # Backend unit tests
│   │   └── test_habits.py
│   ├── seed.py                # Database seeding script
│   ├── requirements.txt       # Python dependencies
│   ├── Dockerfile            # Backend container config
│   └── alembic.ini           # Alembic configuration
│
├── frontend/                  # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── Pet.tsx       # Gamification pet component
│   │   │   ├── HabitGraph.tsx # Recharts visualization
│   │   │   ├── HabitCard.tsx  # Habit display card
│   │   │   └── __tests__/
│   │   │       └── Pet.test.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx  # Main dashboard page
│   │   │   └── Login.tsx      # Authentication page
│   │   ├── services/
│   │   │   └── api.ts         # API service layer
│   │   ├── App.tsx            # Main app component
│   │   ├── main.tsx           # React entry point
│   │   └── index.css          # Tailwind styles
│   ├── public/
│   ├── package.json           # Node dependencies
│   ├── Dockerfile            # Frontend container config
│   ├── vite.config.ts        # Vite configuration
│   ├── tailwind.config.js    # Tailwind configuration
│   └── tsconfig.json         # TypeScript configuration
│
├── docker-compose.yml         # Multi-container orchestration
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
├── README.md                 # Project documentation
├── RUNBOOK.md                # Deployment & operations guide
└── PROJECT_SUMMARY.md        # This file

```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0.23
- **Migrations**: Alembic 1.12.1
- **Authentication**: JWT (python-jose) + Google OAuth2
- **ML**: LightGBM 4.1.0, scikit-learn 1.3.2
- **Testing**: pytest 7.4.3
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: React 18.2.0
- **Language**: TypeScript 5.2.2
- **Build Tool**: Vite 5.0.8
- **Styling**: Tailwind CSS 3.3.6
- **Charts**: Recharts 2.10.3
- **HTTP Client**: Axios 1.6.2
- **Routing**: React Router 6.20.0
- **Testing**: Vitest 1.0.4 + Testing Library

### DevOps
- **Containerization**: Docker + Docker Compose
- **Database**: PostgreSQL 15 (Alpine)
- **Reverse Proxy**: (Ready for Nginx/Traefik)

## 🎨 Key Features

### 1. User Authentication
- Email/password registration and login
- JWT token-based authentication
- Google OAuth2 integration (skeleton)
- Secure password hashing with bcrypt

### 2. Habit Management
- Create, read, update, delete (CRUD) habits
- Customizable habit properties:
  - Title, description, category
  - Frequency (daily, weekly, custom)
  - Color and icon for personalization
  - Difficulty and importance ratings
- Habit activation/deactivation
- Streak tracking (current and longest)

### 3. Event Logging
- Log habit completions
- Track contextual data:
  - Mood (1-5 scale)
  - Energy level (1-5 scale)
  - Time of day
  - Day of week
- Historical event viewing

### 4. AI Predictions
- LightGBM-based success prediction
- Risk score calculation (0-1)
- Feature importance analysis
- Personalized recommendations
- Synthetic training data generation

### 5. Gamification
- Virtual pet system
- Experience points (XP) and leveling
- Pet happiness meter
- Visual feedback based on progress
- Animated SVG pet with emotional states

### 6. Analytics & Visualization
- Dashboard with key metrics:
  - Total habits
  - Active habits
  - Completion rate
  - Average streak
- Interactive charts (Recharts):
  - Line charts for trends
  - Bar charts for comparisons
- Recent activity feed

### 7. Responsive UI
- Dark mode support
- Mobile-friendly design
- Tailwind CSS utility classes
- Smooth animations and transitions

## 🗄️ Database Schema

### Users Table
- id (PK)
- email (unique)
- full_name
- google_id (unique, nullable)
- hashed_password (nullable)
- is_active, is_premium
- pet_level, pet_experience, pet_happiness
- created_at, updated_at

### Habits Table
- id (PK)
- user_id (FK → users)
- title, description, category
- frequency, target_count
- color, icon
- is_active
- current_streak, longest_streak
- difficulty_rating, importance_rating
- created_at, updated_at

### Habit Events Table
- id (PK)
- habit_id (FK → habits)
- completed_at
- notes
- mood, energy_level
- time_of_day, day_of_week

### Predictions Table
- id (PK)
- user_id (FK → users)
- habit_id (FK → habits, nullable)
- risk_score
- prediction_type
- features_used (JSON)
- created_at

## 🔌 API Endpoints

### Authentication
- `POST /auth/token` - Login with email/password
- `POST /auth/register` - Register new user
- `GET /auth/google` - Initiate Google OAuth
- `GET /auth/callback` - OAuth callback handler

### Users
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile

### Habits
- `GET /habits` - List all user habits
- `POST /habits` - Create new habit
- `GET /habits/{id}` - Get specific habit
- `PUT /habits/{id}` - Update habit
- `DELETE /habits/{id}` - Delete habit

### Events
- `GET /habits/{id}/events` - List habit events
- `POST /habits/{id}/events` - Log habit completion

### ML
- `POST /predict` - Get habit success prediction

### Dashboard
- `GET /dashboard` - Get complete dashboard data

## 🧪 Testing

### Backend Tests
- Location: `backend/tests/`
- Framework: pytest
- Coverage: Habit CRUD operations
- Run: `docker-compose exec backend pytest -v`

### Frontend Tests
- Location: `frontend/src/components/__tests__/`
- Framework: Vitest + Testing Library
- Coverage: Pet component
- Run: `docker-compose exec frontend npm test`

## 🚀 Deployment

### Local Development
1. Copy `.env.example` to `.env`
2. Run `docker-compose build`
3. Run `docker-compose up -d`
4. Run migrations: `docker-compose exec backend alembic upgrade head`
5. Train ML model: `docker-compose exec backend python -m app.ml.trainer`
6. Seed data: `docker-compose exec backend python seed.py`
7. Access at http://localhost:5173

### Production Considerations
- Use production WSGI server (Gunicorn)
- Set up HTTPS/SSL certificates
- Configure production database (AWS RDS, etc.)
- Set up monitoring (Prometheus, Grafana)
- Configure logging (ELK stack)
- Implement rate limiting
- Set up CI/CD pipeline
- Configure automated backups
- Use secrets management (AWS Secrets Manager, Vault)

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token authentication
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)
- XSS protection (React escaping)
- Environment variable secrets
- Token expiration
- Secure HTTP-only cookies (ready)

## 📊 ML Model Details

### Training Data
- Synthetic data generation
- 5000 samples
- 14 features:
  - Habit characteristics (difficulty, importance, age)
  - User context (time, day, weekend)
  - Historical performance (completion rates)
  - Gamification stats (pet level, happiness)

### Model Architecture
- Algorithm: LightGBM (Gradient Boosting)
- Objective: Binary classification
- Metrics: Accuracy, AUC-ROC
- Feature importance: Gain-based

### Prediction Output
- Risk score (0-1): Probability of habit failure
- Success probability: 1 - risk_score
- Top 5 feature importances
- Personalized recommendation text

## 🎮 Gamification System

### Pet Mechanics
- Gains XP for each habit completion (+10 XP)
- Levels up every 100 XP × current level
- Happiness increases with completions (+2 per event)
- Visual states: Happy (80%+), Neutral (50-79%), Sad (<50%)
- Animated SVG with emotional expressions

### Progression
- Level 1-50+ supported
- Experience carries over between levels
- Happiness decays over time (future feature)
- Achievements system (future feature)

## 🔄 Data Flow

1. **User Login**
   - Frontend sends credentials to `/auth/token`
   - Backend validates and returns JWT
   - Frontend stores token in localStorage
   - Token included in all subsequent requests

2. **Habit Completion**
   - User clicks "Complete" on habit card
   - Frontend calls `POST /habits/{id}/events`
   - Backend creates event record
   - Backend updates habit streak
   - Backend updates pet stats (+10 XP, +2 happiness)
   - Frontend refreshes dashboard

3. **ML Prediction**
   - Frontend requests prediction for habit
   - Backend loads LightGBM model
   - Backend prepares feature vector
   - Model predicts success probability
   - Backend generates recommendation
   - Frontend displays results

## 📈 Future Enhancements

### Short-term
- [ ] Complete Google OAuth integration
- [ ] Stripe payment integration for premium
- [ ] Habit templates library
- [ ] Social features (friends, leaderboards)
- [ ] Push notifications
- [ ] Mobile app (React Native)

### Medium-term
- [ ] Advanced ML models (LSTM for time series)
- [ ] Personalized coaching messages
- [ ] Habit recommendations based on user profile
- [ ] Integration with wearables (Fitbit, Apple Watch)
- [ ] Community challenges
- [ ] Habit sharing and collaboration

### Long-term
- [ ] Multi-language support
- [ ] Voice assistant integration
- [ ] AR/VR habit environments
- [ ] Behavioral psychology insights
- [ ] Research partnerships
- [ ] White-label solution for organizations

## 🐛 Known Limitations

1. **OAuth**: Google OAuth is skeleton implementation only
2. **Stripe**: Payment integration not fully implemented
3. **ML Model**: Uses synthetic data, needs real user data for accuracy
4. **Notifications**: No push notification system yet
5. **Mobile**: Not optimized for mobile apps (web only)
6. **Offline**: No offline support
7. **Real-time**: No WebSocket for real-time updates

## 📝 Environment Variables

### Required
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key

### Optional
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth secret
- `STRIPE_SECRET_KEY` - Stripe API key
- `CORS_ORIGINS` - Allowed CORS origins
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT expiration time

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

- **Backend**: FastAPI, SQLAlchemy, LightGBM
- **Frontend**: React, TypeScript, Tailwind
- **DevOps**: Docker, PostgreSQL
- **ML**: LightGBM, scikit-learn

## 📞 Support

For issues, questions, or contributions:
- Check the RUNBOOK.md for operational guidance
- Review API documentation at `/docs`
- Check logs: `docker-compose logs -f`

---

**Built with ❤️ using AI-assisted development**

Last Updated: 2024
Version: 1.0.0
