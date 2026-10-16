"""Operator-only local identity provisioning; tokens/keys are never committed."""

import argparse
import secrets
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

import jwt
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import Device, User
from app.security.auth import secret
from app.security.models import DeviceRegistration, Identity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["key", "provision", "revoke"])
    parser.add_argument("--subject", default="local-operator")
    parser.add_argument("--user-id", type=UUID)
    parser.add_argument("--roles", default="owner,approver,operator")
    parser.add_argument("--issuer", default="nova-local")
    parser.add_argument(
        "--device-type", choices=["DESKTOP", "MOBILE", "WEARABLE"], default="DESKTOP"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.operation == "key":
        args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with args.output.open("x") as stream:
            args.output.chmod(0o600)
            stream.write(secrets.token_hex(64))
        return
    roles = args.roles.split(",")
    if not set(roles) <= {"owner", "approver", "operator", "viewer"}:
        parser.error("Unknown server role")
    with SessionLocal.begin() as session:
        identity = session.scalar(
            select(Identity)
            .where(Identity.issuer == args.issuer, Identity.subject == args.subject)
            .with_for_update()
        )
        if args.operation == "revoke":
            if identity:
                identity.enabled = False
                identity.version += 1
            return
        if not identity:
            user_id = args.user_id or uuid4()
            if not session.get(User, user_id):
                session.add(User(id=user_id, name="Local operator provisioned user"))
                session.flush()
            identity = Identity(
                user_id=user_id,
                issuer=args.issuer,
                subject=args.subject,
                roles=roles,
                enabled=True,
                version=1,
                created_at=datetime.now(UTC),
            )
            session.add(identity)
            session.flush()
        else:
            identity.roles, identity.enabled = roles, True
            identity.version += 1
        devices = list(session.scalars(select(Device).where(Device.user_id == identity.user_id)))
        if not devices:
            for kind in ["DESKTOP", "WEARABLE", "MOBILE"]:
                session.add(
                    Device(id=uuid4(), user_id=identity.user_id, name=kind.title(), type=kind)
                )
            session.flush()
            devices = list(
                session.scalars(select(Device).where(Device.user_id == identity.user_id))
            )
        if args.issuer != "nova-local":
            args.output.write_text(
                "OIDC subject grant provisioned; use your issuer's access token."
            )
            return
        selected = next(d for d in devices if d.type == args.device_type)
        registration = session.get(DeviceRegistration, selected.id)
        now = int(datetime.now(UTC).timestamp())
        token = jwt.encode(
            {
                "sub": identity.subject,
                "iss": "nova-local",
                "aud": settings.auth_audience,
                "iat": now,
                "nbf": now,
                "exp": now + 3600,
                "version": identity.version,
                "device_id": str(selected.id),
                "device_version": registration.version if registration else 0,
            },
            secret(),
            algorithm="HS256",
        )
    args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    with args.output.open("w") as stream:
        args.output.chmod(0o600)
        stream.write(token)


if __name__ == "__main__":
    main()
