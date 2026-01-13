"""
ShapeZero - Swiss army toolkit for AI development
Single-file version - just drop this into your project

Usage:
    import shapezero as sz
    
    # Cache responses
    sz.cache.set("prompt", "response")
    cached = sz.cache.get("prompt")
    
    # Parse LLM responses
    data = sz.parse.json('```json\n{"key": "value"}\n```')
    code = sz.parse.code(response, lang="python")
    yes_no = sz.parse.boolean("Yes, I think so")
    
    # Manage conversations
    chat = sz.convo.new(system="You are helpful.")
    chat.user("Hello").assistant("Hi!")
    messages = chat.messages()
    
    # Count tokens
    count = sz.tokens.count("Hello world")
    cost = sz.tokens.estimate_cost(prompt, response)
    
    # Build context from files
    ctx = sz.context.from_folder("./src")
    prompt = f"Review this:\\n{ctx}"
"""

__version__ = "0.1.0"

import hashlib
import json as _json
import fnmatch
import os
import re
import sqlite3
import time
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Literal, Optional, Set, Union


# =============================================================================
# CACHE MODULE
# =============================================================================

class _CacheModule:
    """Cache LLM responses to avoid repeated API calls."""
    
    def __init__(self):
        self._cache_dir = Path.home() / ".shapezero" / "cache"
        self._db_path = self._cache_dir / "responses.db"
        self._conn = None
    
    def _parse_ttl(self, ttl: Union[str, int, None]) -> Optional[int]:
        if ttl is None:
            return None
        if isinstance(ttl, int):
            return ttl
        ttl = ttl.strip().lower()
        multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
        if ttl[-1] in multipliers:
            try:
                return int(ttl[:-1]) * multipliers[ttl[-1]]
            except ValueError:
                pass
        return int(ttl)
    
    def _get_db(self) -> sqlite3.Connection:
        if self._conn is None:
            self._cache_dir.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    created_at REAL,
                    metadata TEXT
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_created ON cache(created_at)")
            self._conn.commit()
        return self._conn
    
    def _hash_prompt(self, prompt: str, model: Optional[str] = None, **kwargs) -> str:
        to_hash = {"prompt": prompt}
        if model:
            to_hash["model"] = model
        if kwargs:
            to_hash["kwargs"] = kwargs
        content = _json.dumps(to_hash, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:32]
    
    def get(self, prompt: str, model: Optional[str] = None, ttl: Union[str, int, None] = None, **kwargs) -> Optional[str]:
        """Get cached response for a prompt."""
        key = self._hash_prompt(prompt, model, **kwargs)
        db = self._get_db()
        cursor = db.execute("SELECT value, created_at FROM cache WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row is None:
            return None
        value, created_at = row
        if ttl is not None:
            max_age = self._parse_ttl(ttl)
            if time.time() - created_at > max_age:
                return None
        return value
    
    def set(self, prompt: str, response: str, model: Optional[str] = None, metadata: Optional[dict] = None, **kwargs) -> None:
        """Cache a response for a prompt."""
        key = self._hash_prompt(prompt, model, **kwargs)
        db = self._get_db()
        db.execute(
            "INSERT OR REPLACE INTO cache (key, value, created_at, metadata) VALUES (?, ?, ?, ?)",
            (key, response, time.time(), _json.dumps(metadata) if metadata else None)
        )
        db.commit()
    
    def prompt(self, ttl: Union[str, int, None] = None, model: Optional[str] = None) -> Callable:
        """Decorator to cache function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                if args:
                    prompt_text = args[0]
                elif 'prompt' in kwargs:
                    prompt_text = kwargs['prompt']
                elif 'messages' in kwargs:
                    prompt_text = _json.dumps(kwargs['messages'])
                else:
                    return func(*args, **kwargs)
                
                cache_model = model or kwargs.get('model')
                cached = self.get(prompt_text, model=cache_model, ttl=ttl)
                if cached is not None:
                    return cached
                
                result = func(*args, **kwargs)
                if isinstance(result, str):
                    self.set(prompt_text, result, model=cache_model)
                elif hasattr(result, 'content') and hasattr(result.content[0], 'text'):
                    self.set(prompt_text, result.content[0].text, model=cache_model)
                return result
            return wrapper
        return decorator
    
    def clear(self, older_than: Union[str, int, None] = None) -> int:
        """Clear cached entries."""
        db = self._get_db()
        if older_than is None:
            cursor = db.execute("DELETE FROM cache")
        else:
            max_age = self._parse_ttl(older_than)
            cutoff = time.time() - max_age
            cursor = db.execute("DELETE FROM cache WHERE created_at < ?", (cutoff,))
        db.commit()
        return cursor.rowcount
    
    def stats(self) -> dict:
        """Get cache statistics."""
        db = self._get_db()
        cursor = db.execute("SELECT COUNT(*), SUM(LENGTH(value)) FROM cache")
        count, total_size = cursor.fetchone()
        cursor = db.execute("SELECT MIN(created_at), MAX(created_at) FROM cache")
        oldest, newest = cursor.fetchone()
        return {"entries": count or 0, "size_bytes": total_size or 0, "oldest": oldest, "newest": newest, "path": str(self._db_path)}


# =============================================================================
# PARSE MODULE
# =============================================================================

class _ParseModule:
    """Extract structured data from LLM responses."""
    
    def json(self, text: str, default: Any = None) -> Any:
        """Extract JSON from LLM response (handles markdown fences, etc.)."""
        if not text or not text.strip():
            return default
        text = text.strip()
        
        for pattern in [r'```json\s*([\s\S]*?)\s*```', r'```\s*([\s\S]*?)\s*```']:
            match = re.search(pattern, text)
            if match:
                text = match.group(1).strip()
                break
        
        try:
            return _json.loads(text)
        except _json.JSONDecodeError:
            pass
        
        for pattern in [r'(\{[\s\S]*\})', r'(\[[\s\S]*\])']:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    return _json.loads(match)
                except _json.JSONDecodeError:
                    fixed = re.sub(r',\s*([}\]])', r'\1', match)
                    try:
                        return _json.loads(fixed)
                    except _json.JSONDecodeError:
                        continue
        return default
    
    def code(self, text: str, lang: Optional[str] = None) -> Optional[str]:
        """Extract first code block from response."""
        blocks = self.code_blocks(text, lang=lang)
        return blocks[0] if blocks else None
    
    def code_blocks(self, text: str, lang: Optional[str] = None) -> List[str]:
        """Extract all code blocks from response."""
        pattern = rf'```{lang}\s*([\s\S]*?)\s*```' if lang else r'```(?:\w*)\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.strip() for m in matches if m.strip()]
    
    def boolean(self, text: str, default: Optional[bool] = None) -> Optional[bool]:
        """Extract yes/no decision from text."""
        text = text.lower().strip()
        positive = {'yes', 'true', 'correct', 'affirmative', 'definitely', 'absolutely', 'indeed', 'certainly', 'right', 'yep', 'yeah'}
        negative = {'no', 'false', 'incorrect', 'negative', 'wrong', 'nope', 'nah', 'denied'}
        words = set(re.findall(r'\b\w+\b', text))
        pos_matches = words & positive
        neg_matches = words & negative
        if pos_matches and not neg_matches:
            return True
        if neg_matches and not pos_matches:
            return False
        first_word = text.split()[0] if text.split() else ""
        if first_word in positive:
            return True
        if first_word in negative:
            return False
        return default
    
    def list_items(self, text: str) -> List[str]:
        """Extract list items from text."""
        numbered = re.findall(r'^\s*\d+[.)]\s*(.+?)$', text, re.MULTILINE)
        if numbered:
            return [item.strip() for item in numbered if item.strip()]
        bulleted = re.findall(r'^\s*[-*•]\s*(.+?)$', text, re.MULTILINE)
        if bulleted:
            return [item.strip() for item in bulleted if item.strip()]
        if text.count('\n') < 3 and ',' in text:
            if ':' in text:
                text = text.split(':', 1)[1]
            items = [item.strip().rstrip('.') for item in text.split(',') if item.strip()]
            if items:
                return items
        return [line.strip() for line in text.split('\n') if line.strip() and not line.strip().endswith(':')]
    
    def emails(self, text: str) -> List[str]:
        """Extract email addresses."""
        return list(set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)))
    
    def urls(self, text: str) -> List[str]:
        """Extract URLs."""
        return list(set(re.findall(r'https?://[^\s<>"\')\]]+[^\s<>"\')\].,;:!?]', text)))
    
    def numbers(self, text: str, as_float: bool = False) -> List[Union[int, float]]:
        """Extract numbers from text."""
        matches = re.findall(r'-?\d+\.?\d*', text)
        return [float(m) if '.' in m or as_float else int(m) for m in matches]
    
    def xml_tag(self, text: str, tag: str) -> Optional[str]:
        """Extract content from XML-style tag."""
        match = re.search(rf'<{tag}>([\s\S]*?)</{tag}>', text, re.IGNORECASE)
        return match.group(1).strip() if match else None
    
    def xml_tags(self, text: str, tag: str) -> List[str]:
        """Extract all instances of an XML-style tag."""
        return [m.strip() for m in re.findall(rf'<{tag}>([\s\S]*?)</{tag}>', text, re.IGNORECASE)]
    
    def clean(self, text: str) -> str:
        """Clean up LLM response text."""
        text = text.strip()
        text = re.sub(r'\n{3,}', '\n\n', text)
        for pattern in [r'^(Sure,?\s+)', r'^(Certainly,?\s+)', r'^(Of course,?\s+)', r'^(Here\'?s?\s+(?:the|a|an|my)\s+)']:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text


# =============================================================================
# TOKENS MODULE
# =============================================================================

class _TokensModule:
    """Token counting and management."""
    
    def __init__(self):
        self._encoder = None
    
    def _get_encoder(self):
        if self._encoder is None:
            try:
                import tiktoken
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self._encoder = "fallback"
        return self._encoder
    
    def count(self, text: str) -> int:
        """Count tokens in text."""
        if not text:
            return 0
        encoder = self._get_encoder()
        if encoder == "fallback":
            return len(text) // 4
        return len(encoder.encode(text))
    
    def count_messages(self, messages: List[dict]) -> int:
        """Count tokens in message list."""
        total = 3
        for msg in messages:
            total += 4 + self.count(msg.get("content", ""))
        return total
    
    def fits(self, text: str, limit: int, buffer: int = 0) -> bool:
        """Check if text fits within token limit."""
        return self.count(text) <= (limit - buffer)
    
    def truncate(self, text: str, max_tokens: int, suffix: str = "\n... [truncated]") -> str:
        """Truncate text to fit token limit."""
        if self.count(text) <= max_tokens:
            return text
        suffix_tokens = self.count(suffix)
        target = max_tokens - suffix_tokens
        if target <= 0:
            return suffix.strip()
        encoder = self._get_encoder()
        if encoder == "fallback":
            return text[:target * 4] + suffix
        tokens_list = encoder.encode(text)
        return encoder.decode(tokens_list[:target]) + suffix
    
    def split(self, text: str, chunk_size: int, overlap: int = 0) -> List[str]:
        """Split text into chunks."""
        if not text:
            return []
        encoder = self._get_encoder()
        if encoder == "fallback":
            char_chunk, char_overlap = chunk_size * 4, overlap * 4
            chunks = []
            start = 0
            while start < len(text):
                chunks.append(text[start:start + char_chunk])
                start += char_chunk - char_overlap
            return chunks
        tokens_list = encoder.encode(text)
        chunks = []
        start = 0
        while start < len(tokens_list):
            chunks.append(encoder.decode(tokens_list[start:start + chunk_size]))
            start += chunk_size - overlap
        return chunks
    
    def estimate_cost(self, input_text: str, output_text: str = "", model: str = "claude-3.5-sonnet") -> dict:
        """Estimate API cost."""
        pricing = {
            "claude-3-opus": {"input": 15.0, "output": 75.0},
            "claude-3-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3.5-sonnet": {"input": 3.0, "output": 15.0},
            "claude-3-haiku": {"input": 0.25, "output": 1.25},
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        }
        input_tokens = self.count(input_text)
        output_tokens = self.count(output_text) if output_text else 0
        prices = next((p for k, p in pricing.items() if k in model.lower()), pricing["claude-3.5-sonnet"])
        input_cost = (input_tokens / 1_000_000) * prices["input"]
        output_cost = (output_tokens / 1_000_000) * prices["output"]
        return {"input_tokens": input_tokens, "output_tokens": output_tokens, "input_cost": round(input_cost, 6), "output_cost": round(output_cost, 6), "total_cost": round(input_cost + output_cost, 6)}


# =============================================================================
# CONVO MODULE
# =============================================================================

@dataclass
class _Message:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


class Conversation:
    """Conversation with message history."""
    
    def __init__(self, system: Optional[str] = None, max_tokens: Optional[int] = None):
        self.system_prompt = system
        self.max_tokens = max_tokens
        self._messages: List[_Message] = []
        self._tokens = _TokensModule()
    
    def _enforce_limit(self) -> None:
        if not self.max_tokens:
            return
        total = self._tokens.count(self.system_prompt or "")
        for msg in self._messages:
            total += self._tokens.count(msg.content)
        while total > self.max_tokens and len(self._messages) > 1:
            removed = self._messages.pop(0)
            total -= self._tokens.count(removed.content)
    
    def add(self, role: str, content: str) -> "Conversation":
        if role == "system":
            self.system_prompt = content
        else:
            self._messages.append(_Message(role=role, content=content))
        self._enforce_limit()
        return self
    
    def user(self, content: str) -> "Conversation":
        return self.add("user", content)
    
    def assistant(self, content: str) -> "Conversation":
        return self.add("assistant", content)
    
    def system(self, content: str) -> "Conversation":
        return self.add("system", content)
    
    def messages(self, include_system: bool = True) -> List[Dict[str, str]]:
        result = []
        if include_system and self.system_prompt:
            result.append({"role": "system", "content": self.system_prompt})
        result.extend(msg.to_dict() for msg in self._messages)
        return result
    
    def last(self, role: Optional[str] = None) -> Optional[_Message]:
        if role:
            for msg in reversed(self._messages):
                if msg.role == role:
                    return msg
            return None
        return self._messages[-1] if self._messages else None
    
    def clear(self, keep_system: bool = True) -> "Conversation":
        self._messages.clear()
        if not keep_system:
            self.system_prompt = None
        return self
    
    def fork(self) -> "Conversation":
        new = Conversation(system=self.system_prompt, max_tokens=self.max_tokens)
        new._messages = deepcopy(self._messages)
        return new
    
    def save(self, path: Union[str, Path]) -> None:
        data = {"system": self.system_prompt, "max_tokens": self.max_tokens, "messages": [{"role": m.role, "content": m.content, "timestamp": m.timestamp} for m in self._messages]}
        Path(path).write_text(_json.dumps(data, indent=2))
    
    def __len__(self) -> int:
        return len(self._messages)
    
    def __str__(self) -> str:
        return f"Conversation({len(self._messages)} messages)"


class _ConvoModule:
    """Conversation management."""
    
    def new(self, system: Optional[str] = None, max_tokens: Optional[int] = None) -> Conversation:
        return Conversation(system=system, max_tokens=max_tokens)
    
    def load(self, path: Union[str, Path]) -> Conversation:
        data = _json.loads(Path(path).read_text())
        conv = Conversation(system=data.get("system"), max_tokens=data.get("max_tokens"))
        for msg in data.get("messages", []):
            conv._messages.append(_Message(role=msg["role"], content=msg["content"], timestamp=msg.get("timestamp", time.time())))
        return conv


# =============================================================================
# CONTEXT MODULE
# =============================================================================

@dataclass
class ContextFile:
    path: str
    content: str
    tokens: int = 0
    
    def __str__(self) -> str:
        return f"### {self.path}\n```\n{self.content}\n```"


@dataclass 
class Context:
    files: List[ContextFile] = field(default_factory=list)
    total_tokens: int = 0
    truncated: bool = False
    
    def __str__(self) -> str:
        return "\n\n".join(str(f) for f in self.files)
    
    def __len__(self) -> int:
        return len(self.files)
    
    def summary(self) -> str:
        return f"{len(self.files)} files, ~{self.total_tokens:,} tokens" + (" (truncated)" if self.truncated else "")


class _ContextModule:
    """Build context from files and folders."""
    
    DEFAULT_IGNORE = {".git", "__pycache__", "node_modules", ".venv", "venv", "*.pyc", "*.exe", "*.dll", "*.so", "*.jpg", "*.png", "*.gif", "*.pdf", "*.zip", "*.tar", "*.gz", ".DS_Store", "package-lock.json"}
    TEXT_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".rb", ".php", ".html", ".css", ".json", ".yaml", ".yml", ".toml", ".md", ".txt", ".sql", ".sh", ".xml", ".csv", ""}
    
    def __init__(self):
        self._tokens = _TokensModule()
    
    def _should_ignore(self, path: Path, ignore_patterns: Set[str]) -> bool:
        name = path.name
        for pattern in ignore_patterns:
            if name == pattern or fnmatch.fnmatch(name, pattern):
                return True
            for parent in path.parents:
                if parent.name == pattern:
                    return True
        return False
    
    def _is_text(self, path: Path) -> bool:
        return path.suffix.lower() in self.TEXT_EXTENSIONS or path.name.lower() in {"makefile", "dockerfile", "readme", "license"}
    
    def _read(self, path: Path, max_chars: Optional[int] = None) -> Optional[str]:
        try:
            content = path.read_text(encoding="utf-8")
            if max_chars and len(content) > max_chars:
                content = content[:max_chars] + "\n... [truncated]"
            return content
        except Exception:
            return None
    
    def from_file(self, path: Union[str, Path]) -> Context:
        path = Path(path)
        content = self._read(path)
        if content is None:
            raise ValueError(f"Could not read: {path}")
        tokens = self._tokens.count(content)
        return Context(files=[ContextFile(path=str(path), content=content, tokens=tokens)], total_tokens=tokens)
    
    def from_folder(self, path: Union[str, Path], ignore: Optional[List[str]] = None, include: Optional[List[str]] = None, max_tokens: Optional[int] = None) -> Context:
        path = Path(path)
        ignore_patterns = self.DEFAULT_IGNORE | set(ignore or [])
        files, total_tokens, truncated = [], 0, False
        
        for file_path in sorted(path.rglob("*")):
            if not file_path.is_file() or self._should_ignore(file_path, ignore_patterns) or not self._is_text(file_path):
                continue
            if include and not any(fnmatch.fnmatch(file_path.name, p) for p in include):
                continue
            content = self._read(file_path)
            if content is None:
                continue
            tokens = self._tokens.count(content)
            if max_tokens and total_tokens + tokens > max_tokens:
                truncated = True
                break
            files.append(ContextFile(path=str(file_path.relative_to(path)), content=content, tokens=tokens))
            total_tokens += tokens
        
        return Context(files=files, total_tokens=total_tokens, truncated=truncated)
    
    def from_string(self, content: str, name: str = "input") -> Context:
        tokens = self._tokens.count(content)
        return Context(files=[ContextFile(path=name, content=content, tokens=tokens)], total_tokens=tokens)


# =============================================================================
# MODULE INSTANCES
# =============================================================================

cache = _CacheModule()
parse = _ParseModule()
tokens = _TokensModule()
convo = _ConvoModule()
context = _ContextModule()
