# Rill Privacy Policy

Effective: October 5, 2026. Publisher: Kuiyu Fu / Chips Studio. This policy describes Rill 1.0 for iPhone and iPad.

## Your device and your services

No Rill account is required. Rill does not operate an inference intermediary, advertising service or analytics backend. This does not mean no data leaves your device: the AI services you choose process your requests.

API keys are stored in the local iOS Keychain, not in chat storage, search indexes or ordinary exports. Rill 1.0 does not enable iCloud Keychain credential sync or CloudKit chat sync. Existing on-device history is retained; iOS device backup remains governed by your system settings.

Messages, branches, drafts, model identities, reactions, settings and attachments are stored locally. A private, rebuildable local search index accelerates search, is excluded from backup, and is not published to system Spotlight or synchronized through CloudKit.

## When information is sent

Before your first inference request to a configured destination, Rill asks for permission to send chat content. Requests may include your current message, the complete applicable original active-branch history, its system prompt, relevant image/file attachments and protocol state needed by that model. Group participants receive their own applicable histories, not other participants’ answers by default. Rill does not silently shorten history or generate lossy summaries.

Your key authenticates directly with that service. It also receives normal network information such as your IP address. Model-directory refresh sends authentication and configuration needed to list models, not chat text, drafts, system prompts or attachments. It can run on demand or opportunistically for eligible configured cloud services.

OpenAI, Anthropic, Google Gemini, xAI and custom OpenAI-compatible endpoints are supported configuration paths. Terms, retention, training controls, account linkage and regional availability differ. A listed model does not guarantee inference access. Consult [AI services information](ai-services.html) before sending sensitive content. Local endpoints remain within a device/network only if the endpoint itself does; Rill cannot control a third-party server’s onward processing.

Rill Demo is a deterministic on-device sample. It sends no network requests, uses no key and does not analyze images.

## Permissions and optional features

Camera access is requested only when you take an attachment photo. System photo/document pickers provide only selected items; Rill does not scan your photo library. Local network access is used for addresses you configure. New-model system notifications are off by default, enabled only by your choice, and contain no chat text or keys.

Read Aloud, voice input and executable HTML previews are not enabled in Rill 1.0. Markdown, tables and code remain display content; generated HTML is not executed. Rill includes no tracking or advertising SDK and does not request tracking authorization.

## Retention and control

Local history stays until you delete it or remove the app. Deletion guards prevent late local work from restoring deleted chats; minimal deletion records may remain for integrity. Exports are separate files under your control. Local deletion cannot delete data already processed by a provider; use that provider’s controls and policy. Revoking destination permission in service settings blocks subsequent requests without erasing history or silently canceling existing requests.

Rill does not upload diagnostic logs or conversations to its publisher. Apple may process app/device diagnostics under your system choices. Support email contains only information you voluntarily include; the publisher and email service receive it. Never send keys or private conversations unnecessarily.

## Website and contact

This static website has no cookies, analytics scripts, forms or remote fonts. GitHub Pages handles hosting and security logs under the [GitHub Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).

Privacy requests and support: [hideinicloud@icloud.com](mailto:hideinicloud@icloud.com). Policy changes will be dated here.
