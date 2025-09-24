import sys
import time
import re
import phonenumbers
from phonenumbers import (
    geocoder,
    carrier,
    timezone,
    PhoneNumberFormat,
    NumberParseException,
    PhoneMetadata,
    PhoneNumberType,
)
try:
    import pycountry
except ImportError:
    pycountry = None
from colorama import Fore, Style, init
from flask import Flask, jsonify

init(autoreset=True)

ascii_art = f"""{Fore.CYAN}
  ___ _                   _        _ 
 | _ \ |_  ___ _ _  ___  /_\  _ __(_)
 |  _/ ' \/ _ \ ' \/ -_)/ _ \| '_ \ |
 |_| |_||_\___/_||_\___/_/ \_\ .__/_|
                             |_|      
{Style.RESET_ALL}
"""

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

def _fmt(k, v, pad=20):
    key = f"{k}".ljust(pad)
    val = f"{v}"
    return f"  {key} → {val}"

def _yesno(v):
    if isinstance(v, bool):
        return "Yes" if v else "No"
    if v is None:
        return "Unknown"
    return str(v)

def sanitize_number(raw):
    s = re.sub(r"[^\d+]", "", raw.strip())
    if not s.startswith("+"):
        default_region = "FR"
        try:
            return phonenumbers.parse(s, default_region)
        except NumberParseException:
            return None
    try:
        return phonenumbers.parse(s, None)
    except NumberParseException:
        return None

def safe_meta_for_region(region_code):
    try:
        return PhoneMetadata.metadata_for_region(region_code)
    except Exception:
        try:
            return PhoneMetadata.metadata_for_region(region_code, None)
        except Exception:
            return None

def lookup_json(number_input):
    parsed = sanitize_number(number_input)
    if not parsed:
        return {"error": "Invalid phone number format"}

    typ = phonenumbers.number_type(parsed)
    result = {}
    result["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
    result["basic"] = {
        "valid": phonenumbers.is_valid_number(parsed),
        "possible": phonenumbers.is_possible_number(parsed),
    }

    region_desc = geocoder.description_for_number(parsed, "en") or "Unknown"
    region_code = phonenumbers.region_code_for_number(parsed) or "Unknown"
    country_code = getattr(parsed, "country_code", "Unknown")
    country_info = {}
    if pycountry and region_code != "Unknown":
        try:
            c = pycountry.countries.get(alpha_2=region_code)
            if c:
                country_info = {
                    "name": c.name,
                    "alpha2": c.alpha_2,
                    "alpha3": getattr(c, "alpha_3", None),
                    "numeric": getattr(c, "numeric", None),
                }
        except Exception:
            pass

    result["geographic"] = {
        "region": region_desc,
        "iso_region": region_code,
        "country_code": f"+{country_code}",
        "country_info": country_info,
    }

    sim_carrier = carrier.name_for_number(parsed, "en") or "Unknown"
    try:
        carrier_region = carrier.region_code_for_number(parsed) or "Unknown"
    except Exception:
        carrier_region = "Unknown"
    result["carrier"] = {"name": sim_carrier, "region": carrier_region}

    tz = timezone.time_zones_for_number(parsed) or []
    result["timezone"] = tz if tz else ["Unknown"]

    type_map = {
        PhoneNumberType.MOBILE: "Mobile",
        PhoneNumberType.FIXED_LINE: "Landline",
        PhoneNumberType.FIXED_LINE_OR_MOBILE: "Mobile or Landline",
        PhoneNumberType.TOLL_FREE: "Toll-Free",
        PhoneNumberType.PREMIUM_RATE: "Premium",
        PhoneNumberType.VOIP: "VoIP",
        PhoneNumberType.PERSONAL_NUMBER: "Personal",
        PhoneNumberType.PAGER: "Pager",
        PhoneNumberType.UAN: "UAN",
        PhoneNumberType.UNKNOWN: "Unknown",
    }
    result["line_type"] = type_map.get(typ, "Unknown")
    result["is_premium"] = typ == PhoneNumberType.PREMIUM_RATE

    try:
        result["formats"] = {
            "e164": phonenumbers.format_number(parsed, PhoneNumberFormat.E164),
            "international": phonenumbers.format_number(parsed, PhoneNumberFormat.INTERNATIONAL),
            "national": phonenumbers.format_number(parsed, PhoneNumberFormat.NATIONAL),
            "rfc3966": phonenumbers.format_number(parsed, PhoneNumberFormat.RFC3966),
        }
    except Exception:
        result["formats"] = {}

    nsn = phonenumbers.national_significant_number(parsed)
    ndc_len = phonenumbers.length_of_national_destination_code(parsed)
    result["structure"] = {
        "national_significant": nsn,
        "ndc_length": ndc_len,
        "total_length": len(nsn) if nsn else None,
    }

    portable = None
    try:
        if region_code != "Unknown":
            portable = phonenumbers.is_mobile_number_portable_region(region_code)
    except Exception:
        portable = None
    result["portability"] = portable

    result["special_checks"] = {
        "short_number_possible": phonenumbers.is_possible_short_number(parsed),
        "emergency_number": (
            phonenumbers.is_emergency_number(str(parsed.national_number), region_code)
            if region_code != "Unknown"
            else False
        ),
    }

    if region_code != "Unknown":
        try:
            example = phonenumbers.example_number(region_code)
            if example:
                result["example_number"] = phonenumbers.format_number(example, PhoneNumberFormat.INTERNATIONAL)
        except Exception:
            pass

    return result

@app.route("/PhoneApi/v1/search=<number>", methods=["GET"])
def api_lookup(number):
    return jsonify(lookup_json(number))

def cli_mode(number_input):
    data = lookup_json(number_input)
    print(ascii_art)
    print(f"[*] phoneapi started @ {data.get('timestamp')}\n")
    print(Fore.CYAN + "┌─ Basic Info")
    for k, v in data["basic"].items():
        print(_fmt(k.capitalize(), _yesno(v)))
    print("")
    print(Fore.CYAN + "┌─ Geographic Info")
    for k, v in data["geographic"].items():
        if isinstance(v, dict):
            for kk, vv in v.items():
                print(_fmt(kk.capitalize(), vv))
        else:
            print(_fmt(k.capitalize(), v))
    print("")
    print(Fore.CYAN + "┌─ Carrier Info")
    for k, v in data["carrier"].items():
        print(_fmt(k.capitalize(), v))
    print("")
    print(Fore.CYAN + "┌─ Line Type")
    print(_fmt("Type", data["line_type"]))
    print(_fmt("Premium", _yesno(data["is_premium"])))
    print("")
    print(Fore.CYAN + "┌─ Formats")
    for k, v in data.get("formats", {}).items():
        print(_fmt(k, v))
    print("")
    print(Fore.CYAN + "┌─ Structure")
    for k, v in data["structure"].items():
        print(_fmt(k.replace("_"," ").capitalize(), v))
    print("")
    print(Fore.CYAN + "┌─ Portability")
    print(_fmt("Mobile Portable", _yesno(data["portability"])))
    print("")
    print(Fore.CYAN + "┌─ Special Checks")
    for k, v in data.get("special_checks", {}).items():
        print(_fmt(k.replace("_"," ").capitalize(), _yesno(v)))
    if "example_number" in data:
        print(_fmt("Example Number", data["example_number"]))
    print(Fore.GREEN + "\n[•] Lookup complete.\n")

def main():
    if len(sys.argv) < 2:
        print(ascii_art)
        print(Fore.YELLOW + "[*] Usage: python phoneapi.py <phone_number> | api")
        return

    if sys.argv[1].lower() == "api":
        print(ascii_art)
        print(Fore.YELLOW + "[i] API running at http://127.0.0.1:5000/PhoneApi/v1/search=<number>")
        print(Fore.YELLOW + "[i] Press Ctrl+C to stop the server and exit.\n")
        import logging
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
        try:
            app.run(host="127.0.0.1", port=5000, debug=False)
        except KeyboardInterrupt:
            print(Fore.RED + "\n[•] API stopped by user. Exiting...")
            sys.exit(0)
    else:
        cli_mode(sys.argv[1])

if __name__ == "__main__":
    main()
