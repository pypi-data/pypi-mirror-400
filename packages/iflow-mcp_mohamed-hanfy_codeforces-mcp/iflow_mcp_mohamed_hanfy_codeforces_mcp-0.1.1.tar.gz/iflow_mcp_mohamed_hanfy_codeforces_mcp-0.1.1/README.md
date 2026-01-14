# Codeforces MCP Server

A Model Context Protocol (MCP) server that provides seamless access to the Codeforces API. This server allows you to interact with Codeforces contests, user data, submissions, and ratings through a standardized MCP interface.

## Features

- **Contest Management**: Get contest lists, standings, and rating changes
- **User Information**: Retrieve user profiles, rating history, and submissions
- **Submission Tracking**: Access recent submissions and contest-specific submissions
- **Rating Data**: Get user rating changes and rated user lists
- **Async Support**: Built with async/await for optimal performance

## Available Tools

### Contest Tools
- `get_contest_list` - Get list of contests (with optional gym and group filters)
- `get_contest_rating_changes` - Get rating changes after a specific contest
- `get_contest_standings` - Get contest standings with customizable filters
- `get_contest_status` - Get submissions for a specific contest

### User Tools
- `get_user_info` - Get detailed user information
- `get_user_rating` - Get user's complete rating history
- `get_user_submissions` - Get user's submission history
- `get_rated_users` - Get list of all rated users

### General Tools
- `get_recent_submissions` - Get recent submissions across the platform

## Project Structure

```
.
├── Dockerfile              # Docker container configuration 
├── LICENSE                 
├── README.md              
└── src/                   
    ├── codeforces_mcp.py  # Main MCP server implementation with Codeforces API integration.
    └── requirements.txt   # Python dependencies.
```
## Installation

### Docker (Recommended)

1. **Pull the image from Docker Hub:**
```bash
docker pull mohamed2x/codeforces-mcp
```

2. **Run the container:**
```bash
docker run -i --rm mohamed2x/codeforces-mcp:latest
```

## Configuration

The server runs on stdio transport by default and connects to the official Codeforces API at `https://codeforces.com/api`.

### Dependencies

- `fastmcp` - MCP server framework
- `httpx` - Async HTTP client
- `urllib.parse` - URL parameter encoding
