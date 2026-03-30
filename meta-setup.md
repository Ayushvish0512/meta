# Meta Ads Setup Guide

This document outlines the steps required to grant the Gemini CLI and the Laiqa Growth Agent access and control over the Meta Ads Manager.

## 1. Meta Business Manager Setup
1.  Go to [Meta Business Suite Settings](https://business.facebook.com/settings).
2.  Ensure you have a **Business Manager** account.
3.  Ensure your **Ad Account** and **Facebook Page** are added.

## 2. Create a Meta App for Developers
1.  Go to the [Meta for Developers](https://developers.facebook.com/) portal.
2.  Click **My Apps** > **Create App** > **Other** > **Business**.
3.  Provide an **App Name** (e.g., "Laiqa Growth Agent").

## 3. Generate a System User Access Token (Recommended)
1.  Go to **Business Settings** > **Users** > **System Users**.
2.  Add a new System User (Admin role).
3.  Assign the **Ad Account** with "Full control".
4.  Click **Generate New Token**, select your App, and choose these permissions:
    *   `ads_management`
    *   `ads_read`
    *   `business_management`
    *   `read_insights`
5.  **Copy this token immediately.**

## 4. Advanced Graph API Configuration (Power User)
To extract deep features for AI analysis, use the following technical specs for your API calls:

### A. Base URL
`https://graph.facebook.com/v19.0/act_<AD_ACCOUNT_ID>/`

### B. Core Insights Endpoint
**Endpoint:** `/insights`
**Recommended Fields:**
`campaign_id, campaign_name, adset_id, adset_name, ad_id, ad_name, impressions, spend, reach, clicks, actions, conversions, cpc, cpm, ctr, cpp`
**Breakdowns (For deep analysis):**
`age, gender, country, publisher_platform, platform_position`

### C. Ad Creative Features
**Endpoint:** `act_<AD_ACCOUNT_ID>/adcreatives`
**Fields:**
`name, title, body, image_url, video_id, call_to_action_type, object_story_spec`
*Allows AI to audit "Copy" and "Visuals" vs Performance.*

## 5. Required Environment Variables
Update your `.env` with these verified values:
```env
META_ACCESS_TOKEN=your_token
META_AD_ACCOUNT_ID=479122674854781
META_API_VERSION=v19.0
```

## 6. Verification
Run a test fetch to ensure connectivity:
`curl -G "https://graph.facebook.com/v19.0/act_479122674854781/insights?access_token=<TOKEN>&date_preset=yesterday"`
