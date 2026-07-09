"""Authentication API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse)
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserRegisterRequest) -> User:
    service = AuthService()
    return await service.register(data)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLoginRequest) -> TokenResponse:
    service = AuthService()
    return await service.login(data.email, data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest) -> TokenResponse:
    service = AuthService()
    return await service.refresh(data.refresh_token)


@router.post("/logout", response_model=MessageResponse)
async def logout(data: RefreshTokenRequest) -> MessageResponse:
    service = AuthService()
    await service.logout(data.refresh_token)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest, current_user: Annotated[User, Depends(get_current_user)]) -> MessageResponse:
    service = AuthService()
    await service.change_password(current_user, data.current_password, data.new_password)
    return MessageResponse(message="Password changed successfully")
