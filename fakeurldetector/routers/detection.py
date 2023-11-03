from uuid import UUID

from fastapi import APIRouter, HTTPException
from ..helpers.database import users
from fakeurldetector import DATABASE, LOGGER, MODEL_DIR
from fastapi.encoders import jsonable_encoder
from ..helpers import get_ssl_certificate, get_redirected_url, extract_url_features
from ..helpers.models import FakeDetectionResponse, FakeDetectionIn
from telebot.async_telebot import AsyncTeleBot
from telebot.util import quick_markup
from urllib.parse import urlparse
import pickle
import re
import pandas as pd

FakeDetectionRouter = APIRouter(
    prefix="/fake",
    tags=["Fake Detection API Endpoints"],
    responses={404: {"error": "Not found"}},
)


@FakeDetectionRouter.post(
    "/detect", response_model=FakeDetectionResponse
)
async def fake_detect(uuid_text: FakeDetectionIn):
    _session_q = users.select().where(users.c.uuid == str(uuid_text.uuid))
    _session = await DATABASE.fetch_one(_session_q)
    url_pattern = r"https?://\S+|www\.\S+|ftp://\S+|\S+\.\S+/\S+"
    uuid_text.text = re.findall(url_pattern, uuid_text.text)
    if uuid_text.text is None:
        raise HTTPException(status_code=404, detail={"Could not find URL in the text you sent"})
    uuid_text.text = uuid_text.text[0]
    _dict = {}
    if _session[2] == "App":
        initial_text = f"""
<b>Given URL :</b><code> {uuid_text.text}</code>    
<b>Checking if URL Redirect 🔄</b>
"""
        _bot = AsyncTeleBot(str(_session[3]))
        _msg = await _bot.send_message(int(_session[4]), initial_text, parse_mode="HTML")
    _dict["original_url"] = str(uuid_text.text)
    check, _original_url = get_redirected_url(str(uuid_text.text))
    if _original_url == "data:,":
        _original_url = uuid_text.text
    if not check:
        LOGGER.info(f"Selenium Could not load the Site 😞'{uuid_text.text}'")
        _original_url = uuid_text.text
    LOGGER.info(f"Selenium Could not load the Site 😞'{uuid_text.text}'")
    _dict["long_url"] = _original_url
    if _session[2] == "App":
        if check:
            middle_text = f"""
<b>Given URL :</b><code> {uuid_text.text}</code>    
<b>Redirected URL :</b><code> {_original_url}</code>           
"""
        else:
            middle_text = f"""
<b>Given URL :</b><code> {uuid_text.text}</code>    
<b>Resolving Failed due to Error 😞 :</b><code> {_original_url}</code>         
"""
        await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), message_id=_msg.id, parse_mode="HTML")

    if _session[2] == "App":
        ssl_msg = """
<b>Getting the SSL Details 🔒, Stay Tight!!</b>
"""
        await _bot.edit_message_text(middle_text + ssl_msg, chat_id=int(_session[4]), message_id=_msg.id,
                                     parse_mode="HTML")
    parsed_hostname = urlparse(_original_url).netloc
    parsed_port = urlparse(_original_url).port
    if parsed_port is None:
        parsed_port = 443
    check, err, cert = get_ssl_certificate(parsed_hostname, parsed_port, timeout=10)
    _dict["ssl_cert"] = {
        "isSSLAvailable": check,
        "SSLPullError": err,
        "Certificate": cert
    }
    if cert is not None:
        _dict["ssl_cert"]["Certificate"]["notBefore"] = _dict["ssl_cert"]["Certificate"]["notBefore"].strftime('%m/%d/%Y')
        _dict["ssl_cert"]["Certificate"]["notAfter"] = _dict["ssl_cert"]["Certificate"]["notAfter"].strftime('%m/%d/%Y')

    if _session[2] == "App":
        if check:
            middle_text += f"""
<b>SSL Certificate is Valid 🔒😃</b>

<b>Date of Issue 📅 : </b><code> {cert["notBefore"]}</code>
<b>Date of Expiry 📅 : </b><code> {cert["notAfter"]}</code>
<b>Issuer 🌐: </b><code> {cert["issuer"]}</code>
<b>Issued to 💼: </b><code> {cert["subject"]}</code>
"""
            await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), message_id=_msg.id,
                                         parse_mode="HTML")
        else:
            if cert is not None:
                middle_text += f"""
<b>SSL Certificate is Invalid 😬</b>

<b>Error Message ❌: </b><code>{err}</code>
<b>Date of Issue 📅 : </b><code> {cert["notBefore"]}</code>
<b>Date of Expiry 📅 : </b><code> {cert["notAfter"]}</code>
<b>Issuer 🌐: </b><code> {cert["issuer"]['O']}</code>
<b>Issued to 💼: </b><code> {cert["subject"]['CN']}</code>              
"""
                await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), message_id=_msg.id,
                                             parse_mode="HTML")
            else:
                middle_text += f"""
<b>Could Not pull the SSL Certificate 😕(Probably it never existed)</b>

<b>Error Message ❌: </b><code>{err}</code>
"""
                await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), message_id=_msg.id,
                                             parse_mode="HTML")

    _features = extract_url_features(_original_url)
    if _session[2] == "App":
        middle_text += f"""
<b>Features of Long URL</b>
    
<b>Host Name 📡: </b> <code>{parsed_hostname}</code>
<b>Port 🔌: </b> <code>{parsed_port}</code>
<b>Length of URL 📏: </b> <code>{_features["length_url"]}</code>
<b>Is hostname an IP? 🌐: </b><code>{"True" if _features["ip"] == 1 else "False"}</code>
<b>Page Rank 📊: </b><code>{_features["page_rank"]}</code>
<b>Domain Age 🕰️: </b><code>{"No Data" if _features["domain_age"] == -1 else _features["domain_age"]} Days</code>
"""
        await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), message_id=_msg.id,
                                     parse_mode="HTML")
        ai_model_message = """
<b>Now Passing all the parameters to AI Model 🤖</b>
"""
        await _bot.edit_message_text(middle_text + ai_model_message, chat_id=int(_session[4]), message_id=_msg.id,
                                     parse_mode="HTML")
    _dict["features"] = _features
    _dict["host_name"] = parsed_hostname
    _dict["port"] = parsed_port
    X = pd.DataFrame(_features, index=[0]).iloc[:, :].values
    with open(MODEL_DIR, 'rb') as model:
        _model = pickle.load(model)
    _pred = _model.predict(X)

    if _session[2] == "App":
        markup = quick_markup({f'Model Prediction 🤖: {"Legit Site✅" if _pred == 0 else "Fake❌"}': {'url': _original_url}})
        await _bot.edit_message_text(middle_text, chat_id=int(_session[4]), reply_markup=markup,message_id=_msg.id,
                                     parse_mode="HTML")
    _dict["ModelPrediction"] = "Legit Site" if _pred == 0 else "Fake"
    return jsonable_encoder(_dict)
