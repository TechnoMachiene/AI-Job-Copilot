import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from app.config import settings
from app.schemas import ApplicationContext
import logging

logger = logging.getLogger(__name__)

class EmailAdapter:
    @staticmethod
    def apply(context: ApplicationContext) -> bool:
        if not context.hr_email:
            raise ValueError("EmailAdapter requires a valid HR email in the context.")

        msg = MIMEMultipart()
        msg['From'] = f"{settings.candidate_name} <{settings.candidate_email}>"
        msg['To'] = context.hr_email
        msg['Subject'] = f"Application for {context.job.job_title or 'Open Position'} - {settings.candidate_name}"

        body = (
            f"Dear Hiring Team,\n\n"
            f"Please find attached my resume and cover letter for the "
            f"{context.job.job_title or 'open'} position.\n\n"
            f"Best regards,\n"
            f"{settings.candidate_name}\n"
            f"{settings.candidate_phone}\n"
            f"{settings.candidate_email}"
        )
        msg.attach(MIMEText(body, 'plain'))

        # Attach artifacts
        for pdf_path in [context.resume_pdf_path, context.cover_letter_pdf_path]:
            if pdf_path:
                try:
                    with open(pdf_path, "rb") as f:
                        part = MIMEApplication(f.read(), Name=pdf_path.split("/")[-1])
                    part['Content-Disposition'] = f'attachment; filename="{pdf_path.split("/")[-1]}"'
                    msg.attach(part)
                except Exception as e:
                    logger.error(f"Failed to attach {pdf_path}: {str(e)}")

        try:
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)
            logger.info(f"Successfully emailed application to {context.hr_email}")
            return True
        except Exception as e:
            logger.error(f"SMTP application failed: {str(e)}")
            raise RuntimeError(f"Email delivery failed: {str(e)}")