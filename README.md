# errdoc

Paste an error, get a plain-English explanation and a suggested fix. Built on the [BharatCode](https://www.bharatcode.ai) model API (Qwen 3.8 27B).

errdoc is a tiny command-line tool for anyone who stares at stack traces: students, developers, anyone debugging at 1 AM. You give it an error message, a log file, or a piped crash - plus the code if you want - and it sends it to BharatCode for a plain-English explanation and a suggested fix. A `--hint` mode gives you a nudge instead of the answer, for when you want to learn.

No dependencies. Python 3.8+ is all you need.

## Setup

```bash
git clone https://github.com/WhitefistEmperor/errdoc.git
cd errdoc
export BHARATCODE_API_KEY=bc_live_your_key_here
```

Get a BharatCode API key at https://www.bharatcode.ai/account - free for verified students (10M tokens/day), or on any paid plan.

## Usage

```bash
# Diagnose an error directly
python3 errdoc.py "IndexError: list index out of range"

# From a log file
python3 errdoc.py --file crash.log

# Include the code that produced it
python3 errdoc.py --file crash.log --code app.py

# Pipe from another command
python3 manage.py test 2>&1 | python3 errdoc.py

# Tutor mode: a hint, not the answer
python3 errdoc.py --hint "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
```

## Example

Illustrative sample output, to show the format:

```
$ python3 errdoc.py "TypeError: can only concatenate str (not \"int\") to str"

## What happened
Python tried to join a string and a number with +, which it does not allow.

## Why it happened
The variable age holds an int, and the expression "Age: " + age mixes types.

## Fix
Convert the number first: "Age: " + str(age), or use an f-string: f"Age: {age}".

## Watch out
Input from input() or a CSV always arrives as a string - convert once, early.
```

## How it works

errdoc sends your error (and optional code) to BharatCode's OpenAI-compatible chat completions endpoint with a strict diagnostic prompt, and prints the answer. Your key stays in an environment variable or a local `.env` file (see `.env.example`) and is never sent anywhere except BharatCode's API.

Note on privacy: prompts on BharatCode's free/student tier may be logged by BharatCode for debugging and quality, per their privacy policy. Don't paste secrets, tokens or other people's private data into errdoc.

## Built for the BharatCode Build League

Entered in the BharatCode Build League (November 2026), Coding & developer tools direction. Built with AI assistance, with the organiser's permission. Votes and stars are part of the judging - if errdoc saved you a headache, a star helps.

## License

MIT - see [LICENSE](LICENSE).
