import imaplib
from email import policy
from email.parser import BytesParser
import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


def obtener_gastos(email_user, email_pass, label="Banco"):
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_user, email_pass)

    mail.select('"Banco"')
    status, messages = mail.search(None, 'UNSEEN')
    mail_ids = messages[0].split()

    data = []

    for i in mail_ids:
        procesado = False
        status, msg_data = mail.fetch(i, "(RFC822)")

        for response_part in msg_data:
            if not isinstance(response_part, tuple):
                continue

            msg = BytesParser(policy=policy.default).parsebytes(response_part[1])

            subject = msg["subject"]

            body = msg.get_body(preferencelist=('plain', 'html'))
            if not body:
                continue

            content = body.get_content()

            if "<html" in content.lower():
                soup = BeautifulSoup(content, "html.parser")
                content = soup.get_text()

            monto_match = re.search(r'TOTAL:\s*CRC\s*([\d.,]+)', content)

            if monto_match:
                monto = limpiar_monto(monto_match.group(1))
            else:
                monto = None

            if monto is None:
                continue

            detalle_match = re.search(r'Compra realizada en (.*?) el', content)

            if detalle_match:
                detalle = detalle_match.group(1).strip()
            else:
                detalle = subject.strip()

            texto = content.lower()
            categoria, subcategoria = "Otros", "Otros"

            if any(x in texto for x in ["uber", "didi", "taxi"]):
                categoria, subcategoria = "Transporte", "Carro"
            elif "ae virtual class" in texto:
                categoria, subcategoria = "Fijo", "AE VIRTUAL"
            elif "sinpe-tp" in texto:
                categoria, subcategoria = "Transporte", "Transporte Público"
            elif any(x in texto for x in ["mcdonald", "pizza", "burger"]):
                categoria, subcategoria = "Comida", "Restaurantes"
            elif any(x in texto for x in ["amazon", "store"]):
                categoria, subcategoria = "Compras", "Online"

            data.append({
                "Categoría": categoria,
                "Subcategoría": subcategoria,
                "Detalle": detalle,
                "Pago": monto,
                "Fecha": datetime.now().strftime("%Y-%m-%d")
            })
            procesado = True
        
        if procesado:
            mail.store(i, '+FLAGS', '\\Seen')


    mail.logout()
    return pd.DataFrame(data)

def limpiar_monto(monto_str):
    if not monto_str:
        return None

    monto_str = monto_str.strip()

    if "," in monto_str and "." in monto_str:
        monto_str = monto_str.replace(",", "")

    elif "," in monto_str:
        monto_str = monto_str.replace(".", "").replace(",", ".")

    try:
        return float(monto_str)
    except:
        return None

