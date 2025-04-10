#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
import random
import re
import time
import httpx
from typing import Optional, List, Dict, Any, Tuple

# --- Configuration ---

PRIMARY_API_URL = "https://deeplx.missuo.ru/translate"
PRIMARY_API_KEY = "GET API FROM https://deeplx.missuo.ru IF NEEDED"

FALLBACK_URLS = [
    "https://deepl.aimoyu.tech/translate",
    "https://deeplx.xcty.gq/translate",
    "https://deeplx.vercel.app/translate",
    "https://deeplxpro.vercel.app/translate",
    "https://deeplx.llleman.com/translate",
    "https://translates.me/v2/translate", # Might have different request/response format? Test needed.
    "https://deeplx.papercar.top/translate",
    "https://dlx.bitjss.com/translate",
    "https://deeplx.ychinfo.com/translate",
    "https://free-deepl.speedcow.top/translate",
    "https://deeplx.keyrotate.com/translate",
    "https://deepl.wuyongx.uk/translate",
    "https://ghhosa.zzaning.com/translate",
    "https://deeplx.he-sb.top/translate",
    "https://deepl.tr1ck.cn/translate",
    "https://translate.dftianyi.com/translate",
    "https://deeplx.2077000.xyz:2087/translate",
    "https://deeplx.030101.xyz/translate",
    "https://deepx.dumpit.top/translate",
    "https://deeplx.ychinfo.com/translate",
    "https://api.deeplx.org/translate(doesn't work)",
    "https://www2.deepl.com/jsonrpc",
    "https://www.deepl.com/",
    "www2.deepl.com",
]

# Enhanced list of potential User-Agents and corresponding headers
DEVICE_PROFILES = [
    # iOS App User Agent
    {
        "User-Agent": "DeepL-iOS/2.9.1 iOS 16.3.0 (iPhone13,2)",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "x-app-os-name": "iOS",
        "x-app-os-version": "16.3.0",
        "x-app-device": "iPhone13,2",
        "x-app-build": "510265",
        "x-app-version": "2.9.1",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    },
    # Newer iOS App User Agent Example
    {
        "User-Agent": "DeepL/1627620 CFNetwork/3826.500.62.2.1 Darwin/24.4.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "x-app-os-name": "iOS",
        "x-app-os-version": "18.4.0", # Keep versions plausible
        "x-app-device": "iPhone16,2", # Keep devices plausible
        "x-app-build": "1627620",
        "x-app-version": "25.1",
        "Referer": "https://www.deepl.com/",
        "X-Product": "translator",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    },
    # Browser Extension Example
     {
        'User-Agent': 'DeepLBrowserExtension/1.29.0 Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh-HK;q=0.6,zh;q=0.5',
        'Authorization': 'None',
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
        'DNT': '1', # Do Not Track
        'Origin': 'chrome-extension://cofdbpoegempjloogbagkncekinflcnj', # Specific to Chrome extensions
        'Pragma': 'no-cache',
        'Referer': 'https://www.deepl.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'none',
        'Sec-GPC': '1', # Global Privacy Control
        'Connection': 'keep-alive',
    },
    # Generic Desktop Browser Example
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.deepl.com/",
        "Origin": "https://www.deepl.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
    }
]

SUPPORTED_LANGUAGES = [
    "auto", "BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI",
    "FR", "HU", "ID", "IT", "JA", "LT", "LV", "NL", "PL", "PT",
    "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH" # Assuming simplified ZH for base
]

# --- Helper Functions ---

def get_random_headers() -> Dict[str, str]:
    """Selects a random device profile and returns its headers."""
    return random.choice(DEVICE_PROFILES).copy()

def get_random_request_id() -> int:
    """Generates a random ID."""
    return random.randint(1000000000, 9999999999)

def format_payload(text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
    """Formats the standard payload for DeepLX-like servers."""
    return {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang,
    }

async def make_request(
    client: httpx.AsyncClient,
    url: str,
    payload: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    is_primary: bool = False
) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[int]]:
    """
    Makes a translation request to a given URL.
    Returns: (json_result, error_message, status_code)
    """
    request_url = url
    request_headers = headers if headers else {}
    request_payload_json = json.dumps(payload)

    if is_primary:
        request_url = f"{url}?key={PRIMARY_API_KEY}"
        request_headers['Content-Type'] = 'application/json'
    else:
        if not headers:
             request_headers = get_random_headers()
        request_headers['Content-Type'] = 'application/json'

    print(f"\nAttempting request to: {request_url}")
    if not is_primary:
        print(f"Using headers: {{'User-Agent': '{request_headers.get('User-Agent', 'N/A')}'}}...")

    try:
        response = await client.post(
            request_url,
            content=request_payload_json,
            headers=request_headers,
            timeout=15.0
        )

        result_json = None
        error_from_json = None
        try:
            result_json = response.json()
            # Debug: Print raw JSON received on potential success or API error
            # print(f"DEBUG: Received JSON from {url}: {result_json}")
            if isinstance(result_json, dict) and 'message' in result_json and response.status_code != 200:
                error_from_json = f"API Error (Code: {result_json.get('code', response.status_code)}): {result_json['message']}"
        except json.JSONDecodeError:
            if response.status_code != 200:
                 error_from_json = f"Non-JSON Response (Status: {response.status_code}): {response.text[:100]}..."

        response.raise_for_status()

        # If we got here, status code is 2xx
        if isinstance(result_json, dict) and 'data' in result_json:
            print(f"Success from {url} (Status: {response.status_code})")
            # Debug: Print the structure of the successful JSON
            # print(f"DEBUG: Successful JSON structure: {result_json}")
            if 'target_lang' not in result_json:
                 result_json['target_lang'] = payload.get('target_lang', 'UNKNOWN')
            # Ensure alternatives is a list, even if missing
            if 'alternatives' not in result_json:
                result_json['alternatives'] = []
            return result_json, None, response.status_code
        else:
            # This case means 2xx status but invalid JSON content
            print(f"Invalid JSON structure received from {url} despite 2xx status: {result_json}")
            return None, f"Invalid Success JSON structure from {url}", response.status_code

    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        error_msg = error_from_json if error_from_json else f"HTTP Error {status_code}: {e.response.text[:100]}..."
        print(f"Failed {url} with Status {status_code}. Error: {error_msg}")
        if status_code == 429:
            return None, "Rate Limited (429)", status_code
        elif status_code == 401 or status_code == 403:
             return None, f"Authorization Error ({status_code})", status_code
        elif status_code == 405 and result_json and isinstance(result_json.get("data"), str) and "Invalid target language" in result_json.get("data",""):
             return None, f"Invalid Target Language ({status_code})", status_code
        else:
            return None, error_msg, status_code
    except httpx.TimeoutException:
        print(f"Timeout connecting to {url}")
        return None, f"Timeout connecting to {url}", None
    except httpx.RequestError as e:
        error_detail = str(e)
        print(f"Request Error connecting to {url}: {error_detail}")
        return None, f"Request Error: {error_detail}", None
    except Exception as e:
        print(f"An unexpected error occurred for {url}: {e}")
        return None, f"Unexpected Error: {e}", None

# --- Core Translation Logic ---

async def translate_text_with_fallback(
    text: str,
    source_lang: str = 'auto',
    target_lang: str = 'en',
    proxy: Optional[str] = None
) -> Dict[str, Any]:
    """
    Translates text using the primary URL first, then fallback URLs sequentially.
    Collects errors from all attempts.
    """
    if not text:
        return {"error": "No text provided for translation."}

    sl = source_lang.upper() if source_lang != 'auto' else 'auto'
    tl = target_lang.upper()

    payload = format_payload(text, sl, tl)
    proxies_dict = {"http://": proxy, "https://": proxy} if proxy else None
    all_errors = [] # List to store error details

    async with httpx.AsyncClient(proxy=proxies_dict, follow_redirects=True) as client:
        # 1. Try Primary URL
        print("-" * 20)
        print("Trying Primary URL...")
        primary_result, primary_error, primary_status = await make_request(
            client, PRIMARY_API_URL, payload, is_primary=True
        )
        if primary_result:
            return primary_result # Success!

        # Log primary error regardless of type
        if primary_error:
            print(f"Primary URL failed: {primary_error}")
            all_errors.append({"url": PRIMARY_API_URL, "error": primary_error, "status": primary_status})
        else:
             print("Primary URL failed (unknown reason).")
             all_errors.append({"url": PRIMARY_API_URL, "error": "Unknown failure", "status": primary_status})


        # 2. Try Fallback URLs ***SEQUENTIALLY***
        print("-" * 20)
        print("Trying Fallback URLs (in listed order)...") # Updated print statement
        # *** CHANGE: Iterate directly over FALLBACK_URLS ***
        for i, url in enumerate(FALLBACK_URLS):
            headers = get_random_headers()
            fallback_result, fallback_error, fallback_status = await make_request(
                client, url, payload, headers=headers, is_primary=False
            )

            if fallback_result:
                return fallback_result # Success!

            # Log fallback error
            if fallback_error:
                 print(f"{url} failed: {fallback_error}. Trying next fallback...")
                 all_errors.append({"url": url, "error": fallback_error, "status": fallback_status})
            else:
                 print(f"{url} failed (unknown reason). Trying next fallback...")
                 all_errors.append({"url": url, "error": "Unknown failure", "status": fallback_status})

            # Delay between all fallback attempts
            if i < len(FALLBACK_URLS) - 1: # Don't sleep after the last attempt
                print(f"Waiting 0.5s before next fallback attempt...")
                await asyncio.sleep(0.5)


    # 3. If all fail
    print("-" * 20)
    # Return the list of all encountered errors
    return {"error": "Translation failed after trying all endpoints.", "all_errors": all_errors}

# --- File Handling ---

async def translate_file(
    file_path: str,
    source_lang: str = 'auto',
    target_lang: str = 'en',
    proxy: Optional[str] = None,
    handle_html: bool = False
) -> Dict[str, Any]:
    """Translates content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Read {len(content)} characters from {file_path}")
    except Exception as e:
        return {"error": f"Failed to read file '{file_path}': {e}"}

    if handle_html:
        print("Note: HTML handling requested, but basic payload doesn't explicitly include tag_handling.")

    result = await translate_text_with_fallback(content, source_lang, target_lang, proxy)

    if 'data' in result:
         result['input_file'] = file_path
    return result

# --- Output Formatting ---

def print_result(result: Dict[str, Any], show_alternatives: bool = False, output_file: Optional[str] = None):
    """Formats and prints the translation result, including detailed errors if present."""
    print("\n" + "=" * 30 + " RESULT " + "=" * 30)

    if 'error' in result:
        print(f"❌ Error: {result['error']}") # Main error message
        if 'all_errors' in result and result['all_errors']:
            print("\n--- Failure Details ---")
            for err_info in result['all_errors']:
                 status_str = f"(Status: {err_info['status']})" if err_info.get('status') else "(Status: N/A)"
                 print(f"- URL: {err_info['url']}")
                 print(f"  Error: {err_info['error']} {status_str}")
            print("---------------------")
        return

    data = result.get('data', '[Translation not found]')
    source = result.get('source_lang', 'N/A')
    target = result.get('target_lang', 'N/A')
    # *** MODIFIED: Get alternatives, default to empty list if missing ***
    alternatives = result.get('alternatives', [])

    print(f"Detected Source Language: {source}")
    print(f"Target Language: {target}")
    print("\n📜 Translation:")
    print(data)

    # *** MODIFIED: Simplified alternatives printing logic ***
    if show_alternatives and isinstance(alternatives, list) and alternatives:
        print("\n🔄 Alternatives:")
        # Check if the first alternative is the same as the main data
        start_index = 0
        if alternatives[0] == data and len(alternatives) > 1:
             start_index = 1 # Skip printing the first if it's identical and there are others

        if len(alternatives) > start_index:
            for i, alt in enumerate(alternatives[start_index:], 1):
                print(f"   {i}. {alt}")
        elif start_index == 0: # Only one alternative, and it might be the same or different
            print(f"   1. {alternatives[0]}")
        else:
            print("   (No different alternatives found)")
    elif show_alternatives:
         print("\n🔄 Alternatives: (None provided by API)")


    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f"\n✅ Translation successfully saved to: {output_file}")
            if 'input_file' in result:
                 print(f"   (Original file: {result['input_file']})")
        except Exception as e:
            print(f"\n❌ Error saving translation to '{output_file}': {e}")

    print("=" * (68))

# --- Main Execution ---

# (Main execution block remains the same as the previous version)
async def main():
    parser = argparse.ArgumentParser(
        description="CLI tool to translate text using DeepLX-like APIs with fallback.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to translate. If omitted and --file is not used, enters interactive mode."
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to a text file to translate."
    )
    parser.add_argument(
        "-s", "--source",
        default="auto",
        help="Source language code (e.g., 'EN', 'DE', 'auto'). Default: auto"
    )
    parser.add_argument(
        "-t", "--target",
        default="EN",
        help="Target language code (e.g., 'EN', 'DE', 'JA'). Default: EN"
    )
    parser.add_argument(
        "-p", "--proxy",
        help="Proxy URL (e.g., 'http://user:pass@host:port'). Reads PROXY env var if set."
    )
    parser.add_argument(
        "-a", "--alternatives",
        action="store_true",
        help="Show alternative translations if available."
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Indicate that the input text might contain HTML (basic)."
    )
    parser.add_argument(
        "-o", "--output",
        help="File path to save the main translation result."
    )

    args = parser.parse_args()

    proxy = args.proxy or os.environ.get('PROXY')
    if proxy:
        print(f"Using proxy: {proxy}")

    result = None
    output_target = args.output

    if args.file:
        if args.text:
            print("Warning: Both text and file provided. Using file.")
        result = await translate_file(args.file, args.source, args.target, proxy, args.html)
        if not output_target and 'data' in result and 'input_file' in result:
            base, _ = os.path.splitext(result['input_file'])
            target_lang_for_file = result.get('target_lang','txt')
            output_target = f"{base}.{target_lang_for_file}.translated.txt"
            print(f"No output file specified, will save to: {output_target}")

    elif args.text:
        result = await translate_text_with_fallback(args.text, args.source, args.target, proxy)
    else:
        # Interactive mode
        print("--- DeepLX Interactive Mode ---")
        print("Enter text to translate. Press Ctrl+D (Unix) or Ctrl+Z+Enter (Windows) when done.")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        print("-------------------------------")

        if lines:
            interactive_text = "\n".join(lines)
            result = await translate_text_with_fallback(interactive_text, args.source, args.target, proxy)
        else:
            print("No input received.")
            parser.print_help()
            return

    if result:
        print_result(result, args.alternatives, output_target)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nTranslation cancelled by user.")