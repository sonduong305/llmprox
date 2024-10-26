# LLMProx

LLMProx is a Django-based application that provides API and WebSocket endpoints for interacting with Large Language Models (LLMs) using the `litellm` library. It leverages Django REST Framework for RESTful APIs, Channels for WebSocket support, and integrates seamlessly with deployment platforms like Vercel.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running in Development](#running-in-development)
- [Running Tests](#running-tests)
- [Deployment on Vercel](#deployment-on-vercel)
- [Project Structure](#project-structure)
- [License](#license)

## Features

- **REST API**: Provides an endpoint for LLM completions.
- **WebSocket Support**: Enables real-time interactions with LLMs.
- **Asynchronous Processing**: Utilizes Django Channels and `litellm` for efficient async operations.
- **Comprehensive Testing**: Includes unit and integration tests using pytest.
- **Deployment-Ready**: Configured for deployment on platforms like Vercel.

## Technology Stack

- **Backend**:
  - [Django](https://www.djangoproject.com/) 5.0.9
  - [Django REST Framework](https://www.django-rest-framework.org/) 3.15.2
  - [Channels](https://channels.readthedocs.io/en/stable/) 4.0.0
  - [litellm](https://github.com/BerriAI/litellm) 1.51.0
- **Testing**:
  - [pytest](https://pytest.org/) 8.3.3
  - [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) 0.24.0
  - [pytest-django](https://github.com/pytest-dev/pytest-django) 4.9.0
- **Deployment**:
  - [Vercel](https://vercel.com/) (Configured via `vercel.json`)
- **Others**:
  - [dotenv](https://github.com/theskumar/python-dotenv) for environment variable management

## Prerequisites

- **Python**: Version 3.12.1
- **pip**: Python package installer
- **Virtual Environment**: Recommended for dependency management

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/sonduong305/llmprox.git
   cd llmprox
   ```

2. **Set Up Virtual Environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   pip install -r requirements.dev.txt
   ```

## Configuration

1. **Environment Variables**

   Copy `.env.example` to create your `.env` file:

   ```bash
   cp .env.example .env
   ```

   Then populate it with the necessary environment variables:

   ```env
   # General
   DJANGO_SETTINGS_MODULE=config.settings
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   ALLOWED_HOSTS="*"
   API_TOKEN=your-secure-api-token-here
   ```

   **Required Variables**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `ANTHROPIC_API_KEY`: Your Anthropic API key (if using Claude)
   - `ALLOWED_HOSTS`: Comma-separated list of allowed hosts (default "*" allows all)
   - `API_TOKEN`: Secure token for API authentication

   **Note**: In production, make sure to set appropriate values for `ALLOWED_HOSTS` instead of using "*"
2. **Django Settings**

   The project uses `django-environ` for managing environment variables. Ensure all required variables are set in the `.env` file.

## Running in Development

1. **Run the Development Server**

   ```bash
   python manage.py runserver
   ```

   The server will be accessible at `http://127.0.0.1:8000/`.

2. **Accessing the API**

   - **LLM Completion API**: `http://127.0.0.1:8000/api/v1/completion/`
   - **WebSocket Endpoint**: `ws://127.0.0.1:8000/ws/api/v1/completion/`

## Running Tests

The project includes comprehensive tests using pytest. To run the tests:

1. **Ensure the Virtual Environment is Activated**

   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Run pytest**

   ```bash
   pytest
   ```

   **Coverage Report**: After running tests, a coverage report in HTML format will be generated in the `htmlcov/` directory. Open `htmlcov/index.html` in your browser to view detailed coverage metrics.


## Deployment on Vercel

1. **Install Vercel CLI** (optional, for local development with Vercel)

   ```bash
   npm i -g vercel
   ```

2. **Prepare for Deployment**

   Create a `build_files.sh` in your project root:
   ```bash
   # build_files.sh
   pip install -r requirements.txt
   python manage.py collectstatic --noinput
   ```

   Make it executable:
   ```bash
   chmod +x build_files.sh
   ```

3. **Deploy Using Vercel CLI**

   For first-time deployment:
   ```bash
   vercel
   ```

   For subsequent deployments:
   ```bash
   vercel --prod
   ```

4. **Deploy Using Vercel Dashboard**

   Alternatively, you can deploy through the Vercel dashboard:
   - Connect your GitHub repository to Vercel
   - Configure the build settings:
     - Framework Preset: Other
     - Build Command: `sh ./build_files.sh`
     - Output Directory: `staticfiles`
     - Install Command: `pip install -r requirements.txt`

5. **Configure Environment Variables**

   In Vercel dashboard, add these environment variables:
   ```
   DJANGO_SETTINGS_MODULE=config.settings
   OPENAI_API_KEY=your-openai-api-key
   ANTHROPIC_API_KEY=your-anthropic-api-key
   ALLOWED_HOSTS=your-vercel-domain.vercel.app
   API_TOKEN=your-secure-api-token-here
   ```

6. **Verify Deployment**

   After deployment, verify your endpoints:
   - REST API: `https://your-project.vercel.app/api/v1/completion/`
   - WebSocket: `wss://your-project.vercel.app/ws/api/v1/completion/`

**Note**: Vercel has a 10-second timeout for serverless functions on hobby plans. For longer-running LLM operations, consider using edge functions or upgrading to a paid plan.


### **WebSocket Support**

Due to Vercel's serverless nature, each request is limited to **10 seconds**, which poses challenges for long-running WebSocket connections. As a result, WebSocket support is currently available only during local development.

#### **Future Deployment Plans for WebSockets**

Deploying WebSocket functionality in production is a planned enhancement. Here are some options being considered:

1. **Dedicated WebSocket Hosting Services**
   - **[Heroku](https://www.heroku.com/)**: Supports persistent WebSocket connections and is compatible with Django Channels.
   - **[AWS Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/)**: Offers scalable infrastructure with support for long-lived connections.
   - **[DigitalOcean App Platform](https://www.digitalocean.com/products/app-platform/)**: Provides flexible deployment options suitable for WebSockets.

2. **Hybrid Deployment Strategy**
   - **Separate API and WebSocket Servers**: Host the REST API on Vercel and the WebSocket server on another platform that supports persistent connections.
   - **Reverse Proxy Setup**: Use a reverse proxy (e.g., Nginx) to manage and route WebSocket traffic to a dedicated server.

3. **Utilize Persistent Infrastructure**
   - **Container-Based Deployments**: Deploy the application using Docker containers on platforms like Kubernetes, ensuring persistent WebSocket support.
   - **Virtual Private Servers (VPS)**: Host the WebSocket server on a VPS where connection limits are more manageable.

Implementing one of these options will enable WebSocket functionality in the deployed application, enhancing real-time interactivity and providing a more robust user experience.

## API Documentation

### Chat Completion Endpoint

**Endpoint**: `/api/v1/chat-completion/`  
**Method**: POST  
**Authentication**: Token-based  

#### Headers
```http
Content-Type: application/json
Authorization: Token your-api-token-here
```

#### Request Body
```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are an English -> Spanish translator. If a user writes something in English, reply by translating that into Spanish."
    },
    {
      "role": "user",
      "content": "orange, apple, watermelon"
    }
  ],
  "params": {
      "model": "gpt-3.5-turbo",  // optional, defaults to "gpt-3.5-turbo"
      "temperature": 0.7,        // optional, defaults to 0.7
      "max_tokens": 1000         // optional, defaults to 1000
  }
}
```

#### Response Format
```json
{
  "messages": [
    {
      "role": "assistant",
      "content": "naranja, manzana, sandía"
    }
  ],
  "metadata": {
    "model": "gpt-3.5-turbo",
    "usage": {
      "prompt_tokens": 5,
      "completion_tokens": 5,
      "total_tokens": 10
    },
    "created": 1616461000
  }
}
```

#### Error Responses

1. **Authentication Error** (401 Unauthorized)
```json
{
  "detail": "Authentication credentials were not provided."
}
```

2. **Invalid Request** (400 Bad Request)
```json
{
  "error": "Invalid request",
  "details": {
    "messages": ["This field is required."]
  }
}
```

3. **LLM Processing Error** (500 Internal Server Error)
```json
{
  "error": "LLM processing error",
  "message": "Error message from LLM service"
}
```

#### Example cURL Request
```bash
curl -X POST http://{assistant-agent-domain}/api/v1/chat-completion/ \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Token your-api-token-here' \
  -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are an English -> Spanish translator. If a user writes something in English, reply by translating that into Spanish."
      },
      {
        "role": "user",
        "content": "orange, apple, watermelon"
      }
    ]
  }'
```

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| messages | array | Yes | - | Array of message objects with role and content |
| model | string | No | "gpt-3.5-turbo" | The LLM model to use |
| temperature | float | No | 0.7 | Controls randomness (0.0-2.0) |
| max_tokens | integer | No | 1000 | Maximum tokens in response |

## Project Structure

```
llmprox/
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── llmprox/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── consumers.py
│   │   ├── exceptions.py
│   │   ├── routing.py
│   │   ├── serializers.py
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_views.py
│   │   └── views.py
│   └── apps.py
├── staticfiles/
├── templates/
├── tests.py
├── manage.py
├── requirements.txt
├── requirements.dev.txt
├── runtime.txt
├── vercel.json
└── pytest.ini
```


## License

This project is licensed under the [MIT License](LICENSE).
