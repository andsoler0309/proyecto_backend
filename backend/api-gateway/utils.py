import jwt
import datetime
from config import Config
from models import db, TokenBlacklist
import uuid


def generate_jwt(agent_id):
    payload = {
        'agent_id': agent_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=Config.JWT_EXP_DELTA_SECONDS),
        'iat': datetime.datetime.utcnow(),
        'jti': str(uuid.uuid4())
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token


def decode_jwt(token):
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def blacklist_token(jti, token):
    blacklisted = TokenBlacklist(jti=jti, token=token)
    db.session.add(blacklisted)
    db.session.commit()


def is_token_blacklisted(jti):
    blacklisted = TokenBlacklist.query.filter_by(jti=jti).first()
    return blacklisted is not None
