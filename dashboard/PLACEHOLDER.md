# dashboard/

This folder contains the fully self-contained interactive HTML dashboard.

| File | Description |
|---|---|
| `index.html` | Complete interactive dashboard — open directly in any browser, zero installation |

## How to open

```bash
# macOS
open dashboard/index.html

# Windows
start dashboard/index.html

# Linux
xdg-open dashboard/index.html
```

## 📊 Dashboard Tabs

| Tab | Content |
|---|---|
| **Overview** | Sentiment distribution · % by category · Monthly trend 2022–2024 |
| **Topics** | Topic distribution · Negative rate per topic · Stacked sentiment breakdown |
| **Companies** | Positive sentiment league table · Star rating · Priority complaint count |
| **Priority Queue** | Auto-flagged complaints with tier, signals, and review extract |
| **Model** | Confusion matrix · Per-class F1 · Training loss curve · Model card |
| **Live Inference** | Type any review → instant sentiment, topic, and priority classification |

## How to deploy as a live URL

1. Go to your GitHub repo → Settings → Pages
2. Source: Deploy from branch → main → folder: /dashboard
3. Your live URL will be: `https://RidhimaGupta4.github.io/AB-Testing-Case-Study/`
