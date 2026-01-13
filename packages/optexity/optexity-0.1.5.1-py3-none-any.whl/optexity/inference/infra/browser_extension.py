from browser_use.browser.profile import BrowserProfile


class BrowserExtension:
    def __init__(self, browser_profile: BrowserProfile = None):
        self.browser_profile = (
            browser_profile if browser_profile is not None else BrowserProfile()
        )

    def get_extension_paths(self):
        return self.browser_profile._get_extension_args()


if __name__ == "__main__":
    browser_profile = BrowserProfile(
        user_data_dir="~/.config/browseruse/profiles/default",
        headless=True,
    )
    paths = browser_profile._get_extension_args()
    print(paths)
