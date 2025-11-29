# Quick Start Guide

## Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Free-tier API key from one of:
  - [DeepSeek](https://api-docs.deepseek.com/) (Recommended - easiest to get)
  - [Google Gemini](https://ai.google.dev/gemini-api/docs)
  - [OpenAI](https://platform.openai.com/docs/api-reference/introduction)

## Installation

### Option 1: Automated Setup (Recommended)

```bash
./setup.sh
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Initialize the database with sample data
- Install frontend dependencies
- Create `.env` file from template

### Option 2: Manual Setup

1. **Create and activate virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize database:**
```bash
mkdir -p data
python scripts/init_database.py
```

4. **Setup frontend:**
```bash
cd frontend
npm install
cd ..
```

5. **Configure environment:**
```bash
cp .env.template .env
# Edit .env and add your API key
```

## Configuration

Edit `.env` file and add your LLM API key:

```env
# Choose one:
DEEPSEEK_API_KEY=your_key_here
# OR
GOOGLE_API_KEY=your_key_here
# OR
OPENAI_API_KEY=your_key_here
```

## Running the Application

### Terminal 1: Backend
```bash
source venv/bin/activate
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Frontend will be available at: http://localhost:3000

## Testing the Chatbot

### Test Scenarios

1. **New Patient Registration:**
   - "I'm a new patient and want to book an appointment"
   - Provide: name, phone, date of birth, insurance

2. **Existing Patient:**
   - "I'm an existing patient" (use phone: +1-555-0101)
   - "I want to reschedule my appointment"

3. **Family Scheduling:**
   - "I want to book appointments for me and my two kids"

4. **Emergency:**
   - "I have a dental emergency"
   - Provide emergency details

5. **General Inquiry:**
   - "What are your hours?"
   - "Do you accept insurance?"
   - "I don't have insurance, what are my options?"

### Sample Conversations

**New Patient:**
```
User: Hi, I'm a new patient and want to schedule a cleaning
Bot: Hello! I'd be happy to help you schedule a cleaning appointment. 
     To get started, I'll need some information. What's your full name?
User: John Doe
Bot: Great! What's your phone number?
...
```

**Existing Patient:**
```
User: I'm an existing patient, my phone is +1-555-0101
Bot: I found your account, John Smith. How can I help you today?
User: I want to reschedule my appointment
Bot: I can help with that. When would you like to reschedule to?
...
```

## Troubleshooting

### Backend Issues

**Import errors:**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**LLM API errors:**
- Check your API key in `.env`
- Verify API key is valid and has credits
- Check API provider status

**Database errors:**
- Run `python scripts/init_database.py` again
- Check `data/` directory exists and is writable

### Frontend Issues

**Build errors:**
- Delete `node_modules` and `.next` folders
- Run `npm install` again

**Connection errors:**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in frontend

## Project Structure

```
.
├── domain/              # Business logic
├── application/         # Use cases & services
├── infrastructure/      # External integrations
├── presentation/        # API & frontend
├── data/               # Database files
├── scripts/            # Utility scripts
├── frontend/           # React frontend
├── main.py            # FastAPI entry point
└── requirements.txt   # Python dependencies
```

## Next Steps

1. **Customize Practice Info:**
   - Edit `.env` for practice name, hours, contact

2. **Add More Sample Data:**
   - Modify `scripts/init_database.py`

3. **Deploy:**
   - Backend: Deploy to Railway, Render, or similar
   - Frontend: Deploy to Vercel, Netlify, or similar
   - Database: Migrate to Supabase for production

## Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Review ARCHITECTURE.md for system design
3. Check API docs at http://localhost:8000/docs

