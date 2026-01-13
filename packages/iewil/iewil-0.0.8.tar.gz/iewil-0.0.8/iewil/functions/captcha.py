import os
import json
import time
import requests
import itertools # spinner
import urllib.parse # antibot

from .display import Display

class Captcha:
    def __init__(self):
        self.providers_file = "cache/providers.json"
        config = self._simpan_apikey()

        self.url = config["url"]
        self.provider = config["provider"]
        self.key = config["apikey"]

    # ================= CONFIG =================

    def _simpan_apikey(self):
        folder = os.path.dirname(self.providers_file)
        if folder and not os.path.exists(folder):
            os.makedirs(folder, exist_ok=True)

        default = {
            "1": {
                "provider": "xevil",
                "url": "https://sctg.xyz/",
                "register": "t.me/Xevil_check_bot?start=1204538927",
                "apikey": ""
            },
            "2": {
                "provider": "multibot",
                "url": "http://api.multibot.in/",
                "register": "http://api.multibot.in",
                "apikey": ""
            }
        }

        if os.path.exists(self.providers_file):
            try:
                with open(self.providers_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = default
        else:
            data = default

        for prov in data.values():
            if prov.get("apikey"):
                return prov

        Display.title("Select Provider")
        Display.menu(1, "Xevil")
        Display.menu(2, "Multibot")
        Display.isi("number")

        choice = input().strip()
        Display.line()

        if choice not in data:
            Display.error("number not valid!")
            raise SystemExit

        prov = data[choice]
        Display.cetak("Register", prov["register"])
        Display.isi("API Key")
        key = input().strip()

        if choice == "1":
            key += "|SOFTID1204538927"

        data[choice]["apikey"] = key
        with open(self.providers_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        prov["apikey"] = key
        return prov

    # ================= API =================

    def _in_api(self, payload, method="GET", headers=None):
        payload["key"] = self.key
        payload["json"] = 1

        if method == "GET":
            r = requests.get(self.url + "in.php", params=payload)
        else:
            r = requests.post(self.url + "in.php", data=payload, headers=headers)

        return r.json()

    def _res_api(self, api_id):
        params = {
            "key": self.key,
            "action": "get",
            "id": api_id,
            "json": 1
        }
        return requests.get(self.url + "res.php", params=params).json()

    # ================= CORE =================

    def _filter(self, method):
        return {
            "userrecaptcha": "RecaptchaV2",
            "hcaptcha": "Hcaptcha",
            "turnstile": "Turnstile",
            "universal": "Ocr",
            "base64": "Ocr",
            "antibot": "Antibot"
        }.get(method)

    def _solving_progress(self, percent, seconds, cap):
        sym = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        spinner = itertools.cycle(sym)

        start = time.time()
        end = start + seconds

        start_percent = percent
        target_percent = 99

        while time.time() < end:
            elapsed = time.time() - start
            ratio = elapsed / seconds

            percent = int(start_percent + (target_percent - start_percent) * ratio)
            if percent > 99:
                percent = 99

            text = f" Bypass {cap} {percent}% {next(spinner)}"
            print(text, end="\r", flush=True)

            time.sleep(0.05)

        return percent


    def _get_result(self, data, method="GET"):
        cap = self._filter(data["method"])
        res = self._in_api(data, method)

        if not res.get("status"):
            Display.error(f"in_api @{self.provider} {res.get('request')}")
            return

        progress = 0
        while True:
            result = self._res_api(res["request"])
            if result["request"] == "CAPCHA_NOT_READY":
                progress = self._solving_progress(progress, 20, cap)
                continue

            if result["status"]:
                Display.sukses(f"Bypass {cap} success", False)
                time.sleep(2)
                Display.clear_line()
                return result["request"]

            Display.error(f"Bypass {cap} failed")
            return

    # ================= PUBLIC =================

    def get_balance(self):
        r = requests.get(self.url + "res.php", params={
            "action": "userinfo",
            "key": self.key
        }).json()
        return r.get("balance")

    def Turnstile(self, sitekey, pageurl):
        return self._get_result({
            "method": "turnstile",
            "sitekey": sitekey,
            "pageurl": pageurl
        })
    
    def RecaptchaV2(self, sitekey, pageurl):
        return self._get_result({
            "method": "userrecaptcha",
            "sitekey": sitekey,
            "pageurl": pageurl
        })
    import urllib.parse

    def AntiBot(self, source):
        # Step 1: cari main image
        try:
            main = source.split('Bot links')[1].split('data:image/png;base64,')[1].split('"')[0]
        except IndexError:
            try:
                main = source.split('Click the buttons in the following order')[1].split('data:image/png;base64,')[1].split('"')[0]
            except IndexError:
                return 0

        # Step 2: siapkan data
        if self.provider == "xevil":
            data = f"method=antibot&main={main}"
        else:
            data = {"method": "antibot", "main": main}

        # Step 3: parse semua images dari source
        src_list = source.split('rel="')
        for idx, sour in enumerate(src_list):
            if idx == 0:
                continue
            no = sour.split('"')[0]
            if self.provider == "xevil":
                try:
                    img = sour.split('data:image/png;base64,')[1].split('"')[0]
                    data += f"&{no}={img}"
                except IndexError:
                    continue
            else:
                try:
                    img = sour.split('src="')[1].split('"')[0]
                    data[no] = img
                except IndexError:
                    continue

        # Step 4: kirim request ke provider
        if self.provider == "xevil":
            res = self._get_result(data, "POST")
        else:
            payload = urllib.parse.urlencode(data)
            headers = {"Content-type": "application/x-www-form-urlencoded"}
            res = self._get_result(payload, "POST", headers)

        # Step 5: format hasil
        if res:
            return " " + res.replace(",", " ")
        return None
    
