from pathlib import Path
from aiogram_part.utils.file_manager import FileManager
from aiogram_part.utils.logger import log_success, log_info

def execute(user: str):
    """Generate systemd service file"""
    base_path = Path.cwd()
    project_name = base_path.name
    
    service_content = f'''[Unit]
Description={project_name} Telegram Bot
After=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={base_path}
ExecStart={base_path}/venv/bin/python {base_path}/bot.py
Restart=always
RestartSec=10

# Environment
EnvironmentFile={base_path}/.env

# Logging
StandardOutput=append:{base_path}/logs/bot.log
StandardError=append:{base_path}/logs/bot.error.log

[Install]
WantedBy=multi-user.target
'''
    
    service_file = base_path / f"{project_name}.service"
    service_file.write_text(service_content)
    
    log_success(f"Systemd service file created: {service_file.name}")
    log_info(f"""
To install:
  sudo cp {service_file.name} /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable {project_name}
  sudo systemctl start {project_name}
  
Check status:
  sudo systemctl status {project_name}
""")
