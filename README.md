# 📞 PhoneApi — Phone Number Intelligence Tool

```text
  ___ _                   _        _ 
 | _ \ |_  ___ _ _  ___  /_\  _ __(_)
 |  _/ ' \/ _ \ ' \/ -_)/ _ \| '_ \ |
 |_| |_||_\___/_||_\___/_/ \_\ .__/_|
                             |_|      
````

**PhoneApi** is a Python tool that analyzes phone numbers and provides useful information such as:

* Validation & possibility checks
* Region & country details
* Carrier info
* Timezones
* Number type (mobile, landline, VoIP, etc.)
* Different formatting styles (E.164, international, national)
* Short/emergency number detection
* A built-in **REST API** for integration with other apps

---

## 🚀 Features

* 🔹 CLI mode for quick lookups
* 🔹 REST API mode (`Flask`) for programmatic access
* 🔹 Colorful & clear terminal output
* 🔹 Country info powered by [pycountry](https://pypi.org/project/pycountry/)
* 🔹 Fully offline lookup (no external API calls)

---

## 📦 Installation

### 1️⃣ Install Python

Make sure Python **3.8+** is installed.
Check your version:

```bash
python3 --version
```

If you don’t have Python, download it from [python.org](https://www.python.org/downloads/).

### 2️⃣ Clone the repo

```bash
git clone https://github.com/seryannn/PhoneApi.git
cd PhoneApi
```

### 3️⃣ (Optional) Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 4️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

> Typical requirements:
>
> ```text
> phonenumbers
> pycountry
> colorama
> flask
> ```

---

## ⚡ Usage

### 🔹 CLI Mode (Default)

```bash
python phoneapi.py +14155552671
```

Example output:

```
[*] Lookup @ 2025-09-24 15:42:11

┌─ Basic Info
  Valid                → Yes
  Possible             → Yes

┌─ Geographic Info
  Region               → California
  Iso_region           → US
  Country_code         → +1
  Name                 → United States

┌─ Carrier Info
  Name                 → AT&T Wireless
  Region               → US

┌─ Line Type
  Type                 → Mobile
  Premium              → No

┌─ Formats
  e164                 → +14155552671
  international        → +1 415-555-2671
  national             → (415) 555-2671
  rfc3966              → tel:+1-415-555-2671
```

---

### 🔹 API Mode

Run the server:

```bash
python phoneapi.py api
```

You’ll see:

```
[i] API running at http://127.0.0.1:5000/PhoneApi/v1/search=<number>
[i] Press Ctrl+C to stop the server and exit.
```

Query the API:

```bash
curl http://127.0.0.1:5000/PhoneApi/v1/search=+14155552671
```

Example JSON response:

```json
{
  "timestamp": "2025-09-24 15:44:00",
  "basic": {
    "valid": true,
    "possible": true
  },
  "geographic": {
    "region": "California",
    "iso_region": "US",
    "country_code": "+1",
    "country_info": {
      "name": "United States",
      "alpha2": "US",
      "alpha3": "USA",
      "numeric": "840"
    }
  },
  "carrier": {
    "name": "AT&T Wireless",
    "region": "US"
  },
  "timezone": ["America/Los_Angeles"],
  "line_type": "Mobile",
  "is_premium": false,
  "formats": {
    "e164": "+14155552671",
    "international": "+1 415-555-2671",
    "national": "(415) 555-2671",
    "rfc3966": "tel:+1-415-555-2671"
  },
  "structure": {
    "national_significant": "4155552671",
    "ndc_length": 3,
    "total_length": 10
  },
  "portability": true,
  "special_checks": {
    "short_number_possible": false,
    "emergency_number": false
  },
  "example_number": "+1 650-253-0000"
}
```

---

## 🛠️ Troubleshooting

| Problem                                     | Possible Fix                                                                |
| ------------------------------------------- | --------------------------------------------------------------------------- |
| `ImportError: No module named phonenumbers` | Run `pip install phonenumbers`                                              |
| `pycountry not found`                       | Install it manually: `pip install pycountry`                                |
| API won’t start                             | Check port 5000 availability or change the port in the script               |
| Weird country info                          | Ensure your number includes the correct country prefix (+XX)                |
| `Invalid phone number format`               | Make sure to pass a full number with country code, or it defaults to **FR** |

---

## ⚙️ Development Notes

* Default region if no country code is provided → **FR**
* Runs fully offline (phonenumbers + metadata are bundled)
* Flask server logs are suppressed for a cleaner console experience

---

## 🧪 Ideas for Expansion

* 🔧 Add Docker support
* 🌐 Deploy as a simple web app
* 🗂️ Add CSV batch lookup mode
* 📱 Optional GUI wrapper

---

## 📝 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 💡 Quick Start

```bash
git clone https://github.com/yourusername/PhoneApi.git
cd PhoneApi
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python phoneapi.py +14155552671
```

Or start the API:

```bash
python phoneapi.py api
```

Your API will run at:
**`http://127.0.0.1:5000/PhoneApi/v1/search=<number>`**
