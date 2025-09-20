# Odyssey 🚀
Task management tool

## Overview
Odyssey is a simple, elegant task management tool built with Node.js and Express. It provides a clean web interface for creating, managing, and tracking tasks.

## Features
- Create new tasks with title and description
- Mark tasks as complete/incomplete
- Delete tasks
- Clean, responsive web interface
- RESTful API for task operations
- Health check endpoint for monitoring

## Quick Start with Docker

### Prerequisites
- Docker
- Docker Compose (optional, for easier deployment)

### Using Docker Compose (Recommended)
1. Clone the repository
2. Navigate to the project directory
3. Run the application:
   ```bash
   docker compose up -d
   ```
4. Access the application at http://localhost:3000

### Using Docker directly
1. Build the image:
   ```bash
   docker build -t odyssey:latest .
   ```
2. Run the container:
   ```bash
   docker run -p 3000:3000 odyssey:latest
   ```
3. Access the application at http://localhost:3000

## Development

### Local Development
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the development server:
   ```bash
   npm start
   ```
3. Access the application at http://localhost:3000

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/:id` - Get specific task
- `POST /api/tasks` - Create new task
- `PUT /api/tasks/:id` - Update task
- `DELETE /api/tasks/:id` - Delete task

## Docker Configuration

The application includes optimized Docker configuration:
- Multi-stage build for smaller image size
- Non-root user for security
- Health checks for monitoring
- Production-ready settings

## Environment Variables

- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (default: production in Docker)
