"""Rich console instance for SignalPilot CLI"""

from rich.console import Console

# Single console instance used throughout the application
console = Console()

# Brand logo
LOGO = """   ┌───┐
   │ ↗ │  ╔═╗┬┌─┐┌┐┌┌─┐┬  ╔═╗┬┬  ┌─┐┌┬┐
   │▓▓▓│  ╚═╗││ ┬│││├─┤│  ╠═╝││  │ │ │
   │▓░░│  ╚═╝┴└─┘┘└┘┴ ┴┴─┘╩  ┴┴─┘└─┘ ┴
   └───┘  Your Trusted CoPilot for Data Analysis"""
