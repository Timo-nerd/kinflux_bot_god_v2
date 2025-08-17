from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import os
import uuid
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="SoccerStream API",
    description="API for soccer streaming platform with live matches, highlights, and schedule data",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = "soccerstream"

# Global database client
client = None
database = None

# Pydantic models
class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    country: str
    logo_url: Optional[str] = None

class Score(BaseModel):
    home: int
    away: int

class Match(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    home_team: str
    away_team: str
    league: str
    date: str
    time: str
    status: str  # 'live', 'upcoming', 'finished'
    score: Optional[Score] = None
    has_highlights: bool = False
    is_free: bool = True
    video_url: Optional[str] = None
    highlights_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class League(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    country: str
    icon: str
    season: str = "2024-25"

class MatchResponse(BaseModel):
    matches: List[Match]
    total: int
    page: int
    limit: int

class UserFavorite(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    match_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Database connection
async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        client = AsyncIOMotorClient(MONGO_URL)
        database = client[DATABASE_NAME]
        
        # Test the connection
        await client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Initialize sample data
        await initialize_sample_data()
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("Disconnected from MongoDB")

async def initialize_sample_data():
    """Initialize the database with sample data"""
    try:
        # Sample leagues
        leagues_data = [
            {
                "id": "premier-league",
                "name": "Premier League",
                "country": "England",
                "icon": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
                "season": "2024-25"
            },
            {
                "id": "la-liga",
                "name": "La Liga",
                "country": "Spain",
                "icon": "🇪🇸",
                "season": "2024-25"
            },
            {
                "id": "champions-league",
                "name": "UEFA Champions League",
                "country": "Europe",
                "icon": "🏆",
                "season": "2024-25"
            },
            {
                "id": "world-cup",
                "name": "FIFA World Cup",
                "country": "World",
                "icon": "🌍",
                "season": "2026"
            },
            {
                "id": "afcon",
                "name": "AFCON",
                "country": "Africa",
                "icon": "🌍",
                "season": "2025"
            }
        ]
        
        # Insert leagues if they don't exist
        for league_data in leagues_data:
            existing_league = await database.leagues.find_one({"id": league_data["id"]})
            if not existing_league:
                await database.leagues.insert_one(league_data)
        
        # Sample matches
        matches_data = [
            {
                "id": str(uuid.uuid4()),
                "home_team": "Manchester United",
                "away_team": "Liverpool",
                "league": "Premier League",
                "date": "2025-01-20",
                "time": "15:00",
                "status": "live",
                "score": {"home": 2, "away": 1},
                "has_highlights": True,
                "is_free": True,
                "video_url": "https://example.com/live/match1",
                "highlights_url": "https://example.com/highlights/match1",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "home_team": "Real Madrid",
                "away_team": "Barcelona",
                "league": "La Liga",
                "date": "2025-01-20",
                "time": "20:00",
                "status": "upcoming",
                "score": None,
                "has_highlights": False,
                "is_free": True,
                "video_url": None,
                "highlights_url": None,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "home_team": "Bayern Munich",
                "away_team": "PSG",
                "league": "UEFA Champions League",
                "date": "2025-01-19",
                "time": "21:00",
                "status": "finished",
                "score": {"home": 3, "away": 2},
                "has_highlights": True,
                "is_free": True,
                "video_url": None,
                "highlights_url": "https://example.com/highlights/match3",
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "home_team": "Nigeria",
                "away_team": "Morocco",
                "league": "AFCON",
                "date": "2025-01-21",
                "time": "18:00",
                "status": "upcoming",
                "score": None,
                "has_highlights": False,
                "is_free": True,
                "video_url": None,
                "highlights_url": None,
                "created_at": datetime.utcnow()
            },
            {
                "id": str(uuid.uuid4()),
                "home_team": "Arsenal",
                "away_team": "Chelsea",
                "league": "Premier League",
                "date": "2025-01-18",
                "time": "17:30",
                "status": "finished",
                "score": {"home": 1, "away": 1},
                "has_highlights": True,
                "is_free": True,
                "video_url": None,
                "highlights_url": "https://example.com/highlights/match5",
                "created_at": datetime.utcnow()
            }
        ]
        
        # Clear existing matches and insert new ones
        await database.matches.delete_many({})
        await database.matches.insert_many(matches_data)
        
        logger.info(f"Initialized database with {len(leagues_data)} leagues and {len(matches_data)} matches")
        
    except Exception as e:
        logger.error(f"Error initializing sample data: {e}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# API Routes

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SoccerStream API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "matches": "/api/matches",
            "leagues": "/api/leagues",
            "match_by_id": "/api/matches/{match_id}",
            "favorites": "/api/favorites"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

@app.get("/api/leagues", response_model=List[League])
async def get_leagues():
    """Get all available leagues"""
    try:
        leagues_cursor = database.leagues.find({})
        leagues = await leagues_cursor.to_list(length=100)
        
        # Convert MongoDB documents to League models
        result = []
        for league in leagues:
            league['_id'] = str(league['_id']) if '_id' in league else None
            result.append(League(**league))
        
        return result
    except Exception as e:
        logger.error(f"Error fetching leagues: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch leagues")

@app.get("/api/matches", response_model=MatchResponse)
async def get_matches(
    status: Optional[str] = Query(None, description="Filter by match status: live, upcoming, finished"),
    league: Optional[str] = Query(None, description="Filter by league name"),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    search: Optional[str] = Query(None, description="Search in team names"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get matches with optional filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if status:
            query["status"] = status
        
        if league:
            query["league"] = {"$regex": league, "$options": "i"}
        
        if date:
            query["date"] = date
        
        if search:
            query["$or"] = [
                {"home_team": {"$regex": search, "$options": "i"}},
                {"away_team": {"$regex": search, "$options": "i"}},
                {"league": {"$regex": search, "$options": "i"}}
            ]
        
        # Get total count
        total = await database.matches.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * limit
        matches_cursor = database.matches.find(query).skip(skip).limit(limit).sort("date", 1)
        matches = await matches_cursor.to_list(length=limit)
        
        # Convert to Match models
        result_matches = []
        for match in matches:
            match['_id'] = str(match['_id']) if '_id' in match else None
            # Convert score dict to Score model if it exists
            if match.get('score'):
                match['score'] = Score(**match['score'])
            result_matches.append(Match(**match))
        
        return MatchResponse(
            matches=result_matches,
            total=total,
            page=page,
            limit=limit
        )
    
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch matches")

@app.get("/api/matches/{match_id}", response_model=Match)
async def get_match_by_id(match_id: str):
    """Get a specific match by ID"""
    try:
        match = await database.matches.find_one({"id": match_id})
        
        if not match:
            raise HTTPException(status_code=404, detail="Match not found")
        
        match['_id'] = str(match['_id']) if '_id' in match else None
        
        # Convert score dict to Score model if it exists
        if match.get('score'):
            match['score'] = Score(**match['score'])
        
        return Match(**match)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching match {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch match")

@app.post("/api/matches", response_model=Match)
async def create_match(match: Match):
    """Create a new match"""
    try:
        # Convert to dict for MongoDB
        match_dict = match.dict()
        
        # Convert Score model to dict if it exists
        if match_dict.get('score'):
            match_dict['score'] = match_dict['score'].dict() if hasattr(match_dict['score'], 'dict') else match_dict['score']
        
        result = await database.matches.insert_one(match_dict)
        
        if result.inserted_id:
            return match
        else:
            raise HTTPException(status_code=500, detail="Failed to create match")
    
    except Exception as e:
        logger.error(f"Error creating match: {e}")
        raise HTTPException(status_code=500, detail="Failed to create match")

@app.put("/api/matches/{match_id}", response_model=Match)
async def update_match(match_id: str, match_update: Dict[str, Any]):
    """Update a match"""
    try:
        # Remove None values and id field
        update_data = {k: v for k, v in match_update.items() if v is not None and k != 'id'}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid update data provided")
        
        result = await database.matches.update_one(
            {"id": match_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Match not found")
        
        # Return updated match
        updated_match = await database.matches.find_one({"id": match_id})
        updated_match['_id'] = str(updated_match['_id']) if '_id' in updated_match else None
        
        if updated_match.get('score'):
            updated_match['score'] = Score(**updated_match['score'])
        
        return Match(**updated_match)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating match {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update match")

@app.delete("/api/matches/{match_id}")
async def delete_match(match_id: str):
    """Delete a match"""
    try:
        result = await database.matches.delete_one({"id": match_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Match not found")
        
        return {"message": "Match deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting match {match_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete match")

@app.get("/api/matches/live/count")
async def get_live_matches_count():
    """Get count of currently live matches"""
    try:
        count = await database.matches.count_documents({"status": "live"})
        return {"live_matches": count}
    except Exception as e:
        logger.error(f"Error counting live matches: {e}")
        raise HTTPException(status_code=500, detail="Failed to count live matches")

@app.get("/api/stats")
async def get_stats():
    """Get platform statistics"""
    try:
        # Aggregate stats
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        status_stats = await database.matches.aggregate(pipeline).to_list(length=10)
        
        total_matches = await database.matches.count_documents({})
        total_leagues = await database.leagues.count_documents({})
        
        # Format status stats
        stats_dict = {stat["_id"]: stat["count"] for stat in status_stats}
        
        return {
            "total_matches": total_matches,
            "total_leagues": total_leagues,
            "live_matches": stats_dict.get("live", 0),
            "upcoming_matches": stats_dict.get("upcoming", 0),
            "finished_matches": stats_dict.get("finished", 0),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)