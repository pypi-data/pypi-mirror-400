# Remote Terminal

**AI-Powered Remote Linux Server Management via MCP**

Remote Terminal lets Claude (the AI assistant) execute commands on your remote Linux servers through a natural chat interface. Watch full output in your browser in real-time while Claude receives smart-filtered summaries optimized for token efficiency.

---

## 🎯 What Is This?

Imagine telling Claude:

```
"Install nginx on my server and configure it with SSL"
"Run complete system diagnostics and tell me if anything looks wrong"
"Find all log errors from the last hour and summarize them"
"Save this batch script and run it again next week"
```

And Claude does it - executing commands, analyzing output, saving useful scripts, and taking action on your behalf.

**That's Remote Terminal.**

---

## ✨ Key Features

### Core Capabilities

- **🖥️ Remote Command Execution** - Run any bash command on Linux servers
- **🌐 Multi-Server Management** - Switch between multiple servers easily
- **📁 File Transfer (SFTP)** - Upload/download files and directories with compression
- **📜 Batch Script Execution** - Run multi-command scripts 10-50x faster
- **📚 Batch Script Library** - Save, browse, and reuse batch scripts (NEW in 3.1)
- **💬 Conversation Tracking** - Group commands by goal with rollback support
- **🎯 Recipe System** - Save successful workflows for reuse
- **🗄️ Database Integration** - Full audit trail with SQLite
- **🌍 Interactive Web Terminal** - Full-featured terminal in browser (type, paste, scroll history)
- **🔄 Multi-Terminal Sync** - Open multiple terminals, all perfectly synchronized
- **✨ Bash Syntax Highlighting** - VS Code-style colors in standalone UI (NEW in 3.1)


### The Interactive Web Terminal

Remote Terminal provides a **fully interactive terminal window** in your browser at `http://localhost:8080` - it looks and feels just like WSL, PuTTY, or any standard terminal:

**You can:**
- Type commands directly (just like any terminal)
- Copy/paste text (Ctrl+C, Ctrl+V)
- Scroll through command history
- Use arrow keys for history navigation
- View real-time command output with colors preserved

**Claude can:**
- Execute commands that appear in your terminal
- See command results instantly
- Continue working while you watch

**The key advantage:** You maintain complete visibility and control. Every command Claude runs appears in your terminal window in real-time. You're never in the dark about what's happening on your server - it's like sitting side-by-side with an assistant who types commands for you while you watch the screen.

**Multi-Terminal Support:** Open multiple browser windows at `http://localhost:8080` - they all stay perfectly synchronized via WebSocket broadcast. Type in one terminal, see it in all terminals instantly. Perfect for multi-monitor setups or sharing your view with others.

⚠️ **Best Practice:** Close unused terminal tabs when done. While the system handles multiple connections efficiently, keeping many old tabs open can consume unnecessary resources and may cause connection issues.

#### 🎬 See It In Action

<video width="800" controls>
  <source src="https://raw.githubusercontent.com/TiM00R/remote-terminal/master/docs/demo.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

https://github.com/user-attachments/assets/98a6fa41-ec4f-410b-8d4a-a2422d8ac7c9

*Watch the interactive web terminal in action - see Claude execute commands while you maintain full visibility and control*

### The Dual-Stream Architecture

Behind the scenes, Remote Terminal uses a smart two-stream approach:

```
           SSH Output from Remote Server
                      ↓
                  [Raw Output]
                      ↓
                 ┌────┴────┐
                 │         │
                 ↓         ↓
             [FULL]    [FILTERED]
                 │         │
                 ↓         ↓
            Web Terminal    Claude
         (You see all)  (Smart summary)
```

**Result:**
- **You:** Full visibility and control in interactive terminal
- **Claude:** Efficient work with 95% token savings  
- **Both:** Shared SSH session, synchronized state
- **Best of both worlds!**


## 🚀 Quick Start

### Installation

**Step 1: Create Installation Directory**
```powershell
# Choose a location for your installation (example: C:\RemoteTerminal)
mkdir C:\RemoteTerminal
cd C:\RemoteTerminal
```

**Step 2: Install Package**
```powershell
# Create dedicated virtual environment
python -m venv remote-terminal-env
remote-terminal-env\Scripts\activate
pip install remote-terminal-mcp
```

**Step 3: Configure Claude Desktop**

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "remote-terminal": {
            "command": "C:\\RemoteTerminal\\remote-terminal-env\\Scripts\\remote-terminal-mcp.exe",
            "env": {
                "REMOTE_TERMINAL_ROOT": "C:\\RemoteTerminal"
            }
        }
    }
}
```

**Important:** Replace `C:\RemoteTerminal` with your actual installation path from Step 1.

**Step 4: First Run - Auto Setup**

Restart Claude Desktop. On first use, configuration files will automatically copy to `C:\RemoteTerminal`:
- `config.yaml` - Default settings (auto-created from package defaults)
- `hosts.yaml` - Server list (auto-created from template)


**Step 5: Configure Your Servers**

You have two options to configure your servers:

**Option A: Manual Configuration (Recommended for first server)**

Edit `C:\RemoteTerminal\hosts.yaml`:
```yaml
servers:
  - name: My Server
    host: 192.168.1.100
    user: username
    password: your_password
    port: 22
    description: My development server
    tags:
      - development
# Optional: Set default server for auto-connect
# Use list_servers to see which server is marked as [DEFAULT]
default_server: My Server
```

**Option B: AI-Assisted Configuration**

Ask Claude to help you add a new server:
```
Claude, add a new server to my configuration:
- Name: Production Server
- Host: 192.168.1.100
- User: admin
- Password: mypassword
- Port: 22
```

Claude will use the `add_server` tool to update your `hosts.yaml` file automatically.

Restart Claude Desktop and test:
```
List my configured servers
```



**Step 6: (Optional) Run Standalone Web Interface**
```powershell
cd C:\RemoteTerminal
remote-terminal-env\Scripts\activate
remote-terminal-standalone
```

Access at:
- Control Panel: http://localhost:8081
- Terminal: http://localhost:8082

---

## 📖 Documentation

Complete guides for every use case:

- **[Quick Start](https://github.com/TiM00R/remote-terminal/blob/master/docs/QUICK_START.md)** — Get running in 5 minutes  
- **[Installation](https://github.com/TiM00R/remote-terminal/blob/master/docs/INSTALLATION.md)** — Detailed setup instructions  
- **[User Guide](https://github.com/TiM00R/remote-terminal/blob/master/docs/USER_GUIDE.md)** — Complete feature walkthrough  
- **[Feature Reference](https://github.com/TiM00R/remote-terminal/blob/master/docs/FEATURE_REFERENCE.md)** — All MCP tools reference  
- **[Troubleshooting](https://github.com/TiM00R/remote-terminal/blob/master/docs/TROUBLESHOOTING.md)** — Common problems and solutions  
- **[WebSocket Broadcast](https://github.com/TiM00R/remote-terminal/blob/master/docs/WEBSOCKET_BROADCAST.md)** — Multi-terminal synchronization details  
- **[Release Notes v3.1](https://github.com/TiM00R/remote-terminal/blob/master/docs/RELEASE_NOTES_v3.1.md)** — Release notes for version 3.1

---

## 💡 Usage Examples

### System Administration

```
"Check disk space and memory usage"
"What processes are using the most CPU?"
"Is nginx running? If not, start it"
"Show me the last 50 lines of the system log"
```

### Software Management

```
"Install htop and verify it works"
"Update all packages"
"Check if docker is installed and what version"
```

### Troubleshooting

```
"Run complete network diagnostics"
"Find all errors in the last hour of logs"
"Check why nginx won't start"
"Analyze disk usage by directory"
```

### File Operations

```
"Upload my local config.json to /etc/app/"
"Download all log files from /var/log/myapp/"
"List files in /var/log modified today"
"Find all files larger than 100MB"
```

### Automation & Script Management

```
"Create a recipe from our successful nginx installation"
"Execute the network diagnostics recipe"
"Start a conversation to configure WiFi"
"List my saved batch scripts"
"Execute script 5"
"Load script 3 for editing"
```

---

## 🎨 Example Session

**You:**
> Install nginx on my production server

**Claude:**
> I'll install nginx. This will create a package installation...

*Interactive terminal opens automatically at http://localhost:8080*

**Web Terminal shows (real-time):**
```
$ sudo apt install nginx
Reading package lists... Done
Building dependency tree... Done
[... 500+ lines of installation output ...]
Setting up nginx (1.18.0-0ubuntu1) ...
Created symlink /etc/systemd/system/multi-user.target.wants/nginx.service
Processing triggers for systemd (245.4-4ubuntu3.23) ...
```

**Claude receives (filtered summary):**
```
nginx installed successfully in 45s
12 packages installed
Service: nginx.service is active
```

**Claude responds:**
> nginx has been successfully installed and is now running. The service is active. Would you like me to configure it or show you the default page?

**Token savings: 96% (15,000 tokens → 600 tokens)**

---

## 🏗️ Architecture

### Project Structure


```
remote_terminal/
├── config/                         # Default configuration templates
│   ├── config.yaml                 # Default settings (packaged)
│   └── hosts.yaml.example          # Server template (packaged)
├── data/                           # SQLite database (user directory)
│   └── remote_terminal.db          # Command history, conversations, recipes, scripts
├── docs/                           # Documentation
│   ├── DATABASE_SCHEMA.md
│   ├── FEATURE_REFERENCE.md
│   ├── INDEX.md
│   ├── INSTALLATION.md
│   ├── QUICK_START.md
│   ├── RELEASE_NOTES_v3.1.md
│   ├── TROUBLESHOOTING.md
│   ├── USER_GUIDE.md
│   └── WEBSOCKET_BROADCAST.md
├── recipes/                        # Example automation recipes
├── src/                            # Source code (modular architecture)
│   ├── batch/                      # Batch execution system
│   │   ├── batch_executor.py
│   │   ├── batch_helpers.py
│   │   └── batch_parser.py
│   ├── config/                     # Configuration management
│   │   ├── config.py
│   │   ├── config_dataclasses.py
│   │   ├── config_init.py
│   │   └── config_loader.py
│   ├── database/                   # Database operations (SQLite)
│   │   ├── database_manager.py     # Core database manager
│   │   ├── database_batch.py       # Batch script storage
│   │   ├── database_batch_execution.py
│   │   ├── database_batch_queries.py
│   │   ├── database_batch_scripts.py
│   │   ├── database_commands.py    # Command history
│   │   ├── database_conversations.py
│   │   ├── database_recipes.py     # Recipe storage
│   │   └── database_servers.py     # Machine identity tracking
│   ├── output/                     # Output filtering & formatting
│   │   ├── output_buffer.py
│   │   ├── output_buffer_base.py
│   │   ├── output_buffer_filtered.py
│   │   ├── output_filter.py        # Smart filtering (95% token savings)
│   │   ├── output_filter_commands.py
│   │   ├── output_filter_decision.py
│   │   └── output_formatter.py
│   ├── prompt/                     # Command completion detection
│   │   ├── prompt_detector.py
│   │   ├── prompt_detector_checks.py
│   │   ├── prompt_detector_pager.py
│   │   └── prompt_detector_patterns.py
│   ├── ssh/                        # SSH/SFTP operations
│   │   ├── ssh_manager.py          # High-level SSH manager
│   │   ├── ssh_connection.py       # Connection lifecycle
│   │   ├── ssh_commands.py         # Command execution
│   │   └── ssh_io.py               # Input/output streaming
│   ├── state/                      # Shared state management
│   │   ├── shared_state_conversation.py
│   │   ├── shared_state_monitor.py
│   │   └── shared_state_transfer.py
│   ├── static/                     # Web terminal static assets
│   │   ├── fragments/              # HTML fragments
│   │   ├── vendor/                 # xterm.js library
│   │   ├── terminal.css
│   │   ├── terminal.js
│   │   └── transfer-panel.js
│   ├── tools/                      # MCP tool modules (modular)
│   │   ├── decorators.py           # Tool decorators
│   │   ├── tools_hosts.py          # Server management (main)
│   │   ├── tools_hosts_crud.py     # Add/remove/update servers
│   │   ├── tools_hosts_select.py   # Server selection & connection
│   │   ├── tools_commands.py       # Command execution (main)
│   │   ├── tools_commands_database.py
│   │   ├── tools_commands_execution.py
│   │   ├── tools_commands_status.py
│   │   ├── tools_commands_system.py
│   │   ├── tools_conversations.py  # Conversation tracking (main)
│   │   ├── tools_conversations_lifecycle.py
│   │   ├── tools_conversations_query.py
│   │   ├── tools_batch.py          # Batch script execution (main)
│   │   ├── tools_batch_execution.py
│   │   ├── tools_batch_helpers.py
│   │   ├── tools_batch_management.py
│   │   ├── tools_recipes.py        # Recipe automation (main)
│   │   ├── tools_recipes_create.py
│   │   ├── tools_recipes_crud.py
│   │   ├── tools_recipes_execution.py
│   │   ├── tools_recipes_helpers.py
│   │   ├── tools_recipes_modify.py
│   │   ├── tools_recipes_query.py
│   │   ├── tools_sftp.py           # File transfer (main)
│   │   ├── tools_sftp_single.py    # Single file transfer
│   │   ├── tools_sftp_directory.py # Directory transfer
│   │   ├── tools_sftp_directory_download.py
│   │   ├── tools_sftp_directory_upload.py
│   │   ├── tools_sftp_exceptions.py
│   │   ├── tools_sftp_utils.py
│   │   ├── sftp_compression.py     # Compression logic
│   │   ├── sftp_compression_download.py
│   │   ├── sftp_compression_tar.py
│   │   ├── sftp_compression_upload.py
│   │   ├── sftp_decisions.py       # Auto/manual compression decisions
│   │   ├── sftp_progress.py        # Progress tracking
│   │   ├── sftp_transfer_compressed.py
│   │   ├── sftp_transfer_download.py
│   │   ├── sftp_transfer_scan.py
│   │   ├── sftp_transfer_standard.py
│   │   ├── sftp_transfer_upload.py
│   │   └── tools_info.py           # System information
│   ├── utils/                      # Utility functions
│   │   ├── utils.py
│   │   ├── utils_format.py
│   │   ├── utils_machine_id.py     # Hardware/OS fingerprinting
│   │   ├── utils_output.py
│   │   └── utils_text.py
│   ├── web/                        # Web terminal (WebSocket-enabled)
│   │   ├── web_terminal.py         # Main web server
│   │   ├── web_terminal_ui.py      # UI components
│   │   └── web_terminal_websocket.py  # Multi-terminal sync
│   ├── mcp_server.py               # MCP server entry point
│   ├── shared_state.py             # Global shared state
│   ├── command_state.py            # Command registry & tracking
│   ├── hosts_manager.py            # Multi-server configuration
│   └── error_check_helper.py       # Error detection
└── standalone/                     # Standalone web UI (no Claude)
├── static/
│   ├── css/                        # Standalone UI styles
│   │   ├── control-forms.css
│   │   ├── control-layout.css
│   │   ├── control-response.css
│   │   └── control-styles.css      # Bash syntax highlighting
│   ├── js/                         # Standalone UI scripts
│   │   ├── control-forms.js
│   │   ├── control-forms-fields.js
│   │   ├── control-forms-generation.js
│   │   ├── control-forms-utils.js
│   │   ├── control-main.js
│   │   └── control-response.js
│   └── tool-schemas/               # MCP tool schemas
│       ├── batch.json
│       ├── commands.json
│       ├── file-transfer.json
│       ├── servers.json
│       └── workflows.json
├── mcp_control.html                # Control panel HTML
├── standalone_mcp.py               # Standalone server entry point
├── standalone_mcp_endpoints.py     # API endpoints
└── standalone_mcp_startup.py       # Initialization & connection
```


### Technology Stack

- **Python 3.9+** - Core language
- **MCP Protocol** - Claude integration
- **Paramiko** - SSH/SFTP library
- **NiceGUI + WebSockets** - Web terminal with multi-terminal sync
- **SQLite** - Database for history/recipes/scripts
- **FastAPI** - Web framework

---

## 🔧 Configuration

### Configuration Files Location

Configuration files are automatically copied to your working directory on first run:

**For PyPI users:**
- Set `REMOTE_TERMINAL_ROOT` in Claude Desktop config
- Files auto-copy to that directory on first run
- Location: `%REMOTE_TERMINAL_ROOT%\config.yaml` and `hosts.yaml`
- User data preserved when reinstalling/upgrading

**Default template files packaged with installation:**
- `config/config.yaml` - Default settings template
- `config/hosts.yaml.example` - Server configuration template

### hosts.yaml

Define your servers:

```yaml
servers:
  - name: production
    host: 192.168.1.100
    user: admin
    password: secure_pass
    port: 22
    description: Production server
    tags: production, critical
    
  - name: development
    host: 192.168.1.101
    user: dev
    password: dev_pass
    tags: development

default_server: production
```

---

## 🛡️ Security Considerations

### Current Status

- Passwords stored in plain text in `hosts.yaml`
- Web terminal bound to localhost only (not network-exposed)
- Full command audit trail in database
- SSH uses standard security (password authentication)
- User config files stored outside package (preserved on reinstall)

---

## 📊 Performance

### Token Efficiency

Average token savings on verbose commands:

| Command Type | Full Output | Filtered | Savings |
|--------------|-------------|----------|---------|
| apt install  | ~15,000     | ~600     | **96%** |
| ls -la /var  | ~8,000      | ~400     | **95%** |
| Log search   | ~12,000     | ~500     | **96%** |
| find /       | ~30,000     | ~800     | **97%** |

**Average: 95-98% token reduction on verbose commands**

### Speed Improvements

Batch execution vs sequential:

- **10 commands sequential:** 5 minutes (10 round-trips)
- **10 commands batch:** 30 seconds (1 round-trip)
- **Speed improvement: 10x faster!**

---

## 🔍 Advanced Features

### Batch Script Library 

Save batch scripts for reuse:

```
1. Run diagnostics → Script auto-saved with deduplication
2. Browse library → "List my batch scripts"
3. Execute saved script → "Execute script 5"
4. Edit existing → "Load script 3 for editing"
5. Track usage → times_used, last_used_at
```

Features:
- **Automatic deduplication** via SHA256 hash
- **Usage statistics** tracking
- **Edit mode** for modifications
- **Search and sort** capabilities
- **Two-step deletion** with confirmation

### Conversation Tracking

Group related commands by goal:

```
Start conversation: "Configure nginx with SSL"
→ [Execute multiple commands]
→ End conversation: success
→ Create recipe from conversation
```

Benefits:
- Organized command history
- Rollback capability
- Context for AI
- Recipe generation

### Recipe System

Save successful workflows:

```python
# Recipe: wifi_diagnostics
1. lspci | grep -i network
2. iwconfig
3. ip link show
4. dmesg | grep -i wifi
5. systemctl status NetworkManager
```

Reuse on any compatible server:
```
Execute wifi_diagnostics recipe on my new server
```

### Machine Identity

Each server tracked by unique machine_id (hardware + OS fingerprint):
- Commands tracked per physical machine
- Recipes execute on compatible systems
- Audit trail maintains integrity
- Handles server IP changes

---

## 🐛 Known Issues & Limitations

### Current Limitations

1. **Designed for Windows local machine**
   - Currently optimized for Windows 10/11
   - Linux/Mac support possible with modifications

2. **SSH Key Support not implemented**
   - Password authentication only
   - SSH keys work with manual SSH but not integrated with MCP tools

3. **Works with only one remote server at a time**
   - Can configure multiple servers
   - Can only actively work with one server per session
   - Switch between servers as needed

---

## 🤝 Contributing

This is Tim's personal project. If you'd like to contribute:

1. Test thoroughly on your setup
2. Document any issues found
3. Suggest improvements
4. Share recipes and scripts you create

---

## 📜 Version History

### Version 1.1.3 (Current - December 20, 2024)

**Configuration System Improvements:**
- ✅ Auto-copy config files on first run
- ✅ User data preserved outside package directory
- ✅ REMOTE_TERMINAL_ROOT environment variable support
- ✅ Simplified installation process
- ✅ Config templates packaged in config/ folder

### Version 3.1 (December 16, 2024)

**NEW - Batch Script Management:**
- ✅ 5 new MCP tools for batch script library management
- ✅ Automatic deduplication via SHA256 content hash
- ✅ Usage statistics tracking (times_used, last_used_at)
- ✅ Edit mode for modifying saved scripts
- ✅ Two-step deletion with confirmation
- ✅ Standalone UI with bash syntax highlighting (VS Code colors)
- ✅ Script dropdown selectors with auto-population

**Tool Renaming (for clarity):**
- ✅ `create_diagnostic_script` → `build_script_from_commands`
- ✅ `execute_batch_script` → `execute_script_content`

### Version 3.0 (December 2024)

- ✅ Converted from PostgreSQL to SQLite
- ✅ Eliminated Docker dependency
- ✅ Multi-server support with server selection
- ✅ Machine identity tracking (hardware fingerprints)
- ✅ Conversation management (pause/resume)
- ✅ Recipe system for automation
- ✅ Batch script execution with progress tracking
- ✅ SFTP directory transfer with compression
- ✅ Comprehensive database integration
- ✅ Full audit trail
- ✅ WebSocket-based multi-terminal synchronization

### Version 2.0 (October 2024)

- ✅ Dual-stream architecture
- ✅ Smart output filtering
- ✅ Web terminal auto-open
- ✅ MCP integration with Claude

### Version 1.0 (Initial Release)

- ✅ Basic SSH command execution
- ✅ Simple web terminal
- ✅ PostgreSQL backend

---

## 📞 Support

For issues or questions:

1. **Check Documentation**
  
2. **Review Logs**
   - Claude Desktop logs (Help → Show Logs)
   
3. **Test Components**
   - Use standalone mode (start_standalone.ps1)
   - Test SSH manually
   - Verify database (view_db.py)

---

## 📄 License

This project is for personal use by Tim. Not currently open source.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude and MCP protocol
- **Paramiko** - SSH library
- **FastAPI** - Web framework
- **NiceGUI** - UI components with WebSocket support

---

**Ready to let Claude manage your servers? Check out [QUICK_START.md](https://github.com/TiM00R/remote-terminal/blob/master/docs/QUICK_START.md) to get started in 5 minutes!**

---

**Version:** 1.2.0 (Auto-config, user data preservation)  
**Last Updated:** December 23, 2024  
**Maintainer:** Tim
