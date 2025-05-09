# PsMCP-MCP-Server-for-Photoshop
An Extensive MCP server with several tools made using win32com to interact with Photoshop. Designing with Photoshop has never been more fun!

[![Watch Demo Video](example/image.png)](https://media-hosting.imagekit.io/0e939780eeb24fd9/PhotoshopMCP.mp4?Expires=1841334328&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=sV1V82oUaMEfNTNYOHGeU7H9gLc8SsuNgQHRthU9j0exVXaC88plw8JiDTCj6IzHlKkToY0x5Xi4NzGndgHTQHKGrIpVHxJvWUCzcfWlq6LA2NEv9Fb4Yn0tDDSkJyWdTT9ISXlCvIXuBNVPgX4VT5TGB7KRM90vC6wIX31LH6DxX6qd4sVaY1o-ydx9gCe~hN9kSMx9IWMXc1NC50mgv~n5nOjgde8NJdrKJPB0WBZylW7BitIRCtiO2O2v6~C4x6bqbC~UTdQMdjldp0AwNTv2M2XT7NtrXsXA-QKOPa6Be0ysMMakMsAJc6xmMR25FJHdwap9ObgimCTZ4J9fIQ__)


## Usage

 **Install Requirements**

   Activate your Python environment and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
 **Run Using the Gradio Client Provided**
 
   ![Gradio Example](example/gradio.png)
   Set Gemini Key in .env
   ```bash
   GEMINI_API_KEY=PASTE_YOUR_KEY_HERE
   ```
  Set Directories for PSDs, Assets and Exports
   ```bash
   PSD_DIRECTORY = r"D:\Photoshop Files"
   EXPORT_DIRECTORY = r"D:\PsMCP-Exports"
   ASSETS_DIR = r"D:\PsMCP-Assets"
   ```
  Run the App and connect to the Server
  
   ```bash
   python app.py
   ```
 **Configure Server with Any MCP Client (Claude, Cursor, etc)**

 Add Server to Config file as follows to access the tools
 
   ```bash
   {
    "mcpServers": {
      "PhotoshopAdv": {
        "command": "uv",
        "args": [
          "--directory",
          "Path/To/Directory",
          "run",
          "psMCP.py"
        ],
        "timeout": 60000 
      }
    }
  }
   ```

   
