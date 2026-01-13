
import sys, time
from colorama import Fore, Style, init, Back
from .utils import (BarError,
                     BACKGROUND_COLOR_MAP, 
                     COLOR_MAP,
                     clear_line,
                     move_cursor_down,
                     move_cursor_up,
                     oup,
                     resolve_color)

init(autoreset=True)

class PBAR:
    def __init__(self, args: dict = {}):
        args = self.args = args or {}
        self.bar = args.get('bar', '█')
        self.space = args.get('space', ' ')
        self.space_clr = args.get('space_clr', '')
        self.head_clr = args.get('head_clr', '')
        self.colors = args.get('colors', [args.get('color', 'white')])
        self.paint = args.get('paint', 'bar')
        self.line_offset = args.get("line", 0)
        self.left_text = args.get('txt_lf', args.get('text_lf', 'Progress Bar'))
        self.right_text = args.get('txt_rt', args.get('text_rt', ''))
        self.fg = args.get('fg', ['white'])
        self.bg = args.get('bg', ['white'])
        self.length = args.get('length', 20)
        self.head = args.get('head', [' '])
        self._last_update = 0
        self._min_interval = args.get("freq", 0.1)
        self.progress = 0
        self.start_time = time.time()
        self.current_iter = 0
        self.total_iter = 0
        self.bar_str = ''
        self.is_visible = True

    def get_color(self, idx):
        color_name = self.colors[idx % len(self.colors)] if self.colors else "white"
        return resolve_color(color_name, 'fg')

    def get_text_color(self, which='left'):
        if self.fg:
            color = self.fg[0] if which == 'left' else self.fg[-1]
            return resolve_color(color, 'fg')
        return resolve_color("white", 'fg')


    def update(self, progress, current_iter=None, total_iter=None):
        now = time.time()
        if now - self._last_update < self._min_interval and progress < 1.0:
            return
        self._last_update = now
        self.progress = progress
        if current_iter is not None:
            self.current_iter = current_iter
        if total_iter is not None:
            self.total_iter = total_iter
        self.build_output()
        if self.line_offset > 0:
            move_cursor_up(self.line_offset)
            clear_line()
            if self.is_visible:
                self.display(self.bar_str)
            move_cursor_down(self.line_offset)
        else:
            if self.is_visible:
                self.display(self.bar_str)

    def process_text_templates(self, text, progress):
        eta_seconds = self.eta = self.calculate_eta_seconds()
        elapsed_seconds = self.elapsed = time.time() - self.start_time
        speed_value = self.calculate_speed_value()

        replacements = {
            'eta': self.format_time(eta_seconds),
            'speed': speed_value,
            'percent': progress * 100,
            'elapsed': self.format_time(elapsed_seconds),
            'iters_current': self.current_iter,
            'iters_total': self.total_iter,
            'iters': f"{self.current_iter}/{self.total_iter}"
        }

        # Check for custom hook in args
        custom_hooks = self.args.get('tokens', {})
        for key, func in custom_hooks.items():
            try:
                replacements[key] = func(self)
            except Exception as e:
                replacements[key] = f"<err:{e}>"

        try:
            return text.format(**replacements)
        except (KeyError, ValueError):
            for k, v in replacements.items():
                text = text.replace(f"{{{k}}}", str(v))
            return text
    def resolve_head(self, idx):
        return self.head[idx % len(self.head)]

    def resolve_head_color(self, idx):
        clr = self.head_clr
        if isinstance(clr, (list, tuple)):
            return resolve_color(clr[idx % len(clr)], 'fg')
        return resolve_color(clr, 'fg')

    def resolve_space_color(self, idx):
        clr = self.space_clr
        if isinstance(clr, (list, tuple)):
            return resolve_color(clr[idx % len(clr)], 'fg')
        return resolve_color(clr, 'fg')

    def build_output(self):
        reset = Style.RESET_ALL
        filled_len = int(self.length * self.progress)

        try:
            left_bg = resolve_color(self.bg[0], 'bg') if self.bg else ''
            right_bg = resolve_color(self.bg[1], 'bg') if self.bg else ''
        except:
            left_bg = right_bg = ''
        try:
            left_fg = resolve_color(self.fg[0], 'fg') if self.fg else ''
            right_fg = resolve_color(self.fg[1], 'fg') if self.fg else ''
        except:
            left_fg = right_fg = ''

        left_text = left_bg + left_fg + self.process_text_templates(self.left_text, self.progress) + reset
        right_text = right_bg + right_fg + self.process_text_templates(self.right_text, self.progress) + reset
        left_txt_color = self.get_text_color('left')
        right_txt_color = self.get_text_color('right')

        bar_seq = self.bar if isinstance(self.bar, (list, tuple)) else [self.bar]
        space_seq = self.space if isinstance(self.space, (list, tuple)) else [self.space]

        head = self.resolve_head(filled_len) if self.progress < 1.0 else ''
        head_color = self.resolve_head_color(filled_len)
        head_colored = head_color + head + reset if head else ''

        if self.paint == "bar-by-bar":
            bar_str = ''
            for i in range(self.length):
                if i < filled_len:
                    bar_str += self.get_color(i) + bar_seq[i % len(bar_seq)]
                    if i == filled_len - 1:
                        bar_str += head_colored
                else:
                    space_color = self.resolve_space_color(i)
                    space_char = space_seq[i % len(space_seq)]
                    bar_str += space_color + space_char + reset
            bar_str += Style.RESET_ALL
            output = f"\r{left_txt_color}{left_text}{reset}{bar_str}{reset}{right_txt_color}{right_text}{Style.RESET_ALL}"

        elif self.paint == "bar":
            color = self.get_color(filled_len - 1 if filled_len > 0 else 0)
            bar_str = ''.join(bar_seq[i % len(bar_seq)] for i in range(filled_len - 1)) if filled_len > 1 else ''
            if filled_len > 0:
                bar_str += bar_seq[(filled_len - 1) % len(bar_seq)]
            bar_str = color + bar_str + Style.RESET_ALL + head_colored
            for i in range(self.length - filled_len):
                space_color = self.resolve_space_color(filled_len + i)
                space_char = space_seq[(filled_len + i) % len(space_seq)]
                bar_str += space_color + space_char + reset
            output = f"\r{left_txt_color}{left_text}{reset}{bar_str}{reset}{right_txt_color}{right_text}{Style.RESET_ALL}"

        else:
            bar_str = ''.join(bar_seq[i % len(bar_seq)] for i in range(filled_len)) + head_colored
            for i in range(self.length - filled_len):
                space_color = self.resolve_space_color(filled_len + i)
                space_char = space_seq[(filled_len + i) % len(space_seq)]
                bar_str += space_color + space_char + reset
            output = f"\r{left_txt_color}{left_text}{reset}{bar_str}{reset}{right_txt_color}{right_text}{Style.RESET_ALL}"

        self.bar_str = output

    def display(self, bar_str):
        oup.write(bar_str)
        oup.flush()

    def calculate_eta_seconds(self):
        if self.current_iter <= 0 or self.total_iter <= 0:
            return float('inf')
        elapsed = time.time() - self.start_time
        smoothed_iter = max(self.current_iter, 1)
        avg_time = elapsed / smoothed_iter
        return avg_time * (self.total_iter - self.current_iter)

    def calculate_speed_value(self):
        elapsed = max(time.time() - self.start_time, 1e-9)
        current_iter = self.current_iter
        return current_iter / elapsed

    def format_time(self, seconds):
        if seconds == float('inf'):
            return "∞"
        mm, ss = divmod(int(seconds), 60)
        hh, mm = divmod(mm, 60)
        return f"{hh:02d}:{mm:02d}:{ss:02d}" if hh else f"{mm:02d}:{ss:02d}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        oup.write('\r')
        oup.flush()
        return False
    def hide(self):
        """Hides the progress bar."""
        if self.line_offset > 0:
            move_cursor_up(self.line_offset)
            clear_line()
            move_cursor_down(self.line_offset)
        else:
            clear_line()
        self.is_visible = False
    def show(self):
        """Shows the progress bar."""
        self.is_visible = True
        self.display(self.bar_str)
class ProgressBar(PBAR):
    def __init__(self, args={}):
        super().__init__(args)
        self.last_update_time = 0
        self.min_update_interval = self._min_interval

    def update(self, progress, current_iter=None, total_iter=None):
        now = time.time()
        if (now - self.last_update_time > self.min_update_interval) or (progress == 1.0):
            super().update(progress, current_iter, total_iter)
            self.last_update_time = now

def nested_bar(main_bar, task_funcs: dict, delay=0.05, auto_arrangement = True):
    """
    Run multiple subtasks with individual progress bars and an overall parent bar.

    - main_bar: ProgressBar instance for overall progress.
    - task_funcs: dict of {task_name: [function, bar_args_dict]}
    - delay: sleep delay between task transitions.
    - auto_arrangement: If true, bars are placed automatically placed in sequence. If not provided, line argument should be passed in the arguments of all bars in nest for correct placement.

    **IMPORTANT:** `line` argument matters. It is crucial for stacking of bars. High value means uppermost line, and this is normally equal to the number of childs. Eg, if childs are 2, then pass parent bar as; Progressbar({'line':2}). 

    Usage:
    -------

    >>> from progressive_py.progress_bar import Progressbar, nested_bar, time
    >>> def task_1(bar):
    ...     for i in range(100):
    ...         time.sleep(0.01) # simulate work
    ...         bar.update(i/99, i+1, 100) # Update the bar.
    >>> def task_2(bar):
    ...     for i in range(50):
    ...         time.sleep(0.01) # simulate work
    ...         bar.update(i/49, i+1, 50) # Update the bar.
    >>> main = Progressbar({'line':2})
    >>> childs = {
    ...     "Task1":[task1, {"txt_lf":"Task1 {percent:.0f}%"}],
    ...     "Task2":[task2, {"txt_lf":"Task2 {percent:.0f}%"}]
    ... }
    >>> nested_bar(main, childs, auto_arrangement=True)
    

    **IMPORTANT NOTE:**  
    If `auto_arrangement=False`, you must specify the `line` argument explicitly for both parent and child bars.  
    - Avoid using the same `line` value for multiple bars to prevent them from overwriting each other.  
    - If you want to reserve vertical space without displaying all bars simultaneously, set all child bars to the same `line` value `n`, and set the parent bar's `line` value to `n+1`.
    """
    task_ids = list(task_funcs.keys())
    task_entries = list(task_funcs.values())

    # Validate all task entries are [function, args_dict]
    for task_name, entry in zip(task_ids, task_entries):
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError(f"Task '{task_name}' must be a list/tuple of (function, args_dict)")

    funcs = [entry[0] for entry in task_entries]
    bar_args = [entry[1] for entry in task_entries]
    
    if auto_arrangement:
        child_bars = [
            ProgressBar({**{'line': len(task_ids) - i - 1}, **bar_args[i]})
            for i in range(len(task_ids))
        ]
    else:
        child_bars = [
            ProgressBar(bar_args[i])
            for i in range(len(task_ids))
        ]
    print("\n")
    main_bar.update(0)

    for idx, (func, bar) in enumerate(zip(funcs, child_bars)):
        bar.update(0)
        func(bar)
        main_bar.update((idx + 1) / len(child_bars))
        time.sleep(delay)
def simple(iterable, args={}, **kwargs):
    """
    Simple generator for single progress bar. Use for iterables with known or given length.
    - iterable: iterable to wrap
    - args: dictionary of progress bar configuration (should include 'total' if len() not available)
    - kwargs: any overrides for args
    Usage:
    ------
    >>> from progressive_py.progress_bar import simple, time
    >>> for i in simple(range(50), txt_lf="Step {iters} [{percent:.0f}%]"):
    ... time.sleep(0.05)
    """
    args = {**(args or {}), **kwargs}
    if 'total' in args:
        total = int(args['total'])
    elif hasattr(iterable, '__len__'):
        total = len(iterable)
    else:
        raise BarError("❌ 'total' must be provided in args['total'] if the iterable has no length.")

    pb = ProgressBar(args)
    try:
        for i, item in enumerate(iterable, 1):
            progress = i / total if total else 0
            pb.update(progress, i, total)
            yield item
    finally:
        print()  # ensure progress bar ends cleanly on its own line
