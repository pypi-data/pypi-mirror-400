import threading, time
from colorama import Style, Fore, Back, init
import sys
import random, uuid

def rgb_fg(r, g, b): return f"\x1b[38;2;{r};{g};{b}m"
def rgb_bg(r, g, b): return f"\x1b[48;2;{r};{g};{b}m"

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(*rgb)

def resolve_color(color_name, mode='fg'):
    if color_name.startswith('#') and len(color_name) == 7:
        r, g, b = hex_to_rgb(color_name)
        return rgb_fg(r, g, b) if mode == 'fg' else rgb_bg(r, g, b)
    return (COLOR_MAP if mode == 'fg' else BACKGROUND_COLOR_MAP).get(color_name.lower(), '')
def gradient_colors(start_color, end_color, steps):
    start_rgb = hex_to_rgb(start_color)
    end_rgb = hex_to_rgb(end_color)
    colors = []

    if steps == 1:
        # If only 1 step, just return start color
        return [start_color]

    for i in range(steps):
        interp = [
            round(start_rgb[j] + (end_rgb[j] - start_rgb[j]) * i / (steps - 1))
            for j in range(3)
        ]
        # Clamp values between 0-255 just in case
        interp = [max(0, min(255, c)) for c in interp]
        colors.append(rgb_to_hex(tuple(interp)))
    return colors

oup = sys.stdout

def hide_cursor():
    oup.write('\033[?25l')
    oup.flush()

def show_cursor():
    oup.write('\033[?25h')
    oup.flush()

def move_cursor_up(n=1):
    """Move the terminal cursor **up** by n lines."""
    oup.write(f"\x1b[{n}A")
    oup.flush()

def move_cursor_down(n=1):
    """Move the terminal cursor **down** by n lines."""
    oup.write(f"\x1b[{n}B")
    oup.flush()

def clear_line():
    """Clear the current terminal line and move cursor to the beginning."""
    oup.write("\x1b[2K\r")
    oup.flush()


COLOR_MAP = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "bright-black": Style.BRIGHT + Fore.BLACK,
    "bright-red": Style.BRIGHT + Fore.RED,
    "bright-green": Style.BRIGHT + Fore.GREEN,
    "bright-yellow": Style.BRIGHT + Fore.YELLOW,
    "bright-blue": Style.BRIGHT + Fore.BLUE,
    "bright-magenta": Style.BRIGHT + Fore.MAGENTA,
    "bright-cyan": Style.BRIGHT + Fore.CYAN,
    "bright-white": Style.BRIGHT + Fore.WHITE,
    "dim-black": Style.DIM + Fore.BLACK,
    "dim-red": Style.DIM + Fore.RED,
    "dim-green": Style.DIM + Fore.GREEN,
    "dim-yellow": Style.DIM + Fore.YELLOW,
    "dim-blue": Style.DIM + Fore.BLUE,
    "dim-magenta": Style.DIM + Fore.MAGENTA,
    "dim-cyan": Style.DIM + Fore.CYAN,
    "dim-white": Style.DIM + Fore.WHITE,
    "reset": Style.RESET_ALL
}


BACKGROUND_COLOR_MAP = {
    "black": Back.BLACK,
    "red": Back.RED,
    "green": Back.GREEN,
    "yellow": Back.YELLOW,
    "blue": Back.BLUE,
    "magenta": Back.MAGENTA,
    "cyan": Back.CYAN,
    "white": Back.WHITE,
    "bright-black": Style.BRIGHT + Back.BLACK,
    "bright-red": Style.BRIGHT + Back.RED,
    "bright-green": Style.BRIGHT + Back.GREEN,
    "bright-yellow": Style.BRIGHT + Back.YELLOW,
    "bright-blue": Style.BRIGHT + Back.BLUE,
    "bright-magenta": Style.BRIGHT + Back.MAGENTA,
    "bright-cyan": Style.BRIGHT + Back.CYAN,
    "bright-white": Style.BRIGHT + Back.WHITE,
    "dim-black": Style.DIM + Back.BLACK,
    "dim-red": Style.DIM + Back.RED,
    "dim-green": Style.DIM + Back.GREEN,
    "dim-yellow": Style.DIM + Back.YELLOW,
    "dim-blue": Style.DIM + Back.BLUE,
    "dim-magenta": Style.DIM + Back.MAGENTA,
    "dim-cyan": Style.DIM + Back.CYAN,
    "dim-white": Style.DIM + Back.WHITE,
    "reset": Style.RESET_ALL
}

class BarError(Exception):
    def __init__(self, msg, *args):
        super().__init__(msg, *args)
        self.msg = msg

class BarThreadManager:
    def __init__(self, thread_tasks: dict):
        """
        MultiBarThreadManager — Manages and runs multiple progress bars concurrently using threads.

        Requires a task dictionary in the form:
        >>> thread_tasks = {
        ...     "thread_name": [bar_instance, bar_task_function],
        ... }

        Where `bar_task_function` is defined as:
        >>> def task(bar, pause_event, stop_check, cool_down=0.05):
        ...     total = 100 # Your Total
        ...     for i in range(total + 1):
        ...         if stop_check():
        ...             break
        ...         pause_event.wait()  # Pause support
        ...         # Do any work here
        ...         time.sleep(cool_down)  # Cool down between updates
        ...         bar.update(i / total, i, total)

        --- Terminal Example ---
        >>> from progressive_py.progress_bar import ProgressBar
        >>> from progressive_py.utils import BarThreadManager
        >>> import time

        >>> def example_task(bar, pause_event, stop_check, cool_down=0.05):
        ...     total = 100
        ...     for i in range(total):
        ...         if stop_check():
        ...             break
        ...         pause_event.wait()
        ...         time.sleep(cool_down)
        ...         bar.update(i / (total - 1), i + 1, total)

        >>> bar1 = ProgressBar({'txt_lf': '🚀 Task 1 {percent:.0f}% {eta} {elapsed}', 'line': 1})
        >>> bar2 = ProgressBar({'txt_lf': '🔧 Task 2 {percent:.0f}% {eta} {elapsed}', 'line': 0})

        >>> tasks = {
        ...     "task1": [bar1, example_task],
        ...     "task2": [bar2, example_task],
        ... }

        >>> manager = BarThreadManager(tasks)
        >>> manager.start_all(cool_down=0.02)
        >>> manager.wait_all()
        >>> time.sleep(0.1)
        >>> print("\\n✅ All tasks completed.")

        --- Notebook Usage ---
        Use `NotebookProgressBar` instead of `ProgressBar`. The structure and task function remain the same.
        The `line` parameter is not needed for notebook bars.
        """


        self.tasks = thread_tasks
        self.threads = {}
        self.status = {}
        self.pause_flags = {}
        self.stop_flags = {}
        self.cool_downs = {}

        for name in thread_tasks:
            self.status[name] = "initialized"
            self.pause_flags[name] = threading.Event()
            self.pause_flags[name].set()  # Not paused by default
            self.stop_flags[name] = False
            self.cool_downs[name] = 0.05  # default cool down

    def start(self, name, cool_down=0.05):
        if name not in self.tasks:
            raise ValueError(f"Thread '{name}' not found.")
        if self.status[name] == "running":
            return

        self.cool_downs[name] = cool_down
        bar, func = self.tasks[name]

        def runner():
            self.status[name] = "running"
            self.stop_flags[name] = False
            self.pause_flags[name].set()
            func(bar, self.pause_flags[name], lambda: self.stop_flags[name], self.cool_downs[name])
            self.status[name] = "completed"

        thread = threading.Thread(target=runner, name=name)
        self.threads[name] = thread
        thread.start()

    def pause(self, name):
        if name in self.pause_flags:
            self.pause_flags[name].clear()
            self.status[name] = "paused"

    def resume(self, name):
        if name in self.pause_flags:
            self.pause_flags[name].set()
            self.status[name] = "running"

    def stop(self, name):
        if name in self.stop_flags:
            self.stop_flags[name] = True
            self.status[name] = "stopped"

    def restart(self, name, cool_down=0.05):
        self.stop(name)
        time.sleep(0.1)
        self.start(name, cool_down)

    def wait(self, name):
        thread = self.threads.get(name)
        if thread:
            thread.join()

    def start_all(self, cool_down=0.05):
        for name in self.tasks:
            self.start(name, cool_down)

    def wait_all(self):
        for name in self.threads:
            self.wait(name)

    def pause_all(self):
        for name in self.tasks:
            self.pause(name)

    def resume_all(self):
        for name in self.tasks:
            self.resume(name)

    def stop_all(self):
        for name in self.tasks:
            self.stop(name)

    def restart_all(self, cool_down=0.05):
        for name in self.tasks:
            self.restart(name, cool_down)



def fast_unique_id(prefix = '', suffix = ''):
    frac_part = str(time.perf_counter()).split(".")[1]
    time_part = frac_part[-5:]
    rand_part = str(random.randint(100, 999))
    return str(prefix) + f"{time_part}{rand_part}" + str(suffix)