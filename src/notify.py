from configparser import ConfigParser
from time import sleep  # To not surcharge the CPU while waiting
from enum import Enum  # To make readable return value
from mimetypes import guess_type  # To parse the type/subtype of MIME documents
from .logger import get_logger  # Logging utility
import os  # File existence check, process lookup
import smtplib, ssl  # sending secure messages
import email.message as mail  # Formatting the mail
import getpass  # Getting password wihtout echoing it on the terminal
import glob
import psutil

# Get the logger
logger = get_logger()

# Allow to set the configuration from the top level module e_notify
# TODO : Find a cleaner solution
def set_conf(config):
    global conf
    conf = config


class ReturnValue(Enum):
    Success = 0
    LoginError = 1
    OtherError = 2


def _format_mail(args, sender, msg):
    # ============ Creating the mail ===================

    email = mail.EmailMessage()
    email["Subject"] = "Your process has finished"
    email["From"] = sender

    logger.debug(f"Changed the email header 'From' to {sender}")

    if args.to is not None:
        email["To"] = ", ".join(args.to)
    elif args.destlist is not None:
        receivers = args.destlist.read().split("\n")
        email["To"] = ", ".join(receivers)
    else:
        logger.info(
            f"E-mail header 'To' wasn't fed to cmd, defaulting to {conf['defaults']['receiver']}"
        )
        email["To"] = conf["defaults"]["receiver"]

    logger.debug(f"Changed the email header 'To' to {email['To']}")

    # If there's no attachment, do an early return
    if args.attachments is None:
        return email

    for attach_path in args.attachments:
        # Permits the use of Unix-style wildcards
        for attach_file in glob.iglob(attach_path):

            # Only take valid files
            if not os.path.isfile(attach_file):
                logger.warning(
                    f"{attach_file.capitalize()} doesn't exist or isn't a file, skipping it"
                )
                continue

            ctype, encoding = guess_type(attach_file)
            if ctype is None or encoding is not None:
                # No guess could be made, or the file is encoded (compressed), so
                # use a generic bag-of-bits type.
                ctype = "application/octet-stream"
                logger.info(
                    f"The MIME type for the file '{attach_file}' could not be guessed, default to 'application/octet-stream'"
                )

            maintype, subtype = ctype.split("/", 1)
            with open(args.attach, "rb") as file:
                email.add_attachment(
                    file.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=os.path.basename(attach_file),
                )
            logger.debug(f"Successfully attached the file {attach_file} the the mail")

    return email


def _send_mail(
    args, smtp_server, smtp_port, sender_email, password, ssl_context, test_login=False
):

    msg = "Your process has finished"

    # initiate the secure connexion to the server
    with smtplib.SMTP(smtp_server, smtp_port) as server:

        logger.debug("Initiating ehlo for the tls handshake")
        server.ehlo()
        server.starttls(context=ssl_context)
        server.ehlo()
        logger.debug("Ended ehlo for the tls handshake")

        try:
            # authenticate to the server
            server.login(sender_email, password)
        except smtplib.SMTPAuthenticationError:
            logger.error(
                "Error during the login process, most probably the username/password combination was wrong"
            )
            return ReturnValue.LoginError
        except Exception as err:
            logger.error(f"An unexpected error occured : {err}")
            return ReturnValue.OtherError

        if not test_login:
            # Send the email
            logger.info("Sending the mail")
            server.send_message(_format_mail(args, sender_email, msg))

        return ReturnValue.Success


def _wait_process(args, smtp_server, smtp_port, sender_email, password, ssl_context):

    procs = psutil.Process(args.pid)

    # Waiting for the process to end
    alive = [procs]
    while len(alive) != 0:
        ended, alive = psutil.wait_procs([procs], timeout=1)

    _send_mail(args, smtp_server, smtp_port, sender_email, password, ssl_context)


def notify(args):

    smtp_server = conf["SMTP.servers"]["server"]
    smtp_port = conf["SMTP.port"]["port"]
    sender_email = conf["SMTP.login"]["sender"]

    # SSL secure context
    ssl_context = ssl.create_default_context()

    # Testing authentication
    authentication_success = False
    for _ in range(3):

        # Get the password from the environment, if it is not there ask the user
        password = os.environ.get("E-NOTIFY-PASS")
        if password is None:
            password = getpass.getpass("Your password :")

        return_value = _send_mail(
            args,
            smtp_server,
            smtp_port,
            sender_email,
            password,
            ssl_context,
            test_login=True,
        )

        if return_value == ReturnValue.Success:
            authentication_success = True
            break
        elif return_value == ReturnValue.OtherError:
            exit(0)

    if not authentication_success:
        print("You failed your password too much times")
        logger.warning("The username/password combination was failed too much time")
        exit(0)

    # Make the process non-blocking, child process goes to wait, parent (owner of the cmd) ends
    # Thus freeing the console from waiting. Note that the parents share stdout/stderr with the child
    pid = os.fork()
    if pid == 0:
        _wait_process(args, smtp_server, smtp_port, sender_email, password, ssl_context)
