# Discord Channel Summarizer

This project retrieves messages from specific Discord channels and generates summaries using the Anthropic API. It's designed to provide concise updates from multiple Discord channels, focusing on recent and significant events.

## Setup

1. Clone the repository:   ```
   git clone https://github.com/ghsaboias/discord-summarizer.git
   cd discord-summarizer   ```

2. Install dependencies:   ```
   pip install -r requirements.txt   ```

3. Copy `.env.example` to `.env` and fill in your actual values:   ```
   cp .env.example .env   ```
   Then edit the `.env` file with your Discord token, Guild ID, and Anthropic API key.

4. Run the script:   ```
   python main.py   ```

## Requirements

- Python 3.7+
- Discord Bot Token
- Anthropic API Key

## Usage

1. Ensure your Discord bot is added to the server (guild) you want to summarize channels from.

2. The script will automatically retrieve messages from channels that meet certain criteria (e.g., having an emoji at the start of the channel name).

3. For each relevant channel, the script will:
   - Retrieve recent messages
   - Use the Anthropic API to generate a summary of the latest updates
   - Save the summaries to `output.txt`

4. The `output.txt` file will contain summaries for each channel, including:
   - Channel name
   - Number of messages analyzed
   - Latest updates with dates, locations, event descriptions, parties involved, and relevant numbers

5. You can customize the channel selection criteria and summary format by modifying the `main.py` file.

## Troubleshooting

- If you encounter authentication errors, make sure your Discord token and Anthropic API key are correct in the `.env` file.
- If certain channels are not being summarized, check that they meet the criteria defined in the `get_guild_channels` function.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
