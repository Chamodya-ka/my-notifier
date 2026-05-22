# Simple and much needed

At the program directory setup a config file named `my_notifier.yaml`

```
ntfy:
  server: "https://ntfy.sh"
  topic: "ml-alerts"

email:
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  username: "user@gmail.com"
  password: "app_password"
  to: "user@gmail.com"

rules:
  - name: crash
    regex: "(ERROR|FATAL|Traceback)"
    modes:
      - email
      - ntfy
    once: true

  - name: completed
    regex: "Training complete"
    modes:
      - ntfy
    once: true
```

Works for all programs that follow `<command> <arguments>`

