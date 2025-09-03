"""
Redis utilities for handling JWT tokens and user data storage.
This module provides functions to store and retrieve user data that persists
beyond JWT token expiration.
"""

import json
import time
from typing import Dict, Optional, Any
from app.core.redis import redis_client


class RedisUserManager:
    """Manages user data in Redis with different TTL strategies"""
    
    # TTL Constants (in seconds)
    JWT_TTL_BUFFER = 60  # 1 minute buffer for JWT storage
    USER_DATA_TTL = 30 * 24 * 60 * 60  # 30 days
    SESSION_TTL = 7 * 24 * 60 * 60  # 7 days
    
    @staticmethod
    def store_jwt_payload(jti: str, payload: Dict[str, Any], ttl: int) -> bool:
        """
        Store JWT payload with JTI key (expires with token)
        
        Args:
            jti: JWT ID
            payload: JWT payload
            ttl: Time to live in seconds
            
        Returns:
            bool: Success status
        """
        try:
            redis_client.setex(f"jwt:{jti}", ttl, json.dumps(payload))
            return True
        except Exception as e:
            print(f"Error storing JWT payload: {e}")
            return False
    
    @staticmethod
    def get_jwt_payload(jti: str) -> Optional[Dict[str, Any]]:
        """
        Get JWT payload by JTI (only works if token hasn't expired)
        
        Args:
            jti: JWT ID
            
        Returns:
            Dict containing JWT payload or None
        """
        try:
            data = redis_client.get(f"jwt:{jti}")
            if not data:
                return None
            return json.loads(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error retrieving JWT payload: {e}")
            return None
    
    @staticmethod
    def store_user_data(user_id: str, payload: Dict[str, Any]) -> bool:
        """
        Store essential user data with extended TTL (persists beyond JWT expiration)
        
        Args:
            user_id: User identifier
            payload: JWT payload or user data
            
        Returns:
            bool: Success status
        """
        try:
            user_data = {
                "user_id": user_id,
                "jti": payload.get("jti"),
                "aud": payload.get("aud"),
                "scopes": payload.get("scopes", []),
                "stored_at": int(time.time()),
                "exp": payload.get("exp")
            }
            
            # Store user data with extended TTL
            redis_client.setex(
                f"user:{user_id}:data", 
                RedisUserManager.USER_DATA_TTL, 
                json.dumps(user_data)
            )
            
            # Store latest JTI mapping
            redis_client.setex(
                f"user:{user_id}:latest_jti", 
                RedisUserManager.USER_DATA_TTL, 
                payload.get("jti", "")
            )
            
            return True
        except Exception as e:
            print(f"Error storing user data: {e}")
            return False
    
    @staticmethod
    def get_user_data(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user data by user_id (works even after JWT expiration)
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing user data or None
        """
        try:
            data = redis_client.get(f"user:{user_id}:data")
            if not data:
                return None
            return json.loads(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error retrieving user data: {e}")
            return None
    
    @staticmethod
    def get_user_latest_jti(user_id: str) -> Optional[str]:
        """
        Get the latest JTI for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            str: Latest JTI or None
        """
        try:
            return redis_client.get(f"user:{user_id}:latest_jti")
        except Exception as e:
            print(f"Error retrieving latest JTI: {e}")
            return None
    
    @staticmethod
    def store_session_data(user_id: str, data: Dict[str, Any]) -> bool:
        """
        Store additional session data for user
        
        Args:
            user_id: User identifier
            data: Session data to store
            
        Returns:
            bool: Success status
        """
        try:
            session_data = {
                **data,
                "updated_at": int(time.time())
            }
            redis_client.setex(
                f"user:{user_id}:session", 
                RedisUserManager.SESSION_TTL, 
                json.dumps(session_data)
            )
            return True
        except Exception as e:
            print(f"Error storing session data: {e}")
            return False
    
    @staticmethod
    def get_session_data(user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data for user
        
        Args:
            user_id: User identifier
            
        Returns:
            Dict containing session data or None
        """
        try:
            data = redis_client.get(f"user:{user_id}:session")
            if not data:
                return None
            return json.loads(data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error retrieving session data: {e}")
            return None
    
    @staticmethod
    def delete_user_data(user_id: str) -> bool:
        """
        Delete all user data from Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: Success status
        """
        try:
            keys_to_delete = [
                f"user:{user_id}:data",
                f"user:{user_id}:latest_jti",
                f"user:{user_id}:session"
            ]
            
            # Also delete JWT if we have the JTI
            jti = RedisUserManager.get_user_latest_jti(user_id)
            if jti:
                keys_to_delete.append(f"jwt:{jti}")
            
            deleted_count = redis_client.delete(*keys_to_delete)
            return deleted_count > 0
        except Exception as e:
            print(f"Error deleting user data: {e}")
            return False
    
    @staticmethod
    def is_user_data_valid(user_id: str) -> bool:
        """
        Check if user has valid data in Redis
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if user data exists and is valid
        """
        try:
            user_data = RedisUserManager.get_user_data(user_id)
            if not user_data:
                return False
            
            # Check if data is not too old (optional validation)
            stored_at = user_data.get("stored_at", 0)
            current_time = int(time.time())
            max_age = RedisUserManager.USER_DATA_TTL
            
            return (current_time - stored_at) < max_age
        except Exception as e:
            print(f"Error validating user data: {e}")
            return False


# Create instance for easy import
redis_user_manager = RedisUserManager()