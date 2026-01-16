import sys
import os
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from network_manager import NetworkManager
from network_exporter import NetworkExporter
from datetime import datetime

console = Console()
manager = NetworkManager()

def display_table(data):
    table = Table(title="Network Management List")

    table.add_column("AID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Building", style="green")
    table.add_column("IP Location", style="yellow")
    table.add_column("Public IP", style="blue")
    table.add_column("Private IP", style="blue")
    table.add_column("Bandwidth", style="white")
    table.add_column("Status", justify="center")
    table.add_column("Install Date", style="dim")

    for item in data:
        status_style = "green" if item['status'].lower() == 'active' else "red" if item['status'].lower() == 'suspended' else "white"
        table.add_row(
            str(item.get('aid')),
            item.get('name'),
            item.get('building'),
            item.get('ip_location'),
            item.get('public_ip'),
            item.get('private_ip'),
            item.get('bandwidth'),
            f"[{status_style}]{item.get('status')}[/{status_style}]",
            item.get('install_date')
        )

    console.print(table)

def add_network():
    console.print(Panel("Add New Network Entry", style="bold green"))
    
    aid = Prompt.ask("AID (e.g. NAA-17797)", default="N/A")
    name = Prompt.ask("Name")
    building = Prompt.ask("Building")
    ip_location = Prompt.ask("IP Location")
    public_ip = Prompt.ask("Public IP")
    private_ip = Prompt.ask("Private IP")
    bandwidth = Prompt.ask("Bandwidth")
    
    status = Prompt.ask("Status", choices=["active", "suspended", "inactive"], default="active")
    install_date = Prompt.ask("Install Date (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))

    entry = {
        "aid": aid,
        "name": name,
        "building": building,
        "ip_location": ip_location,
        "public_ip": public_ip,
        "private_ip": private_ip,
        "bandwidth": bandwidth,
        "status": status,
        "install_date": install_date
    }

    new_id = manager.add_entry(entry)
    console.print(f"[bold green]Successfully added network entry with AID: {new_id}[/bold green]")

def get_identifier():
    choice = Prompt.ask("Identify by", choices=["aid", "name"], default="aid")
    if choice == "aid":
        return Prompt.ask("Enter AID")
    else:
        return Prompt.ask("Enter Name")

def delete_network():
    console.print(Panel("Delete Network Entry", style="bold red"))
    identifier = get_identifier()
    if identifier is None:
        console.print("[red]Invalid identifier[/red]")
        return
        
    if manager.delete_entry(identifier):
        console.print(f"[bold green]Successfully deleted entry: {identifier}[/bold green]")
    else:
        console.print(f"[red]Entry not found: {identifier}[/red]")

def update_network():
    console.print(Panel("Update Network Entry", style="bold blue"))
    identifier = get_identifier()
    if identifier is None:
        console.print("[red]Invalid identifier[/red]")
        return
        
    entry = manager.get_entry(identifier)
    if not entry:
        console.print(f"[red]Entry not found: {identifier}[/red]")
        return

    update_mode = Prompt.ask("Update Mode", choices=["all", "column"], default="column")
    updates = {}

    if update_mode == "all":
        updates["name"] = Prompt.ask("Name", default=entry.get('name', ''))
        updates["building"] = Prompt.ask("Building", default=entry.get('building', ''))
        updates["ip_location"] = Prompt.ask("IP Location", default=entry.get('ip_location', ''))
        updates["public_ip"] = Prompt.ask("Public IP", default=entry.get('public_ip', ''))
        updates["private_ip"] = Prompt.ask("Private IP", default=entry.get('private_ip', ''))
        updates["bandwidth"] = Prompt.ask("Bandwidth", default=entry.get('bandwidth', ''))
        updates["status"] = Prompt.ask("Status", choices=["active", "suspended", "inactive"], default=entry.get('status', 'active'))
    else:
        column = Prompt.ask("Select Column", choices=["name", "building", "ip_location", "public_ip", "private_ip", "bandwidth", "status"])
        if column == "status":
            updates[column] = Prompt.ask("New Status", choices=["active", "suspended", "inactive"], default=entry.get('status', 'active'))
        else:
            updates[column] = Prompt.ask(f"New {column}", default=entry.get(column, ''))

    note = Prompt.ask("Update Note (e.g. Customer Upgrade)")
    
    if manager.update_entry(identifier, updates, note):
        console.print("[bold green]Entry updated successfully![/bold green]")
    else:
        console.print("[yellow]No changes made or error occurred.[/yellow]")

def activity_log():
    console.print(Panel("Activity Log", style="bold magenta"))
    console.print("Select category to view history:")
    choices = ["all", "bandwidth", "private_ip", "public_ip", "ip_location", "status"]
    category = Prompt.ask("Category", choices=choices, default="all")
    
    logs = manager.get_activity_log(category)
    
    table = Table(title=f"Activity Log ({category.upper()})")
    table.add_column("Date", style="dim")
    table.add_column("Network (AID)", style="cyan")
    table.add_column("Field", style="magenta")
    table.add_column("Old Value", style="red")
    table.add_column("New Value", style="green")
    table.add_column("Note", style="white")

    for log in logs:
        table.add_row(
            log.get('date'),
            f"{log.get('network_name')} ({log.get('network_aid')})",
            log.get('field', 'N/A'),
            str(log.get('old_value', '-')),
            str(log.get('new_value', '-')),
            log.get('note', '')
        )
    
    console.print(table)

    
    console.print(table)

def export_menu():
    console.print(Panel("Export Data", style="bold cyan"))
    
    # 1. Filter Selection
    data_to_export = manager.get_data()
    filter_choice = Prompt.ask("Export Filter", choices=["all", "building"], default="all")
    
    if filter_choice == "building":
        buildings = manager.get_buildings()
        if not buildings:
            console.print("[red]No buildings found.[/red]")
            return
        
        console.print("Available Buildings:")
        for idx, b in enumerate(buildings, 1):
            console.print(f"{idx}. {b}")
            
        b_index = Prompt.ask("Select Building Number", default="1")
        if b_index.isdigit() and 1 <= int(b_index) <= len(buildings):
            selected_building = buildings[int(b_index)-1]
            data_to_export = [d for d in data_to_export if d.get('building') == selected_building]
            console.print(f"[green]Filtered for building: {selected_building}[/green]")
        else:
            console.print("[red]Invalid selection, exporting all.[/red]")

    # 2. Activity Log Selection
    include_log = Prompt.ask("Include Activity Log?", choices=["y", "n"], default="n") == "y"

    # Generate Files
    files_generated = []
    
    # Export Network List
    exporter = NetworkExporter(data_to_export)
    with console.status("Generating Network List..."):
        if exporter.export_csv("network_list.csv"):
            files_generated.append("network_list.csv")
            console.print("[green]network_list.csv created.[/green]")
        if exporter.export_jpg("network_list.jpg", title="Network List"):
             files_generated.append("network_list.jpg")
             console.print("[green]network_list.jpg created.[/green]")

    # Export Activity Log
    if include_log:
        logs = manager.get_activity_log() # Get all logs
        # If filtering by building, we should filter logs too?
        # User said "Select all build and select building to export", implies filtering applies to everything.
        if filter_choice == "building":
            # Filter logs where network_name is in our filtered data list (or match building logic again)
            # Simpler: Filter logs logic here
             # We have data_to_export which contains the filtered networks.
             # Get AIDs of filtered networks
            filtered_aids = [d.get('aid') for d in data_to_export]
            logs = [l for l in logs if l.get('network_aid') in filtered_aids]
        
        log_exporter = NetworkExporter(logs)
        with console.status("Generating Activity Log..."):
            if log_exporter.export_activity_log_csv("activity_log.csv"):
                files_generated.append("activity_log.csv")
                console.print("[green]activity_log.csv created.[/green]")
            if log_exporter.export_jpg("activity_log.jpg", title="Activity Log"):
                files_generated.append("activity_log.jpg")
                console.print("[green]activity_log.jpg created.[/green]")

    # 3. Telegram
    if Prompt.ask("Send to Telegram?", choices=["y", "n"]) == "y":
        saved_chat_id = manager.get_telegram_chat_id()
        default_prompt = f" (Default: {saved_chat_id})" if saved_chat_id else ""
        
        chat_id_input = Prompt.ask(f"Enter Telegram Chat ID/Username{default_prompt}")
        
        # Use input if provided, otherwise use saved. If neither, fail.
        chat_id = chat_id_input if chat_id_input else saved_chat_id
        
        if not chat_id:
            console.print("[red]No Chat ID provided.[/red]")
        else:
            # Save the used ID for next time
            manager.set_telegram_chat_id(chat_id)
            
            if files_generated:
                with console.status(f"Sending {len(files_generated)} files to Telegram ({chat_id})..."):
                    if exporter.send_to_telegram(chat_id, files_generated):
                        console.print("[bold green]All files sent to Telegram successfully![/bold green]")
                    else:
                        console.print("[bold red]Some files failed to send.[/bold red]")

def browse_files(start_dir="."):
    """Interactive file browser for selecting CSV files."""
    current_dir = os.path.abspath(start_dir)
    
    while True:
        console.clear()
        console.print(Panel(f"Browsing: [bold blue]{current_dir}[/bold blue]", style="bold yellow"))
        
        try:
            items = os.listdir(current_dir)
        except PermissionError:
            console.print("[red]Permission Denied[/red]")
            current_dir = os.path.dirname(current_dir)
            Prompt.ask("Press Enter to continue")
            continue
            
        dirs = sorted([d for d in items if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.')])
        files = sorted([f for f in items if os.path.isfile(os.path.join(current_dir, f)) and f.lower().endswith('.csv')])
        
        # Display Navigation
        console.print("0.  [bold red].. (Up One Level)[/bold red]")
        
        choices = ["0"]
        idx = 1
        
        # List Directories
        if dirs:
            console.print("[bold]Directories:[/bold]")
            for d in dirs:
                console.print(f"{idx}. [bold cyan]{d}/[/bold cyan]")
                choices.append(str(idx))
                idx += 1
                
        # List Files
        file_start_idx = idx
        if files:
            console.print("[bold]Files:[/bold]")
            for f in files:
                console.print(f"{idx}. [green]{f}[/green]")
                choices.append(str(idx))
                idx += 1
                
        console.print("-" * 40)
        console.print("[dim]Enter number, 'cd <path>', or 'exit'[/dim]")
        
        selection = Prompt.ask("Select", default="0") # Default up?
        
        if selection == "exit":
            return None
            
        if selection == "0" or selection == "..":
            current_dir = os.path.dirname(current_dir)
            continue
            
        if selection.startswith("cd "):
            path = selection[3:].strip()
            new_path = os.path.join(current_dir, path)
            if os.path.exists(new_path) and os.path.isdir(new_path):
                current_dir = os.path.abspath(new_path)
            else:
                console.print(f"[red]Invalid directory: {path}[/red]")
                Prompt.ask("Press Enter")
            continue
            
        if selection in choices:
            choice_idx = int(selection)
            # Check if dir or file
            if choice_idx < file_start_idx:
                # It's a directory
                dir_name = dirs[choice_idx - 1]
                current_dir = os.path.join(current_dir, dir_name)
            else:
                # It's a file
                file_name = files[choice_idx - file_start_idx]
                return os.path.join(current_dir, file_name)
        else:
            # Maybe they typed a path?
            if os.path.exists(selection) and os.path.isfile(selection):
                return os.path.abspath(selection)
            console.print("[red]Invalid selection[/red]")
            Prompt.ask("Press Enter")

def import_menu():
    console.print(Panel("Import CSV", style="bold yellow"))
    
    console.print("1. Current Directory")
    console.print("2. Browse/Navigate")
    choice = Prompt.ask("Select Method", choices=["1", "2"], default="1")
    
    if choice == "1":
        filename = Prompt.ask("Enter CSV Filename", default="network_list.csv")
    else:
        filename = browse_files()
        
    if not filename:
        return # User cancelled

    if not os.path.exists(filename):
        console.print(f"[red]File '{filename}' not found.[/red]")
        return

    if Prompt.ask(f"Import from '{filename}'? (Duplicates will be skipped)", choices=["y", "n"]) == "y":
        with console.status("Importing..."):
            result = manager.import_from_csv(filename)
            
        if result.get("error"):
            console.print(f"[red]Error: {result['error']}[/red]")
        else:
            console.print(f"[green]Import Complete![/green]")
            console.print(f"Added: [bold]{result['added']}[/bold]")
            console.print(f"Skipped (Duplicates): [dim]{result['skipped']}[/dim]")

def search_network():
    query = Prompt.ask("Enter search term (Name, IP, or Building)")
    results = manager.search(query)
    if results:
        display_table(results)
    else:
        console.print("[red]No results found.[/red]")

def main():
    while True:
        console.print("\n[bold]Network Management CLI[/bold]", justify="center")
        console.print("1. [bold cyan]List[/bold cyan] All Networks")
        console.print("2. [bold green]Add[/bold green] New Network")
        console.print("3. [bold yellow]Search[/bold yellow] Network")
        console.print("4. [bold blue]Update[/bold blue] Network")
        console.print("5. [bold red]Delete[/bold red] Network")
        console.print("6. [bold red]Exit[/bold red]")
        console.print("7. [bold magenta]Activity Log[/bold magenta]")
        console.print("8. [bold cyan]Export & Telegram[/bold cyan]")
        console.print("9. [bold yellow]Import CSV[/bold yellow]")
        
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

        if choice == "1":
            display_table(manager.get_all())
        elif choice == "2":
            add_network()
        elif choice == "3":
            search_network()
        elif choice == "4":
            update_network()
        elif choice == "5":
            delete_network()
        elif choice == "6":
            console.print("Goodbye!")
            sys.exit()
        elif choice == "7":
            activity_log()
        elif choice == "8":
            export_menu()
        elif choice == "9":
            import_menu()

if __name__ == "__main__":
    main()
