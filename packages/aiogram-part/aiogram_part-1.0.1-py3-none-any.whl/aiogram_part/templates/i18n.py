class I18nTemplates:
    @staticmethod
    def get_middleware_template() -> str:
        return '''from typing import Dict, Any
from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18n, SimpleI18nMiddleware

i18n = I18n(path="locales", default_locale="en", domain="messages")

class I18nMiddleware(SimpleI18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: Dict[str, Any]) -> str:
        user = data.get("event_from_user")
        if user and hasattr(user, "language_code"):
            return user.language_code
        return self.i18n.default_locale
'''
    
    @staticmethod
    def get_po_template(lang: str) -> str:
        return f'''# Translation file for {lang.upper()}
msgid ""
msgstr ""
"Language: {lang}\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "key"
msgstr "value"
'''
    
    @staticmethod
    def get_pot_template() -> str:
        return '''# Translation template file
msgid ""
msgstr ""
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "key"
msgstr ""
'''
    
    @staticmethod
    def get_makefile() -> str:
        return '''LOCALES_DIR = locales
LOCALES = en ru uz
DOMAIN = messages

.PHONY: translate compile extract

extract:
\t@echo "Extracting messages..."
\tpybabel extract --input-dirs=. -o $(LOCALES_DIR)/$(DOMAIN).pot --project=aiogram-bot

update:
\t@echo "Updating translations..."
\t@for locale in $(LOCALES); do \\
\t\tpybabel update -d $(LOCALES_DIR) -l $$locale -i $(LOCALES_DIR)/$(DOMAIN).pot -D $(DOMAIN); \\
\tdone

compile:
\t@echo "Compiling translations..."
\tpybabel compile -d $(LOCALES_DIR) -D $(DOMAIN)

translate: extract update compile
\t@echo "✅ Translations updated!"

init-locale:
\t@echo "Initializing new locale..."
\t@read -p "Enter locale code (e.g., en, ru, uz): " locale; \\
\tpybabel init -d $(LOCALES_DIR) -l $$locale -i $(LOCALES_DIR)/$(DOMAIN).pot -D $(DOMAIN)
'''
