# Discord Message Summarizer - Full Stack Application

A full-stack application that scrapes messages from Discord channels and generates AI-powered summaries. The project consists of a Python backend for Discord message processing and a Next.js frontend for visualization and interaction.

## Features

- **Backend:**
  - Discord message scraping from specific channels
  - AI-powered message summarization using Claude AI
  - HTML and text summary generation
  - RESTful API endpoints

- **Frontend:**
  - Modern Next.js web interface
  - Real-time summary viewing
  - Channel selection and management
  - Responsive design with Tailwind CSS

## Prerequisites

- Node.js 18+ for the frontend
- Python 3.6+ for the backend
- Discord Bot Token
- Anthropic API Key

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your credentials:
   ```
   DISCORD_TOKEN=your_discord_token_here
   GUILD_ID=your_guild_id_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your configuration.

## Running the Application

### Backend

Start the Python backend server:
```bash
cd backend
python main.py
```

### Frontend

Start the Next.js development server:
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## API Documentation

The backend exposes the following endpoints:

- `GET /api/channels` - List available Discord channels
- `POST /api/summarize` - Generate summary for a specific channel

## Scripts

### Usage - scrape_single_server.py

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

### Usage - scrape_and_create_html_report.py

Run the script with the desired channel name as an argument, or without arguments to select a channel from the list:

```
python scrape_and_create_html_report.py <channel_name>
```

Replace `<channel_name>` with the name of the Discord channel you want to scrape, or leave blank to select a channel from the list.

The script will:

1. Retrieve messages from the specified channel
2. Filter messages from the last 24 hours
3. Create an HTML report with the summary

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Authors

GitHub: [@ghsaboias](https://github.com/ghsaboias)

## Acknowledgments

- Discord.py library
- Anthropic Claude AI
- Next.js team
- All contributors and supporters
