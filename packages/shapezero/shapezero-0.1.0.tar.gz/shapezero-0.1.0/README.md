# shapezero

Swiss army knife for AI developers.

```bash
pip install shapezero
```

## Why?

Because every AI project needs the same boring utilities:
- Cache LLM responses (stop burning money on duplicate calls)
- Parse messy outputs (extract JSON from markdown fences)
- Count tokens (will this fit in context?)
- Manage conversations (track message history)
- Build context (turn folders into prompts)

One import. Zero dependencies. Just works.

## Quick Start

```python
import shapezero as sz

# Cache responses
sz.cache.set("my prompt", "my response")
cached = sz.cache.get("my prompt")  # Returns "my response"

# Parse LLM outputs
data = sz.parse.json('Sure! Here\'s the JSON:\n```json\n{"key": "value"}\n```')
# Returns: {"key": "value"}

code = sz.parse.code('```python\nprint("hello")\n```', lang="python")
# Returns: 'print("hello")'

answer = sz.parse.boolean("Yes, I think that's correct")
# Returns: True

# Count tokens
count = sz.tokens.count("Hello world")
# Returns: 2

# Manage conversations
chat = sz.convo.new(system="You are helpful.")
chat.user("Hello").assistant("Hi there!")
messages = chat.messages()
# Returns: [{"role": "system", "content": "You are helpful."}, ...]

# Build context from files
ctx = sz.context.from_folder("./src", max_tokens=4000)
prompt = f"Review this code:\n{ctx}"
```

## Modules

### `sz.cache` — Response Caching

```python
# Basic get/set
sz.cache.set("prompt", "response", model="gpt-4")
sz.cache.get("prompt", model="gpt-4")

# With TTL (time-to-live)
sz.cache.get("prompt", ttl="1h")   # Expire after 1 hour
sz.cache.get("prompt", ttl="7d")   # Expire after 7 days

# As decorator
@sz.cache.prompt(ttl="1d", model="claude-3")
def ask_llm(prompt):
    return client.complete(prompt)

# Cleanup
sz.cache.clear()                   # Clear all
sz.cache.clear(older_than="7d")    # Clear old entries
sz.cache.stats()                   # Get cache stats
```

### `sz.parse` — Extract Structured Data

```python
# JSON (handles markdown fences, trailing commas, etc.)
sz.parse.json('```json\n{"key": "value"}\n```')

# Code blocks
sz.parse.code(response, lang="python")
sz.parse.code_blocks(response)  # Get all blocks

# Boolean from natural language
sz.parse.boolean("Yes, definitely")  # True
sz.parse.boolean("No, I don't think so")  # False

# Lists
sz.parse.list_items("1. First\n2. Second\n3. Third")

# Extract from text
sz.parse.emails("Contact me at test@example.com")
sz.parse.urls("Check out https://example.com")
sz.parse.numbers("The price is $19.99")

# XML-style tags
sz.parse.xml_tag("<answer>42</answer>", "answer")  # "42"

# Clean LLM fluff
sz.parse.clean("Sure! Here's what you asked for...")
```

### `sz.tokens` — Token Management

```python
# Count tokens
sz.tokens.count("Hello world")
sz.tokens.count_messages([{"role": "user", "content": "Hi"}])

# Check limits
sz.tokens.fits("long text...", limit=4096)

# Truncate to fit
sz.tokens.truncate("very long text...", max_tokens=100)

# Split into chunks
sz.tokens.split(long_document, chunk_size=1000, overlap=100)

# Estimate cost
sz.tokens.estimate_cost(prompt, response, model="claude-3.5-sonnet")
# Returns: {"input_tokens": 50, "output_tokens": 100, "total_cost": 0.00045}
```

### `sz.convo` — Conversation Management

```python
# Create conversation
chat = sz.convo.new(system="You are a helpful assistant.")

# Add messages (chainable)
chat.user("Hello").assistant("Hi!").user("How are you?")

# Get messages for API
messages = chat.messages()

# Get last message
last = chat.last()
last_user = chat.last(role="user")

# Fork conversation (for branching)
branch = chat.fork()

# Save/load
chat.save("conversation.json")
chat = sz.convo.load("conversation.json")

# Context window management
chat = sz.convo.new(system="...", max_tokens=4000)
# Automatically drops old messages when limit exceeded
```

### `sz.context` — Build Prompts from Files

```python
# From single file
ctx = sz.context.from_file("main.py")

# From folder
ctx = sz.context.from_folder("./src")

# With filters
ctx = sz.context.from_folder(
    "./src",
    ignore=["tests", "*.test.js"],
    include=["*.py", "*.js"],
    max_tokens=8000
)

# Use in prompt
prompt = f"Review this code:\n\n{ctx}"

# Get info
print(ctx.summary())  # "12 files, ~3,450 tokens"
print(len(ctx))       # 12
```

## Installation

**Zero dependencies** (pure Python):
```bash
pip install shapezero
```

**With accurate token counting** (requires tiktoken):
```bash
pip install shapezero[tiktoken]
```

Without tiktoken, token counts are estimated as `len(text) // 4`.

## Single File

Don't want to pip install? Just copy `shapezero/__init__.py` into your project:

```bash
curl -o shapezero.py https://raw.githubusercontent.com/shapezero/shapezero/main/shapezero/__init__.py
```

```python
import shapezero as sz
# Done.
```

## License

MIT — do whatever you want.

## Links

- Website: [shapezeroai.com](https://shapezeroai.com)
- GitHub: [github.com/shapezero/shapezero](https://github.com/shapezero/shapezero)
