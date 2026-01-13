from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success, log_info
from aiogram_part.templates.i18n import I18nTemplates

def execute():
    base_path = Path.cwd()
    
    languages = ["en", "ru", "uz"]
    
    for lang in languages:
        locale_dir = base_path / "locales" / lang / "LC_MESSAGES"
        FileManager.create_directory(locale_dir)
        
        po_file = locale_dir / "messages.po"
        pot_file = base_path / "locales" / "messages.pot"
        
        FileManager.create_file(po_file, I18nTemplates.get_po_template(lang))
        
    FileManager.create_file(pot_file, I18nTemplates.get_pot_template())
    
    middleware_path = base_path / "middlewares" / "i18n.py"
    FileManager.create_file(middleware_path, I18nTemplates.get_middleware_template())
    
    init_path = middleware_path.parent / "__init__.py"
    FileManager.update_middleware_init(init_path, "i18n", "I18nMiddleware")
    
    makefile_path = base_path / "Makefile"
    FileManager.create_file(makefile_path, I18nTemplates.get_makefile())
    
    requirements_path = base_path / "requirements.txt"
    if requirements_path.exists():
        content = requirements_path.read_text()
        if "aiogram[i18n]" not in content:
            content += "\naiogram[i18n]>=3.22.0\nBabel>=2.12.0\n"
            requirements_path.write_text(content)
    
    log_success("Multi-language support created!")
    log_info("Next steps:")
    log_info("  1. Add translations to locales/*/LC_MESSAGES/messages.po")
    log_info("  2. Run: make translate")
    log_info("  3. Use i18n in handlers: await message.answer(i18n.get('welcome'))")
