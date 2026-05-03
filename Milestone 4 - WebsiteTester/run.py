import traceback

try:
    from app import app
    print("✅ app imported OK")
    app.run(debug=True, port=5000, use_reloader=False)
except Exception as e:
    print("❌ ERROR:")
    traceback.print_exc()