# 📡 Network Management CLI

A powerful, cross-platform Command Line Interface tool for managing network inventory, tracking changes, and exporting data with Telegram integration.

| Feature 🌟 | Description 📝 |
| :--- | :--- |
| **Network Inventory** | Add, Update, Delete, and Search network entries (AID, Name, IP, Bandwidth, etc.). |
| **Activity Log** | detailed tracking of all changes (Old Value → New Value) with custom notes. |
| **Advanced Export** | Export data to **CSV** (Spreadsheet) and **JPG** (Image Table). |
| **Telegram Integration** | Send exported files directly to a **Telegram Chat/Channel** (Saved Chat ID supported). |
| **Smart Import** | Import networks from CSV files with automatic duplicate skipping. |
| **Filtered View** | Export or View data filtered by specific **Buildings**. |
| **Cross-Platform** | Optimized for Windows 🪟, Linux 🐧, and macOS 🍎. |
| **Beautiful UI** | Rich, colored terminal interface with interactive menus and tables. |

## 🚀 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
    *(Requires Python 3.7+)*

## 🛠️ Usage

Run the application:
```bash
python main.py
```

### 📋 Main Menu Options

| Option | Action | Details |
| :---: | :--- | :--- |
| **1** | **List All Networks** | View the full inventory in a colored table. |
| **2** | **Add New Network** | Create a new entry with manual AID, IP, and Status. |
| **3** | **Search Network** | Find networks by Name, IP, or Building. |
| **4** | **Update Network** | Modify any field (Status, Bandwidth, etc.) & add update notes. |
| **5** | **Delete Network** | Remove an entry permanently. |
| **6** | **Exit** | Close the application. |
| **7** | **Activity Log** | View history of all changes filtered by field. |
| **8** | **Export & Telegram** | Generate CSV/JPG and send to Telegram (Filter by Building supported). |
| **9** | **Import CSV** | Import data from a CSV file (File Browser included). |

## ⚙️ Configuration

-   **Data Storage**: All network data is stored in `network_data.json`.
-   **Config**: Telegram Chat IDs are cached in `config.json`.

## 📤 Telegram Bot Setup

To use the Telegram integration:
1.  The tool uses a pre-configured Bot Token (or you can update it in `network_exporter.py`).
2.  When exporting, simply enter your **Chat ID** (User ID) or **Channel Username** (e.g., `@my_network_channel`).
3.  The App remembers your ID for future exports!

---
*Built with Python 🐍 and Rich 🌈*
