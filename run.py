# Entry point for the Flask application.
# Imports the application factory function `create_app` from the `app` module
# and uses it to create the Flask app instance.
#
# When this script is run directly (not imported as a module), the development
# server starts on port 5001 with debug mode enabled, which provides:
#   - Automatic reloading on code changes
#   - An interactive debugger in the browser on errors
#   - Detailed error messages in the console
#
# Note: Debug mode should be disabled in production environments.

from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5001)