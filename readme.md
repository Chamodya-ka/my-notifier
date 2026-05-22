# my-notifier

Wrap any long-running terminal command and receive notifications when its output matches regex patterns. Useful for monitoring ML training runs, server logs, or any process that prints to stdout.

## Installation

```bash
git clone <repo-url>
cd my-notifier
pip install pyyaml requests
./setup.sh
```

Restart your terminal (or `source ~/.zshrc`) after running `setup.sh`. This adds a `my_notifier` alias that points to the cloned repo.

## Usage

Navigate to the directory containing your script and a `my_notifier.yaml` config file, then prefix your command with `my_notifier`:

```bash
my_notifier python train.py
my_notifier python server.py --port 8080
```

The subprocess output is printed to the console as normal. Notifications fire when a line matches a configured rule.

Press `Ctrl+C` to stop — the notifier exits cleanly and the child process is also stopped.

## Configuration

Create `my_notifier.yaml` in the directory you run the command from.

### Email via SMTP

```yaml
email:
  to: "you@example.com"
  from_address: "you@example.com"
  subject: "my-notifier alert"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  username: "you@example.com"
  password: "your_app_password"
```

### Email via API (e.g. Postmark)

```yaml
email:
  to: "you@example.com"
  from_address: "you@example.com"
  subject: "my-notifier alert"
  api_url: "https://api.postmarkapp.com/email"
  message_stream: "outbound"
  authentication:
    token_name: "X-Postmark-Server-Token"
    token: "your_token_here"
```

### ntfy

```yaml
ntfy:
  server: "https://ntfy.sh"
  topic: "your-topic-name"
```

### Rules

```yaml
rules:
  - name: crash
    regex: "(ERROR|FATAL|Traceback)"
    modes:
      - email
      - ntfy
    once: true

  - name: epoch_progress
    regex: "Epoch \\d+"
    modes:
      - ntfy
    every_n_matches: 5

  - name: loss_report
    regex: "Train Loss:"
    modes:
      - email
    lines_after: 3

  - name: heartbeat
    regex: "ping"
    modes:
      - ntfy
    alert_if_missing_for_seconds: 60
```

### Rule options

| Option | Type | Description |
|---|---|---|
| `name` | string | Unique identifier for the rule |
| `regex` | string | Python regex pattern to match against each output line |
| `modes` | list | Notification channels: `email`, `ntfy` |
| `once` | bool | Fire only on the first match (default: `false`) |
| `every_n_matches` | int | Fire every nth match (e.g. `5` = on match 5, 10, 15…) |
| `cooldown` | int | Minimum seconds between notifications for this rule |
| `lines_after` | int | Collect this many lines after the match and include them all in the notification body |
| `alert_if_missing_for_seconds` | int | Send an alert if the regex is *not* seen within this many seconds |

