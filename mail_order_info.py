### send some basic stats about the profit and avg buy price for the last 10 trades same as avg sell price 








import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from config import usr , passwrd




def send_order_info(SYMBOL_ , TYPE_ , AMT_ ,PRICE_ , PRED_PRICE):

    

    message = MIMEMultipart("alternative")
    message["Subject"] = "STATUS : "+str(SYMBOL_)
    message["From"] = usr
    message["To"] = usr

    


    # Create the plain-text and HTML version of your message
    text = """\
        {} 
    
    """.format(TYPE_ )


    html = """\
    <html>
    <body>
        <p>{}<br>
        Order with amount : {} and market price : {} <br>

        <br>Predicted price : {} <br>

        </p>
    </body>
    </html>
    """.format(TYPE_ , AMT_ , PRICE_ ,PRED_PRICE)

# Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    






# Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(usr, password=passwrd)
        server.sendmail(
        usr, usr, message.as_string()
        )

    print ("Done")
    return 

#try:

#send_order_info(SYMBOL_="BTCBUSD" ,TYPE_="BUY" , AMT_="0.3" ,PRICE_="55460" , PRED_PRICE="56000")

#except:
#    print ("failed to send the email ")


                 




def send_test_order_info(SYMBOL_ , SIDE_, TYPE_ , AMT_ ,PRICE_ , PRED_PRICE):

    

    message = MIMEMultipart("alternative")
    message["Subject"] = "STATUS : "+str(SYMBOL_)
    message["From"] = usr
    message["To"] = usr

    


    # Create the plain-text and HTML version of your message
    text = """\
        {} 
    
    """.format(TYPE_ )


    html = """\
    <html>
    <body>
        <p>{}<br>
        Test order {} with amount : {} and market price : {} <br>
        <br>Predicted price : {} <br>
        </p>
    </body>
    </html>
    """.format(TYPE_ ,SIDE_, AMT_ , PRICE_ ,PRED_PRICE)

# Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    






# Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(usr, password=passwrd)
        server.sendmail(
        usr, usr, message.as_string()
        )

    print ("Done")
    return 


    pass 