# Speaking Agent Backend

## Overview
The Speaking Agent is a backend application designed to facilitate live conversations with users, focusing on improving their English skills. It leverages the ChatGPT real-time API to provide interactive chat experiences and includes speech recognition and synthesis functionalities.

## Project Structure
```
speaking-agent-backend
├── src
│   ├── app.ts
│   ├── controllers
│   │   ├── chatController.ts
│   │   └── realtimeController.ts
│   ├── services
│   │   ├── openaiService.ts
│   │   └── speechService.ts
│   ├── middleware
│   │   ├── auth.ts
│   │   └── validation.ts
│   ├── routes
│   │   ├── api.ts
│   │   └── websocket.ts
│   ├── types
│   │   └── index.ts
│   └── utils
│       └── logger.ts
├── client
│   ├── index.html
│   ├── css
│   │   └── styles.css
│   ├── js
│   │   ├── app.js
│   │   └── websocket.js
│   └── assets
│       └── icons
├── package.json
├── tsconfig.json
├── .env.example
└── README.md
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   cd speaking-agent-backend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in the required values.

## Usage
1. Start the server:
   ```
   npm start
   ```

2. Access the client application by opening `client/index.html` in your web browser.

## Features
- Real-time chat with the ChatGPT API for language practice.
- Speech recognition and synthesis for interactive learning.
- User authentication and message validation for secure interactions.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.