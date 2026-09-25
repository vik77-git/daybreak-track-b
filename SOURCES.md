# Sources

| Source / direct URL | Access date | Claim it supports | Limitation / remaining question |
|---|---|---|---|
| Microsoft Support — Create a file request — https://support.microsoft.com/en-us/onedrive/create-a-file-request | 2026-09-25 | OneDrive for Business File Requests let people with the link upload files without a OneDrive account; uploads land in a selected folder; the requester receives an upload notification. | Applies to OneDrive for Business; feature availability/admin enablement matters. This documents capability, not Daybreak adoption or reconciliation quality. |
| Microsoft — Microsoft 365 Business plans and pricing (India) — https://www.microsoft.com/en-in/microsoft-365/business/microsoft-365-plans-and-pricing | 2026-09-25 | Current India list price shown for Business Basic: ₹170/user/month with Teams or ₹130/user/month without Teams, paid yearly; GST extra. | Price is for a subscription, not incremental cost for an already-licensed Daybreak tenant. Actual licensing need is unverified. |
| Dropbox Help — Create and manage file requests — https://help.dropbox.com/share/create-file-request | 2026-09-25 | Dropbox file requests can collect files from people without Dropbox accounts; file requests are available across Dropbox plans. | File collection is not request reconciliation or structured quote approval. Storage limits/plan details depend on plan. |
| Jotform — Jotform Approvals FAQ — https://www.jotform.com/products/approvals/faq/ | 2026-09-25 | Jotform Approvals supports approval workflows, reminders, escalation, expiration and conditional branching; a free version is advertised. | Better fit for approval workflows than missing-photo collection; free-plan limits and real customer adoption were not tested. |

## Technical-claim conclusion

The vendor documentation verifies the **capability** of OneDrive/Dropbox file-request mechanisms, not the complete Daybreak workflow. The local experiment verifies a separate but necessary workflow property: a receipt signal must suppress a follow-up even when a request row still says `pending`. No external service was called.