# PlatformIQ - AI Integration Portal

A modern, Backstage-inspired AI-powered platform for monitoring and managing your cloud infrastructure, GitHub repositories, and APIs.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- GitHub account (for GitHub integration)

### Installation

1. **Clone/Navigate to project**:
   ```bash
   cd Cloud-craft-AI
   ```

2. **Install Python dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Start the backend**:
   ```bash
   python -m uvicorn main:app --reload
   ```

4. **Open in browser**:
   ```
   http://localhost:8000
   ```

## 🔌 Plugin Integrations

### GitHub Integration
Connect your GitHub repository to see:
- 📝 Recent commits and authors
- ⚡ GitHub Actions workflows and CI/CD status
- 🔀 Pull requests and review status
- 🐛 Issues and bug tracking
- 🌿 Branches and protection status

**Setup**: See [GITHUB_SETUP.md](./GITHUB_SETUP.md)

### AWS Integration
Monitor your cloud infrastructure:
- 💰 Cost tracking and analysis
- 🖥️ EC2 instances and scaling
- 🗄️ RDS databases
- 🪣 S3 buckets and storage
- ⚡ Resource utilization metrics

### Postman Integration
Manage API testing and documentation:
- 📮 API collections and workspaces
- ✅ Test results and monitoring
- 📊 API schemas and endpoints
- 🔍 Request/response analysis

### AI Assistant
Ask questions about your infrastructure:
- "What's my current cloud cost?"
- "Show me recent deployments"
- "Are there any failing tests?"
- "What is my API health status?"

## 📊 Dashboard Features

- **Real-time metrics** - Cloud costs, incidents, AI insights
- **Activity feed** - Cross-plugin activity timeline
- **Plugin overview** - Quick access to all integrations
- **Dark theme** - Modern, easy-on-eyes interface
- **Responsive design** - Works on desktop and tablet

## ⚙️ Configuration

All configurations are in the **Settings** page (⚙️ icon):

1. Enter your GitHub token and repository
2. Connect AWS credentials (optional)
3. Add Postman workspace details (optional)
4. Customize portal settings

Or use environment variables in `.env`:
```env
GITHUB_TOKEN=ghp_xxxxx
GITHUB_REPO=owner/repo
AWS_REGION=us-east-1
```

## 🛠️ Technical Stack

- **Frontend**: HTML5, CSS3, Modern JavaScript (Vanilla)
- **Backend**: FastAPI (Python)
- **API Integration**: GitHub API, AWS SDK, Postman API
- **Styling**: Custom CSS with dark theme

## 📁 Project Structure

```
backend/
├── main.py                 # FastAPI app
├── requirements.txt        # Python dependencies
├── static/                 # CSS and JavaScript
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html         # Portal UI
├── api/
│   ├── query.py           # AI queries
│   └── plugins.py         # Plugin endpoints
└── integrations/
    ├── github_connector.py
    ├── aws_connector.py
    └── saas_connector.py
```

## 🔐 Security

- Store sensitive credentials in `.env` file (not in git)
- GitHub tokens created with limited scopes
- AWS credentials secured in environment variables
- Never expose tokens in browser console

## 📝 Environment Variables

Create a `.env` file in the `backend` folder:

```env
# GitHub
GITHUB_TOKEN=your_token_here
GITHUB_REPO=owner/repo

# AWS (optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=xxxxx
AWS_SECRET_ACCESS_KEY=xxxxx

# Postman (optional)
POSTMAN_API_KEY=xxxxx
POSTMAN_WORKSPACE_ID=xxxxx
```

## 🐛 Troubleshooting

### Portal not loading
- Check if backend is running: `python -m uvicorn main:app --reload`
- Verify port 8000 is not in use
- Check browser console (F12) for errors

### GitHub data not showing
- Verify GitHub token is valid
- Check repository format: `owner/repo`
- Ensure token has `repo` and `read:actions` scopes
- Restart backend after changing `.env`

### Slow performance
- Check network connection
- Verify API rate limits haven't been exceeded
- Consider reducing refresh frequency

## 🚀 Future Enhancements

- [ ] Real-time notifications
- [ ] Slack integration
- [ ] Custom dashboards
- [ ] Advanced analytics
- [ ] Webhook support
- [ ] Multi-repository support
- [ ] Docker containerization
- [ ] Auto-deployment setup

## 📚 Documentation

- [GitHub Setup Guide](./GITHUB_SETUP.md)
- [FastAPI Docs](http://localhost:8000/docs) - Auto-generated API documentation
- [GitHub API Reference](https://docs.github.com/en/rest)

## 🤝 Contributing

Found a bug? Have a feature request? Feel free to open an issue or submit a pull request!

## 📄 License

MIT License - feel free to use for personal and commercial projects.

## 💡 Tips

1. **Bookmark the Settings page** for easy configuration
2. **Use the Sync button** to manually refresh plugin data
3. **Check the AI Assistant** for quick infrastructure insights
4. **Monitor the activity feed** for real-time updates

---

**Made with ❤️ by the Cloud-craft-AI team**
