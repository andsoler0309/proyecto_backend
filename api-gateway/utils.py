import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import jwt
import datetime
from config import Config
from models import db, TokenBlacklist, FailedAttempt, Session, IPAddressLoginAttempt, AgentIPAddress
import uuid
import ipaddress
from flask import current_app, request
import requests


def generate_jwt(agent_id, session_id):
    payload = {
        'agent_id': agent_id,
        'session_id': session_id,
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


def notify_admin(subject, message):
    # Fetch all admin email addresses via API call
    try:
        response = requests.get(
            f"{Config.GESTOR_AGENTES_BASE_URL}/agents/admins",
            timeout=5
        )
        if response.status_code != 200:
            current_app.logger.error("Failed to fetch admin email addresses.")
            return
        admin_agents = response.json()
        admin_emails = [admin['email'] for admin in admin_agents]
    except Exception as e:
        current_app.logger.error(f"Error fetching admin emails: {e}")
        return

    if not admin_emails:
        current_app.logger.warning("No admin email addresses found.")
        return

    current_app.logger.info(f"Admin Notification - {subject}: {message}")
    
    # Email configuration
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = os.getenv('EMAIL_ADDRESS')  # Your Gmail address
    sender_password = os.getenv('EMAIL_PASSWORD')  # Your Gmail App Password

    if not sender_email or not sender_password:
        current_app.logger.error("Email credentials are not set in environment variables.")
        return

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ', '.join(admin_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    print(f"Admin Notification Sent - {subject}")

    # try:
    #     # Connect to the Gmail SMTP server and send the email
    #     server = smtplib.SMTP(smtp_server, smtp_port)
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.sendmail(sender_email, admin_emails, msg.as_string())
    #     server.quit()
    #     current_app.logger.info(f"Admin Notification Sent - {subject}")
    # except Exception as e:
    #     current_app.logger.error(f"Failed to send admin notification email: {e}")


def reset_failed_attempts(agent_id):
    FailedAttempt.query.filter_by(agent_id=agent_id).delete()
    db.session.commit()


def increment_failed_attempts(agent_id):
    attempt = FailedAttempt.query.filter_by(agent_id=agent_id).first()
    if attempt:
        attempt.attempts += 1
        attempt.last_attempt = datetime.datetime.utcnow()
    else:
        attempt = FailedAttempt(agent_id=agent_id, attempts=1)
        db.session.add(attempt)
    db.session.commit()
    return attempt.attempts


def lock_agent_account(agent_id):
    # Send a request to Gestor-Agente to lock the agent account
    try:
        response = requests.post(
            f"{Config.GESTOR_AGENTES_BASE_URL}/agents/{agent_id}/lock",
            timeout=5
        )
        if response.status_code == 200:
            current_app.logger.info(f"Agent {agent_id} has been locked due to multiple failed attempts.")
        else:
            current_app.logger.error(f"Failed to lock agent {agent_id}: {response.text}")
    except Exception as e:
        current_app.logger.error(f"Error communicating with Gestor-Agente: {e}")


def is_new_ip(agent_id, client_ip):
    """
    Determine if the client_ip is new for the user based on /24 subnet.
    """
    client_network = ipaddress.ip_network(f"{client_ip}/24", strict=False)

    # Fetch all known IPs for the user
    known_ips = db.session.query(AgentIPAddress.ip_address).filter_by(agent_id=agent_id).all()

    for (ip_str,) in known_ips:
        known_network = ipaddress.ip_network(f"{ip_str}/24", strict=False)
        if client_network.overlaps(known_network):
            return False  # IP is within an existing /24 subnet
    return True
