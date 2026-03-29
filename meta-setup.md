# Meta Ads Setup Guide

This document outlines the steps required to grant the Gemini CLI and the Laiqa Growth Agent access and control over the Meta Ads Manager.

## 1. Meta Business Suite / Business Manager Setup
1.  Go to [Meta Business Suite Settings](https://business.facebook.com/settings).
2.  Ensure you have a **Business Manager** account.
3.  Ensure your **Ad Account** and **Facebook Page** are added to this Business Manager.

## 2. Create a Meta App for Developers
1.  Go to the [Meta for Developers](https://developers.facebook.com/) portal.
2.  Click **My Apps** > **Create App**.
3.  Select **Other** as the use case, then click **Next**.
4.  Select **Business** as the app type.
5.  Provide an **App Name** (e.g., "Laiqa Growth Agent") and select your **Business Account**.
6.  Click **Create app**.

## 3. Configure Marketing API
1.  In the App Dashboard, find the **Add products to your app** section.
2.  Locate **Marketing API** and click **Set up**.
3.  In the left sidebar under "Marketing API", go to **Tools**.

## 4. Generate a System User Access Token (Recommended for Automation)
1.  Go back to **Business Settings** > **Users** > **System Users**.
2.  Click **Add** to create a new System User (Select "Admin" role).
3.  Select the System User and click **Assign Assets**.
4.  Assign the **Ad Account** with "Full control" (Manage campaigns).
5.  Click **Generate New Token**.
6.  Select your App (from Step 2).
7.  Select the following **Permissions**:
    *   `ads_management`
    *   `ads_read`
    *   `business_management`
    *   `read_insights`
8.  Click **Generate Token**. **Copy this token immediately**; it will only be shown once.

## 5. Retrieve Required IDs
*   **META_ACCESS_TOKEN**: The token you just generated.
*   **META_AD_ACCOUNT_ID**: Go to [Ads Manager](https://adsmanager.facebook.com/adsmanager). Your ID is the number after `act_` in the URL (e.g., `act_123456789`).
*   **META_PIXEL_ID**: Found in Business Settings > Data Sources > Datasets (formerly Pixels).
*   **META_API_VERSION**: Use `v19.0` or the latest stable version.

## 6. Environment Configuration
Update the `.env` file in the `laiqa-growth-agent/` directory with these values:

```env
META_ACCESS_TOKEN=your_system_user_token_here
META_AD_ACCOUNT_ID=act_XXXXXXXXXX
META_PIXEL_ID=XXXXXXXXXX
META_API_VERSION=v19.0
```

## 7. Verification
Once configured, the agent will have the ability to:
*   Read campaign performance data.
*   Update budgets and bids.
*   Pause/Resume campaigns and ad sets.
*   Propose and execute new creative strategies.
