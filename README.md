# Raspberry Pi Home Automation Project

This project has desinged for geting secured home via. raspberry pi 4b and upper versions.

## Work principe

Via head changed YoLO raspberry pi may classify if there is a people or not. 
If there is someone it starts to recording the video.
Whene camera stop to see somenone it sends a video on the chat that you want!

## Features

- Control home appliances via GPIO
- Monitor sensors (temperature, humidity, camera)
- Web interface for remote control (Not ended)
- Easy to extend and customize

## Requirements

- Raspberry Pi (4b and upper)
- Raspbian OS or compatible Linux distribution
- Python 3.x
- Required Python libraries (see below)

## Setup

1. **Clone the repository:**

   ```sh
   git clone https://github.com/Davitestro/Raspbery-homealarm
   cd "Rasbpery_pi Home"
   ```
2. **Install dependencies:**

   ```sh
   pip3 install -r requirements.txt
   ```
3. **Connect your hardware:**

   - Attach sensors and relays to the appropriate GPIO pins as described in the code or documentation.
4. **Run the main script:**

   ```sh
   python3 Object_recorder.py
   ```

   ```sh
   python3 Alarm.py
   ```

## Usage

- Follow on-screen instructions or access the web interface (if available).
- Modify configuration files to match your hardware setup.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
