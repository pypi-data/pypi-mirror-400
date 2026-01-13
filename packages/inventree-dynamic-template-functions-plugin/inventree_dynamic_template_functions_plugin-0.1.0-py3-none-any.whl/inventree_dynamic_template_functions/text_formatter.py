from math import floor

import re
from typing import Sequence
from hyphen import Hyphenator
import itertools

hyphenator = Hyphenator("de_DE")

class DoesNotFitLabelError(Exception):
    """Exception raised for custom error scenarios.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)




from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def weasy_text_width_px(
    text: str,
    font_family: str = "Roboto",
    font_size_px: float = 16,
    font_weight: str | int = "normal",
    font_style: str = "normal",
) -> float:
    # Make the page huge so nothing wraps.
    css = f"""
    @page {{ size: 10000px 200px; margin: 0; }}
    html, body {{ margin: 0; padding: 0; }}
    .m {{
      font-family: {font_family};
      font-size: {font_size_px}px;
      font-weight: {font_weight};
      font-style: {font_style};
      white-space: pre;       /* preserve spaces, no wrapping */
      display: inline-block;  /* width = text advance */
    }}
    """
    html = f"<span class='m'>{_escape_html(text)}</span>"

    font_config = FontConfiguration()
    doc = HTML(string=html).render(stylesheets=[CSS(string=css)], font_config=font_config)

    page = doc.pages[0]
    # Traverse layout boxes to find the span
    box = _find_first_box_with_element_tag(page._page_box, "span")
    if box is None:
        raise RuntimeError("Could not find span box")
    return box.width

def _find_first_box_with_element_tag(box, tag: str):
    el = getattr(box, "element_tag", None)
    if el == tag:
        return box
    for child in getattr(box, "children", []) or []:
        found = _find_first_box_with_element_tag(child, tag)
        if found is not None:
            return found
    return None

def _escape_html(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&#39;"))




class TextFormatter:

    def __init__(self, text, font, font_size, max_width, preferred_width, max_lines, min_lines = 2):
        self.text = text
        self.font = font
        self.font_size = font_size
        self.max_width = max_width
        self.preferred_width = min(preferred_width, max_width)
        self.max_lines = max_lines
        self.min_lines = min_lines

    def format(self):
        # Easiest Case the whole text fits into the preferred width, just return it
        if self.calculate_width(self.text, self.font_size) < self.preferred_width:
            return ([self.text], self.font_size, self.min_lines)

        words = self.text.split(" ")
        syllables = [self._syllables_preserve_punctuation(w) for w in words]

        lines = 2
        font_size = self.font_size

        while True:
            words_with_size = list(map(lambda w: (w, True, self.calculate_width(w + " ", font_size)), words))

            syllables_with_size = []
            for word in syllables:
                for syllable in word:
                    syllables_with_size.append((syllable, False, self.calculate_width(syllable, font_size)))
                if len(syllables_with_size) > 0:
                    syllables_with_size[-1] = (syllables_with_size[-1][0], True, syllables_with_size[-1][2])

            print_debug(words_with_size)
            print_debug(syllables_with_size)

            distributed_words = self.partition_tuples(words_with_size, lines)
            distributed_syllables = self.partition_tuples(syllables_with_size, lines)

            print_debug(distributed_words)
            print_debug(distributed_syllables)

            word_lines = self.combine_parts(distributed_words)
            syllables_lines = self.combine_parts(distributed_syllables)

            words_width = max((self.calculate_width(line, font_size) for line in word_lines), default=0)
            syllables_width = max((self.calculate_width(line, font_size) for line in syllables_lines), default=0)

            # words_width = max(((sum(w[2] for w in line)) for line in distributed_words), default=0)
            # syllables_width = max(((sum(w[2] for w in line)) for line in distributed_syllables), default=0)

            print_debug(words_width)
            print_debug(syllables_width)

            # If two lines split by spaces fit into the preferred width, return those
            if words_width < self.preferred_width:

                # But if the hyphenation is a lot better use that
                if syllables_width < words_width * 0.3:
                    print_debug("syllables much better than words")
                    return (syllables_lines, font_size, max(self.min_lines, lines))

                # If not just return the space separated variant, as its
                print_debug("syllables not much better than words")
                return (word_lines, font_size, max(self.min_lines, lines))

            if words_width < self.max_width:
                print_debug("words fit into max width")
                return (word_lines, font_size, max(self.min_lines, lines))

            if syllables_width < self.max_width:
                print_debug("syllables fit into max width")
                return (syllables_lines, font_size, max(self.min_lines, lines))

            if lines >= self.max_lines:
                print_debug("line count exhausted, does not fit into max width")
                raise DoesNotFitLabelError("The given text does not fit into the given size constraints.")

            print_debug("increasing line count")
            lines += 1
            font_size = floor(floor((self.font_size * 2) / lines) / 2) * 2

    _LEADING_PUNCT_RE = re.compile(r'^[\(\[\{<"\'„“]+')
    _TRAILING_PUNCT_RE = re.compile(r'[\)\]\}>"\'„“.,;:!?…]+$')

    def _syllables_preserve_punctuation(self, word: str) -> list[str]:
        """
        Split `word` into (prefix_punct, core, suffix_punct), hyphenate `core`,
        then re-attach punctuation to the first/last syllable.
        """
        if not word:
            return [word]

        # Extract leading punctuation
        prefix = ""
        m = self._LEADING_PUNCT_RE.match(word)
        if m:
            prefix = m.group(0)
            word = word[len(prefix):]

        # Extract trailing punctuation
        suffix = ""
        m = self._TRAILING_PUNCT_RE.search(word)
        if m and m.end() == len(word):
            suffix = m.group(0)
            word = word[: -len(suffix)]

        core = word
        if not core:
            # Token is only punctuation; keep it as-is
            return [prefix + suffix]

        core_syllables = hyphenator.syllables(core)
        if not core_syllables:
            core_syllables = [core]

        # Re-attach punctuation
        core_syllables = list(core_syllables)
        core_syllables[0] = prefix + core_syllables[0]
        core_syllables[-1] = core_syllables[-1] + suffix
        return core_syllables

    def combine_parts(self, lines):
        output = []
        for line in lines:
            line_string = ""
            for part in line:
                line_string += part[0]
                if part[1]:
                    line_string += " "

            if line_string.endswith(" "):
                line_string = line_string[:-1]
            else:
                line_string += "-"

            output.append(line_string)
        return output

    def partition_tuples(self, data, m):
        n = len(data)
        if not data or m <= 0: return []
        if m >= n: return [[x] for x in data]

        # Extract values from the last element of the tuple for calculation
        values = [tup[-1] for tup in data]

        # Precompute prefix sums for O(1) range sum lookups
        prefix_sums = [0] * (n + 1)
        for i in range(n):
            prefix_sums[i + 1] = prefix_sums[i] + values[i]

        # table[i][j] = minimum "maximum sum" for first i elements into j parts
        table = [[0] * (m + 1) for _ in range(n + 1)]
        # solution[i][j] = split point to achieve that minimum
        solution = [[0] * (m + 1) for _ in range(n + 1)]

        # Base case: 1 partition (sum of all elements up to i)
        for i in range(1, n + 1):
            table[i][1] = prefix_sums[i]

        # Fill the DP table
        for j in range(2, m + 1):  # number of partitions
            for i in range(1, n + 1):  # number of elements
                table[i][j] = float('inf')
                for x in range(1, i):  # try every possible split point
                    # The cost is the max of (previous partitions' cost) vs (current partition sum)
                    current_partition_sum = prefix_sums[i] - prefix_sums[x]
                    cost = max(table[x][j - 1], current_partition_sum)

                    if cost <= table[i][j]:
                        table[i][j] = cost
                        solution[i][j] = x

        # Reconstruct the partitions using the stored split points
        def reconstruct(n_idx, m_idx):
            if m_idx == 1:
                return [data[:n_idx]]
            split_point = solution[n_idx][m_idx]
            return reconstruct(split_point, m_idx - 1) + [data[split_point:n_idx]]

        return reconstruct(n, m)

    def max_line_width(self, lines: Sequence[str], font_size) -> int:
        """
        Return the greatest rendered width among `lines` using `calculate_width`.
        """
        return max((self.calculate_width(s, font_size) for s in lines), default=0)

    def calculate_width(self, text, font_size):
        width = weasy_text_width_px(text, font_size_px=font_size)
        print(f"Calculated width: {width}, from text: '{text}', font size: {font_size}")
        return width

        # mreturn int(Text(font_size, text, self.font_path, font_size=font_size).render().size[0])


def print_debug(text):
    print(text)
    pass


def print_text(text):
    text_formatter = TextFormatter(text=text, font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size=9,
                                   preferred_width=70, max_width=100, max_lines=4)
    print(text)

    print("")

    for line in text_formatter.format():
        print(line)

    print("--------------------------------")


# if __name__ == "__main__":
#
#
#     print_text("Hello, world!")
#     print_text("Kaltgerätekabel")
#     print_text("Kaltgerätekabel (10m)")
#     print_text("Schuko: Kabel, Stecker")
#     print_text("Schuko: Kabel, Stecker, Schalter")
#     print_text("Schuko: Kabel, Stecker, Schalter, Kabel, Stecker")
#     print_text("Schuko: Kabel, Stecker, Schalter, Kabel, Stecker, Schalter, Kabel, Stecker, Stecker")
#     print_text("Mixed M3 Schrauben & Muttern (bitte nachfüllen)")
#     print_text("M3x45 Senkkopfschraube (DIN 7991, A2)")
#     print_text("M2.5x6 Zylinderkopfschraube Innensechskant (DIN 912)")
#     print_text("M4 Unterlegscheiben, Edelstahl, DIN 125-A")
#     print_text("M3 Muttern selbstsichernd (Nyloc) – 100 Stk.")
#     print_text("Holzschrauben 3.5x16 / 4x30 / 5x60 (Torx)")
#     print_text("Spanplattenschrauben, Senkkopf, TX20, verzinkt")
#     print_text("0603 1k Resistors (1%, 0.1W)")
#     print_text("0805 10µF X5R 16V KerKo (MLCC)")
#     print_text("SMD-LED 0603 grün (typ. 20mA)")
#     print_text("SMD-LED 0805 rot/gelb/grün (gemischt)")
#     print_text("Dioden 1N4148 / 1N4007 / SS14 (SMD)")
#     print_text("Z-Dioden 3V3 / 5V1 / 12V (THT & SMD)")
#     print_text("JST-XH 2.54mm Stecker + Buchse + Crimpkontakte")
#     print_text("Dupont Jumper Kabel (m/m, m/f, f/f) – Set")
#     print_text("Stiftleisten 2.54mm (gerade / gewinkelt / abbrechbar)")
#     print_text("Buchsenleisten 2.54mm (gerade / SMD)")
#     print_text("Schrumpfschlauch 2:1, 3mm/1.5mm, schwarz (Meterware)")
#     print_text("Kaptonband 10mm x 33m (Hitze/Isolierung)")
#     print_text("Isolierband (PVC), rot/gelb/grün/blau/schwarz")
#     print_text("Kabelbinder 100mm, natur + schwarz (UV)")
#     print_text("Acrylplatte 3mm (Reststücke, transparent/weiß/schwarz)")
#     print_text("Birke Multiplex 6mm (Laserzuschnitt, Reststücke)")
#     print_text("PLA Filament 1.75mm – Schwarz (0.5kg)")
#     print_text("PETG Filament 1.75mm – Transparent (1kg)")
#     print_text("Nozzles 0.4mm/0.6mm/0.8mm + Silikonsocken")
#     print_text("Lötkolbenspitzen T12-BC2, T12-K, T12-I (wechseln/putzen)")
#     print_text("Lötzinn Sn60Pb40 0.7mm + Flussmittelkern")
#     print_text("Entlötlitze 2.5mm / 5mm, Entlötpumpe, Flux Pen (No-Clean)")
#     print_text("IPA Isopropanol 99.9% – Platinen/Nozzle-Reinigung")
#     print_text("Sicherungen 5x20mm: T1A, T2A, F500mA (sortiert)")
#     print_text("Netzteil 12V 5A (Hohlstecker 5.5/2.1) + Adapter")
#     print_text("USB-C PD Trigger Board (5V/9V/12V/15V/20V)")
#     print_text("ESP32 DevKitC (WROOM-32) + Stiftleisten (2x19)")
#     print_text("Raspberry Pi Pico W – WiFi, Headers, Debug-Kabel")
#     print_text("Arduino Nano (Clone) – CH340, Mini-USB Kabel")
#     print_text("MOSFET IRLZ44N / AO3400A (Logic-Level, N-Kanal)")
#     print_text("OpAmp LM358 / TL072, NE555, 74HC595, MCP3008 (gemischt)")
#     print_text("SRD-05VDC-SL-C (5V) + Sockel + Freilaufdiode")
#     print_text("Steckbrett 830 Tie-Points + Jumper-Set + Krokoklemmen")
#     print_text("Schraubendreher-Bits PH0/PH1/PH2, PZ1/PZ2, T6–T30, HEX 1.5–6mm")
#     print_text("Bananenstecker 4mm -> Krokoklemme / Prüfspitze / Dupont")
#     print_text("„Kleinteile gemischt“ (bitte NICHT hier reinwerfen...)")
#     print_text("\"Kleinteile gemischt\" (bitte NICHT hier reinwerfen...)")
#     print_text("STM32F103C8T6 (LQFP-48) + ST-LINK/V2 Clone")
#     print_text("ATmega328P-AU (TQFP-32) / ATmega328P-PU (DIP-28)")
#     print_text("ESP32-WROOM-32E-N4 / ESP32-S3-WROOM-1-N8R2")
#     print_text("CH340G + USB Micro-B Buchse (U2/U3 Ersatz)")
#     print_text("AMS1117-3.3 (SOT-223) / LM2596S-ADJ (TO-263)")
#     print_text("MCP3008-I/P (DIP) + MCP3008T-I/SL (SOIC)")
#     print_text("74HC595N / SN74HC595DR / 74LVC245APW (SOIC/TSSOP)")
#     print_text("NEO-6M-0-001 GPS Modul (u-blox) + Antenne u.FL")
#     print_text("BME280 (Bosch) / BMP280 / SHT31-D (I2C, Breakout)")
#     print_text("LM358DR / TL072CP / OPA2134PA (Audio/OpAmp gemischt)")
#     print_text("IRLZ44NPBF / IRLB8721PBF / AO3400A (MOSFET N-Kanal)")
#     print_text("SS34 / SS54 / B5819W / MBR20100CT (Schottky & Doppeldiode)")
#     print_text("CR2032-Halter Keystone 3000 + CR2032 (Panasonic)")
#     print_text("DS18B20+ (TO-92) / DS18B20Z (SMD) 1-Wire Sensor")
#     print_text("WS2812B-2020 / SK6812MINI-E / APA102C (Addressable LEDs)")
#     print_text("2N7002K,215 / BSS138 / BS170 (Level-Shifter & MOSFET klein)")
#     print_text("LM1117IMPX-3.3/NOPB (Reel) – P/N 926-LM1117IMPX33")
#     print_text("Mouser 595-NE555P / DigiKey 296-1602-5-ND (Beispiel-SKUs)")
#     print_text("EAN 4260123456789 / UPC 012345678905 (Barcode-Nummern)")
#     print_text("P/N: RFM69HCW-868S2 + PCB Rev.A3 (2024-11-07)")
#     print_text("A-1234_B-56/C78 (Rev2.1) [Prototype] {DoNotMix}")
#     print_text("CUI PJ-102AH DC Jack 5.5x2.1mm / Kycon KLDX-0202-A")
#     print_text("TE 1-2834010-1 / JST B2B-XH-A (LF)(SN) / Molex 22-23-2021")
#     print_text("A000066 (Arduino Uno R3) + A000073 (Mega 2560)")
#     print_text("FT232RL-REEL / CP2102N-A02-GQFN24R (USB-UART)")
#     print_text("NCP1117ST33T3G / AP2112K-3.3TRG1 (LDOs)")
#     print_text("MP1584EN-LF-Z / SY8208B / TPS5430DDAR (Buck-Regler)")
#     print_text("74HC14D,652 / 74HCT125D / 74HC00D (NXP/ON Codes)")
#     print_text("Kondensator: GRM188R61E106KA73D (MLCC 10µF 25V 0603)")
#     print_text("Widerstand: RC0603FR-071KL (1k 1% 0603) / ERJ-3EKF1001V")
#     print_text("Diode: SSM3J355R,LF / BAT54S (SOT-23) / BAV99 (SOT-23)")
#     print_text("Stecker: GX12-4 Aviation Connector (Male/Female) + Kabel")
#     print_text("Sicherung: 0034.3126 (Littelfuse) 5x20 T2A 250V")
#     print_text("LongTokenTest: QFN48_STM32G0B1KET6TR_2025-12_BATCH#A1B2C3D4E5")