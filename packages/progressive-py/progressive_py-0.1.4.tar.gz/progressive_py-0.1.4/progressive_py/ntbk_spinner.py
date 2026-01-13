import time, threading
from collections.abc import Iterable
from IPython.display import display, HTML, Javascript
from .utils import fast_unique_id
from .ntbk_progbar import NotebookProgressBar
import json

class NotebookDivSpinner:
    def __init__(self, args={}, **kwargs):
        self.args = args.copy() if args else {}
        self.args.update(kwargs)
        self.id = self.args.get('id', f"{fast_unique_id('py-prog-spin-')}")

        self.text = self.args.get("text", "Loading")
        self.final_text = self.args.get("final_text", f"{self.text}... Done!")
        self.spn_side = str(self.args.get("spin_side", "right")).lower()
        self.speed = float(self.args.get("speed", 1.0))
        assert self.speed > 0, "Speed must be greater than zero."
        self.refresh_interval = self.args.get('refresh', 0.05)
        self.running = False
        self.phase = 0
        self.last_switch = time.perf_counter()
        self._thread = None
        self.visible = True

        def listify(val):
            if isinstance(val, str): return [val]
            elif isinstance(val, Iterable): return list(val)
            return [str(val)]

        self.fg_text = listify(self.args.get("fg_text", "#6e6efc"))
        self.bg_text = listify(self.args.get("bg_text", "transparent"))
        self.clr_interval = self._parse_intervals(self.args.get("clr_interval", [0.5]))

        def css_inline(css):
            if isinstance(css, dict):
                return "; ".join(f"{k}: {v}" for k, v in css.items())
            return css or ""

        spinner_args = self.args.get('spinner', {})
        ####################################
        # Spinner arg have form 
        # [
        #  spinner : {
        #       spinner_html: "spinner html single, can be svg block."
        #       others...
        #       }
        # ]
        ####################################
        self.animation = spinner_args.get('animation', {
            f"spin {1/self.speed}s linear infinite":
            "0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }"
        })

        self.animation_style = list(self.animation.keys())[0]
        self.animation_name = self.animation_style.split(' ')[0]
        self.animation_code = self.animation[self.animation_style]

        self.container_css = css_inline(self.args.get('container_css', """
            font-family: monospace;
            font-size: 16px;
            padding: 6px 14px;
            border-radius: 6px;
            display: inline-flex;
            align-items: center;
            user-select: none;
            transition: background-color 0.5s, color 0.5s;
        """))

        fg_spn = self._get_from_cycle(self.fg_text)
        bg_spn = self._get_from_cycle(self.bg_text)
        self.spinner_css = css_inline(spinner_args.get('spinner_css', f"""
            display: inline-block;
            vertical-align: middle;
            transition: border-color 0.5s;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            border: 4px solid {bg_spn};
            border-top: 4px solid {fg_spn};
            animation: {self.animation_style};
        """))
        self.add_css = self.args.get("add_css", '')

        self.text_css = css_inline(spinner_args.get('text_css', 'margin:10px'))
        self.final_css = css_inline(spinner_args.get('final_css', ''))
        self.spinner_html = ''

        self.running = False
        self.phase = 0
        self.last_switch = time.perf_counter()
        self._thread = None
        self.visible = True

    def _parse_intervals(self, val):
        if isinstance(val, (int, float, str)):
            return [float(val)]
        elif isinstance(val, Iterable):
            return [float(v) for v in val]
        return [0.5]

    def _get_from_cycle(self, seq):
        try:
            return seq[self.phase % len(seq)]
        except ZeroDivisionError:
            return seq[0] if seq else ""

    def update_colors_if_needed(self):
        now = time.perf_counter()
        interval = self.clr_interval[self.phase % len(self.clr_interval)]
        if now - self.last_switch >= interval:
            self.phase += 1
            self.last_switch = now
            return True
        return False

    def inject_static_css(self):
        layout = "row-reverse" if self.spn_side == "right" else "row"
        css = f"""
        <style>
        @keyframes {self.animation_name} {{
            {self.animation_code}
        }}
        #{self.id}-spinner {{
            animation: {self.animation_style};
            {self.spinner_css}
        }}
        #{self.id}-container {{
            flex-direction: {layout};
            {self.container_css}
        }}
        #{self.id}-text {{
            {self.text_css}
        }}
        {self.add_css}
        </style>
        """
        display(HTML(css))

    def build_html(self):
        fg_txt = self._get_from_cycle(self.fg_text)
        bg_txt = self._get_from_cycle(self.bg_text)

        spinner_html = self.args.get('spinner', {}).get('spinner_html')
        if not spinner_html:
            spinner_html = f""

        self.spinner_html = f"""
        <div id="{self.id}-container" style="background-color:{bg_txt};color:{fg_txt};">
            <div id="{self.id}-spinner">
                {spinner_html}
            </div>
            <div id="{self.id}-text">{self.text}</div>
        </div>
        """
        return self.spinner_html

    def _loop(self):
        self.inject_static_css()
        display(HTML(self.build_html()))
        while self.running:
            if self.update_colors_if_needed():
                fg_txt = self._get_from_cycle(self.fg_text)
                bg_txt = self._get_from_cycle(self.bg_text)

                js = f"""
                var el = document.getElementById("{self.id}-container");
                if (el) {{
                    el.style.backgroundColor = "{bg_txt}";
                    el.style.color = "{fg_txt}";
                }}
                """
                display(Javascript(js))
            time.sleep(self.refresh_interval)

    def start(self):
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        display(Javascript(f"""
            var elem = document.getElementById("{self.id}-container");
            if (elem) elem.remove();
        """))
        display(HTML(f"<div style='{self.final_css}'>{self.final_text}</div>"))

    def hide(self):
        self.visible = False
        display(Javascript(f"""
            var elem = document.getElementById("{self.id}-container");
            if (elem) elem.style.display = "none";
        """))

    def show(self):
        if not self.visible:
            self.visible = True
            display(Javascript(f"""
                var elem = document.getElementById("{self.id}-container");
                if (elem) elem.style.display = "inline-flex";
            """))

    def pause(self):
        self.running = False

    def resume(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def set_text(self, text):
        self.text = text
        safe_text = json.dumps(str(text))  # Safely quoted and escaped
        display(Javascript(f"""
            var el = document.getElementById("{self.id}-text");
            if (el) el.innerHTML = {safe_text};
        """))

    def __enter__(self): 
        self.start() 
        return self

    def __exit__(self, *a): 
        self.stop()



def work(pb, spn):
    for i in range(101):
        pb.update(i/100, i, 100)
        spn.set_text(pb.get_inline_html())
        time.sleep(0.025)


def run_spin_with_bar(
    spinner_args=None,
    bar_args=None,
    work = lambda pb, spn: work(pb, spn)
):
    """
    Spinner-as-parent wrapper that updates its text with an embedded progress bar.

    Usage:
    ------
    >>> from progressive_py.ntbk_spinner import run_spin_with_bar

    >>> def work(pb, spn):
    ...     for i in range(101):
    ...         pb.update(i/100, i, 100)
    ...         spn.set_text(pb.get_inline_html())
    ...         time.sleep(0.025)
    ...     
    
    >>> run_spinner_with_bar({}, {}, work) # Spinner's text arg and bar's line arg have no value now!
    
    Returns:
    tuple(ProgressBar, Spinner)
    """
    spinner_args = spinner_args or {"line": 0, "final_clear": False}
    bar_args = bar_args or {"txt_lf": "{percent:.0f}% "}
    
    spn = NotebookDivSpinner(spinner_args)
    pb = NotebookProgressBar(bar_args)
    pb.hide()

    try:
        spn.start()
        work(pb, spn)
        time.sleep(0.1)
    finally:
        spn.stop()
    return pb, spn