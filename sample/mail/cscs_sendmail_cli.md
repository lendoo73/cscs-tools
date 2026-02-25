
# 🚀 Command‑Line Interface (CLI) — cscs-sendmail

The `cscs-tools` package provides a built‑in command‑line utility for sending emails from terminals, scripts, and CI/CD pipelines.

Once installed:

```
pip install cscs-tools
```

Run:

```
cscs-sendmail --help
```

---

## ✅ Basic Usage

### Send a simple text email

```
cscs-sendmail \
  --smtp-server smtp.mycompany.com \
  --from do-not-reply@mycompany.com \
  --to user@example.com \
  --subject "Hello" \
  --body "This is a test message."
```

---

## 📧 Multiple Recipients

Comma‑separated list:

```
--to "a@example.com,b@example.com,c@example.com"
```

Or repeat flags:

```
--to a@example.com --to b@example.com
```

The tool normalizes both forms.

---

## 🔐 Authentication & Security

### STARTTLS (default)
```
--security STARTTLS
```

### SSL (port 465)
```
--security SSL --smtp-port 465
```

### No encryption (not recommended)
```
--security NONE
```

Add credentials:
```
--user myuser --password mypass
```

---

## 📨 HTML Email

```
cscs-sendmail \
  --smtp-server smtp.mycompany.com \
  --from do-not-reply@mycompany.com \
  --to user@example.com \
  --subject "Report" \
  --html reports/weekly.html
```

---

## 📎 Attachments

Repeat the `--attach` flag:

```
cscs-sendmail \
  --smtp-server smtp.mycompany.com \
  --from do-not-reply@mycompany.com \
  --to user@example.com \
  --subject "Deployment Logs" \
  --body "See attached." \
  --attach logs/deploy.log \
  --attach build/output.zip
```

---

## 🔧 CI/CD Usage Examples

Useful for sending deployment notifications, pipeline results, and Teams alerts.

### GitHub Actions

```yaml
- name: Send deployment notification
  run: |
    cscs-sendmail \
      --smtp-server smtp.mycompany.com \
      --from ci@mycompany.com \
      --to teams-channel@emea.teams.ms \
      --subject "Deployment Completed" \
      --body "Version ${{ github.sha }} deployed." \
      --security STARTTLS \
      --user ${{ secrets.SMTP_USER }} \
      --password ${{ secrets.SMTP_PASS }}
```

### GitLab CI

```yaml
deploy_notify:
  stage: notify
  script:
    - cscs-sendmail \
        --smtp-server smtp.mycompany.com \
        --from ci@mycompany.com \
        --to teams-channel@emea.teams.ms \
        --subject "Pipeline Finished" \
        --body "Build $CI_PIPELINE_ID complete." \
        --security STARTTLS \
        --user "$SMTP_USER" \
        --password "$SMTP_PASS"
```

---

## 📝 CLI Options Summary

| Option | Description |
|--------|-------------|
| `--smtp-server` | SMTP host (required) |
| `--smtp-port` | Port number (default: 25) |
| `--security` | `STARTTLS` \| `SSL` \| `NONE` |
| `--user` | SMTP username |
| `--password` | SMTP password |
| `--from` | Sender address (required) |
| `--to` | Recipients, comma‑separated or repeated flags (required) |
| `--subject` | Email subject |
| `--body` | Plain text body |
| `--html` | Path to HTML file |
| `--attach` | Attachment file path (repeatable) |

---

This CLI tool is ideal for automation, alerts, notifications, and CI/CD pipelines.

---

🔙 [**Back to main documentation**](README.md)