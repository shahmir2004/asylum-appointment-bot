# 🚀 Setup Guide for Chaudhry - Asylum Bot Collaboration

**Hey Chaudhry!** Welcome to the asylum appointment bot project. Follow this guide to get everything set up on your machine.

## 📋 **What You'll Need**
- [ ] Python 3.11+ installed
- [ ] Git installed  
- [ ] GitHub account
- [ ] Gmail account (for testing notifications)
- [ ] Code editor (VS Code recommended)

---

## 🔧 **Step-by-Step Setup**

### **Step 1: Install Required Software**

#### **Python 3.11+**
1. Go to https://python.org/downloads
2. Download Python 3.11 or newer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation:
   ```bash
   python --version
   # Should show Python 3.11.x
   ```

#### **Git**
1. Go to https://git-scm.com/download
2. Download and install Git
3. Verify installation:
   ```bash
   git --version
   # Should show git version
   ```

#### **VS Code (Recommended)**
1. Go to https://code.visualstudio.com
2. Download and install
3. Install Python extension in VS Code

### **Step 2: Set Up GitHub Access**

#### **Create GitHub Account**
1. Go to https://github.com
2. Create account if you don't have one
3. Send your GitHub username to your brother

#### **Configure Git**
```bash
# Set your name and email (use your GitHub email)
git config --global user.name "Your Name"
git config --global user.email "your-email@gmail.com"
```

### **Step 3: Clone the Project**

```bash
# Navigate to where you want the project
cd C:\Projects  # or wherever you want it

# Clone the repository (replace with actual repo URL)
git clone https://github.com/YourBrother/asylum-appointment-bot.git

# Enter the project directory
cd asylum-appointment-bot

# Switch to development branch
git checkout 001-a-bot-that

# Check status
git status
```

### **Step 4: Set Up Python Environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# You should see (venv) in your command prompt now

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt

# Install Playwright browsers (this will take a few minutes)
python -m playwright install chromium
```

### **Step 5: Configure the Bot**

#### **Set Up Environment File**
```bash
# Copy the example configuration
copy .env.example .env

# Edit the .env file with your settings
notepad .env  # Windows
code .env     # VS Code
nano .env     # Mac/Linux
```

#### **Configure Gmail for Notifications**

**🚨 IMPORTANT: Don't use your regular Gmail password!**

1. **Enable 2-Factor Authentication on Gmail**:
   - Go to https://myaccount.google.com/security
   - Turn on 2-Step Verification

2. **Create App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your OS)
   - Copy the 16-character password

3. **Update .env file**:
   ```env
   GMAIL_USERNAME=your-gmail@gmail.com
   GMAIL_PASSWORD=abcd-efgh-ijkl-mnop  # App password from step 2
   RECIPIENT_EMAIL=your-gmail@gmail.com
   DEFAULT_USER_NAME=Your Full Name
   DEFAULT_USER_EMAIL=your-gmail@gmail.com
   ```

### **Step 6: Test the Setup**

#### **Test Configuration**
```bash
# Test if everything is configured correctly
python test_config.py
```
You should see:
```
✅ Configuration loaded successfully
✅ Configuration validation passed!
🎉 Configuration is ready!
```

#### **Test Email System (Optional)**
```bash
# Test email notifications
python test_email_notifications.py
```
Check your Gmail for a test email.

#### **Test Stealth Capabilities**
```bash
# Test browser automation
python test_stealth.py
```

### **Step 7: Run the Bot**

```bash
# Start the bot in safe mode (no real bookings)
python run.py
```

You should see:
```
🤖 Asylum Appointment Booking Bot (MVP)
✅ Configuration validation passed
🛡️ SAFETY MODE: Booking attempts will be simulated only
🚀 Initializing bot...
✅ All services ready
🎯 Starting monitoring...
```

**Press Ctrl+C to stop the bot**

---

## 🔧 **Daily Development Workflow**

### **Before Starting Work**
```bash
# 1. Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 2. Pull latest changes
git checkout 001-a-bot-that
git pull origin 001-a-bot-that

# 3. Create feature branch for your work
git checkout -b feature/your-feature-name
```

### **While Working**
```bash
# Run tests frequently
python test_config.py
python -m pytest tests/ -v

# Test your changes
python run.py  # Start bot to test
```

### **When Done**
```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add description of what you did"

# Push to GitHub
git push origin feature/your-feature-name

# Create Pull Request on GitHub for review
```

---

## 🚨 **Troubleshooting Common Issues**

### **Problem: Python not found**
```bash
# Try these commands:
python --version
python3 --version
py --version

# If none work, reinstall Python with "Add to PATH" checked
```

### **Problem: pip install fails**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Then try installing requirements again
pip install -r requirements.txt
```

### **Problem: Playwright browser not working**
```bash
# Reinstall browsers
python -m playwright install chromium

# If still not working, try:
python -m playwright install
```

### **Problem: Email not sending**
1. **Check Gmail App Password**:
   - Must be 16 characters with dashes
   - Not your regular Gmail password
   - 2FA must be enabled first

2. **Check .env file**:
   - No spaces around the = sign
   - No quotes around values
   - File must be named exactly `.env`

### **Problem: Import errors**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate

# Make sure you're in the project directory
cd asylum-appointment-bot

# Reinstall dependencies
pip install -r requirements.txt
```

### **Problem: Git issues**
```bash
# Check if you're in a git repository
git status

# If "not a git repository", you're in wrong folder
cd asylum-appointment-bot

# Check current branch
git branch

# Should show 001-a-bot-that as current branch
```

---

## 📱 **Quick Reference Commands**

### **Daily Commands**
```bash
# Activate environment
venv\Scripts\activate

# Pull latest changes
git pull origin 001-a-bot-that

# Run tests
python test_config.py

# Start bot
python run.py

# Stop bot
Ctrl+C
```

### **Git Commands**
```bash
# Check status
git status

# Create new branch
git checkout -b feature/feature-name

# Stage changes
git add .

# Commit changes
git commit -m "description"

# Push changes
git push origin branch-name

# Switch branches
git checkout branch-name
```

---

## 🎯 **What's Already Working**

The bot is **95% complete** and includes:

✅ **Website Monitoring**: Checks Spanish government site every 2 minutes  
✅ **Advanced Stealth**: Bypasses anti-bot detection  
✅ **Email Notifications**: Sends alerts when appointments found  
✅ **Safety Mode**: No real bookings (simulation only)  
✅ **Error Handling**: Graceful recovery from errors  
✅ **Database**: Stores appointment and office data  
✅ **Logging**: Comprehensive activity logging  

---

## 🤝 **Working Together**

### **Communication**
- **GitHub Issues**: For bugs and feature requests
- **Pull Requests**: For code review
- **Direct messaging**: For quick questions

### **Code Review Process**
1. Create feature branch
2. Make changes
3. Push to GitHub
4. Create Pull Request
5. Request review
6. Address feedback
7. Merge when approved

### **Areas to Work On**
1. **Proxy Integration**: Add IP rotation
2. **CAPTCHA Solving**: Handle website puzzles
3. **Multi-Office Support**: Monitor multiple offices
4. **Performance**: Speed improvements
5. **Testing**: More comprehensive tests

---

## 🎉 **You're Ready!**

If you've completed all steps above, you're ready to collaborate on the asylum appointment bot project!

**Next steps**:
1. Familiarize yourself with the code in `src/` folder
2. Read through the tests in `tests/` folder
3. Look at the project specifications in `specs/` folder
4. Start with small improvements or bug fixes

**Need help?** Create a GitHub issue or ask your brother!

**Happy coding! 🚀**
