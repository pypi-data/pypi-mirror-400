from typing import List, Dict, Optional, Any
from flotorch.sdk.utils import session_utils
from flotorch.sdk.logger.global_logger import get_logger
from flotorch.sdk.logger.utils.models import ObjectCreation, Error, SessionOperation

logger = get_logger()


class FlotorchSession:
    def __init__(
        self,
        api_key: str,
        base_url: str,
    ):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty.")
        
        self.api_key = api_key
        self.base_url = base_url
        
        # Log object creation
        logger.info(
            ObjectCreation(
                class_name='FlotorchSession',
                extras={'base_url': base_url}
            ))
        

    def create(
        self,
        app_name: str,
        user_id: str,
        uid: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not app_name or not app_name.strip():
            raise ValueError("App name cannot be empty.")
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty.")
        
        logger.info(
            SessionOperation(
                operation='create',
                session_uid=uid,
                params={'app_name': app_name, 'user_id': user_id}
            ))
        
        try:
            result = session_utils.create_session(
                base_url=self.base_url,
                api_key=self.api_key,
                app_name=app_name,
                user_id=user_id,
                uid=uid,
                state=state,
            )

            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchSession.create', error=e))
            raise

    def get(
        self,
        uid: str,
        after_timestamp: Optional[int] = None,
        num_recent_events: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(
                SessionOperation(
                    operation='get',
                    session_uid=uid,
                    params={'num_recent_events': num_recent_events}
                    ))
        try:
            result = session_utils.get_session(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
                after_timestamp=after_timestamp,
                num_recent_events=num_recent_events,
            )
            return result
        except Exception as e:
            raise

    def list(
        self,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        
        logger.info(
            SessionOperation(
                operation='list',
                params={'app_name': app_name, 'user_id': user_id}
            )
        )
        try:
            result = session_utils.list_sessions(
                base_url=self.base_url,
                api_key=self.api_key,
                app_name=app_name,
                user_id=user_id,
            )
            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchSession.list', error=e))
            raise

    def delete(self, uid: str) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(
            SessionOperation(operation='delete', session_uid=uid))
        try:
            result = session_utils.delete_session(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
            )
            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchSession.delete', error=e))
            raise

    def get_events(self, uid: str) -> List[Dict[str, Any]]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(SessionOperation(operation='get_events', session_uid=uid))
        
        return session_utils.get_session_events(
            base_url=self.base_url,
            api_key=self.api_key,
            uid=uid,
        )

    def add_event(
        self,
        uid: str,
        invocation_id: str,
        author: str,
        uid_event: Optional[str] = None,
        branch: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        actions: Optional[Dict[str, Any]] = None,
        long_running_tool_ids_json: Optional[str] = None,
        grounding_metadata: Optional[Dict[str, Any]] = None,
        partial: Optional[bool] = False,
        turn_complete: Optional[bool] = False,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        interrupted: Optional[bool] = False,
    ) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        if not invocation_id or not invocation_id.strip():
            raise ValueError("Invocation ID cannot be empty.")
        if not author or not author.strip():
            raise ValueError("Author cannot be empty.")
        
        logger.info(
            SessionOperation(
                operation='add_event',
                session_uid=uid,
                params={
                    'invocation_id': invocation_id,
                    'author': author,
                    'turn_complete': turn_complete
                }))
        try:
            result = session_utils.add_session_event(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
                invocation_id=invocation_id,
                author=author,
                uid_event=uid_event,
                branch=branch,
                content=content,
                actions=actions,
                long_running_tool_ids_json=long_running_tool_ids_json,
                grounding_metadata=grounding_metadata,
                partial=partial,
                turn_complete=turn_complete,
                error_code=error_code,
                error_message=error_message,
                interrupted=interrupted,
            )
            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchSession.add_event', error=e))
            raise

    # Helper methods for state management
    def create_state_delta(
        self,
        app_state: Optional[Dict[str, Any]] = None,
        user_state: Optional[Dict[str, Any]] = None,
        session_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return session_utils.create_state_delta(
            app_state=app_state,
            user_state=user_state,
            session_state=session_state,
        )

    def create_event_actions(
        self,
        state_delta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return session_utils.create_event_actions(state_delta)

    def extract_messages(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return session_utils.extract_session_messages(session_data)

    def extract_context(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return session_utils.extract_session_context(session_data)

    def extract_events(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return session_utils.extract_session_events(session_data)


class FlotorchAsyncSession:
    def __init__(
        self,
        api_key: str,
        base_url: str,
    ):
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty.")
        
        self.api_key = api_key
        self.base_url = base_url
        
        # Log object creation
        logger.info(
            ObjectCreation(class_name='FlotorchAsyncSession',extras={'base_url': base_url})
        )

    async def create(
        self,
        app_name: str,
        user_id: str,
        uid: Optional[str] = None,
        state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not app_name or not app_name.strip():
            raise ValueError("App name cannot be empty.")
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty.")
        
        logger.info(
            SessionOperation(
                operation='create',
                session_uid=uid,
                params={'app_name': app_name, 'user_id': user_id},
                request_type='async'
            )
        )
        try:
            result = await session_utils.async_create_session(
                base_url=self.base_url,
                api_key=self.api_key,
                app_name=app_name,
                user_id=user_id,
                uid=uid,
                state=state,
            )
            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchAsyncSession.create', error=e))
            raise

    async def get(
        self,
        uid: str,
        after_timestamp: Optional[int] = None,
        num_recent_events: Optional[int] = None,
    ) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(
            SessionOperation(
                operation='get',
                session_uid=uid,
                params={'num_recent_event': num_recent_events},
                request_type='async',
            )
        )
        try:
            return await session_utils.async_get_session(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
                after_timestamp=after_timestamp,
                num_recent_events=num_recent_events,
            )
        except Exception as e:
            logger.error(Error(operation='FlotorchAsyncSession.get', error=e))
            raise

    async def list(
        self,
        app_name: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        
        logger.info(
            SessionOperation(
                operation='list',
                params={'app_name': app_name, 'user_id': user_id},
                request_type='async'
            )
        )
        try:
            return await session_utils.async_list_sessions(
                base_url=self.base_url,
                api_key=self.api_key,
                app_name=app_name,
                user_id=user_id,
            )
        except Exception as e:
            logger.error(Error(operation='FlotorchAsyncSession.list', error=e))
            raise

    async def delete(self, uid: str) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(
            SessionOperation(operation='delete', session_uid=uid, request_type='async')
        )
        try:
            return await session_utils.async_delete_session(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
            )
        except Exception as e:
            logger.error(Error(Operation="FlotorchAsyncSession.delete", error=e))
            raise
            

    async def get_events(self, uid: str) -> List[Dict[str, Any]]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        
        logger.info(
            SessionOperation(operation='get_events', session_uid=uid, request_type='async')
        )
        try:
            return await session_utils.async_get_session_events(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
            )
        except Exception as e:
            logger.error(Error(operation='FlotorchAsyncSession.get_events', error=e))

    async def add_event(
        self,
        uid: str,
        invocation_id: str,
        author: str,
        uid_event: Optional[str] = None,
        branch: Optional[str] = None,
        content: Optional[Dict[str, Any]] = None,
        actions: Optional[Dict[str, Any]] = None,
        long_running_tool_ids_json: Optional[str] = None,
        grounding_metadata: Optional[Dict[str, Any]] = None,
        partial: Optional[bool] = False,
        turn_complete: Optional[bool] = False,
        error_code: Optional[str] = None,
        error_message: Optional[str] = None,
        interrupted: Optional[bool] = False,
    ) -> Dict[str, Any]:
        if not uid or not uid.strip():
            raise ValueError("Session UID cannot be empty.")
        if not invocation_id or not invocation_id.strip():
            raise ValueError("Invocation ID cannot be empty.")
        if not author or not author.strip():
            raise ValueError("Author cannot be empty.")
        
        logger.info(
            SessionOperation(
                operation='add_event',
                session_uid=uid,
                params={
                    'invocation_id': invocation_id,
                    'author': author,
                    'turn_complete': turn_complete
                },
                request_type='async'
            )
        )
        try:
            result = await session_utils.async_add_session_event(
                base_url=self.base_url,
                api_key=self.api_key,
                uid=uid,
                invocation_id=invocation_id,
                author=author,
                uid_event=uid_event,
                branch=branch,
                content=content,
                actions=actions,
                long_running_tool_ids_json=long_running_tool_ids_json,
                grounding_metadata=grounding_metadata,
                partial=partial,
                turn_complete=turn_complete,
                error_code=error_code,
                error_message=error_message,
                interrupted=interrupted,
            )
            return result
        except Exception as e:
            logger.error(Error(operation='FlotorchAsyncSession.add_event', error=e))
            raise

    # Helper methods for state management (these are sync since they don't make API calls)
    def create_state_delta(
        self,
        app_state: Optional[Dict[str, Any]] = None,
        user_state: Optional[Dict[str, Any]] = None,
        session_state: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return session_utils.create_state_delta(
            app_state=app_state,
            user_state=user_state,
            session_state=session_state,
        )

    def create_event_actions(
        self,
        state_delta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return session_utils.create_event_actions(state_delta)

    def extract_messages(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return session_utils.extract_session_messages(session_data)

    def extract_context(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        return session_utils.extract_session_context(session_data)

    def extract_events(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return session_utils.extract_session_events(session_data)
