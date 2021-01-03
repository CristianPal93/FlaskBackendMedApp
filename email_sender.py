import smtplib
import re
def recoverPassword(dest,paswd):
    print("Send recovery")
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("medsoftapp18@gmail.com", "4wayst0p")
    MESAJ=''
    try:
        name = re.split('[._]', dest)
    except Exception:
        name=dest
    MESAJ += "Buna, " + name[0].capitalize() + "!\n"
    MESAJ += "Parola pentru contul "+dest+ " este '"+paswd+"' #StaySafe!"
    message = "\r\n".join([
    "From: MedSoft support Team",
    "To:" + dest,
    "Subject:Recuperare parola",
    "", MESAJ + "\n"
     ])
    s.sendmail("medsoftapp18@gmail.com", "palcristi01@gmail.com", message)
    s.quit()
    print("Alert sent!")

