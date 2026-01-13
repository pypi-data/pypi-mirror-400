from pydantic import BaseModel 
from typing import Optional, List 
# --- Schémas secondaires --- 
class RatingBase(BaseModel): 
    userId: int 
    movieId: int 
    rating: float 
    timestamp: int 
    class Config: 
      from_attributes = True
class TagBase(BaseModel): 
    userId: int 
    movieId: int 
    tag: str 
    timestamp: int 
    class Config: 
       from_attributes = True 
class LinkBase(BaseModel): 
    imdbId: Optional[str] 
    tmdbId: Optional[int] 
    class Config: 
        from_attributes = True 
# --- Schéma principal pour Movie --
class MovieBase(BaseModel): 
    movieId: int 
    title: str 
    genres: Optional[str] = None 
    class Config: 
        from_attributes = True
class MovieDetailed(MovieBase): 
    ratings: List[RatingBase] = [] 
    tags: List[TagBase] = [] 
    link: Optional[LinkBase] = None
    class Config: 
        from_attributes = True 
     # --- Schéma pour liste de films (sans détails imbriqués) --
class MovieSimple(BaseModel): 
    movieId: int 
    title: str 
    genres: Optional[str] 
    class Config: 
        from_attributes = True 
# --- Pour les endpoints de /ratings et /tags si appelés seuls --
class RatingSimple(BaseModel): 
    userId: int 
    movieId: int 
    rating: float 
    timestamp: int 
    class Config: 
       from_attributes = True
class TagSimple(BaseModel): 
    userId: int 
    movieId: int 
    tag: str 
    timestamp: int 
    class Config: 
        from_attributes = True
class LinkSimple(BaseModel): 
    movieId: int 
    imdbId: Optional[str] 
    tmdbId: Optional[int] 
    class Config: 
        from_attributes = True
class AnalyticsResponse(BaseModel):
    movie_count: int
    rating_count: int
    tag_count: int
    link_count: int
    class Config:
        from_attributes = True