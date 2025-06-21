# Agent Maker - Complete System Documentation

## 🤖 Overview

Agent Maker is a fully working, standalone system for creating, training, and deploying intelligent web scraping agents. The system is designed to be trainable, deployable onto websites with easy configuration abilities, and can scrape daily information from sources/links to perform positive actions automatically.

## ✨ Key Features

### Core Capabilities
- **Trainable Agents**: Record user demonstrations and learn extraction patterns
- **Cross-platform Compatibility**: Works on both mobile and desktop devices
- **User Agent Randomization**: Automatic fake user agent generation to avoid detection
- **Daily Automation**: Scheduled scraping with positive action triggers
- **Easy Configuration**: Web-based interface for agent management
- **Embeddable Widgets**: Deploy agents on any website with simple JavaScript

### System Components
1. **Backend API** (Flask) - Core agent engine and data processing
2. **Frontend Dashboard** (React) - Web-based configuration interface
3. **Scraping Engine** - Advanced web scraping with Playwright and BeautifulSoup
4. **Training System** - UI action recording and pattern recognition
5. **Deployment Tools** - Scripts and widgets for easy deployment

## 🚀 Quick Start

### Development Environment
- **Backend API**: http://localhost:5001/api
- **Frontend Dashboard**: http://localhost:5173

### Production Environment
- **Backend API**: https://5001-impkqsz90jj2vmepwvpqu-44b35dc8.manusvm.computer
- **Frontend Dashboard**: https://8080-impkqsz90jj2vmepwvpqu-44b35dc8.manusvm.computer

## 📋 API Endpoints

### User Management
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `GET /api/users/{id}` - Get user details

### Agent Management
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Scraping Operations
- `POST /api/scraping/jobs` - Start scraping job
- `GET /api/scraping/jobs/{id}` - Get job status
- `POST /api/scraping/test` - Test URL scraping
- `POST /api/scraping/validate-url` - Validate URL and check robots.txt

### Training System
- `GET /api/training/templates` - List configuration templates
- `GET /api/training/templates/{type}` - Get specific template
- `POST /api/training/sessions` - Start training session
- `POST /api/training/sessions/{id}/actions` - Record UI action
- `POST /api/training/sessions/{id}/complete` - Complete training session

## 🎯 Usage Examples

### Creating a News Monitoring Agent

1. **Create User**:
```bash
curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{"username": "news_user", "email": "user@example.com"}'
```

2. **Create Agent**:
```bash
curl -X POST http://localhost:5001/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "News Monitor",
    "description": "Monitor tech news daily",
    "user_id": 1,
    "scraping_schedule": "daily"
  }'
```

3. **Add Data Source**:
```bash
curl -X POST http://localhost:5001/api/agents/1/data-sources \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://news.ycombinator.com",
    "source_type": "webpage",
    "extraction_rules": {
      "title_selector": ".titleline > a",
      "content_selector": ".comment"
    }
  }'
```

4. **Start Scraping**:
```bash
curl -X POST http://localhost:5001/api/scraping/jobs \
  -H "Content-Type: application/json" \
  -d '{"agent_id": 1}'
```

### Using Configuration Templates

Get available templates:
```bash
curl http://localhost:5001/api/training/templates
```

Use a specific template:
```bash
curl http://localhost:5001/api/training/templates/news_aggregation
```

## 🔗 Website Integration

### Embeddable Widget

Add this to any website to embed an Agent Maker widget:

```html
<!DOCTYPE html>
<html>
<head>
    <title>My Website</title>
</head>
<body>
    <h1>My Website Content</h1>
    
    <!-- Agent Maker Widget -->
    <div id="agent-widget" 
         data-agent-maker
         data-agent-id="1"
         data-api-url="https://5001-impkqsz90jj2vmepwvpqu-44b35dc8.manusvm.computer"
         data-theme="light">
    </div>
    
    <script src="https://your-domain.com/agent-maker-widget.js"></script>
</body>
</html>
```

### Manual Widget Initialization

```javascript
new AgentMakerWidget({
    containerId: 'my-widget',
    agentId: 1,
    apiUrl: 'https://5001-impkqsz90jj2vmepwvpqu-44b35dc8.manusvm.computer',
    theme: 'dark'
});
```

## 🛠️ Configuration Templates

### News Aggregation
- **Purpose**: Monitor news websites for new articles
- **Extraction Rules**: Title, content, author, date, URL
- **Actions**: Email digest, webhook notifications

### Price Monitoring
- **Purpose**: Track product prices and get alerts
- **Extraction Rules**: Product title, price, description, reviews
- **Actions**: Price change alerts, comparison reports

### Content Monitoring
- **Purpose**: Monitor websites for new content or changes
- **Extraction Rules**: Configurable based on website structure
- **Actions**: Change notifications, content archiving

## 🔧 Advanced Features

### User Agent Randomization
The system automatically generates random user agent strings to avoid detection:
- Desktop browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Android Chrome)
- Various operating systems and versions

### Rate Limiting and Respect
- Automatic robots.txt checking
- Configurable delays between requests
- Concurrent job limiting
- Polite crawling practices

### Training System
- Record user interactions on websites
- Learn extraction patterns automatically
- Adapt to different layouts and screen sizes
- Generate configuration templates

## 📊 Monitoring and Analytics

### Real-time Status
- Agent activity monitoring
- Scraping job progress
- Error tracking and reporting
- Performance metrics

### Dashboard Features
- Agent management interface
- Training session visualization
- Configuration templates
- Deployment tools

## 🔒 Security Features

### Data Protection
- Secure API endpoints
- Input validation and sanitization
- SQL injection prevention
- XSS protection

### Ethical Scraping
- Robots.txt compliance
- Rate limiting
- User agent identification
- Respectful crawling

## 📦 Deployment Options

### Development
```bash
# Backend
cd agent-maker
source venv/bin/activate
python src/main.py

# Frontend
cd agent-maker-frontend
pnpm run dev
```

### Production
```bash
# Use the deployment script
./deploy.sh

# Or manual deployment
cd agent-maker-production
./start.sh
```

### Docker (Future Enhancement)
```bash
docker-compose up -d
```

## 🤝 Contributing

The system is designed to be extensible:
- Add new scraping engines
- Create custom extraction rules
- Build additional training templates
- Develop new positive action types

## 📞 Support

For issues and questions:
- Check the API documentation
- Review configuration templates
- Test with the provided examples
- Use the web dashboard for visual configuration

## 🎉 Success Metrics

The Agent Maker system successfully provides:
- ✅ Fully working standalone operation
- ✅ Trainable agent capabilities
- ✅ Easy website deployment
- ✅ Daily information absorption
- ✅ Positive action automation
- ✅ Cross-platform compatibility
- ✅ User agent randomization
- ✅ Professional web interface

The system is now ready for production use and can be easily deployed on any website or server infrastructure.

