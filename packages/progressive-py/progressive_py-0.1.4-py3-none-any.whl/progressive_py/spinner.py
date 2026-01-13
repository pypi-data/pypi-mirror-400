import sys, time, threading
from .utils import (BACKGROUND_COLOR_MAP, 
                     COLOR_MAP,
                     clear_line,
                     move_cursor_down,
                     move_cursor_up,
                     oup,
                     init,
                     Style,
                     resolve_color,
                     show_cursor,
                     hide_cursor)
from .progress_bar import ProgressBar
init(autoreset=True)
oup = sys.stdout
output_lock = threading.Lock()


class Spinner:
    def __init__(self, args = {}, **kwargs):
        self.args = args or {}
        self.args.update(kwargs)
        self.text = self.args.get("text","Loading")
        self.side = self.args.get("spn_side","right")
        self.line_offset = self.args.get("line", 0)
        self.spinner_seq = self.args.get("seq", ['|', '/', '-', '\\'])
        self.delay = self.args.get("interval", 0.05)
        self.idx = 0
        self.running = False
        self._thread = None
        self.color_phase = 0
        self.last_color_switch = time.perf_counter()
        self.final_text = self.args.get("final_text", self.text + '...Done!')
        self.final_clear = self.args.get("final_clear", True)

        self.fg_text = self.args.get("fg_text", ['white'])
        self.bg_text = self.args.get("bg_text", ['black'])
        
        # Default spinner colors = text colors if not provided
        self.fg_spnr = self.args.get("fg_spnr", self.fg_text)
        self.bg_spnr = self.args.get("bg_spnr", self.bg_text)
        
        self.clr_interval = self.args.get("clr_interval", [self.delay])
        self.spn_str = ''
        self.text_str = ''
        self.spn_char = ''
        self.show()

    def color_code(self, fg=None, bg=None):
        return resolve_color(fg, 'fg') + resolve_color(bg, 'bg')


    def update_colors_if_needed(self):
        now = time.perf_counter()
        interval = self.clr_interval[self.color_phase % len(self.clr_interval)]
        if now - self.last_color_switch >= interval:
            self.color_phase = (self.color_phase + 1) % max(len(self.fg_text), len(self.bg_text), len(self.fg_spnr), len(self.bg_spnr), len(self.clr_interval))
            self.last_color_switch = now

    def display(self):
        self.build_output()

        if not self.visible:
            return

        with output_lock:
            if self.line_offset > 0:
                move_cursor_up(self.line_offset)
                clear_line()
            else:
                oup.write('\r')
                clear_line()

            oup.write(self.spn_str)
            oup.flush()

            if self.line_offset > 0:
                move_cursor_down(self.line_offset)

    def build_output(self):
        self.update_colors_if_needed()
        phase = self.color_phase
        text_fg = self.fg_text[phase % len(self.fg_text)]
        text_bg = self.bg_text[phase % len(self.bg_text)]
        spnr_fg = self.fg_spnr[phase % len(self.fg_spnr)]
        spnr_bg = self.bg_spnr[phase % len(self.bg_spnr)]

        text_color = self.color_code(text_fg, text_bg)
        spinner_color = self.color_code(spnr_fg, spnr_bg)

        spinner_char = self.spinner_seq[self.idx % len(self.spinner_seq)]
        if self.side == 'right':
            output = f"{text_color}{self.text}{spinner_color}{spinner_char}{Style.RESET_ALL}"
        else:
            output = f"{spinner_color}{spinner_char}{text_color}{self.text}{Style.RESET_ALL}"
        self.spn_str = output

    def update(self):
        self.idx = (self.idx + 1) % len(self.spinner_seq)
        self.display()

    def _spin_loop(self):
        while self.running:
            self.update()
            time.sleep(self.delay)

    def start(self):
        if not self.running:
            hide_cursor()
            self.running = True
            self.last_color_switch = time.perf_counter()
            self._thread = threading.Thread(target=self._spin_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()
        with output_lock:
            if self.final_clear:
                if self.line_offset > 0:
                    move_cursor_up(self.line_offset)
                    clear_line()
                    move_cursor_down(self.line_offset)
                else:
                    clear_line()
                phase = self.color_phase % len(self.fg_text)
                text_color = self.color_code(
                    self.fg_text[phase % len(self.fg_text)],
                    self.bg_text[phase % len(self.bg_text)]
                )
                oup.write(f"{text_color}{self.final_text}{Style.RESET_ALL}\n")
            else:
                pass
        show_cursor()

    def pause(self):
        self.running = False
        show_cursor()

    def hide(self):
        self.visible = False
        with output_lock:
            if self.line_offset > 0:
                move_cursor_up(self.line_offset)
                clear_line()
                move_cursor_down(self.line_offset)
            else:
                clear_line()

    def show(self):
        self.visible = True
        with output_lock:
            oup.write(self.spn_str)
            oup.flush()

    def resume(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._spin_loop, daemon=True)
            self._thread.start()
        hide_cursor()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


def spinning_work(args={}, work=lambda: time.sleep(10)):
    spinner = Spinner(args)
    spinner.start()
    try:
        otp = work(spinner)
    finally:
        spinner.stop()
    return spinner, otp

def work(pb, spn):
    total = 100
    for i in range(total + 1):
        pb.update(i / total, i + 1, total)
        spn.text = "Processing:" + pb.bar_str.replace('\r', '')
        time.sleep(0.05) # Simulate work

def run_spinner_with_bar(
    spinner_args=None,
    bar_args=None,
    work = lambda pb, spn: work(pb, spn)
):
    """
    Spinner-as-parent wrapper that updates its text with an embedded progress bar.

    Usage:
    ------
    >>> from progressive_py.spinner import run_spinner_with_bar

    >>> def work(pb, spn):
    ...     total = 100
    ...     for i in range(total + 1):
    ...         pb.update(i / total, i + 1, total)
    ...         spn.text = "Processing:" + pb.bar_str.replace('\\r', '')
    ...         time.sleep(0.05) # Simulate work
    
    >>> run_spinner_with_bar({}, {}, work) # Spinner's text arg and bar's line arg have no value now!
    
    Returns:
    tuple(ProgressBar, Spinner, output_work)
    """
    spinner_args = spinner_args or {"line": 0, "final_clear": False}
    bar_args = bar_args or {"txt_lf": "{percent:.0f}% "}
    
    spn = Spinner(spinner_args)
    pb = ProgressBar(bar_args)
    pb.hide()

    try:
        spn.start()
        otp = work(pb, spn)
        time.sleep(0.1)
    finally:
        spn.stop()
    return pb, spn, otp