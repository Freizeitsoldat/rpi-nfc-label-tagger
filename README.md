# RPI NFC + LabelWriter REST API

## Installation

```
git clone ...
python3 -m venv .env
source .env/bin/activate
pip install -r requirements.txt
python run.py
```

## Settings

```
    # Flask settings
    SECRET_KEY = 'S3CR3T'
    HOST = '0.0.0.0'
    DEBUG = True
    PORT = 5000

    # Printer settings
    PRINT_WIDTH = 40
    PRINT_HEIGHT = 89
    PRINT_FONT_SIZE = 40
```

## API Endpoints

### POST /api/label

| Parameter    | Beschreibung
| ------------ | ------------
| url          | URL der Seite 
| description  | Beschreibung des Labels
| uuid         | Optional

```json
{
    "uuid":"<uuid>",
    "state": "success|missing params|something went wrong"
}
```
> HTTP Status Code: 200|400|500

### POST /api/nfc

| Parameter    | Beschreibung
| ------------ | ------------
| url          | URL der Seite 
| description  | Beschreibung des Labels
| uuid         | Optional

```json
{
    "uuid":"<uuid>",
    "state": "success|waiting|something went wrong"
}
```
> HTTP Status Code: 200|503|500


Alternativ kann der Status über folgenden Endpoint abgefragt werden

### GET /api/nfc/<uuid>

```json
{
    "state": "success|waiting"
}
```
> HTTP Status Code: 200|503