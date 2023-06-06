import subprocess
import curses
import fcntl
import sys

LOCK_FILE = "/tmp/redcli.lock"


def main():
    # Try to acquire the lock file
    lock_file = open(LOCK_FILE, 'w')
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # Another instance is already running
        print("Another instance of redcli is already running.")
        sys.exit(1)

    # Initialize the Redshift state
    redshift_on = True
    color_temperature = 3500

    # Initialize curses
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)

    # Define the ASCII geometry
    ascii_geometry = [
        "┌────────────────────────────────────────┐",
        "│            Redshift Control            │",
        "├────────────────────────────────────────┤",
        "│   Color Temperature:       [ ] K      │",
        "│                                        │",
        "│           [Toggle]    [Quit]           │",
        "└────────────────────────────────────────┘"
    ]

    # Set initial cursor position
    cursor_x = 7
    cursor_y = 3

    # Display the initial status
    display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)

    while True:
        # Refresh the screen
        stdscr.refresh()

        # Wait for user input
        user_input = stdscr.get_wch()

        if user_input == 't':
            redshift_on = not redshift_on
            apply_color_temperature(redshift_on, color_temperature)
            display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)
        elif user_input == 'q':
            quit_program(stdscr, redshift_on)
            break
        elif user_input in ('+', '='):
            color_temperature += 100
            color_temperature = min(6000, color_temperature)
            apply_color_temperature(redshift_on, color_temperature)
            display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)
        elif user_input in ('-', '_'):
            color_temperature -= 100
            color_temperature = max(1200, color_temperature)
            apply_color_temperature(redshift_on, color_temperature)
            display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)
        elif user_input == 'j':
            color_temperature -= 100
            color_temperature = max(1200, color_temperature)
            apply_color_temperature(redshift_on, color_temperature)
            display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)
        elif user_input == 'k':
            color_temperature += 100
            color_temperature = min(6000, color_temperature)
            apply_color_temperature(redshift_on, color_temperature)
            display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y)

    # Release the lock file
    fcntl.lockf(lock_file, fcntl.LOCK_UN)
    lock_file.close()


def display_status(stdscr, ascii_geometry, redshift_on, color_temperature, cursor_x, cursor_y):
    # Clear the screen
    stdscr.clear()

    # Display ASCII geometry
    for i, line in enumerate(ascii_geometry):
        stdscr.addstr(i, 0, line)

    # Display the current status
    stdscr.addstr(2, 29, "Redshift is " + ("on " if redshift_on else "off"))
    stdscr.addstr(3, 23, "Color temperature: {0: >4} K".format(color_temperature))

    # Draw toggle button
    toggle_button = "[x]" if redshift_on else "[ ]"
    if cursor_x == 22:
        stdscr.addstr(3, 22, toggle_button, curses.A_REVERSE)
    else:
        stdscr.addstr(3, 22, toggle_button)

    # Move the cursor to its current position
    stdscr.move(cursor_y, cursor_x)


def apply_color_temperature(redshift_on, color_temperature):
    if redshift_on:
        subprocess.run(['redshift', '-P', '-O', str(color_temperature)])
    else:
        subprocess.run(['redshift', '-x'])


def quit_program(stdscr, redshift_on):
    if redshift_on:
        subprocess.run(['redshift', '-x'])
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()


if __name__ == "__main__":
    main()
#With lock 