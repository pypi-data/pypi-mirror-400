from IPython.display import display, HTML, update_display
import uuid
import time
from .utils import BarError, fast_unique_id
from datetime import timedelta

class Bar:
    def __init__(self, args:dict={}):
        self.args = args or {}
        self.id = self.args.get('id', fast_unique_id("py-prog-bar"))
        self.label = self.args.get('txt_lf', 'Progress')
        self.length = self.args.get('length', 40)
        self.bar = self.args.get('bar', ['█'])
        self.space = self.args.get('space', ' ')
        self.right_text = self.args.get('txt_rt', '')
        self.paint = self.args.get('paint', 'bar-by-bar')
        self.colors = self.args.get('colors', ['green'])
        self.bar_style = self.args.get('bar_style', '')
        self.space_style = self.args.get('space_style', 'color: #eee;')
        self.progressbar_style = self.args.get('progressbar_style', "font-family:monospace;width:100%;background:transparent;border-radius:5px;overflow:hidden")
        self.add_css = self.args.get('add_css','')
        self._id = str(uuid.uuid4())
        self._last_percent = -1
        self.current_iter = 0
        self.total_iter = 1
        self.progress = 0
        self.text_color = self.args.get('text_color', '#eee')
        self.start_time = time.time()
        self.last_update_time = self.start_time
        self.last_progress = 0
        self.avg_speed = None
        self.bar_html = ''
        self.visible = True
        self.bar_segments = ''
        self.display_handle = display(HTML(self.render(0)), display_id=self._id)
        eta_seconds = self.eta = self.calculate_eta_seconds()
        elapsed_seconds = self.elapsed = time.time() - self.start_time

    def get_color(self, idx:int):
        # Accepts color names or hex codes
        if isinstance(self.colors, list):
            return self.colors[idx % len(self.colors)]
        return self.colors[0]

    def calculate_eta(self):
        if self.current_iter <= 0 or self.total_iter <= 0:
            return "∞"
        
        elapsed = max(time.time() - self.start_time, 1e-9)
        remaining_time = (elapsed / self.current_iter) * (self.total_iter - self.current_iter)
        
        if remaining_time <= 0:
            return "∞"
        
        # Using timedelta for robust formatting
        delta = timedelta(seconds=int(remaining_time))
        if delta.total_seconds() > 3600:
            return str(delta).split('.')[0]  # HH:MM:SS
        else:
            mm, ss = divmod(int(remaining_time), 60)
            return f"{mm:02d}:{ss:02d}"  # MM:SS
    
    def calculate_speed(self):
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return "∞"
        speed = self.current_iter / elapsed
        return f"{speed:.2f}/s"

    def process_text_templates(self, text:str, progress:float):
        """
        Replace tokens in the provided text with current progress stats.

        Supported tokens:
        - {eta}, {elapsed}, {speed}, {percent}, {iters}, {iters_current}, {iters_total}
        - And any custom token provided in args['tokens'].

        Parameters:
        -----------
        text : str
            The string template to format.
        progress : float
            Progress value between 0 and 1.

        Returns:
        --------
        str
            Text with tokens replaced by current progress values.
        """
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
    
    def calculate_eta_seconds(self):
        if self.current_iter <= 0 or self.total_iter <= 0:
            return float('inf')
        
        # Time elapsed
        elapsed = time.time() - self.start_time
        
        # Add a tiny warm-up buffer to prevent early-zero
        smoothed_iter = abs(max(self.current_iter, 1))  # Acts like a damping factor
        
        avg_time_per_iter = elapsed / smoothed_iter
        remaining_iters = self.total_iter - self.current_iter
        
        eta = avg_time_per_iter * remaining_iters
        return eta

    def calculate_speed_value(self):
        elapsed = max(time.time() - self.start_time, 1e-9)
        return self.current_iter / elapsed

    def format_time(self, seconds):
        if seconds == float('inf'):
            return "∞"
        mm, ss = divmod(int(seconds), 60)
        hh, mm = divmod(mm, 60)
        if hh > 0:
            return f"{hh:02d}:{mm:02d}:{ss:02d}"
        return f"{mm:02d}:{ss:02d}"

    def render(self, progress):
        percent = int(progress * 100)
        filled_len = int(self.length * progress)
        bar_seq = self.bar if isinstance(self.bar, (list, tuple)) else [self.bar]

        label_color = self.text_color[0] if isinstance(self.text_color, (list, tuple)) else self.text_color
        right_color = self.text_color[1] if isinstance(self.text_color, (list, tuple)) else self.text_color

        processed_lf = self.process_text_templates(self.label, progress)
        processed_rt = self.process_text_templates(self.right_text, progress)

        if self.paint == "bar-by-bar":
            bar_html = ""
            for i in range(self.length):
                bar_char = bar_seq[i % len(bar_seq)]
                if i < filled_len:
                    bar_html += f'<span style="color:{self.get_color(i)};{self.bar_style}">{bar_char}</span>'
                else:
                    space_char = self.space[i % len(self.space)] if isinstance(self.space, (list, tuple)) else self.space
                    bar_html += f'<span style="{self.space_style}">{space_char}</span>'
            content = (
                f'<span style="color:{label_color}">{processed_lf} </span>'
                f'{bar_html}'
                f'<span style="color:{right_color}"> {processed_rt}</span>'
            )

        elif self.paint == "bar":
            color = self.get_color(filled_len)
            bar_html = ""
            for i in range(filled_len):
                bar_char = bar_seq[i % len(bar_seq)]
                bar_html += f'<span style="color:{color};{self.bar_style}">{bar_char}</span>'
            for i in range(self.length - filled_len):
                space_char = self.space[i % len(self.space)] if isinstance(self.space, (list, tuple)) else self.space
                bar_html += f'<span style="{self.space_style}">{space_char}</span>'
            content = (
                f'<span style="color:{label_color}">{processed_lf} </span>'
                f'{bar_html}'
                f'<span style="color:{right_color}"> {processed_rt}</span>'
            )

        elif self.paint == "progress-bar":
            bar_html = ""
            for i in range(filled_len):
                bar_char = bar_seq[i % len(bar_seq)]
                bar_html += bar_char
            for i in range(self.length - filled_len):
                space_char = self.space[i % len(self.space)] if isinstance(self.space, (list, tuple)) else self.space
                bar_html += space_char
            content = (
                f'<span style="{self.progressbar_style}">{processed_lf} {bar_html} {processed_rt}</span>'
            )

        else:
            # Fallback paint method
            bar_html = ""
            for i in range(filled_len):
                bar_char = bar_seq[i % len(bar_seq)]
                bar_html += bar_char
            for i in range(self.length - filled_len):
                space_char = self.space[i % len(self.space)] if isinstance(self.space, (list, tuple)) else self.space
                bar_html += f"<span style='{self.space_style}'>{space_char}</span>"
            content = (
                f'<span style="color:{label_color}">{processed_lf} </span><span style="{self.bar_style}">{bar_html}</span><span> {processed_rt}</span>'
            )
        self.bar_segments = content
        self.bar_html = f"""
        <style>
        {self.add_css}
        </style>
        <div style="{self.progressbar_style}" id='{self.id}'>
            {content}
        </div>
        """
        return self.bar_html

    def update(self, progress, current_iter=None, total_iter=None):
        """
        Update the progress bar in the notebook.

        Parameters:
        -----------
        progress : float
            A float between 0 and 1 indicating the current progress.
        current_iter : int, optional
            Current iteration count (used for speed/ETA calculation).
        total_iter : int, optional
            Total number of iterations.
        """
        percent = int(progress * 100)
        self.progress = progress
        self.bar_html = self.render(progress)
        if current_iter is not None:
            self.current_iter = current_iter
        if total_iter is not None:
            self.total_iter = total_iter
        if percent != self._last_percent or current_iter is not None:
            if self.visible:
                self.display_handle.update(HTML(self.bar_html))
            else:
                self.display_handle.update(HTML(""))
                
            self._last_percent = percent

    def get_inline_html(self):
        return ''.join(self.bar_segments)  # only the span parts

    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

def simple(iterable, total=None, args=None, **kwargs):
    """
    Simple generator for single progress bar. It is suggested to use this function for single bar.
    - iterable: any iterable instance. If it doesn't supports __len__ method,`total` must be provided.
    - args: arguments for progress bar.
    - kwargs: additional arguments to update the args.

    Usage:
    ------

    >>> from progressive_py.notebook_progress_bar import simple, time
    >>> for i in simple(range(100), txt_lf = "Processing {iters} ")
    ...     time.sleep(0.1)
    """
    args = args or {}
    args.update(dict(**kwargs))

    if total in args:
        total = int(args['total'])
    elif hasattr(iterable, '__len__'):
        total = len(iterable)
    else:
        raise BarError("❌ 'total' must be provided in args if the iterable has no length.")
    
    pb = NotebookProgressBar(args)

    for i, item in enumerate(iterable):
        pb.update((i + 1) / total, i + 1, total)
        yield item

def nested_bar(main_bar, task_funcs: dict, delay=0.05):
    """
    Run multiple subtasks with individual progress bars and an overall parent bar.

    - main_bar: ProgressBar instance for overall progress.
    - task_funcs: dict of {task_name: [function, bar_args_dict]}
    - delay: sleep delay between task transitions.

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
    >>> main = Progressbar()
    >>> childs = {
    ...     "Task1":[task1, {"txt_lf":"Task1 {percent:.0f}%"}],
    ...     "Task2":[task2, {"txt_lf":"Task2 {percent:.0f}%"}]
    ... }
    >>> nested_bar(main, childs)
    """
    task_ids = list(task_funcs.keys())
    task_entries = list(task_funcs.values())

    # Validate all task entries are [function, args_dict]
    for task_name, entry in zip(task_ids, task_entries):
        if not isinstance(entry, (list, tuple)) or len(entry) != 2:
            raise ValueError(f"Task '{task_name}' must be a list/tuple of (function, args_dict)")

    funcs = [entry[0] for entry in task_entries]
    bar_args = [entry[1] for entry in task_entries]
    
    child_bars = [
        NotebookProgressBar(bar_args[i])
        for i in range(len(task_ids))
    ]

    print("\n")
    main_bar.update(0, 0, len(child_bars))

    for idx, (func, bar) in enumerate(zip(funcs, child_bars)):
        bar.update(0, 0, 0)
        func(bar)
        main_bar.update((idx + 1) / len(child_bars), idx+1, len(child_bars))
        time.sleep(delay)

class NotebookProgressBar(Bar):
    """
    A progress bar class optimized for Jupyter notebooks with throttled update frequency
    and full HTML/CSS rendering capabilities.

    Parameters
    ----------
    args : dict, optional
        Configuration dictionary to customize the bar appearance and behavior:
        - txt_lf (str): Left-side text template (e.g., "{percent}%" or "{iters}").
        - txt_rf (str): Right-side text template (e.g., "ETA: {eta}").
        - bar (str or list): Characters used for the filled portion of the bar.
        - space (str): Character used to represent empty space.
        - paint (str): Painting style: "bar", "bar-by-bar", or "progress-bar".
        - colors (list): CSS color values for individual bar segments.
        - bar_style (str): Inline CSS style for each bar character.
        - space_style (str): CSS style for empty space segments.
        - progressbar_style (str): CSS style for the wrapper div.
        - add_css (str): Additional CSS (e.g., keyframes or `#{self.id}` rules).
        - text_color (str or list): Color(s) for left and right label text.
        - tokens (dict): Custom format hooks, e.g. `{spinner}`.
        - freq (float): Throttling update frequency in seconds. Default is 0.1.

    Attributes
    ----------
    current_iter : int
        The current iteration number.
    total_iter : int
        The total number of iterations expected.
    progress : float
        Current progress value in the range [0, 1].

    Example
    -------
    >>> from progressive_py.ntbk_progbar import NotebookProgressBar
    >>> from progressive_py.utils import gradient_colors
    >>> import time
    >>> 
    >>> pb = NotebookProgressBar({
    ...     'txt_lf': "Neon Progress {iters} | {percent:.0f}%",
    ...     'txt_rt': "| ETA {eta} | Elapsed {elapsed}",
    ...     'colors': gradient_colors('#00ff00', '#0000ff', 10) + gradient_colors('#0000ff', '#00ff00', 10),
    ...     'paint': 'bar-by-bar',
    ...     'length': 30,
    ...     'text_color': ['#efa', '#afe']
    ... })
    >>> 
    >>> total = 100
    >>> for i in range(total + 1):
    ...     pb.update(i / total, current_iter=i, total_iter=total)
    ...     time.sleep(0.03)
    >>> 
    >>> print("Progress Complete!")
    """
    def __init__(self, args={}, **kwargs):
        args = args or {}
        args.update(kwargs)
        super().__init__(args)
        self.last_update_time = 0
        self.min_update_interval = args.get('freq', 0.1)

    def update(self, progress, current_iter, total_iter):
        now = time.time()
        if (now - self.last_update_time > self.min_update_interval) or (progress == 1.0):
            super().update(progress, current_iter, total_iter)
            self.last_update_time = now
