from src.infrastructure import OracleContainer

def main():
    infra = OracleContainer()

    try:
        # 1. Start Container & Wait for Data Load
        infra.start()

        # 2. Print Connection Details for your other library
        print("\n" + "="*50)
        print("✅ ORACLE DATABASE IS READY & EXPOSED")
        print("="*50)
        print("🔗 Host:      localhost")
        print("🔌 Port:      1521")
        print("QRY Service:  FREEPDB1")
        print("👤 User:      PROD_OG_OWNR")
        print("🔑 Password:  ParserPassword123")
        print("="*50)
        print("You may now run your external Python module/library.")

    except Exception as e:
        print(f"❌ Error: {e}")
        # Optional: Stop it if setup failed
        # infra.stop() 

if __name__ == "__main__":
    main()