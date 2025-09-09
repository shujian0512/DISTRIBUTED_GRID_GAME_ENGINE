# Distributed Grid Game Engine

A FastAPI-based game engine with concurrent gameplay support, comprehensive testing, and real-time simulation capabilities.

## Features

- 🎮 **Game Logic**: Complete game implementation with win/draw detection
- 🚀 **FastAPI Backend**: Modern, async Python web framework
- 🏆 **Leaderboards**: Track player statistics (wins, win rate, efficiency)
- 🧪 **Comprehensive Testing**: Unit, integration, and API tests
- 📊 **Test Coverage**: Built-in coverage reporting
- 🎯 **Simulation Tools**: Concurrent game simulation for testing and analysis
- 📚 **Interactive API Docs**: Swagger UI for API exploration

## Prerequisites

- **Python 3.11+** (tested with Python 3.11)
- **pip** (Python package installer)
- **Virtual environment** (recommended)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/shujian0512/DISTRIBUTED_GRID_GAME_ENGINE.git
cd DISTRIBUTED_GRID_GAME_ENGINE
```

### 2. Create Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
## How to Run the Application

### Start the FastAPI Server
```bash
cd app
fastapi dev main.py
```

The server will start at:
- **API Base URL**: http://127.0.0.1:8000
- **Interactive API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Docs**: http://127.0.0.1:8000/redoc

## API Endpoints

### Players
- `POST /players` - Create a new player
- `GET /players/{player_id}` - Get player information

### Games
- `POST /games` - Create a new game
- `GET /games/available` - Get available games to join
- `POST /games/{game_id}/join` - Join a game
- `POST /games/{game_id}/move` - Make a move

### Leaderboards
- `GET /leaderboard/wins` - Top players by total wins
- `GET /leaderboard/win_rate` - Top players by win percentage
- `GET /leaderboard/efficiency` - Top players by average moves per win

## How to Run Tests

### Run All Tests
```bash
pytest
```
## How to Run Test Coverage

### Generate Coverage Report
```bash
# Basic coverage
pytest --cov=app

# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Combined: terminal + HTML report
pytest --cov=app --cov-report=term-missing --cov-report=html
```

## How to Run Simulation Script

The simulation script runs concurrent games to test the system under load and analyze performance.

### Basic Simulation
```bash
python3 simulation.py
```

This runs a tournament simulation with multiple rounds:
- **Round 1-3**: Winning games for specific players
- **Round 4**: Draw games for all players
- **Round 5**: Additional winning games


### Simulation Output
The script will:
1. Create 10 players
2. Run concurrent games across multiple rounds
3. Display formatted leaderboard results
4. Show summary statistics

### Example Output
```
--- Creating 10 players ---
Players created: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

--- Running Tournament Simulation ---
Round 1: All 5 pairs play - Players 1,2,3,4,5 will win
Round 2: 3 pairs play - Players 1,2,3 will win
...

================================================================================
LEADERBOARD RESULTS
================================================================================

---  Top Players by Wins ---
#1: Player 1 | Wins: 3 | Games Played: 4 | Win Rate: 75.0% | Efficiency: 4.67 moves/win
...
```

## API Documentation

### Swagger UI (Recommended)
Once the server is running, visit:
**http://127.0.0.1:8000/docs**

Features:
- 📋 Complete API endpoint documentation
- 🧪 Interactive testing interface
- 📝 Request/response examples
- 🔧 Try-it-out functionality

### ReDoc (Alternative)
**http://127.0.0.1:8000/redoc**

Features:
- 📖 Clean, readable documentation format
- 📊 Detailed schema information
- 🎨 Professional documentation layout

### API Testing Examples

#### Create a Player
```bash
curl -X POST "http://127.0.0.1:8000/players" -H "Content-Type: application/json"
```

#### Create a Game
```bash
curl -X POST "http://127.0.0.1:8000/games" -H "Content-Type: application/json" -d '{"player_id": 1}'
```

#### Make a Move
```bash
curl -X POST "http://127.0.0.1:8000/games/1/move" -H "Content-Type: application/json" -d '{"player_id": 1, "position": 0}'
```
