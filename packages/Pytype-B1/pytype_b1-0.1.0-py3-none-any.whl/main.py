
import random
import time
import textwrap
import sys

try:
	import curses
except ImportError: 
	print("The curses module is required. On Windows: `pip install windows-curses`.")
	sys.exit(1)

from utils import choose_text, calc_wpm, calc_accuracy


def draw_text(stdscr, y: int, x: int, width: int, target: str, typed: str):
	"""Render the target text and typed overlay with simple coloring."""
	lines = textwrap.wrap(target, width)
	typed_lines = textwrap.wrap(typed, width)

	for i, line in enumerate(lines):
		stdscr.addstr(y + i, x, line, curses.color_pair(0))

	pos = 0
	for i, tline in enumerate(lines):
		for j, ch in enumerate(tline):
			if pos >= len(typed):
				break
			typed_ch = typed[pos]
			correct = typed_ch == ch
			color = curses.color_pair(1) if correct else curses.color_pair(2)
			stdscr.addstr(y + i, x + j, typed_ch, color)
			pos += 1


def run_test(stdscr, duration=60):
	curses.curs_set(0)
	stdscr.nodelay(True)
	stdscr.timeout(50)

	curses.start_color()
	curses.use_default_colors()
	curses.init_pair(1, curses.COLOR_GREEN, -1)
	curses.init_pair(2, curses.COLOR_RED, -1)
	curses.init_pair(3, curses.COLOR_CYAN, -1)

	height, width = stdscr.getmaxyx()

	while True:
		stdscr.clear()
		title = "Terminal Typing Test (curses) - Press 's' to start, 'q' to quit"
		stdscr.addstr(1, max(0, (width - len(title)) // 2), title, curses.color_pair(3))
		stdscr.addstr(3, 2, "Press 's' to start a timed test (default 60s). Use Backspace to correct. Test ends when you finish typing the prompt or time runs out.")
		stdscr.addstr(4, 2, "Press 'q' to exit.")
		stdscr.refresh()

		ch = stdscr.getch()
		if ch in (ord("q"), ord("Q")):
			return
		if ch in (ord("s"), ord("S")):
			break


	target = choose_text()
	typed = ""
	start = time.time()
	elapsed = 0.0

	while elapsed < duration:
		elapsed = time.time() - start
		remaining = max(0, int(duration - elapsed))

		stdscr.erase()
		header = f"Time: {remaining}s | WPM: -- | Accuracy: --%"
		stdscr.addstr(0, 2, header, curses.color_pair(3))


		draw_text(stdscr, 2, 2, width - 4, target, typed)


		correct = sum(1 for i, ch in enumerate(typed) if i < len(target) and ch == target[i])
		total = len(typed)
		wpm = calc_wpm(total, elapsed) if elapsed > 0 else 0.0
		acc = calc_accuracy(correct, total)

		stats = f"WPM: {wpm:.1f} | Accuracy: {acc:.1f}% | Typed: {total}"
		stdscr.addstr(height - 2, 2, stats)

		stdscr.refresh()

		try:
			key = stdscr.getch()
		except KeyboardInterrupt:
			return

		if key == -1:
			continue
		if key in (27, ord("q")):
			return
		if key in (curses.KEY_BACKSPACE, 127, 8):
			typed = typed[:-1]
			continue
		if key in (10, 13): 
			break
		if 0 <= key <= 255:

			ch = chr(key)
			if ch.isprintable():
				typed += ch
				
				if len(typed) >= len(target):
					break

	final_elapsed = time.time() - start
	correct = sum(1 for i, ch in enumerate(typed) if i < len(target) and ch == target[i])
	total = len(typed)
	final_wpm = calc_wpm(total, final_elapsed)
	final_acc = calc_accuracy(correct, total)

	stdscr.nodelay(False)
	stdscr.erase()
	stdscr.addstr(2, 2, "Time's up! Results:", curses.A_BOLD)
	stdscr.addstr(4, 4, f"Elapsed: {final_elapsed:.1f}s")
	stdscr.addstr(5, 4, f"Typed: {total}")
	stdscr.addstr(6, 4, f"Correct chars: {correct}")
	stdscr.addstr(7, 4, f"WPM: {final_wpm:.1f}")
	stdscr.addstr(8, 4, f"Accuracy: {final_acc:.1f}%")

	stdscr.addstr(10, 2, "Press 'r' to retry, or 'q' to quit.")
	stdscr.refresh()

	while True:
		key = stdscr.getch()
		if key in (ord("q"), ord("Q")):
			return
		if key in (ord("r"), ord("R")):
			run_test(stdscr, duration)
			return


def main():
	try:
		curses.wrapper(run_test)
	except Exception as exc: 
		print("An error occurred:", exc)


if __name__ == "__main__":
	main()

