from fastapi import Header, HTTPException, status
from data.store import verify_session_token

ALLOWED_ROLES = {"dispatcher", "volunteer", "admin"}


def verify_bearer_and_role(
    required_roles: list[str],
    authorization: str | None = Header(default=None),
    x_user_role: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> dict:
    # 1. Require valid Bearer token format
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization Bearer token",
        )

    raw_token = authorization.removeprefix("Bearer ").strip()
    session = verify_session_token(raw_token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive session token",
        )

    token_role = session["role"]
    token_user_id = session["user_id"]

    # 2. Prevent header spoofing if X-User-Role or X-User-Id is also sent
    if x_user_role and x_user_role.lower().strip() != token_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role header does not match authenticated Bearer token",
        )

    if x_user_id and x_user_id.upper().strip() != token_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID header does not match authenticated Bearer token",
        )

    # 3. Enforce RBAC permission check
    if token_role not in ALLOWED_ROLES or token_role not in [r.lower() for r in required_roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{token_role}' is not permitted for this action",
        )

    return {"user_id": token_user_id, "role": token_role}
