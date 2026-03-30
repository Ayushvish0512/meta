# Meta Graph API Setup — Laiqa Growth Agent

Complete reference for connecting the Laiqa n8n pipeline to the Meta Marketing API.
Covers app creation, token setup, every API endpoint used in the workflows, and how to test each one.

---

## 1. Meta Business Manager Setup

1. Go to [business.facebook.com/settings](https://business.facebook.com/settings)
2. Confirm your **Ad Account** is listed under **Accounts > Ad Accounts**
3. Confirm your **Facebook Page** is listed under **Accounts > Pages**
4. Note your **Business Manager ID** — visible in the URL: `business.facebook.com/settings/info`

---

## 2. Create a Meta Developer App

1. Go to [developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Click **Create App**
3. Use case: **Other** → Next
4. App type: **Business**
5. App name: `Laiqa Growth Agent`
6. Business account: select your Business Manager
7. Click **Create App**
8. In the App Dashboard → **Add Products** → find **Marketing API** → click **Set Up**

Note your **App ID** and **App Secret** from App Settings > Basic.

---

## 3. Create a System User Token (Required for Automation)

User tokens expire in 24h. System User tokens last up to 60 days and are the correct choice for server automation.

### 3a. Create the System User

1. Business Settings → **Users** → **System Users**
2. Click **Add** → name it `laiqa-agent` → role: **Admin**
3. Click **Assign Assets**:
   - Asset type: **Ad Accounts** → select your account → permission: **Manage campaigns**
   - Asset type: **Pages** → select your page → permission: **Manage page**

### 3b. Generate the Token

1. Select the system user → click **Generate New Token**
2. Select your app (`Laiqa Growth Agent`)
3. Select these permissions:

| Permission | Why |
|---|---|
| `ads_management` | Pause/resume ads, update budgets |
| `ads_read` | Read campaign, adset, ad data |
| `read_insights` | Pull Insights API metrics |
| `business_management` | Access business assets |

4. Click **Generate Token** — copy it immediately, it won't show again
5. Paste into `.env` as `META_ACCESS_TOKEN`

### 3c. Extend Token Expiry (Optional)

System User tokens can be set to never expire:
- Business Settings → System Users → select user → Generate New Token → check **Never expire**

---

## 4. Retrieve Your IDs

| Variable | Where to find it |
|---|---|
| `META_AD_ACCOUNT_ID` | [adsmanager.facebook.com](https://adsmanager.facebook.com) — number in URL after `act_`, include the `act_` prefix |
| `META_PIXEL_ID` | Business Settings → Data Sources → Datasets |
| `META_API_VERSION` | Use `v19.0` (current stable) |

---

## 5. Graph API Endpoints Used in the Workflows

Base URL for all calls: `https://graph.facebook.com/{version}`

### 5a. Campaign Insights (WF01)

Pulls daily campaign-level metrics.

```
GET /v19.0/{META_AD_ACCOUNT_ID}/insights
```

**Required query params:**

```
access_token  = {META_ACCESS_TOKEN}
level         = campaign
fields        = campaign_id,campaign_name,impressions,reach,clicks,spend,actions,frequency,ctr,cpc,cpp,account_currency
time_range    = {"since":"2025-01-01","until":"2025-01-01"}
time_increment= 1
limit         = 500
```

**Test with curl:**
```bash
curl -G "https://graph.facebook.com/v19.0/act_YOUR_ACCOUNT_ID/insights" \
  --data-urlencode "access_token=YOUR_TOKEN" \
  --data-urlencode "level=campaign" \
  --data-urlencode 'fields=campaign_id,campaign_name,impressions,reach,clicks,spend,actions,frequency,ctr,cpc' \
  --data-urlencode 'time_range={"since":"2025-01-01","until":"2025-01-01"}' \
  --data-urlencode "time_increment=1"
```

---

### 5b. AdSet Insights (WF01)

```
GET /v19.0/{META_AD_ACCOUNT_ID}/insights
```

**Required query params:**

```
access_token  = {META_ACCESS_TOKEN}
level         = adset
fields        = adset_id,adset_name,campaign_id,impressions,reach,clicks,spend,actions,frequency,ctr,cpc,cpp,account_currency
time_range    = {"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}
time_increment= 1
limit         = 500
```

---

### 5c. Ad-Level Insights (WF01)

```
GET /v19.0/{META_AD_ACCOUNT_ID}/insights
```

**Required query params:**

```
access_token  = {META_ACCESS_TOKEN}
level         = ad
fields        = ad_id,ad_name,adset_id,campaign_id,impressions,reach,clicks,spend,actions,frequency,ctr,cpc,cpp,account_currency
time_range    = {"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}
time_increment= 1
limit         = 500
```

**Extracting conversions from `actions` array:**

The `actions` field returns an array. Purchase conversions are under these action types:
```
purchase
offsite_conversion.fb_pixel_purchase
omni_purchase
```

Example response:
```json
{
  "actions": [
    { "action_type": "link_click", "value": "45" },
    { "action_type": "offsite_conversion.fb_pixel_purchase", "value": "3" }
  ]
}
```

The normalise node in WF01 filters and sums these automatically.

---

### 5d. Pause an Ad / AdSet / Campaign (WF05)

```
POST /v19.0/{entity_id}
```

**Body:**
```json
{ "status": "PAUSED" }
```

**Query param:**
```
access_token = {META_ACCESS_TOKEN}
```

**Test with curl:**
```bash
curl -X POST "https://graph.facebook.com/v19.0/YOUR_ADSET_ID" \
  -d "access_token=YOUR_TOKEN" \
  -d "status=PAUSED"
```

**To re-enable (rollback):**
```bash
curl -X POST "https://graph.facebook.com/v19.0/YOUR_ADSET_ID" \
  -d "access_token=YOUR_TOKEN" \
  -d "status=ACTIVE"
```

---

### 5e. Update Daily Budget (WF05 — scale_budget action)

```
POST /v19.0/{adset_id}
```

**Body:**
```json
{ "daily_budget": 150000 }
```

Note: `daily_budget` is in **cents** (or the smallest currency unit). For INR 1500/day → send `150000`.

**Test with curl:**
```bash
curl -X POST "https://graph.facebook.com/v19.0/YOUR_ADSET_ID" \
  -d "access_token=YOUR_TOKEN" \
  -d "daily_budget=150000"
```

---

### 5f. Verify Token Permissions

Check what permissions your token has and when it expires:

```bash
curl -G "https://graph.facebook.com/v19.0/me" \
  --data-urlencode "access_token=YOUR_TOKEN" \
  --data-urlencode "fields=id,name,permissions"
```

Check token debug info:
```bash
curl -G "https://graph.facebook.com/v19.0/debug_token" \
  --data-urlencode "input_token=YOUR_TOKEN" \
  --data-urlencode "access_token=YOUR_APP_ID|YOUR_APP_SECRET"
```

Look for `"is_valid": true` and confirm `ads_management`, `ads_read`, `read_insights` are in the `scopes` array.

---

## 6. Insights Fields Reference

Full list of fields available on the Insights edge:

| Field | Description |
|---|---|
| `impressions` | Total times ads were shown |
| `reach` | Unique accounts that saw the ad |
| `clicks` | All clicks |
| `spend` | Amount spent (in account currency) |
| `actions` | Array of conversion events (purchases, leads, etc.) |
| `frequency` | impressions ÷ reach |
| `ctr` | Click-through rate (clicks ÷ impressions) |
| `cpc` | Cost per click |
| `cpp` | Cost per 1000 people reached |
| `account_currency` | Currency code (e.g. INR) |
| `campaign_id` / `campaign_name` | Campaign identifiers |
| `adset_id` / `adset_name` | AdSet identifiers |
| `ad_id` / `ad_name` | Ad identifiers |

---

## 7. Common Errors and Fixes

| Error | Cause | Fix |
|---|---|---|
| `(#200) Requires ads_read permission` | Token missing permission | Regenerate token with `ads_read` checked |
| `(#100) Invalid parameter` | Wrong `level` or missing `time_range` | Check query params match the endpoint |
| `(#190) Access token expired` | User token used instead of System User token | Use System User token |
| `(#17) User request limit reached` | Rate limited | Add retry with 5s backoff (already in WF01) |
| `(#368) Ad account is disabled` | Account suspended | Check account status in Ads Manager |
| `Invalid date format` | `time_range` not valid JSON string | Ensure format is `{"since":"YYYY-MM-DD","until":"YYYY-MM-DD"}` |

---

## 8. Rate Limits

Meta Marketing API uses a score-based rate limit system:

- Each call costs points based on complexity
- Limit resets every hour
- Headers `x-business-use-case-usage` and `x-app-usage` show current usage
- WF01 has `retry: maxTries 3, waitBetweenTries 5000ms` to handle 429s automatically

For 500 ads pulling daily insights, you are well within free tier limits.

---

## 9. Update .env After Setup

```env
META_ACCESS_TOKEN=your_system_user_token_here
META_AD_ACCOUNT_ID=act_XXXXXXXXXX
META_PIXEL_ID=XXXXXXXXXX
META_API_VERSION=v19.0
```

Then restart n8n to pick up the new values:
```bash
docker compose up -d --force-recreate n8n
```

Verify the token is visible inside the container:
```bash
docker exec laiqa-growth-agent-n8n-1 printenv META_ACCESS_TOKEN
```

---

## 10. Minimal Test Before Running WF01

Run this single curl to confirm everything is wired correctly before triggering the full pipeline:

```bash
curl -G "https://graph.facebook.com/v19.0/act_YOUR_ACCOUNT_ID/insights" \
  --data-urlencode "access_token=YOUR_TOKEN" \
  --data-urlencode "level=adset" \
  --data-urlencode 'fields=adset_id,adset_name,impressions,spend,clicks,actions' \
  --data-urlencode 'time_range={"since":"2025-01-01","until":"2025-01-07"}' \
  --data-urlencode "time_increment=1" \
  --data-urlencode "limit=10"
```

If you get a `data` array with rows back — you're good. If you get an error object, fix it using the table in section 7 before importing the workflows.
