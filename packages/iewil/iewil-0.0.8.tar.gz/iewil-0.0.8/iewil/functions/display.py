import os
import sys
import time
from typing import Dict, List

class Display:
    AUTHOR = "iewil"
    TITLE = ""
    REGISTER = ""

    # ==============================
    # KONFIGURASI WARNA & SIMBOL
    # ==============================
    color_scheme: Dict[str, List[List[int]]] = {
        "success": [[0, 255, 0], [0, 128, 0]],
        "warning": [[255, 0, 0], [128, 0, 0]],
        "debug":   [[255, 255, 0], [128, 128, 0]],
        "info":    [[0, 0, 255], [0, 0, 128]],
        "default": [[0, 128, 255], [0, 255, 255]],
    }

    symbols: Dict[str, str] = {
        "success": "✓",
        "warning": "!",
        "debug": "?",
        "info": "i",
        "default": "›",
    }

    # ==============================
    # GRADIENT STRING
    # ==============================
    @staticmethod
    def gradient(text: str, start: List[int], end: List[int]) -> str:
        length = len(text)
        if length == 0:
            return ""

        result = ""
        for i, char in enumerate(text):
            r = int(start[0] + (end[0] - start[0]) * i / length)
            g = int(start[1] + (end[1] - start[1]) * i / length)
            b = int(start[2] + (end[2] - start[2]) * i / length)
            result += f"\033[38;2;{r};{g};{b}m{char}\033[0m"
        return result

    # ==============================
    # SIMBOL WARNA
    # ==============================
    @staticmethod
    def symbol_color(type_: str) -> str:
        color = Display.color_scheme.get(type_, Display.color_scheme["default"])[0]
        symbol = Display.symbols.get(type_, Display.symbols["default"])
        return f"\033[38;2;{color[0]};{color[1]};{color[2]}m{symbol}\033[0m"

    # ==============================
    # CETAK FORMAT RATA
    # ==============================
    @staticmethod
    def rata(type_: str, message: str) -> str:
        length = 8
        spaces = max(length - len(type_), 0)

        scheme = Display.color_scheme.get(type_, Display.color_scheme["default"])
        start, end = scheme

        symbol = Display.symbol_color(type_)
        label = Display.gradient(type_, start, end)
        value = Display.gradient(message, start, end)

        return f"{symbol} {label}{' ' * spaces}:: {value}"

    # ==============================
    # MENU PILIHAN
    # ==============================
    @staticmethod
    def menu(no, title, last=None):
        s = [180, 0, 255]
        e = [255, 0, 150]

        left = Display.gradient(f"-[{no}]", s, e)
        title = Display.gradient(title, s, e)

        if last is not None:
            print(f"{left} {title}\t{Display.gradient(str(last), s, e)}")
        else:
            print(f"{left} {title}")

    # ==============================
    # BANNER
    # ==============================
    @staticmethod
    def banner(author="iewil"):
        import os
        os.system("clear" if os.name == "posix" else "cls")

        # Garis atas
        Display.line()
        Display.cetak("AUTHOR", author)
        if Display.TITLE:
            Display.cetak("TITLE", Display.TITLE)

            # Gradient background merah, teks putih, penuh garis
            warning_text = "FREE SCRIPT NOT FOR SALE!"
            line_len = 45
            # hitung spasi kiri untuk center
            left_padding = (line_len - len(warning_text)) // 2
            right_padding = line_len - len(warning_text) - left_padding

            text = " " * left_padding + warning_text + " " * right_padding

            start_color = [255, 0, 0]   # merah terang
            end_color   = [128, 0, 0]   # merah gelap

            out = ""
            for i, char in enumerate(text):
                r = int(start_color[0] + (end_color[0]-start_color[0]) * i / len(text))
                g = int(start_color[1] + (end_color[1]-start_color[1]) * i / len(text))
                b = int(start_color[2] + (end_color[2]-start_color[2]) * i / len(text))
                out += f"\033[48;2;{r};{g};{b}m\033[38;2;255;255;255m{char}"  # teks putih
            out += "\033[0m"
            print(out)

        if Display.REGISTER:
            Display.cetak("REGISTER", Display.REGISTER)
        Display.line()

    # ==============================
    # CLEAR LINE
    # ==============================
    @staticmethod
    def clear_line():
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()

    # ==============================
    # CETAK
    # ==============================
    @staticmethod
    def cetak(key: str, val: str):
        print(Display.rata(key, val))

    # ==============================
    # TITLE BLOCK
    # ==============================
    @staticmethod
    def title(text: str):
        length = 45
        padded = text.upper().center(length)

        start = [0, 180, 0]
        end = [255, 255, 0]

        out = ""
        max_len = len(padded) - 1 or 1

        for i, char in enumerate(padded):
            ratio = i / max_len
            r = int(start[0] + (end[0] - start[0]) * ratio)
            g = int(start[1] + (end[1] - start[1]) * ratio)
            b = int(start[2] + (end[2] - start[2]) * ratio)

            out += f"\033[48;2;{r};{g};{b}m\033[38;2;0;0;0m{char}"

        print(out + "\033[0m")

    # ==============================
    # GARIS
    # ==============================
    @staticmethod
    def line(length: int = 45):
        print("\033[0m" + "─" * length)

    # ==============================
    # TABLE
    # ==============================
    @staticmethod
    def table(data: dict):
        for k, v in data.items():
            print(Display.rata(str(k), str(v)))

    # ==============================
    # SHORTCUT
    # ==============================
    @staticmethod
    def debug(msg: str):
        print(Display.rata("debug", msg))

    @staticmethod
    def info(msg: str):
        print(Display.rata("info", msg))

    @staticmethod
    def error(msg: str = ""):
        print(Display.rata("warning", msg))

    @staticmethod
    def sukses(msg: str, newline: bool = True):
        out = Display.rata("success", msg)
        print(out if newline else out, end="\n" if newline else "")

    # ==============================
    # INPUT BOX
    # ==============================
    @staticmethod
    def isi(msg: str):
        s = [180, 0, 255]
        e = [255, 0, 150]

        text = Display.gradient(f"[Input {msg}]", s, e)
        print(f"\033[38;2;{s[0]};{s[1]};{s[2]}m╭\033[0m{text}")
        print(f"\033[38;2;{s[0]};{s[1]};{s[2]}m╰\033[0m", end="")
        print(f"\033[38;2;{e[0]};{e[1]};{e[2]}m> \033[0m", end="")

    # ==============================
    # TIMER
    # ==============================
    @staticmethod
    def timer(seconds: int):
        spinner_chars = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']

        def _gradient_color(start_rgb, end_rgb, ratio):
            """Hitung warna RGB di antara start dan end berdasarkan ratio 0..1"""
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            return f"\033[38;2;{r};{g};{b}m"

        start_time = time.time()
        end_time = start_time + seconds
        i = 0  # frame counter

        while (remaining := end_time - time.time()) > 0:
            remaining_int = int(remaining)
            h, rem = divmod(remaining_int, 3600)
            m, s = divmod(rem, 60)
            time_str = f"{h:02d}:{m:02d}:{s:02d}"

            # Rainbow timer dengan shift = i → kelap-kelip / bergerak
            rainbow = ""
            length = len(time_str)
            for j, ch in enumerate(time_str):
                shift_pos = (j + i) % length
                ratio = shift_pos / max(length - 1, 1)
                color_code = _gradient_color([255, 50, 50], [50, 255, 100], ratio)
                rainbow += f"{color_code}{ch}\033[0m"

            # Spinner gradient bergerak
            spinner_ratio = ((i * 2) % len(spinner_chars)) / len(spinner_chars)
            sp_color = _gradient_color([0, 255, 255], [255, 0, 255], spinner_ratio)
            sp = f"{sp_color}{spinner_chars[i % len(spinner_chars)]}\033[0m"

            # Print line
            print(f"\r{sp} {rainbow}", end="", flush=True)

            time.sleep(0.05)
            i += 1

        # Clear line setelah selesai
        print("\r" + " " * (length + 2) + "\r", end="")
