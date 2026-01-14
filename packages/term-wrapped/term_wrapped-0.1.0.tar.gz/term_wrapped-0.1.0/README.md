# terminal wrapped

<p align="center">
  <img src="screenshot1.png" alt="Screenshot 1" width="49%">
  <img src="screenshot2.png" alt="Screenshot 2" width="49%">
</p>

Reads in your shell's history file (for now just`~/.bash_history` or `~/.zsh_history`)
and makes a little command line "wrapped" in the terminal with various stats over
your commands (if there are no timestamps then it just uses all the data)

So far the stats are:

- Top commands
- Top cd targets + Top z targets (since lots of people use zoxide or something)
- Top git subcommands
- Day of week (Only if `export INC_APPEND_HISTORY=true` in zsh)
- Time of day
- Power stats
- Useless cat
- Typos
- Most piped commands
- Finale
  
You can run it with `uvx run terminal-wrapped` or `pipx run terminal-wrapped` if you have uv or pipx installed.

You can install it is `pip install terminal-wrapped` and then just run `terminal-wrapped` in your shell.
