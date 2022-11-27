from random import randrange
from colorama import Fore, Style
from dataclasses import dataclass

USABLE_FORE = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]


@dataclass
class SourceData:
    color: str
    cached_text: str
    line_stop: str


class LogPresenter:
    '''
    Log presenter is a log multiplexer to display logs from multiple sources at once to stdout.

    Example:
    ```
    p = LogPresenter() # New line is also the default
    with p:
        p.add('node1', 'Hello World\n My friend.')
        p.add('node2', 'Hell Web\n\n', line_stop='\n\n')
    ```

    The above will result in the following text being displayed to console.
    ```
    node1 | Hello World
    node2 | Hello Web
    node1 | My Friend.
    ```

    Lines will be printed to stdout after a newline is received. Text which is not followed by a newline will be cached until a newline is received. The final message of **"My friend"** shows that the cache will be dumped to console after the context manager calls the `__exit__` method.
    '''

    def __init__(self) -> None:
        # Making a copy of the fore colors so we can remove them inclemently from this copy to avoid overlap where possible.
        self._fore_options = USABLE_FORE[:]
        # Used to pad the source name so text is aligned
        self._max_width = 0

        self._data = {}

    def __enter__(self):
        return self

    def _select_color(self) -> str:
        '''
        This method handles color selection from the remaining `_fore_options` and removing of that color from the options. If the options are empty, it will be regenerated from `USABLE_FORE`.
        '''
        if len(self._fore_options) == 0:
            self._fore_options = USABLE_FORE[:]

        idx = randrange(len(self._fore_options))
        return self._fore_options.pop(idx)

    def _get_data(self, source: str, line_stop: str):
        if source in self._data:
            return self._data[source]

        new_data = SourceData(self._select_color(), '', line_stop)
        self._data[source] = new_data

        # Update the max width if applicable
        if len(source) > self._max_width:
            self._max_width = len(source)

        return new_data

    def add(self, source: str, text: str, line_stop='\n'):
        if len(text) == 0:
            return

        data = self._get_data(source, line_stop)
        split = text.split(data.line_stop)

        # If no line stop add text to cache and return
        if len(split) == 1:
            data.cached_text += text
            return

        # Only if there are new lines in input will we need to print (no newlines in cache)
        first_line = split.pop(0)
        last_line = split.pop() # This will be '' if `text` ends in a line stop

        # Add previous cached text if there is any
        if len(data.cached_text) != 0:
            first_line += data.cached_text

        self._print(source, first_line, data.color)
        data.cached_text = last_line

        # Print all other lines (don't have to deal with the cache now)
        for line in split:
            self._print(source, line, data.color)

    def _print(self, source: str, text: str, color: str, end='\n'):
        # Print source header
        print(f'{color}{source.rjust(self._max_width)} | {Style.RESET_ALL}', end='')
        # Print text without color
        print(text, end=end)
    
    def __exit__(self, exc_type, exc_value, traceback):
        # Flush all cached text
        for source, data in self._data.items():
            if len(data.cached_text) != 0:
                self._print(source, data.cached_text, data.color)
        
        # Reset the cache for reuse
        self._data = {}