import re
import threading
import time
from config import Config, Rule
from notifications.email import EmailClient


class _RuleState:
    def __init__(self):
        self.triggered: bool = False  # for once
        self.match_count: int = 0  # for every_n_matches
        self.last_notified: float | None = None  # for cooldown
        self.stall_timer: threading.Timer | None = (
            None  # for alert_if_missing_for_seconds
        )
        self.pending_lines_after: int = 0  # for lines_after
        self.collected_lines: list[str] = []  # for lines_after


class Matcher:
    def __init__(self, config: Config):
        self.config = config
        self._state: dict[str, _RuleState] = {
            rule.name: _RuleState() for rule in config.rules
        }
        self.email_sender = EmailClient(config.email) if config.email else None
        self.ntfy_sender = None  # TODO: implement NtfyClient and initialize here

    def notify(self, rule: Rule, line: str):
        if self.config.email:
            self.email_sender.send(rule, line)

    def _notify_guarded(self, rule: Rule, line: str):
        """Apply cooldown guard then call notify."""
        state = self._state[rule.name]
        now = time.monotonic()
        if rule.cooldown is not None:
            if (
                state.last_notified is not None
                and (now - state.last_notified) < rule.cooldown
            ):
                return
        state.last_notified = now
        self.notify(rule, line)

    def _reset_stall_timer(self, rule: Rule):
        """Cancel any existing stall timer and start a fresh one."""
        state = self._state[rule.name]
        if state.stall_timer is not None:
            state.stall_timer.cancel()
        timer = threading.Timer(
            rule.alert_if_missing_for_seconds,
            self._on_stall,
            args=(rule,),
        )
        timer.daemon = True
        timer.start()
        state.stall_timer = timer

    def _on_stall(self, rule: Rule):
        """Called when the stall timer fires (regex not seen within the window)."""
        self._notify_guarded(
            rule,
            f"[stall] '{rule.name}' regex not seen for {rule.alert_if_missing_for_seconds}s",
        )

    def match_line(self, line: str):
        for rule in self.config.rules:
            state = self._state[rule.name]

            # Collect lines_after lines following a match
            if state.pending_lines_after > 0:
                state.collected_lines.append(line)
                state.pending_lines_after -= 1
                if state.pending_lines_after == 0:
                    combined = "\n".join(state.collected_lines)
                    state.collected_lines = []
                    self._notify_guarded(rule, combined)
                continue

            # Reset stall timer whenever a line arrives (regardless of match)
            if rule.alert_if_missing_for_seconds is not None:
                if re.search(rule.regex, line):
                    self._reset_stall_timer(rule)
                elif state.stall_timer is None:
                    # Arm the timer on the very first line even without a match
                    self._reset_stall_timer(rule)

            if not re.search(rule.regex, line):
                continue

            # once — fire only on the first match
            if rule.once:
                if state.triggered:
                    continue
                state.triggered = True

            # every_n_matches — fire only on every nth match
            if rule.every_n_matches is not None:
                state.match_count += 1
                if state.match_count % rule.every_n_matches != 0:
                    continue

            # lines_after — collect subsequent lines before notifying
            if rule.lines_after:
                state.collected_lines = [line]
                state.pending_lines_after = rule.lines_after
                continue

            self._notify_guarded(rule, line)

    def stop(self):
        """Cancel all active stall timers (call on process exit)."""
        for state in self._state.values():
            if state.stall_timer is not None:
                state.stall_timer.cancel()
