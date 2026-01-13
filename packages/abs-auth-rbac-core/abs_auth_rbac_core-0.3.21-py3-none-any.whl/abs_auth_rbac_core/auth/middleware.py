from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import HTTPException
import logging
from typing import Callable, Any, Optional

from .jwt_functions import JWTFunctions
from .auth_functions import get_user_by_attribute
from abs_exception_core.exceptions import UnauthorizedError, AuthError, NotFoundError
from abs_nosql_repository_core.repository import BaseRepository
from fastapi.security.utils import get_authorization_scheme_param

class CustomHTTPBearer(HTTPBearer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        
        if not (authorization and scheme and credentials):
            if self.auto_error:
                raise UnauthorizedError(detail="Invalid authentication credentials")
            else:
                return None
        
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise UnauthorizedError(detail="Invalid authentication credentials")
            else:
                return None
        
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=credentials)

security = CustomHTTPBearer()
# security = HTTPBearer()
logger = logging.getLogger(__name__)


# Dependency acting like per-route middleware
def auth_middleware(
    db_session: Callable[...,Any],
    jwt_secret_key:str,
    jwt_algorithm:str
):
    """
    This middleware is used for authentication of the user.
    Args:
        db_session: Callable[...,Any]: Session of the SQLAlchemy database engine
        jwt_secret_key: Secret key of the JWT for jwt functions
        jwt_algorithm: Algorithm used for JWT

    Returns:
    """
    async def get_auth(request: Request, token: HTTPAuthorizationCredentials = Depends(security)):
        jwt_functions = JWTFunctions(secret_key=jwt_secret_key,algorithm=jwt_algorithm)
        try:
            if not token or not token.credentials:
                raise UnauthorizedError(detail="Invalid authentication credentials")

            payload = jwt_functions.get_data(token=token.credentials)
            uuid = payload.get("uuid")

            user = get_user_by_attribute(db_session=db_session,attribute="uuid", value=uuid)
            
            if not user:
                logger.error(f"Authentication failed: User with id {uuid} not found")
                raise UnauthorizedError(detail="Authentication failed")

            # Attach user to request state
            request.state.user = user
            return user 

        except UnauthorizedError as e:
            logger.error(e)
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise UnauthorizedError(detail="Authentication failed")
    
    return get_auth


def contacts_auth_middleware(
    entity_records_service,
    jwt_secret_key: str,
    jwt_algorithm: str
):
    """
    Contact authentication middleware using EntityRecordsService.

    This middleware validates contact JWT tokens and attaches contact data to request.state.

    JWT Payload Structure:
        {
            "sub": "contact@example.com",
            "cid": "contact_record_id",  # KEY IDENTIFIER for contacts
            "uuid": "unique-uuid",
            "exp": 1234567890,
            "iat": 1234567890
        }

    Args:
        entity_records_service: EntityRecordsService for entity operations
        jwt_secret_key: JWT secret key
        jwt_algorithm: JWT algorithm (e.g., HS256)

    Returns:
        FastAPI dependency function that validates contact authentication
    """

    async def get_auth(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(security)
    ):
        jwt_functions = JWTFunctions(
            secret_key=jwt_secret_key,
            algorithm=jwt_algorithm
        )

        try:
            if not token or not token.credentials:
                raise UnauthorizedError(detail="Invalid authentication credentials")

            # Decode JWT and extract payload
            payload = jwt_functions.get_data(token=token.credentials)

            # Extract cid (required for contact authentication)
            cid = payload.get("cid")
            if not cid:
                raise UnauthorizedError(detail="Invalid contact token")

            # Extract app_id from path parameters
            app_id = request.path_params.get("app_id")
            if not app_id:
                raise UnauthorizedError(detail="App ID is required")

            logger.info(f"Contact auth: app_id={app_id}, cid={cid}")

            # Get app configuration (apps collection is not an entity collection)
            # We still need BaseRepository for this until apps get moved to a service
            base_repo = BaseRepository(db=entity_records_service.repository.db)
            app = await base_repo.get_by_attr("id", app_id, collection_name="apps")
            if not app:
                logger.error(f"App not found: {app_id}")
                raise UnauthorizedError(detail="App not found")

            # Extract contact entity ID from app metadata
            metadata = app.get("metadata", {})
            if not metadata:
                raise UnauthorizedError(detail="App doesn't have support for contacts")

            features_entities = metadata.get("features_entities", {})
            if "CONTACT" not in features_entities:
                raise UnauthorizedError(detail="App doesn't have support for contacts")

            contact_config = features_entities.get("CONTACT", {})
            contact_entity_id = contact_config.get("Contacts")

            if not contact_entity_id:
                raise UnauthorizedError(detail="Contact entity not configured")

            logger.info(f"Contact entity ID: {contact_entity_id}")

            # Get contact record using EntityRecordsService
            try:
                contact = await entity_records_service.get_record_by_id(
                    entity_id=contact_entity_id,
                    record_id=cid,
                    convert_ids=False  # Keep ObjectIds for internal use
                )
            except NotFoundError:
                logger.error(f"Authentication failed: contact with id {cid} not found")
                raise UnauthorizedError(detail="Authentication failed")

            logger.info(f"✅ Contact authenticated: {cid}")

            # Attach contact to request state
            request.state.contact = contact
            request.state.contact_entity_id = contact_entity_id

            return contact

        except UnauthorizedError:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}", exc_info=True)
            raise UnauthorizedError(detail="Authentication failed")

    return get_auth


def unified_auth_middleware(
    jwt_secret_key: str,
    jwt_algorithm: str,
    get_user_auth_middleware: Callable,
    get_contact_auth_middleware: Callable,
):
    """
    Unified authentication middleware that intelligently routes to the correct
    authentication flow based on JWT payload.

    Detection Logic:
        - If JWT contains "cid" field → Contact authentication
        - Otherwise → User authentication

    Benefits:
        - Single entry point for all authentication
        - JWT decoded only once for efficiency
        - Transparent routing based on token type
        - No code changes needed in route handlers

    Args:
        jwt_secret_key: JWT secret key
        jwt_algorithm: JWT algorithm (e.g., HS256)
        get_user_auth_middleware: User auth middleware callable
        get_contact_auth_middleware: Contact auth middleware callable

    Returns:
        FastAPI dependency that handles unified authentication
    """
    async def get_auth(
        request: Request,
        token: HTTPAuthorizationCredentials = Depends(security)
    ):
        if not token or not token.credentials:
            raise UnauthorizedError(detail="Invalid authentication credentials")

        # Decode JWT once to inspect payload
        jwt_functions = JWTFunctions(
            secret_key=jwt_secret_key,
            algorithm=jwt_algorithm
        )
        payload = jwt_functions.get_data(token=token.credentials)

        # Route based on payload content
        cid = payload.get("cid")
        if cid:
            # Contact flow: JWT contains contact ID
            return await get_contact_auth_middleware(request=request, token=token)

        # User flow: Standard user authentication
        return await get_user_auth_middleware(request=request, token=token)

    return get_auth