import sys
import traceback

try:
    from app import create_app
    from config import Config

    application = create_app()
    print("Application created successfully!", file=sys.stderr)
except Exception as e:
    print(f"ERROR creating application: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    raise

if __name__ == '__main__':
    application.run(
        host=Config.HOST if hasattr(Config, 'HOST') else '0.0.0.0',
        port=Config.PORT if hasattr(Config, 'PORT') else 5000,
        debug=Config.DEBUG if hasattr(Config, 'DEBUG') else True
    )
