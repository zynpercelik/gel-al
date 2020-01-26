from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def send_mail(to,subject,content):
    msg = MIMEMultipart()
    message = content
    ###setup the parameters of the message
    password = "E7kFKYjVnX"
    msg['From'] = "metaboliticsdb@gmail.com"
    #
    # password = "KEAnun39"
    # msg['From'] = "tajsaleh96@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 25')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

# send_mail("tajothman@std.sehir.edu.tr",'test','test')

