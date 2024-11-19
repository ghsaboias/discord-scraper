# Discord Bot Message Scraper and Summarizer

This project provides a Python script for scraping messages from a specific Discord channel and creating an HTML report with the summary, or a simple text summary made with Claude AI.

## Features

- Scrape messages from a specific Discord channel
- Generate a summary using the Anthropic Claude AI model
- Create an HTML report with the summary

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/ghsaboias/discord-summarizer.git
   cd discord-summarizer
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Copy the `.env.example` file to `.env`:

   ```
   cp .env.example .env
   ```

2. Edit the `.env` file and add your Discord token, Guild ID, and Anthropic API key:
   ```
   DISCORD_TOKEN=your_discord_token_here
   GUILD_ID=your_guild_id_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Usage - scrape_single_server.py

Run the script with the desired channel name as an argument, or without arguments to select a channel from the list:

```
python scrape_single_server.py <channel_name>
```

Replace `<channel_name>` with the name of the Discord channel you want to scrape, or leave blank to select a channel from the list.

The script will:

1. Retrieve messages from the specified channel
2. Filter messages from the last 24 hours
3. Generate a summary using Claude AI
4. Save the summary to a file in the `summaries` directory

## Usage - scrape_and_create_html_report.py

Run the script with the desired channel name as an argument, or without arguments to select a channel from the list:

```
python scrape_and_create_html_report.py <channel_name>
```

Replace `<channel_name>` with the name of the Discord channel you want to scrape, or leave blank to select a channel from the list.

The script will:

1. Retrieve messages from the specified channel
2. Filter messages from the last 24 hours
3. Create an HTML report with the summary

## Requirements

- Python 3.6+
- Discord API access (Bot token)
- Anthropic API key
- Required Python packages (see `requirements.txt`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

## Author

GitHub: [@ghsaboias](https://github.com/ghsaboias)
