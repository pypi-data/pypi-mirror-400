overlay_popup_prompt = """
The primary goal of this task is to **automatically dismiss obstructing overlay popups** to enable a human-like, unobstructed view and interaction with the main website content.

---

### 🎯 Goal
Clear the entire viewport of any modal, overlay, or blocking element that prevents access to the underlying webpage content.

### 📜 Scope of Target Overlays
Target elements include, but are not limited to, the following common types of overlays:
* Cookie Consent Banners/Modals
* Privacy Policy Notices
* Email/Newsletter Sign-up Prompts
* Age Verification Gates
* Blocking Promotional Offers

### ⚙️ Action Priority and Rules

The agent must only dismiss overlays that a typical human user would close to proceed with the site. The actions must follow these specific rules in order of priority:

1.  **Cookie Consent:** When encountering a cookie or privacy consent overlay, **always accept** or agree to the policy. Click buttons labeled "Accept," "Agree," "Got it," "Allow All," or similar positive confirmation phrases.
2.  **General Dismissal:** For all other overlays (sign-ups, promotions, etc.), prioritize clicking **dismissive buttons** that close the popup without requiring user input. Look for labels like "Close," "X" (close icon), "No Thanks," "Maybe Later," "Skip," or "Continue to site."
3.  **Avoidance:** Do **not** input text, or click buttons like "Sign Up," "Learn More," or links that navigate away from the current page (e.g., "Read Full Policy"). The goal is solely to dismiss the current obstruction.

### 🛑 Completion State
The task is considered complete when the main body of the webpage is fully visible and ready for a user to interact with, meaning **no active overlays** are obstructing the content.
"""
