from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success, log_info, log_error

def setup(domain: str):
    """Setup webhook configuration"""
    base_path = Path.cwd()
    
    # Update .env
    env_file = base_path / ".env"
    if env_file.exists():
        content = env_file.read_text()
        
        # Update webhook settings
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('WEBHOOK_ENABLED='):
                updated_lines.append('WEBHOOK_ENABLED=true')
            elif line.startswith('WEBHOOK_URL='):
                updated_lines.append(f'WEBHOOK_URL=https://{domain}/webhook')
            else:
                updated_lines.append(line)
        
        env_file.write_text('\n'.join(updated_lines))
        log_success(f"Webhook configured for domain: {domain}")
        log_info("Don't forget to update your bot.py to use webhook mode!")
    else:
        log_error(".env file not found")

def status():
    """Show webhook status"""
    base_path = Path.cwd()
    env_file = base_path / ".env"
    
    if env_file.exists():
        content = env_file.read_text()
        
        enabled = False
        url = None
        
        for line in content.split('\n'):
            if line.startswith('WEBHOOK_ENABLED='):
                enabled = 'true' in line.lower()
            elif line.startswith('WEBHOOK_URL='):
                url = line.split('=', 1)[1] if '=' in line else None
        
        if enabled:
            log_success(f"✅ Webhook enabled: {url}")
        else:
            log_info("❌ Webhook disabled (using polling)")
    else:
        log_error(".env file not found")
