# Set locale FIRST before importing anything else
import os
import locale

# Set environment variable for locale (affects child processes and some libraries)
os.environ['LC_NUMERIC'] = 'C'

try:
    locale.setlocale(locale.LC_NUMERIC, 'C')  # Ensure decimal point is '.'
except locale.Error:
    pass  # Fallback if 'C' locale is not available

from .core import main

if __name__ == "__main__":
    main()