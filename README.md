# that README is outdated, i don't see any people on my github, any questions or ask help at issues tab or at socials.
(use a script that is the latest in the releases)

https://github.com/user-attachments/assets/85a6807d-ce7e-4b98-a7f7-c2bec47b3283

❗ readme was made by AI and reviewed by @kolqvr
# DeepLX CLI Translator with Fallback 🚀


A command-line tool to translate text using DeepL translation services. It prioritizes a primary DeepLX API endpoint (doesn't really require the api key, you decide) and gracefully falls back to a list of public DeepLX-like endpoints if the primary fails.

## ✨ Key Features

*   **Primary API Priority:** Uses a specified primary API endpoint (`https://deeplx.missuo.ru/translate` by default) with an API key for potentially more reliable translations.
*   **Sequential Fallback:** If the primary API fails, it automatically tries a curated list of public fallback DeepLX endpoints *in sequential order* until one succeeds.
*   **Multiple Input Modes:**
    *   Translate text directly from the command line.
    *   Translate the entire content of a text file (`-f` / `--file`).
    *   Use interactive mode for multi-line input (run without text or file arguments).
*   **File Output:** Save the translation result directly to a specified file (`-o` / `--output`). Automatically suggests an output filename if translating a file and no output is specified.
*   **Proxy Support:** Route requests through an HTTP/HTTPS proxy (`-p` / `--proxy` or `PROXY` environment variable).
*   **Show Alternatives:** Display alternative translations if provided by the API (`-a` / `--alternatives`).
*   **Error Handling:** Provides detailed error messages if all endpoints fail, listing the specific error encountered for each URL.
*   **Randomized Headers:** Uses randomized User-Agent strings and associated headers for fallback endpoints to mimic various clients.
*   **Language Support:** Supports source (`auto` detection included) and target language specification.

## 🔧 Getting Started

### Prerequisites

*   **Python:** Version 3.7 or higher is recommended (due to `asyncio` and `httpx`).
*   **pip:** Python package installer.

### Installation

1.  **Clone the Repository:**
    I'm so sorry, i don't know how does it works so just download the file from [(here.)](https://github.com/kolqvr/DeepLXcli/blob/main/deeplx_cli.py)

2.  **Install Dependencies:**
    This script requires the `httpx` library for asynchronous HTTP requests.
    ```bash
    pip install httpx
    ```

3.  **Get and Configure the Primary API Key:**

    *   **Why?** The script is configured to use `https://deeplx.missuo.ru/translate` as its primary, preferred endpoint. This endpoint requires an API key for access.
    *   **How?**
        1.  Go to the service provider's website: [https://deeplx.missuo.ru/](https://deeplx.missuo.ru/)
        2.  Follow their instructions to sign up (typically involving GitHub authentication) and obtain your unique API key.
    *   **Configure:**
        1.  Open the `deeplx_cli.py` script in a text editor or VS code.
        2.  Locate the line:
            ```python
            PRIMARY_API_KEY = "GET API FROM https://deeplx.missuo.ru IF NEEDED"
            ```
        3.  **Replace the placeholder key** `"GET API FROM https://deeplx.missuo.ru IF NEEDED"` with the **actual API key** you obtained.
            ```python
            # Example after replacement:
            PRIMARY_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
            ```

## 💡 Usage

The script can be run directly using `python`.

```bash
python deeplx_cli.py [options] [TEXT_TO_TRANSLATE]
```

### Examples

1.  **Translate a Simple String (Auto-detect source, default target EN):**
    ```bash
    python deeplx_cli.py "Bonjour le monde"
    ```

2.  **Translate a String with Specific Languages:**
    ```bash
    python deeplx_cli.py "Hello world" -s EN -t ES
    ```

3.  **Translate from a File:**
    ```bash
    # Translate input.txt (auto-detect source) to Japanese (JA)
    # Save result to output.ja.txt
    python deeplx_cli.py -f input.txt -t JA -o output.ja.txt
    ```

4.  **Translate from a File (Auto-naming Output):**
    If `-o` is omitted when using `-f`, the script will suggest saving to `original_filename.TARGET_LANG.translated.txt`.
    ```bash
    # Translates input.txt to German (DE)
    # Will save to input.DE.translated.txt (after printing the suggested name)
    python deeplx_cli.py -f input.txt -t DE
    ```

5.  **Interactive Mode (for multi-line input):**
    ```bash
    python deeplx_cli.py -s auto -t FR
    ```
    *   Then, type or paste your text.
    *   Press `Enter` after each line.
    *   When finished, press `Ctrl+D` (Linux/macOS) or `Ctrl+Z` followed by `Enter` (Windows).

6.  **Using a Proxy:**
    ```bash
    # Option 1: Command-line argument
    python deeplx_cli.py "Translate this" -t DE -p http://user:pass@proxyserver:port

    # Option 2: Environment variable
    export PROXY="http://user:pass@proxyserver:port"
    python deeplx_cli.py "Translate this" -t DE
    ```

7.  **Show Alternative Translations:**
    ```bash
    python deeplx_cli.py "A complex phrase to translate" -t RU -a
    ```

### Command-Line Arguments

```
usage: deeplx_cli.py [-h] [-f FILE] [-s SOURCE] [-t TARGET] [-p PROXY] [-a] [--html] [-o OUTPUT] [text]

CLI tool to translate text using DeepLX-like APIs with fallback.

positional arguments:
  text                  Text to translate. If omitted and --file is not used, enters interactive mode.

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to a text file to translate.
  -s SOURCE, --source SOURCE
                        Source language code (e.g., 'EN', 'DE', 'auto'). Default: auto
  -t TARGET, --target TARGET
                        Target language code (e.g., 'EN', 'DE', 'JA'). Default: EN
  -p PROXY, --proxy PROXY
                        Proxy URL (e.g., 'http://user:pass@host:port'). Reads PROXY env var if set.
  -a, --alternatives    Show alternative translations if available.
  --html                Indicate that the input text might contain HTML (basic). Note: Affects payload slightly but DeepLX handling varies.
  -o OUTPUT, --output OUTPUT
                        File path to save the main translation result.
```

## ⚙️ How it Works

1.  **Payload Preparation:** The input text, source language, and target language are formatted into a JSON payload suitable for DeepLX APIs.
2.  **Primary Attempt:** The script first attempts to send the payload to the `PRIMARY_API_URL` using the provided `PRIMARY_API_KEY`.
3.  **Fallback Sequence:** If the primary attempt fails (due to network error, API error, timeout, etc.), the script iterates through the `FALLBACK_URLS` list *in the order they appear*.
4.  **Request Logic:** For each fallback URL, it sends the same payload but uses a randomly selected set of headers (including `User-Agent`) from the `DEVICE_PROFILES` list to mimic different clients. A short delay is added between fallback attempts.
5.  **Success:** If any request (primary or fallback) returns a successful (2xx status) response with the expected JSON structure (`{"data": "translation", ...}`), that translation is returned, and the process stops.
6.  **Failure:** If all endpoints in the primary and fallback lists are tried and none succeed, the script returns an error message along with a detailed list of errors encountered for each attempted URL.

## 🌐 Supported Languages (in Script)

The script explicitly lists these language codes as potentially supported by the APIs (DeepL itself supports more, but these are often targeted by DeepLX):

`auto`, `BG`, `CS`, `DA`, `DE`, `EL`, `EN`, `ES`, `ET`, `FI`, `FR`, `HU`, `ID`, `IT`, `JA`, `LT`, `LV`, `NL`, `PL`, `PT`, `RO`, `RU`, `SK`, `SL`, `SV`, `TR`, `UK`, `ZH`

*(Note: `auto` means the API should attempt to detect the source language.)*

## 📜 Fallback Endpoints (in Script)

The script includes a list of public DeepLX-like endpoints. The availability and reliability of these public endpoints can vary greatly and change without notice. Some might be rate-limited, offline, or require specific request formats not fully handled by this script. *Note: Some URLs in the list might be outdated or non-functional (e.g., one is explicitly marked `(doesn't work)` in the code).*

## 🤝 Contributing

Contributions are welcome! If you find bugs, have suggestions for improvements, or want to add features (like better handling of different API response formats or improved configuration management), please feel free to open an issue or submit a pull request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (or add an MIT license file if you don't have one).

## ⚠️ Disclaimer

*   This tool relies on third-party APIs (both the primary one and the public fallbacks). Their availability, terms of service, and functionality are subject to change without notice.
*   The public fallback endpoints may be unstable, rate-limited, or may disappear. Use them responsibly and at your own risk.
*   Always respect the terms of service of the DeepL API and any proxy services you use. This tool is intended for personal, educational, or experimental use.
*   Ensure you have the right to translate the content you are processing.
*   The primary API key system relies on the service provided at `https://deeplx.missuo.ru/`. Refer to their terms and conditions.
