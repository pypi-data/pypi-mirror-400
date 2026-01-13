# Tolkapy - aka TamilRulepy

Tolkapy is a python package known earlier as tamilrulepy 
which provides functions based on tolkapiyam rules to validate tamil words.

## பதிப்பு V0.0.2

## About

Code Repository : https://gitlab.com/kachilug/tamilrulepy
Issues : https://gitlab.com/kachilug/tamilrulepy/-/issues

தமிழ் விக்கிமூலத்தில் எழுத்துணிரியாக்கம்(OCR) செய்த தரவுகளைத் துப்புரவு செய்ய, இக்கூட்டுமுயற்சி மேற்கொள்ளப்படுகிறது.

தொல்காப்பியரின் விதிகளை முழுமையாக நிரலாக்கம் செய்தால் எழுத்துணரியாக்கப் பிழைகளைக் களைய முடியும்.

Tamil is one of the still existing classical language. 
It has been used around 10 million around world. so we
planed to develop this library for help helping tamil
application.  

## Documentation

தமிழ் [English](https://tamilrulepy.readthedocs.io/en/latest/)

## ஆவணங்களை புதுப்பிக்க

```bash 
make html
```

## ஆவணம் தயாரிப்பு சூழல் அமைத்தல்

```bash
cd [root folder]

python3 -m venv tamilrulepy-venv

source tamilrulepy-venv/bin/activate

pip install -r requirements.txt

cd source --> rst கோப்புகளை திருத்த 
cd tamilrulepy --> py கோப்புகளில் ஆவணப்படுத்த """" doc strings ஐ""" பயன்படுத்த

(எ.க) vidhikal.rst ஐ பார்க்க
```

### தொடுப்புகள்

[சிபினிக்ஸ் ஆவணம் தயாரிப்பான் பயன்பாட்டு குறிப்பு](https://eikonomega.medium.com/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365)

## For Building

```bash
uv build --wheel
```

## Contact

Community (Telegram) : https://t.me/+Flv200UT_Lg0ODk1