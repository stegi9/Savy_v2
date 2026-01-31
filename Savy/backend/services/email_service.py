"""
Email service for sending transactional emails.
Supports SMTP (Gmail, SendGrid, etc.)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from config import settings
import structlog

logger = structlog.get_logger()


class EmailService:
    """Service for sending emails via SMTP."""
    
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.smtp_use_tls = settings.smtp_use_tls
        self.email_from = settings.email_from
        self.email_from_name = settings.email_from_name
    
    def send_email(
        self,
        to: str | List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email(s)
            subject: Email subject
            html_content: HTML body
            text_content: Plain text fallback (optional)
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Convert single recipient to list
            recipients = [to] if isinstance(to, str) else to
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.email_from_name} <{self.email_from}>"
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Attach text and HTML parts
            if text_content:
                msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info("email_sent", to=recipients, subject=subject)
            return True
            
        except Exception as e:
            logger.error("email_send_failed", error=str(e), to=recipients, subject=subject)
            return False
    
    def send_verification_email(self, to: str, full_name: str, token: str) -> bool:
        """Send email verification link."""
        verification_url = f"{settings.frontend_url}/verify-email?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verifica la tua email - Savy</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f7; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">Benvenuto su Savy!</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1d1d1f; margin-bottom: 20px;">
                        Ciao <strong>{full_name}</strong>,
                    </p>
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-bottom: 30px;">
                        Grazie per esserti registrato su <strong>Savy</strong>, il tuo coach finanziario personale con AI! 🎉
                    </p>
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-bottom: 30px;">
                        Per completare la registrazione, verifica il tuo indirizzo email cliccando sul pulsante qui sotto:
                    </p>
                    
                    <!-- Button -->
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="{verification_url}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);">
                            Verifica Email
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #86868b; margin-top: 30px; padding-top: 30px; border-top: 1px solid #e5e5ea;">
                        Oppure copia e incolla questo link nel tuo browser:<br>
                        <span style="color: #667eea; word-break: break-all;">{verification_url}</span>
                    </p>
                    
                    <p style="font-size: 14px; color: #86868b; margin-top: 20px;">
                        Questo link scadrà tra <strong>24 ore</strong>.
                    </p>
                    
                    <p style="font-size: 14px; color: #86868b; margin-top: 30px;">
                        Se non hai richiesto questa registrazione, ignora questa email.
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f5f5f7; padding: 30px; text-align: center; border-top: 1px solid #e5e5ea;">
                    <p style="font-size: 14px; color: #86868b; margin: 0;">
                        © 2026 Savy - Il tuo coach finanziario AI
                    </p>
                    <p style="font-size: 12px; color: #86868b; margin-top: 10px;">
                        Non rispondere a questa email. Per supporto, contatta support@savy.app
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Benvenuto su Savy!
        
        Ciao {full_name},
        
        Grazie per esserti registrato su Savy, il tuo coach finanziario personale con AI!
        
        Per completare la registrazione, verifica il tuo indirizzo email visitando questo link:
        {verification_url}
        
        Questo link scadrà tra 24 ore.
        
        Se non hai richiesto questa registrazione, ignora questa email.
        
        © 2026 Savy - Il tuo coach finanziario AI
        """
        
        return self.send_email(
            to=to,
            subject="Verifica il tuo account Savy",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_password_reset_email(self, to: str, full_name: str, token: str) -> bool:
        """Send password reset link."""
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Password - Savy</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f7; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: 600;">🔒 Reset Password</h1>
                </div>
                
                <!-- Content -->
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1d1d1f; margin-bottom: 20px;">
                        Ciao <strong>{full_name}</strong>,
                    </p>
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-bottom: 30px;">
                        Hai richiesto di reimpostare la password del tuo account Savy.
                    </p>
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-bottom: 30px;">
                        Clicca sul pulsante qui sotto per creare una nuova password:
                    </p>
                    
                    <!-- Button -->
                    <div style="text-align: center; margin: 40px 0;">
                        <a href="{reset_url}" style="display: inline-block; background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%); color: #ffffff; text-decoration: none; padding: 16px 40px; border-radius: 12px; font-size: 16px; font-weight: 600; box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);">
                            Reimposta Password
                        </a>
                    </div>
                    
                    <p style="font-size: 14px; color: #86868b; margin-top: 30px; padding-top: 30px; border-top: 1px solid #e5e5ea;">
                        Oppure copia e incolla questo link nel tuo browser:<br>
                        <span style="color: #ff6b6b; word-break: break-all;">{reset_url}</span>
                    </p>
                    
                    <p style="font-size: 14px; color: #86868b; margin-top: 20px;">
                        Questo link scadrà tra <strong>1 ora</strong>.
                    </p>
                    
                    <p style="font-size: 14px; color: #c92a2a; font-weight: 600; margin-top: 30px;">
                        ⚠️ Se non hai richiesto questo reset, ignora questa email e la tua password rimarrà invariata.
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="background-color: #f5f5f7; padding: 30px; text-align: center; border-top: 1px solid #e5e5ea;">
                    <p style="font-size: 14px; color: #86868b; margin: 0;">
                        © 2026 Savy - Il tuo coach finanziario AI
                    </p>
                    <p style="font-size: 12px; color: #86868b; margin-top: 10px;">
                        Non rispondere a questa email. Per supporto, contatta support@savy.app
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Reset Password - Savy
        
        Ciao {full_name},
        
        Hai richiesto di reimpostare la password del tuo account Savy.
        
        Visita questo link per creare una nuova password:
        {reset_url}
        
        Questo link scadrà tra 1 ora.
        
        Se non hai richiesto questo reset, ignora questa email e la tua password rimarrà invariata.
        
        © 2026 Savy - Il tuo coach finanziario AI
        """
        
        return self.send_email(
            to=to,
            subject="Reset della password - Savy",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_bill_reminder_email(self, to: str, full_name: str, bill_name: str, amount: float, due_date: str) -> bool:
        """Send bill payment reminder."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Promemoria Bolletta - Savy</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f7; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
                <div style="background: linear-gradient(135deg, #ffd93d 0%, #f6c23e 100%); padding: 40px 20px; text-align: center;">
                    <h1 style="color: #1d1d1f; margin: 0; font-size: 28px; font-weight: 600;">⏰ Promemoria Pagamento</h1>
                </div>
                
                <div style="padding: 40px 30px;">
                    <p style="font-size: 16px; color: #1d1d1f; margin-bottom: 20px;">
                        Ciao <strong>{full_name}</strong>,
                    </p>
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-bottom: 30px;">
                        Ti ricordiamo che la bolletta <strong>{bill_name}</strong> scade a breve:
                    </p>
                    
                    <div style="background-color: #f5f5f7; padding: 20px; border-radius: 12px; margin: 30px 0;">
                        <p style="font-size: 14px; color: #86868b; margin: 0 0 10px 0;">Importo:</p>
                        <p style="font-size: 32px; color: #1d1d1f; font-weight: 700; margin: 0;">€{amount:.2f}</p>
                        <p style="font-size: 14px; color: #86868b; margin: 20px 0 0 0;">Scadenza:</p>
                        <p style="font-size: 18px; color: #ff6b6b; font-weight: 600; margin: 5px 0 0 0;">{due_date}</p>
                    </div>
                    
                    <p style="font-size: 16px; color: #1d1d1f; line-height: 1.6; margin-top: 30px;">
                        Non dimenticare di effettuare il pagamento per evitare penali! 💰
                    </p>
                </div>
                
                <div style="background-color: #f5f5f7; padding: 30px; text-align: center; border-top: 1px solid #e5e5ea;">
                    <p style="font-size: 14px; color: #86868b; margin: 0;">
                        © 2026 Savy - Il tuo coach finanziario AI
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to=to,
            subject=f"Promemoria: {bill_name} in scadenza",
            html_content=html_content
        )


# Singleton instance
_email_service = None

def get_email_service() -> EmailService:
    """Get singleton email service instance."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
