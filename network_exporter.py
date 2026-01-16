import csv
import requests
from rich.console import Console
from rich.table import Table
from PIL import Image, ImageDraw, ImageFont
import io # Import io module

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8288214942:AAHaoETdhD3FGIRlaLqfULJeY1NqDKc-UUQ"

class NetworkExporter:
    def __init__(self, data):
        self.data = data
        self.console = Console(record=True, width=150) # Increased width for image capture

    def export_csv(self, filename="network_list.csv"):
        if not self.data:
            return False
        
        keys = self.data[0].keys()
        # Ensure 'history' is handled gracefully (maybe exclude or stringify)
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # Header
                header = ["AID", "Name", "Building", "IP Location", "Public IP", 
                          "Private IP", "Bandwidth", "Status", "Install Date", "Last Note"]
                writer.writerow(header)
                
                for item in self.data:
                    # Get last history note if available
                    last_note = ""
                    if item.get('history') and len(item['history']) > 1:
                         last_note = item['history'][-1].get('note', '')
                    elif item.get('history'):
                         last_note = item['history'][0].get('note', '')

                    writer.writerow([
                        item.get('aid'),
                        item.get('name'),
                        item.get('building'),
                        item.get('ip_location'),
                        item.get('public_ip'),
                        item.get('private_ip'),
                        item.get('bandwidth'),
                        item.get('status'),
                        item.get('install_date'),
                        last_note
                    ])
            return True
        except Exception as e:
            print(f"CSV Export Error: {e}")
            return False

    def export_jpg(self, filename="network_list.jpg", title="Network List Export"):
        # Generate table string using rich
        table = Table(title=title)
        
        # Check if we are exporting network list or activity log based on data structure
        # Heuristic: Activity log has 'network_name', 'field', etc.
        if self.data and 'network_name' in self.data[0]:
             # Activity Log Columns
            table.add_column("Date")
            table.add_column("Net(AID)")
            table.add_column("Field")
            table.add_column("Old")
            table.add_column("New")
            table.add_column("Note")
            
            for item in self.data:
                table.add_row(
                    item.get('date', ''),
                    f"{item.get('network_name')} ({item.get('network_aid')})",
                    item.get('field', ''),
                    str(item.get('old_value', '')),
                    str(item.get('new_value', '')),
                    item.get('note', '')
                )
        else:
            # Network List Columns
            table.add_column("AID")
            table.add_column("Name")
            table.add_column("Building")
            table.add_column("IP Loc")
            table.add_column("Pub IP")
            table.add_column("Priv IP")
            table.add_column("BW")
            table.add_column("Status")
            table.add_column("Date")
            
            for item in self.data:
                table.add_row(
                    str(item.get('aid', '')),
                    item.get('name', ''),
                    item.get('building', ''),
                    item.get('ip_location', ''),
                    item.get('public_ip', ''),
                    item.get('private_ip', ''),
                    item.get('bandwidth', ''),
                    item.get('status', ''),
                    item.get('install_date', '')
                )
        
        self.console.print(table)
        text_output = self.console.export_text()
        
        # Create Image
        # Estimate size
        lines = text_output.split('\n')
        width = max(len(line) for line in lines) * 10  # Approx 10px per char
        height = len(lines) * 20 # Approx 20px per line
        
        # Minimum dimensions
        width = max(width, 400)
        height = max(height, 200)

        image = Image.new('RGB', (width + 40, height + 40), color='white')
        draw = ImageDraw.Draw(image)
        
        # Load a default font (system dependent, fall back to default)
        try:
            # Try to grab a monospace font on Windows
            font = ImageFont.truetype("consola.ttf", 15)
        except:
             try:
                 font = ImageFont.truetype("arial.ttf", 15)
             except:
                 font = ImageFont.load_default()

        draw.text((20, 20), text_output, fill='black', font=font)
        
        try:
            image.save(filename)
            return True
        except Exception as e:
            print(f"JPG Export Error: {e}")
            return False

    def export_activity_log_csv(self, filename="activity_log.csv"):
        if not self.data:
            return False
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                header = ["Date", "Network Name", "AID", "Field", "Old Value", "New Value", "Note"]
                writer.writerow(header)
                for item in self.data:
                    writer.writerow([
                        item.get('date'),
                        item.get('network_name'),
                        item.get('network_aid'),
                        item.get('field'),
                        item.get('old_value'),
                        item.get('new_value'),
                        item.get('note')
                    ])
            return True
        except Exception as e:
            print(f"Activity Log CSV Error: {e}")
            return False

    def send_to_telegram(self, chat_id, files):
        if not chat_id:
            return False
            
        url_doc = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
        # url_photo = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto" # For JPG as photo
        
        success = True
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(url_doc, data={"chat_id": chat_id}, files={"document": f})
                    if response.status_code != 200:
                        print(f"Failed to send {file_path}: {response.text}")
                        success = False
            except Exception as e:
                print(f"Telegram Error for {file_path}: {e}")
                success = False
        return success
