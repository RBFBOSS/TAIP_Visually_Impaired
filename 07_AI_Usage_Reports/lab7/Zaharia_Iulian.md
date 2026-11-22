# AI Usage Report

## Accessible UI/UX Research & Basic Interface

* **Real-world research:** Used AI to research how blind and low-vision students use web apps in practice: user surveys, published studies (Dosono et al. 2015, Napoli et al. 2021, CISPA 2025), screen reader walkthroughs (NVDA, JAWS, VoiceOver, TalkBack), and products that already solve the problem (GOV.UK Design System, Accessibyte, Be My Eyes).
* **UI/UX rules:** Turned the findings into `01_Documentation/05_Accessible_UIUX_Research.md`: 57 numbered rules (R1–R57), screen specifications, a WCAG 2.2 AA checklist, and a test plan. The key rules are high contrast (at least 7:1), large text (20px base), reflow at 400% zoom, a clear focus outline, error summaries that receive focus, and success messages that are read aloud.
* **Mock-ups:** Generated nine figures of the sign-in, registration, upload, and study screens from reference pages that passed an axe-core scan and all 113 automated accessibility checks.
* **Basic interface:** Built the first React + Vite + TypeScript pages with these rules applied: Sign in, Create an account, Account created, and Your documents. Every page has Display settings (light, dark, or system theme, and text size). Sign-in uses a mock service until the backend is ready.
* **Checking the output:** Sources, statistics, and contrast ratios were re-checked against the original sources. Screen reader announcements still need to be confirmed with a real screen reader.
* **AI tool:** Factory Droid using models: Fable 5.2 for research and Opus 5.5 for spec
