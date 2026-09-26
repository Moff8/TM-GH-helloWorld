"""
RFID Card Access System with LCD1602 Display
Main application loop that integrates all functions
"""

from LCD1602 import LCD1602
from mfrc522 import WS1850S
from gpiozero import Buzzer, LED
import time
import os


# Initialize devices
def initialize_devices():
    """Initialize all hardware devices."""
    try:
        lcd = LCD1602(16, 2)
        rfid = WS1850S()
        buzzer = Buzzer(20)
        led = LED(16)
        
        print("✓ All devices initialized successfully")
        return lcd, rfid, buzzer, led
    except Exception as e:
        print(f"✗ Error initializing devices: {e}")
        return None, None, None, None


def log_card_audit(card_uid, username, filename='card_audit.csv'):
    """Write an audit log entry for a card read with timestamp."""
    from datetime import datetime
    
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a') as f:
            if not file_exists:
                f.write("Timestamp,Card UID,Username\n")
            f.write(f"{timestamp},{card_uid},{username}\n")
        
        print(f"✓ Audit logged: {timestamp} - {card_uid} ({username})")
        return True
    
    except Exception as e:
        print(f"✗ Error writing audit log: {e}")
        return False


def display_user_on_lcd(username, lcd):
    """Display username and current date/time on LCD1602 display."""
    from datetime import datetime
    
    try:
        now = datetime.now()
        date_str = now.strftime("%m/%d %H:%M")
        
        username_display = username[:16].ljust(16)
        date_display = date_str[:16].ljust(16)
        
        lcd.clear()
        lcd.setCursor(0, 0)
        lcd.printout(username_display)
        lcd.setCursor(0, 1)
        lcd.printout(date_display)
        
        return True
    
    except Exception as e:
        print(f"✗ Error displaying on LCD: {e}")
        return False


def add_card(card_uid, username, card_dict):
    """Add a new card to the dictionary."""
    if card_uid in card_dict:
        print(f"Card {card_uid} already exists: {card_dict[card_uid]}")
        return card_dict
    
    card_dict[card_uid] = username
    print(f"✓ Added: {card_uid} -> {username}")
    return card_dict


def update_card(card_uid, username, card_dict):
    """Update an existing card in the dictionary."""
    if card_uid not in card_dict:
        print(f"Card {card_uid} not found")
        return card_dict
    
    old_username = card_dict[card_uid]
    card_dict[card_uid] = username
    print(f"✓ Updated: {card_uid} from {old_username} to {username}")
    return card_dict


def delete_card(card_uid, card_dict):
    """Delete a card from the dictionary."""
    if card_uid not in card_dict:
        print(f"Card {card_uid} not found")
        return card_dict
    
    username = card_dict[card_uid]
    del card_dict[card_uid]
    print(f"✓ Deleted: {card_uid} ({username})")
    return card_dict


def view_cards(card_dict):
    """Display all cards in the dictionary."""
    if not card_dict:
        print("No cards in dictionary")
        return
    
    print("\n" + "="*40)
    print("Registered Cards")
    print("="*40)
    
    for card_uid, username in card_dict.items():
        print(f"{card_uid:<15} -> {username}")
    
    print("="*40 + "\n")


def audit_log_to_html(csv_file='card_audit.csv', html_file='card_audit.html'):
    """Convert audit log CSV to HTML format."""
    from datetime import datetime
    
    try:
        if not os.path.isfile(csv_file):
            print(f"Error: {csv_file} not found")
            return False
        
        with open(csv_file, 'r') as f:
            lines = f.readlines()
        
        if len(lines) < 1:
            print("Error: CSV file is empty")
            return False
        
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Card Audit Log</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th {
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
            border: 1px solid #ddd;
        }
        td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        tr:hover {
            background-color: #f0f0f0;
        }
        .footer {
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <h1>Card Audit Log</h1>
    <table>
        <tr>
"""
        
        header = lines[0].strip().split(',')
        for col in header:
            html_content += f"            <th>{col}</th>\n"
        
        html_content += "        </tr>\n"
        
        for line in lines[1:]:
            if line.strip():
                html_content += "        <tr>\n"
                cols = line.strip().split(',')
                for col in cols:
                    html_content += f"            <td>{col}</td>\n"
                html_content += "        </tr>\n"
        
        html_content += "    </table>\n"
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html_content += f"""
    <div class="footer">
        <p>Generated: {now}</p>
        <p>Total records: {len(lines) - 1}</p>
    </div>
</body>
</html>
"""
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        print(f"✓ HTML file created: {html_file}")
        return True
    
    except Exception as e:
        print(f"Error converting to HTML: {e}")
        return False


def process_card_read(card_uid, card_dict, lcd, buzzer, led):
    """Process a card read: lookup user, display on LCD, and log to audit file."""
    try:
        username = card_dict.get(card_uid)
        
        if username:
            print(f"✓ Card recognized: {username}")
            
            # Display on LCD
            display_user_on_lcd(username, lcd)
            
            # Log to audit file
            log_card_audit(card_uid, username)
            
            # Beep and flash LED
            buzzer.on()
            time.sleep(0.1)
            buzzer.off()
            led.on()
            time.sleep(1)
            led.off()
            
            return username
        else:
            print(f"✗ Unknown card: {card_uid}")
            
            # Display error on LCD
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.printout("Unknown Card")
            lcd.setCursor(0, 1)
            lcd.printout(card_uid[:16])
            
            # Log unknown card
            log_card_audit(card_uid, "UNKNOWN")
            
            return None
    
    except Exception as e:
        print(f"Error processing card: {e}")
        return None


def display_menu():
    """Display main menu options."""
    print("\n" + "="*40)
    print("RFID Card Access System")
    print("="*40)
    print("1. Read card (wait for tap)")
    print("2. Add new card")
    print("3. Update card")
    print("4. Delete card")
    print("5. View all cards")
    print("6. Generate HTML report")
    print("7. Exit")
    print("="*40)


def main_loop():
    """Main application loop."""
    print("Starting RFID Card Access System...\n")
    
    # Initialize devices
    lcd, rfid, buzzer, led = initialize_devices()
    if not lcd:
        print("Failed to initialize devices. Exiting.")
        return
    
    # Display welcome message
    lcd.clear()
    lcd.setCursor(0, 0)
    lcd.printout("Access System")
    lcd.setCursor(0, 1)
    lcd.printout("Ready")
    time.sleep(2)
    
    # Card dictionary - add your cards here
    cards = {
        'FF AA BB CC': 'john_smith',
        'DD EE FF 11': 'jane_doe',
        '12 34 56 78': 'bob_jones'
    }
    
    # Main loop
    running = True
    while running:
        display_menu()
        choice = input("Enter choice (1-7): ").strip()
        
        if choice == '1':
            # Read card
            print("\nWaiting for card tap (press Ctrl+C to cancel)...")
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.printout("Waiting for")
            lcd.setCursor(0, 1)
            lcd.printout("card...")
            
            try:
                start_time = time.time()
                while time.time() - start_time < 30:  # 30 second timeout
                    if rfid.is_new_card_present():
                        uid = rfid.read_card_uid()
                        if uid:
                            uid_hex = ' '.join([f'{b:02X}' for b in uid])
                            print(f"\nCard detected: {uid_hex}")
                            process_card_read(uid_hex, cards, lcd, buzzer, led)
                            break
                    time.sleep(0.1)
                else:
                    print("Timeout: No card detected")
                    lcd.clear()
                    lcd.setCursor(0, 0)
                    lcd.printout("No Card")
                    lcd.setCursor(0, 1)
                    lcd.printout("Detected")
                    time.sleep(2)
            
            except KeyboardInterrupt:
                print("Cancelled")
        
        elif choice == '2':
            # Add new card
            print("\nPlace new card on reader...")
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.printout("Tap new card")
            
            try:
                start_time = time.time()
                while time.time() - start_time < 30:
                    if rfid.is_new_card_present():
                        uid = rfid.read_card_uid()
                        if uid:
                            uid_hex = ' '.join([f'{b:02X}' for b in uid])
                            print(f"Card UID: {uid_hex}")
                            
                            username = input("Enter username: ").strip()
                            if username:
                                cards = add_card(uid_hex, username, cards)
                            break
                    time.sleep(0.1)
            
            except KeyboardInterrupt:
                print("Cancelled")
        
        elif choice == '3':
            # Update card
            card_uid = input("Enter card UID (e.g., FF AA BB CC): ").strip()
            username = input("Enter new username: ").strip()
            if card_uid and username:
                cards = update_card(card_uid, username, cards)
        
        elif choice == '4':
            # Delete card
            card_uid = input("Enter card UID to delete: ").strip()
            cards = delete_card(card_uid, cards)
        
        elif choice == '5':
            # View all cards
            view_cards(cards)
        
        elif choice == '6':
            # Generate HTML report
            audit_log_to_html()
        
        elif choice == '7':
            # Exit
            print("Shutting down...")
            lcd.clear()
            lcd.setCursor(0, 0)
            lcd.printout("Goodbye!")
            time.sleep(2)
            lcd.clear()
            running = False
        
        else:
            print("Invalid choice. Please try again.")
        
        time.sleep(0.5)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nApplication stopped by user")
    except Exception as e:
        print(f"\nFatal error: {e}")
