import os
import pickle
from typing import Optional, Dict, Any, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import hashlib
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserAuth:
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        """
        Initialize the UserAuth class
        
        Args:
            credentials_path (str): Path to the Google OAuth credentials file
            token_path (str): Path to store the token pickle file
        """
        self.SCOPES = [
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.drive_service = None
        self.user_info = None
        
        # Create users directory if it doesn't exist
        os.makedirs('data/users', exist_ok=True)
        
        # Check if credentials file exists
        if not os.path.exists(credentials_path):
            logger.warning(f"Credentials file not found at {credentials_path}. Authentication will fail.")
    
    def login(self) -> Dict[str, Any]:
        """
        Authenticate user with Google OAuth and return user profile
        
        Returns:
            Dict[str, Any]: User profile information
            
        Raises:
            ValueError: If authentication fails
        """
        try:
            if self.authenticate():
                return self.get_user_info()
            raise ValueError("Authentication failed")
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise ValueError(f"Login failed: {str(e)}")
    
    def authenticate(self) -> bool:
        """
        Authenticate user with Google OAuth
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            # Check if token file exists and load credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If credentials are not valid, refresh or create new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                    except RefreshError:
                        logger.warning("Token refresh failed, initiating new authentication flow")
                        self._initiate_auth_flow()
                else:
                    self._initiate_auth_flow()
                
                # Save the credentials for future use
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Initialize Drive service
            self.drive_service = build('drive', 'v3', credentials=self.creds)
            logger.info("Authentication successful")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False
    
    def _initiate_auth_flow(self):
        """Initiate the OAuth flow for user authentication"""
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, self.SCOPES)
            self.creds = flow.run_local_server(port=0)
        except Exception as e:
            logger.error(f"Auth flow error: {str(e)}")
            raise ValueError(f"Authentication flow failed: {str(e)}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get authenticated user's information
        
        Returns:
            Dict[str, Any]: User profile information
            
        Raises:
            ValueError: If not authenticated
        """
        if not self.creds:
            raise ValueError("Not authenticated. Call authenticate() first.")
        
        try:
            # Get user info from Google
            service = build('oauth2', 'v2', credentials=self.creds)
            user_info = service.userinfo().get().execute()
            
            # Generate a unique user ID
            user_id = self._generate_user_id(user_info['email'])
            
            # Create or update user profile
            user_profile = {
                'user_id': user_id,
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'last_login': datetime.now().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            # Save user profile
            self._save_user_profile(user_profile)
            
            self.user_info = user_profile
            logger.info(f"User info retrieved for {user_info['email']}")
            return user_profile
            
        except HttpError as e:
            logger.error(f"HTTP error getting user info: {str(e)}")
            raise ValueError(f"Failed to get user info: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            raise ValueError(f"Failed to get user info: {str(e)}")
    
    def _generate_user_id(self, email: str) -> str:
        """
        Generate a unique user ID from email
        
        Args:
            email (str): User's email address
            
        Returns:
            str: Unique user ID
        """
        return hashlib.sha256(email.encode()).hexdigest()[:12]
    
    def _save_user_profile(self, profile: Dict[str, Any]):
        """
        Save user profile to disk
        
        Args:
            profile (Dict[str, Any]): User profile information
        """
        profile_path = f"data/users/{profile['user_id']}.json"
        
        try:
            # Load existing profile if it exists
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    existing_profile = json.load(f)
                    profile['created_at'] = existing_profile['created_at']
            
            # Save updated profile
            with open(profile_path, 'w') as f:
                json.dump(profile, f, indent=2)
                
            logger.info(f"User profile saved for {profile['email']}")
        except Exception as e:
            logger.error(f"Error saving user profile: {str(e)}")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current authenticated user's profile
        
        Returns:
            Optional[Dict[str, Any]]: User profile information or None if not authenticated
        """
        return self.user_info
    
    def is_authenticated(self) -> bool:
        """
        Check if user is authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.creds is not None and self.creds.valid
    
    def get_drive_service(self):
        """
        Get the Google Drive service
        
        Returns:
            Resource: Google Drive service
            
        Raises:
            ValueError: If not authenticated
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated. Call login() first.")
        return self.drive_service
    
    def logout(self):
        """Log out the current user"""
        try:
            if os.path.exists(self.token_path):
                os.remove(self.token_path)
                logger.info("Token file removed")
            
            self.creds = None
            self.drive_service = None
            self.user_info = None
            logger.info("User logged out successfully")
        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
    
    def revoke_access(self) -> bool:
        """
        Revoke access to the user's Google account
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.creds and self.creds.revoke_token:
                self.creds.revoke(Request())
                logger.info("Access revoked successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Error revoking access: {str(e)}")
            return False 